package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.security.*;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.MountainRangeSurvey.*;

/** Immutable continuation pages over an unchanged, validated V1 survey base.
 * Page exhaustion continues the SAME frontier; only its true boundary completes
 * a range. Fresh processes must audit every observation against native terrain.
 * This is an owned server-thread journal, not concurrent multi-writer storage. */
public final class PagedMountainRangeJournal {
    private static final int MAGIC=0x49434d50, VERSION=1, MAX_PAGE_BYTES=65536;
    private final Path base,directory;
    private final MountainRangeJournal.Identity identity;
    private final String baseHash,binding;
    private final MountainRangeSurvey survey;
    private final Object baseFileKey;
    private final long baseSize;
    private final java.nio.file.attribute.FileTime baseTime;
    private final List<String> pageHashes=new ArrayList<>();
    private int verified;
    private boolean changed,completeAudited,failed;
    private byte[] expectedHead;
    private String chain,component;
    private Range range;

    private PagedMountainRangeJournal(Path path,MountainRangeJournal.Identity identity)throws IOException{
        base=path.toAbsolutePath().normalize();directory=base.resolveSibling(base.getFileName()+".pages");this.identity=identity;
        var legacy=MountainRangeJournal.open(base,identity);
        var snapshot=legacy.savedSnapshot();
        // A changed legacy journal must never be laundered into continuation.
        changed=legacy.progress().phase()==MountainRangeJournal.Phase.HELD_CHANGED;
        survey=MountainRangeSurvey.restore(snapshot);
        var attributes=attributes(base);baseFileKey=attributes.fileKey();baseSize=attributes.size();baseTime=attributes.lastModifiedTime();
        baseHash=hash(Files.readAllBytes(base));chain=baseHash;
        binding=hash(("IC_MOUNTAIN_PAGES_V1\n"+identity.fingerprint()+"\n"+baseHash).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        if(Files.exists(directory,LinkOption.NOFOLLOW_LINKS))loadPages();
        checkBase(true);
    }
    public static PagedMountainRangeJournal open(Path path,MountainRangeJournal.Identity identity)throws IOException{
        return new PagedMountainRangeJournal(path,Objects.requireNonNull(identity));
    }
    public static PagedMountainRangeJournal create(Path path,MountainRangeJournal.Identity identity)throws IOException{
        MountainRangeJournal.create(path,identity);
        return open(path,identity);
    }
    public MountainRangeJournal.Identity identity(){return identity;}
    public Snapshot savedSnapshot()throws IOException{checkBase(false);return survey.snapshot();}
    public List<Observation> observationsSince(int cursor)throws IOException{checkBase(false);return survey.observationsSince(cursor);}
    public Status savedStatus()throws IOException{checkBase(false);return survey.progress().status();}
    public boolean observedMountain(Column column){return survey.observedMountain(column);}
    public MountainRangeJournal.Progress progress()throws IOException{
        checkBase(false);var p=survey.progress();MountainRangeJournal.Phase phase;
        if(changed)phase=MountainRangeJournal.Phase.HELD_CHANGED;
        else if(p.status()==Status.HELD_DOMAIN)phase=MountainRangeJournal.Phase.HELD_DOMAIN;
        else if(verified<p.observations())phase=MountainRangeJournal.Phase.VERIFYING;
        else if(p.status()==Status.HELD_LIMIT||p.status()==Status.SEARCHING)phase=MountainRangeJournal.Phase.DISCOVERING;
        else phase=MountainRangeJournal.Phase.valueOf(p.status().name());
        return new MountainRangeJournal.Progress(phase,p,verified);
    }
    public MountainRangeJournal.Progress advance(int budget,Terrain terrain)throws IOException{
        return locked(()->advanceOwned(budget,terrain));
    }
    private MountainRangeJournal.Progress advanceOwned(int budget,Terrain terrain)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Mountain read budget1..4096");Objects.requireNonNull(terrain);
        checkBase(false);checkNoPending();
        if(changed||survey.progress().status()==Status.HELD_DOMAIN)return progress();
        int remaining=budget;
        while(remaining>0&&verified<survey.progress().observations()){
            var row=survey.observation(verified);remaining--;
            if(terrain.mountain(row.column().x(),row.column().z())!=row.mountain()){
                persist(List.of(),true);changed=true;return progress();
            }
            verified++;
        }
        if(remaining==0||survey.progress().status()==Status.COMPLETE||survey.progress().status()==Status.NOT_MOUNTAIN)return progress();
        int before=survey.progress().observations();
        Exception failure=null;
        try{
            // One input budget can cross a small test page, but never reads more
            // columns than requested. The page limit is a work segment, not an
            // artificial mountain boundary or resource allocation boundary.
            while(remaining>0&&(survey.progress().status()==Status.SEARCHING||survey.progress().status()==Status.HELD_LIMIT)){
                if(survey.progress().status()==Status.HELD_LIMIT)survey.continueWorkPage(identity.maximumObservations());
                int count=survey.progress().observations();survey.advance(remaining,terrain);
                remaining-=survey.progress().observations()-count;
            }
        }catch(IOException|RuntimeException e){failure=e;}
        var added=survey.observationsSince(before);
        if(!added.isEmpty()){
            try{persist(added,false);verified=survey.progress().observations();}
            catch(IOException persistence){if(failure!=null)persistence.addSuppressed(failure);throw persistence;}
        }
        if(failure instanceof IOException io)throw io;
        if(failure instanceof RuntimeException runtime)throw runtime;
        return progress();
    }
    public Range completedRange()throws IOException{
        requireComplete();if(range==null)range=survey.completedRange();return range;
    }
    public String completedIdentity()throws IOException{
        requireComplete();if(component!=null)return component;
        var result=completedRange();var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        // Exactly the legacy identity domain and canonical encoding. Paging and
        // entry seed cannot manufacture a new allocation for the same component.
        out.writeUTF("IC_CONNECTED_MOUNTAIN_V1");out.writeUTF(identity.environmentFingerprint());
        for(var list:List.of(result.members(),result.boundary())){out.writeInt(list.size());for(var column:list){out.writeInt(column.x());out.writeInt(column.z());}}
        out.flush();return component=hash(bytes.toByteArray());
    }
    private void requireComplete()throws IOException{
        if(progress().phase()!=MountainRangeJournal.Phase.COMPLETE)throw new IOException("Mountain range is not complete and currently verified");
        if(!completeAudited){checkBase(true);auditPages();completeAudited=true;}
    }
    private static BasicFileAttributes attributes(Path path)throws IOException{
        var a=Files.readAttributes(path,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
        if(!a.isRegularFile())throw new IOException("Mountain journal is not a regular file");return a;
    }
    private void checkBase(boolean full)throws IOException{
        if(failed)throw new IOException("Mountain continuation requires recovery after failed persistence");
        var a=attributes(base);
        if(a.size()!=baseSize||!a.lastModifiedTime().equals(baseTime)||!Objects.equals(a.fileKey(),baseFileKey))throw new IOException("Mountain base changed during owned session");
        if(full&&!hash(Files.readAllBytes(base)).equals(baseHash))throw new IOException("Mountain base checksum changed");
        // Commissioning authority is tiny and always checked, including after
        // completion. Full immutable payload checks occur at open and admission.
        var marker=base.resolveSibling(base.getFileName()+".started");
        if(!Arrays.equals(Files.readAllBytes(marker),HexFormat.of().parseHex(identity.fingerprint())))throw new IOException("Mountain commissioning identity changed");
        if(expectedHead!=null){
            if(!Arrays.equals(Files.readAllBytes(directory.resolve("head")),expectedHead))throw new IOException("Mountain continuation authority changed during owned session");
            if(!pageHashes.isEmpty()&&!hash(readPage(page(pageHashes.size()-1))).equals(chain))throw new IOException("Mountain continuation tip changed");
        }else if(Files.exists(directory,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unobserved mountain continuation authority");
    }
    private Path page(int index){return directory.resolve(String.format(Locale.ROOT,"page-%08d.bin",index));}
    private void checkNoPending()throws IOException{
        try(var stream=Files.newDirectoryStream(base.getParent(),base.getFileName()+".pending-*")){
            if(stream.iterator().hasNext())throw new IOException("Unresolved legacy mountain write");
        }
        if(Files.exists(directory,LinkOption.NOFOLLOW_LINKS))try(var stream=Files.newDirectoryStream(directory,"*.pending-*")){
            if(stream.iterator().hasNext())throw new IOException("Unresolved mountain continuation write");
        }
    }
    private void initialize()throws IOException{
        if(Files.exists(directory,LinkOption.NOFOLLOW_LINKS))return;
        Files.createDirectory(directory);
        try(var channel=FileChannel.open(directory.resolve("identity"),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            put(channel,HexFormat.of().parseHex(binding));channel.force(true);
        }
        writeHead(0,chain);
    }
    private void loadPages()throws IOException{
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid mountain page directory");
        if(!Arrays.equals(Files.readAllBytes(directory.resolve("identity")),HexFormat.of().parseHex(binding)))throw new IOException("Mountain continuation identity changed");
        checkNoPending();var paths=new ArrayList<Path>();
        try(var stream=Files.list(directory)){
            for(var path:stream.toList()){
                String name=path.getFileName().toString();
                if(name.equals("identity")||name.equals("head"))continue;
                if(!name.matches("page-[0-9]{8}\\.bin"))throw new IOException("Unknown mountain continuation entry: "+name);
                paths.add(path);
            }
        }
        paths.sort(Comparator.comparing(p->p.getFileName().toString()));
        for(int index=0;index<paths.size();index++){
            if(!paths.get(index).equals(page(index)))throw new IOException("Missing mountain continuation page");
            replay(readPage(page(index)),index);
        }
        expectedHead=Files.readAllBytes(directory.resolve("head"));
        if(!Arrays.equals(expectedHead,headBytes(pageHashes.size(),chain)))throw new IOException("Missing or unacknowledged mountain continuation page");
    }
    private byte[] readPage(Path path)throws IOException{
        var a=attributes(path);if(a.size()<48||a.size()>MAX_PAGE_BYTES)throw new IOException("Mountain page length");
        byte[] bytes=Files.readAllBytes(path);int n=bytes.length-32;
        if(!MessageDigest.isEqual(hashBytes(Arrays.copyOf(bytes,n)),Arrays.copyOfRange(bytes,n,bytes.length)))throw new IOException("Mountain page checksum");
        return bytes;
    }
    private void replay(byte[] bytes,int index)throws IOException{
        if(changed)throw new IOException("Continuation after changed-terrain hold");
        try(var in=new DataInputStream(new ByteArrayInputStream(bytes,0,bytes.length-32))){
            if(in.readInt()!=MAGIC||in.readInt()!=VERSION||!in.readUTF().equals(binding)||!in.readUTF().equals(chain)||in.readInt()!=index)throw new IOException("Mountain page identity/order");
            int start=in.readInt(),count=in.readInt();boolean held=flag(in);var status=Status.valueOf(in.readUTF());int limit=in.readInt();
            if(start!=survey.progress().observations()||count<0||count>4096||(count==0&&!held))throw new IOException("Mountain page cursor/count");
            for(int i=0;i<count;i++){
                int x=in.readInt(),z=in.readInt();boolean mountain=flag(in);
                if(survey.progress().status()==Status.HELD_LIMIT)survey.continueWorkPage(identity.maximumObservations());
                survey.advance(1,(px,pz)->{if(px!=x||pz!=z)throw new IOException("Noncanonical continued mountain frontier");return mountain;});
            }
            if(in.available()!=0||survey.progress().status()!=status||survey.snapshotLimit()!=limit)throw new IOException("Mountain page terminal state");
            changed=held;chain=hash(bytes);pageHashes.add(chain);
        }catch(IllegalArgumentException|IllegalStateException e){throw new IOException("Invalid mountain continuation",e);}
    }
    private void append(List<Observation> rows,boolean held)throws IOException{
        initialize();checkNoPending();int index=pageHashes.size();
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(VERSION);out.writeUTF(binding);out.writeUTF(chain);out.writeInt(index);
        out.writeInt(survey.progress().observations()-rows.size());out.writeInt(rows.size());out.writeBoolean(held);out.writeUTF(survey.progress().status().name());out.writeInt(survey.snapshotLimit());
        for(var row:rows){out.writeInt(row.column().x());out.writeInt(row.column().z());out.writeBoolean(row.mountain());}out.flush();
        byte[] body=bytes.toByteArray();bytes.writeBytes(hashBytes(body));byte[] expected=bytes.toByteArray();
        if(expected.length>MAX_PAGE_BYTES)throw new IOException("Mountain continuation exceeds page bound");
        Path target=page(index),pending=target.resolveSibling(target.getFileName()+".pending-"+UUID.randomUUID());
        if(Files.exists(target,LinkOption.NOFOLLOW_LINKS))throw new IOException("Mountain page already exists; no overwrite");
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){put(channel,expected);channel.force(true);}
        Files.move(pending,target,StandardCopyOption.ATOMIC_MOVE);
        if(!Arrays.equals(readPage(target),expected))throw new IOException("Mountain continuation readback differs");
        String next=hash(expected);writeHead(index+1,next);
        chain=next;pageHashes.add(chain);completeAudited=false;
    }
    private void persist(List<Observation> rows,boolean held)throws IOException{
        try{append(rows,held);}catch(IOException|RuntimeException|Error e){failed=true;throw e;}
    }
    private byte[] headBytes(int count,String tip)throws IOException{
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeUTF(binding);out.writeInt(count);out.writeUTF(tip);out.flush();bytes.writeBytes(hashBytes(bytes.toByteArray()));return bytes.toByteArray();
    }
    private void writeHead(int count,String tip)throws IOException{
        byte[] expected=headBytes(count,tip);Path head=directory.resolve("head"),pending=directory.resolve("head.pending-"+UUID.randomUUID());
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){put(channel,expected);channel.force(true);}
        Files.move(pending,head,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        if(!Arrays.equals(Files.readAllBytes(head),expected))throw new IOException("Mountain page-head readback differs");expectedHead=expected;
    }
    private void auditPages()throws IOException{
        checkNoPending();if(pageHashes.isEmpty())return;
        if(!Arrays.equals(Files.readAllBytes(directory.resolve("identity")),HexFormat.of().parseHex(binding)))throw new IOException("Mountain continuation identity changed");
        try(var stream=Files.list(directory)){
            if(stream.count()!=pageHashes.size()+2L)throw new IOException("Mountain continuation entry set changed");
        }
        for(int i=0;i<pageHashes.size();i++)if(!hash(readPage(page(i))).equals(pageHashes.get(i)))throw new IOException("Mountain continuation page changed");
    }
    private static boolean flag(DataInputStream in)throws IOException{int v=in.readUnsignedByte();if(v>1)throw new IOException("Invalid mountain flag");return v==1;}
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        Path lockPath=base.resolveSibling(base.getFileName()+".pages.lock");
        try(var channel=FileChannel.open(lockPath,StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            java.nio.channels.FileLock lock;try{lock=channel.tryLock();}catch(java.nio.channels.OverlappingFileLockException e){throw new IOException("Mountain continuation busy",e);}
            if(lock==null)throw new IOException("Mountain continuation busy");try(lock){return action.run();}
        }
    }
    private static void put(FileChannel channel,byte[] bytes)throws IOException{var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);}
    private static String hash(byte[] bytes){return HexFormat.of().formatHex(hashBytes(bytes));}
    private static byte[] hashBytes(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
