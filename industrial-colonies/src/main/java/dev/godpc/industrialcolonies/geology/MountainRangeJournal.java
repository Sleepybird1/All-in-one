package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.MountainRangeSurvey.*;

/** Saved topology discovery only. No ore placement, reserve allocation or implicit recovery. */
public final class MountainRangeJournal {
    public record Identity(long worldSeed,String dimension,String presetSha256,String classifierSha256,
                           Column seed,int maximumObservations){
        public Identity {
            if(dimension==null||dimension.length()>256||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")
                    ||presetSha256==null||!presetSha256.matches("[0-9a-f]{64}")
                    ||classifierSha256==null||!classifierSha256.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid mountain world/classifier identity");
            new MountainRangeSurvey(seed,maximumObservations);
        }
        public String fingerprint(){return digest(true);}
        public String environmentFingerprint(){return digest(false);}
        private String digest(boolean includeRequest){
            try{var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
                out.writeUTF("IC_MOUNTAIN_RANGE_CARDINAL_V1");out.writeLong(worldSeed);out.writeUTF(dimension);out.writeUTF(presetSha256);out.writeUTF(classifierSha256);
                if(includeRequest){out.writeInt(seed.x());out.writeInt(seed.z());out.writeInt(maximumObservations);}
                out.flush();return HexFormat.of().formatHex(hash(bytes.toByteArray()));
            }catch(IOException impossible){throw new AssertionError(impossible);}
        }
    }
    public enum Phase { VERIFYING, DISCOVERING, COMPLETE, NOT_MOUNTAIN, HELD_LIMIT, HELD_DOMAIN, HELD_CHANGED }
    public record Progress(Phase phase,MountainRangeSurvey.Progress topology,int verifiedObservations) {}
    private record Saved(Snapshot snapshot,boolean changed,String digest,MountainRangeSurvey.Progress topology) {}
    private static final int MAGIC=0x49434d52,VERSION=1;
    private final Path path;
    private final Identity identity;
    private String verifiedDigest="";
    private int verified;
    // Only an exact byte-for-byte disk match can reuse decoded topology. Marker,
    // pending-file and file-length checks still run on every read, under the lock.
    private byte[] cachedBytes;
    private Saved cachedSaved;
    private MountainRangeSurvey cachedSurvey;
    private String completedDigest="",componentIdentity;
    private Range completedRange;
    private void clearCache(){cachedBytes=null;cachedSaved=null;cachedSurvey=null;}
    private MountainRangeJournal(Path path,Identity identity){this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();this.identity=Objects.requireNonNull(identity);}
    public Identity identity(){return identity;}
    public static MountainRangeJournal create(Path path,Identity identity)throws IOException{
        var result=new MountainRangeJournal(path,identity);Files.createDirectories(result.path.getParent());
        if(!Files.isDirectory(result.path.getParent(),LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid mountain journal parent");
        return result.locked(()->{
            if(Files.exists(result.path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Mountain survey already exists");result.noPending();
            try(var marker=FileChannel.open(result.marker(),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
                put(marker,HexFormat.of().parseHex(identity.fingerprint()));marker.force(true);
            }
            var initial=new MountainRangeSurvey(identity.seed(),identity.maximumObservations());result.write(initial,false);return result;
        });
    }
    public static MountainRangeJournal open(Path path,Identity identity)throws IOException{
        var result=new MountainRangeJournal(path,identity);result.read();return result;
    }
    public Snapshot savedSnapshot()throws IOException{return locked(()->loaded().snapshot());}
    public Progress progress()throws IOException{return locked(()->progress(loaded()));}
    public Progress advance(int budget,Terrain terrain)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Mountain read budget1..4096");Objects.requireNonNull(terrain);
        return locked(()->{
            Saved before=loaded();var snapshot=before.snapshot();
            if(before.changed()||snapshot.status()==Status.HELD_LIMIT||snapshot.status()==Status.HELD_DOMAIN)return progress(before);
            int remaining=budget;
            while(remaining>0&&verified<snapshot.observations().size()){
                var row=snapshot.observations().get(verified);boolean actual=terrain.mountain(row.column().x(),row.column().z());remaining--;
                if(actual!=row.mountain()){
                    Saved held=write(cachedSurvey,true);verifiedDigest=held.digest();return progress(held);
                }
                verified++;
            }
            if(remaining==0||verified<snapshot.observations().size()||snapshot.status()!=Status.SEARCHING)return progress(before);
            // loaded() just checked the complete disk bytes against this state.
            // Detach it before mutation: a failed write must never publish it as
            // the previously saved prefix.
            var survey=cachedSurvey;clearCache();
            try{survey.advance(remaining,terrain);}
            catch(IOException|RuntimeException|Error failure){
                if(!survey.snapshot().equals(snapshot))try{acceptNew(write(survey,false));}catch(IOException persistence){verified=0;verifiedDigest="";failure.addSuppressed(persistence);}
                throw failure;
            }
            Saved after=write(survey,false);acceptNew(after);return progress(after);
        });
    }
    private void acceptNew(Saved saved){verifiedDigest=saved.digest();verified=saved.snapshot().observations().size();}
    /** Every persisted observation must be revalidated in this session before release. */
    public Range completedRange()throws IOException{return locked(()->completed(loaded()));}
    private Range completed(Saved saved)throws IOException{
        if(progress(saved).phase()!=Phase.COMPLETE)throw new IOException("Mountain range is not complete and currently verified");
        if(!saved.digest().equals(completedDigest)){
            // loaded() validated every current disk byte and reconstructed this
            // exact survey. Never repeat the entire traversal for every source read.
            completedRange=cachedSurvey.completedRange();completedDigest=saved.digest();componentIdentity=null;
        }
        return completedRange;
    }
    /** Same world/component identity for different entry seeds or work limits. No resource allocation is implied. */
    public String completedIdentity()throws IOException{return locked(()->{
        var range=completed(loaded());var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        if(componentIdentity!=null)return componentIdentity;
        out.writeUTF("IC_CONNECTED_MOUNTAIN_V1");out.writeUTF(identity.environmentFingerprint());
        for(var list:List.of(range.members(),range.boundary())){out.writeInt(list.size());for(var column:list){out.writeInt(column.x());out.writeInt(column.z());}}
        out.flush();componentIdentity=HexFormat.of().formatHex(hash(bytes.toByteArray()));return componentIdentity;
    });}
    private Saved loaded()throws IOException{
        Saved saved=read();if(!saved.digest().equals(verifiedDigest)){verifiedDigest=saved.digest();verified=0;}return saved;
    }
    private Progress progress(Saved saved){
        var topology=saved.topology();Phase phase;
        if(saved.changed())phase=Phase.HELD_CHANGED;
        else if(topology.status()==Status.HELD_LIMIT)phase=Phase.HELD_LIMIT;
        else if(topology.status()==Status.HELD_DOMAIN)phase=Phase.HELD_DOMAIN;
        else if(verified<topology.observations())phase=Phase.VERIFYING;
        else phase=topology.status()==Status.SEARCHING?Phase.DISCOVERING:Phase.valueOf(topology.status().name());
        return new Progress(phase,topology,verified);
    }
    private Path marker(){return path.resolveSibling(path.getFileName()+".started");}
    private void noPending()throws IOException{
        try(var pending=Files.newDirectoryStream(path.getParent(),path.getFileName()+".pending-*")){
            if(pending.iterator().hasNext())throw new IOException("Unresolved mountain journal write; explicit recovery required");
        }
    }
    private void verifyMarker()throws IOException{
        byte[] bytes;try(var in=Files.newInputStream(marker(),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(33);}
        if(!Arrays.equals(bytes,HexFormat.of().parseHex(identity.fingerprint())))throw new IOException("Mountain commissioning identity changed");
    }
    private byte[] readBytes()throws IOException{
        verifyMarker();noPending();int maximum=4096+9*identity.maximumObservations();byte[] bytes;
        try(var in=Files.newInputStream(path,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(maximum+1);}
        if(bytes.length<40||bytes.length>maximum)throw new IOException("Mountain journal length");
        return bytes;
    }
    private Saved read()throws IOException{
        byte[] bytes=readBytes();
        if(cachedSaved!=null&&Arrays.equals(bytes,cachedBytes))return cachedSaved;
        byte[] body=Arrays.copyOf(bytes,bytes.length-32),checksum=Arrays.copyOfRange(bytes,bytes.length-32,bytes.length);
        if(!MessageDigest.isEqual(hash(body),checksum))throw new IOException("Mountain journal checksum");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||in.readInt()!=VERSION||!in.readUTF().equals(identity.fingerprint()))throw new IOException("Mountain journal identity/version changed");
            boolean changed=flag(in);var status=Status.valueOf(in.readUTF());int count=in.readInt();
            if(count<0||count>identity.maximumObservations())throw new IOException("Mountain observation count");
            var observations=new ArrayList<Observation>(count);
            for(int i=0;i<count;i++)observations.add(new Observation(new Column(in.readInt(),in.readInt()),flag(in)));
            if(in.available()!=0)throw new IOException("Trailing mountain survey data");
            var snapshot=new Snapshot(identity.seed(),identity.maximumObservations(),observations,status);
            var survey=MountainRangeSurvey.restore(snapshot);
            var saved=new Saved(snapshot,changed,HexFormat.of().formatHex(checksum),survey.progress());
            cachedBytes=bytes;cachedSaved=saved;cachedSurvey=survey;return saved;
        }catch(IllegalArgumentException|IllegalStateException e){throw new IOException("Invalid mountain survey prefix",e);}
    }
    private static boolean flag(DataInputStream in)throws IOException{int flag=in.readUnsignedByte();if(flag>1)throw new IOException("Invalid mountain flag");return flag==1;}
    private Saved write(MountainRangeSurvey survey,boolean changed)throws IOException{
        Snapshot snapshot=survey.snapshot();clearCache();
        if(!snapshot.seed().equals(identity.seed())||snapshot.maximumObservations()!=identity.maximumObservations())throw new IOException("Mountain snapshot request changed");
        // This state comes only from a validated read or deterministic advance.
        // Verify every written byte before publishing it; do not reconstruct the
        // entire traversal merely to prove bytes this same state just generated.
        verifyMarker();noPending();var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(VERSION);out.writeUTF(identity.fingerprint());out.writeBoolean(changed);out.writeUTF(snapshot.status().name());out.writeInt(snapshot.observations().size());
        for(var row:snapshot.observations()){out.writeInt(row.column().x());out.writeInt(row.column().z());out.writeBoolean(row.mountain());}out.flush();byte[] body=bytes.toByteArray();
        Path pending=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        byte[] checksum=hash(body),expected=Arrays.copyOf(body,body.length+checksum.length);System.arraycopy(checksum,0,expected,body.length,checksum.length);
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){put(channel,expected);channel.force(true);}
        Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        if(!Arrays.equals(readBytes(),expected))throw new IOException("Mountain write readback differs");
        Saved saved=new Saved(snapshot,changed,HexFormat.of().formatHex(checksum),survey.progress());
        cachedBytes=expected;cachedSaved=saved;cachedSurvey=survey;return saved;
    }
    private static void put(FileChannel channel,byte[] bytes)throws IOException{var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);}
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            java.nio.channels.FileLock lock;try{lock=channel.tryLock();}catch(java.nio.channels.OverlappingFileLockException e){throw new IOException("Mountain journal busy",e);}
            if(lock==null)throw new IOException("Mountain journal busy");try(lock){return action.run();}
        }
    }
    private static byte[] hash(byte[] value){try{return MessageDigest.getInstance("SHA-256").digest(value);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
