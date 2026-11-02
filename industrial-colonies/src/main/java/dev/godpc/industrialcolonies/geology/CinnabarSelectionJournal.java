package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.CinnabarConcentrations.*;
import static dev.godpc.industrialcolonies.geology.MountainRangeSurvey.Column;

/** Persist selected locations and full geometry hashes, never reroll them on restart. No ore writes. */
public final class CinnabarSelectionJournal {
    public enum Phase { VERIFYING, READY, HELD_CHANGED }
    public record Progress(Phase phase,int verified,int requested) {}
    private record Descriptor(Column anchor,int width,int anchorY,String geometryHash) {}
    private record Saved(boolean held,List<Descriptor> descriptors,String digest) {}
    private static final int MAGIC=0x49434353,VERSION=1,MAX_BYTES=16384;
    private final Path path;
    private final CinnabarConcentrations verifier;
    private final String binding;
    private String auditDigest="";
    private final List<Selection> audited=new ArrayList<>();
    private final Set<GeologyMath.Voxel> occupied=new HashSet<>();
    private CinnabarSelectionJournal(Path path,CinnabarConcentrations verifier){
        this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();this.verifier=Objects.requireNonNull(verifier);
        binding=hashData(out->{
            out.writeUTF("IC_CINNABAR_SELECTIONS_V1");out.writeUTF(verifier.allocation().componentIdentity());out.writeUTF(verifier.policy().fingerprint());
            out.writeInt(verifier.allocation().plan().concentrationReserves().size());for(int n:verifier.allocation().plan().concentrationReserves())out.writeInt(n);
        });
    }
    public static CinnabarSelectionJournal create(Path path,CinnabarConcentrations completed)throws IOException{
        var plans=completed.completed();var result=new CinnabarSelectionJournal(path,completed);
        var rows=new ArrayList<Descriptor>();for(var plan:plans)rows.add(new Descriptor(plan.anchor(),plan.width(),plan.anchorY(),geometryHash(plan)));
        Files.createDirectories(result.path.getParent());
        return result.locked(()->{
            if(Files.exists(result.path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Cinnabar selections already exist");result.noPending();
            try(var channel=FileChannel.open(result.marker(),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){put(channel,HexFormat.of().parseHex(result.binding));channel.force(true);}
            result.write(false,rows);return result;
        });
    }
    public static CinnabarSelectionJournal open(Path path,CinnabarConcentrations verifier)throws IOException{
        var result=new CinnabarSelectionJournal(path,verifier);result.read();return result;
    }
    public Progress progress()throws IOException{return locked(()->progress(loaded()));}
    /** Reads only saved locations. Unavailable reads retry; a different complete geometry persists a hold. */
    public Progress advance(int concentrationBudget,Heights heights)throws IOException{
        if(concentrationBudget<1||concentrationBudget>64)throw new IllegalArgumentException("Revalidation budget1..64");Objects.requireNonNull(heights);
        return locked(()->{
            Saved saved=loaded();if(saved.held())return progress(saved);
            for(int i=0;i<concentrationBudget&&audited.size()<saved.descriptors().size();i++){
                var row=saved.descriptors().get(audited.size());Selection actual;
                try{actual=verifier.revalidate(audited.size(),row.anchor(),row.width(),heights);}
                catch(IllegalArgumentException changed){actual=null;}
                if(actual==null||actual.anchorY()!=row.anchorY()||!geometryHash(actual).equals(row.geometryHash())||!Collections.disjoint(occupied,actual.geometry().blocks())){
                    Saved held=write(true,saved.descriptors());audited.clear();occupied.clear();auditDigest=held.digest();return progress(held);
                }
                audited.add(actual);occupied.addAll(actual.geometry().blocks());
            }
            return progress(saved);
        });
    }
    /** No partial release. These are reconstructed plans, not proof of block replacement or custody. */
    public List<Selection> completed()throws IOException{return locked(()->{
        if(progress(loaded()).phase()!=Phase.READY)throw new IOException("Saved cinnabar selections require complete current terrain audit");return List.copyOf(audited);
    });}
    private Progress progress(Saved saved){return new Progress(saved.held()?Phase.HELD_CHANGED:audited.size()==saved.descriptors().size()?Phase.READY:Phase.VERIFYING,audited.size(),saved.descriptors().size());}
    private Saved loaded()throws IOException{
        Saved saved=read();if(!saved.digest().equals(auditDigest)){audited.clear();occupied.clear();auditDigest=saved.digest();}return saved;
    }
    private Path marker(){return path.resolveSibling(path.getFileName()+".started");}
    private void noPending()throws IOException{
        try(var files=Files.newDirectoryStream(path.getParent(),path.getFileName()+".pending-*")){if(files.iterator().hasNext())throw new IOException("Unresolved selection write requires explicit recovery");}
    }
    private void verifyMarker()throws IOException{
        byte[] bytes;try(var in=Files.newInputStream(marker(),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(33);}
        if(!MessageDigest.isEqual(bytes,HexFormat.of().parseHex(binding)))throw new IOException("Selection allocation/policy binding changed");
    }
    private Saved read()throws IOException{
        verifyMarker();noPending();byte[] bytes;
        try(var in=Files.newInputStream(path,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(MAX_BYTES+1);}
        if(bytes.length<40||bytes.length>MAX_BYTES)throw new IOException("Selection record length");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32),checksum=Arrays.copyOfRange(bytes,bytes.length-32,bytes.length);
        if(!MessageDigest.isEqual(hash(body),checksum))throw new IOException("Selection record checksum");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||in.readInt()!=VERSION||!in.readUTF().equals(binding))throw new IOException("Selection identity/version");
            int flag=in.readUnsignedByte();if(flag>1)throw new IOException("Selection hold flag");int count=in.readInt();
            if(count!=verifier.policy().concentrations())throw new IOException("Selection count differs from allocated request");
            var rows=new ArrayList<Descriptor>();
            for(int i=0;i<count;i++){
                var anchor=new Column(in.readInt(),in.readInt());int width=in.readInt(),y=in.readInt();String fingerprint=in.readUTF();
                if(width<1||width>verifier.policy().maximumWidth()||y<verifier.policy().minimumY()||y>=400||!fingerprint.matches("[0-9a-f]{64}"))throw new IOException("Invalid saved concentration descriptor");
                rows.add(new Descriptor(anchor,width,y,fingerprint));
            }
            if(in.available()!=0)throw new IOException("Trailing selection data");return new Saved(flag==1,List.copyOf(rows),HexFormat.of().formatHex(checksum));
        }catch(IllegalArgumentException e){throw new IOException("Invalid selection record",e);}
    }
    private Saved write(boolean held,List<Descriptor> rows)throws IOException{
        verifyMarker();noPending();var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(VERSION);out.writeUTF(binding);out.writeBoolean(held);out.writeInt(rows.size());
        for(var row:rows){out.writeInt(row.anchor().x());out.writeInt(row.anchor().z());out.writeInt(row.width());out.writeInt(row.anchorY());out.writeUTF(row.geometryHash());}out.flush();byte[] body=bytes.toByteArray();
        Path pending=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){put(channel,body);put(channel,hash(body));channel.force(true);}
        Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        Saved saved=read();if(saved.held()!=held||!saved.descriptors().equals(rows))throw new IOException("Selection readback differs");return saved;
    }
    public static String geometryHash(Selection selection){return hashData(out->{
        out.writeUTF("IC_CINNABAR_GEOMETRY_V1");out.writeUTF(selection.identity());out.writeInt(selection.anchor().x());out.writeInt(selection.anchor().z());
        out.writeInt(selection.anchorY());out.writeInt(selection.width());out.writeDouble(selection.frequencyRoll());var geometry=selection.geometry();
        out.writeBoolean(geometry.admitted());out.writeUTF(geometry.reason());out.writeDouble(geometry.frequency());out.writeInt(geometry.eligibleFronts());out.writeInt(geometry.strokes().size());
        for(var stroke:geometry.strokes()){
            voxel(out,stroke.face().front());out.writeInt(stroke.face().dx());out.writeInt(stroke.face().dy());out.writeInt(stroke.face().dz());out.writeInt(stroke.blocks().size());for(var block:stroke.blocks())voxel(out,block);
        }
    });}
    private static void voxel(DataOutputStream out,GeologyMath.Voxel voxel)throws IOException{out.writeInt(voxel.x());out.writeInt(voxel.y());out.writeInt(voxel.z());}
    @FunctionalInterface private interface Writer {void write(DataOutputStream out)throws IOException;}
    private static String hashData(Writer writer){
        try{var digest=MessageDigest.getInstance("SHA-256");var out=new DataOutputStream(new DigestOutputStream(OutputStream.nullOutputStream(),digest));writer.write(out);out.flush();return HexFormat.of().formatHex(digest.digest());}
        catch(IOException|NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
    }
    private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
    private static void put(FileChannel channel,byte[] bytes)throws IOException{var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);}
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            FileLock lock;try{lock=channel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Selection journal busy",e);}
            if(lock==null)throw new IOException("Selection journal busy");try(lock){return action.run();}
        }
    }
}
