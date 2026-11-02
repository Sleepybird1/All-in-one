package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Finite per-slot discovery, separate from optional-resource occurrence and physical placement.
 * Exhaustion reports an unfittable requested layout; it never certifies coal absence or supply. */
public final class CoalDiscoveryJournal {
    public enum Status { SEARCHING, SELECTED, UNFITTED, HELD_CHANGED_SELECTION }
    public record Progress(long visited,Status status,NativeCoalCandidateQualifier.Selection selected,long selectionIndex){
        public Progress(long visited,Status status,NativeCoalCandidateQualifier.Selection selected){this(visited,status,selected,selected==null?-1:visited-1);}
    }
    @FunctionalInterface public interface Qualifier {
        Optional<NativeCoalCandidateQualifier.Selection> qualify(int x,int z)throws IOException;
    }
    private static final int MAGIC=0x49434353,VERSION=1,MAX_BYTES=8192;
    private final Path path;
    private final CoalPlacementRequest request;
    private final GeographicColumnSurvey.Window window;
    private final ContinentLocalTraversal traversal;
    private final CoalHabitatPreference preference;
    private CoalDiscoveryJournal(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window){
        this(path,request,window,null);
    }
    private CoalDiscoveryJournal(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window,CoalHabitatPreference preference){
        this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();this.request=Objects.requireNonNull(request);this.window=Objects.requireNonNull(window);
        this.preference=preference;
        long seed=ByteBuffer.wrap(HexFormat.of().parseHex(request.fingerprint())).getLong();
        traversal=new ContinentLocalTraversal(window,request.continent().centerX(),request.continent().centerZ(),seed);
    }
    public static CoalDiscoveryJournal create(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window)throws IOException{
        return create(path,request,window,null);
    }
    public static CoalDiscoveryJournal create(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window,CoalHabitatPreference preference)throws IOException{
        var journal=new CoalDiscoveryJournal(path,request,window,preference);request.verify();Files.createDirectories(journal.path.getParent());
        return journal.locked(()->{
            if(Files.exists(journal.path,LinkOption.NOFOLLOW_LINKS))throw new IOException("Coal search already exists");journal.noPending();
            try(var out=FileChannel.open(journal.marker(),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
                var bytes=ByteBuffer.wrap(HexFormat.of().parseHex(request.fingerprint()));while(bytes.hasRemaining())out.write(bytes);out.force(true);
            }
            journal.write(new Progress(0,Status.SEARCHING,null));return journal;
        });
    }
    public static CoalDiscoveryJournal open(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window)throws IOException{
        return open(path,request,window,null);
    }
    public static CoalDiscoveryJournal open(Path path,CoalPlacementRequest request,GeographicColumnSurvey.Window window,CoalHabitatPreference preference)throws IOException{
        var journal=new CoalDiscoveryJournal(path,request,window,preference);journal.snapshot();return journal;
    }
    public static CoalDiscoveryJournal createNative(Path path,NativeCoalCandidateQualifier qualifier)throws IOException{
        qualifier.checkConfiguration();return create(path,qualifier.request(),qualifier.window(),qualifier.preference());
    }
    public static CoalDiscoveryJournal openNative(Path path,NativeCoalCandidateQualifier qualifier)throws IOException{
        qualifier.checkConfiguration();return open(path,qualifier.request(),qualifier.window(),qualifier.preference());
    }
    public Progress advanceNative(int budget,NativeCoalCandidateQualifier qualifier)throws IOException{
        qualifier.checkConfiguration();
        if(!request.fingerprint().equals(qualifier.request().fingerprint())||!window.equals(qualifier.window())
                ||!Objects.equals(preference==null?null:preference.fingerprint(),qualifier.preference()==null?null:qualifier.preference().fingerprint()))throw new IOException("Coal native qualifier changed");
        return advance(budget,(x,z)->qualifier.qualifies(x,z)?qualifier.selection():Optional.empty());
    }
    public Progress snapshot()throws IOException{return read();}
    public Progress advance(int budget,Qualifier qualifier)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Coal discovery budget1..4096");Objects.requireNonNull(qualifier);
        return locked(()->{
            Progress before=read(),next=before;
            try{
                if(before.selected()!=null&&(before.status()==Status.SELECTED||before.status()==Status.SEARCHING)){
                    var selected=before.selected();var actual=Objects.requireNonNull(qualifier.qualify(selected.x(),selected.z()));
                    if(actual.isEmpty()||!selected.equals(actual.get()))next=new Progress(before.visited(),Status.HELD_CHANGED_SELECTION,selected,before.selectionIndex());
                }
                if(next.status()==Status.SEARCHING){
                    for(int i=0;i<budget&&next.status()==Status.SEARCHING;i++){
                        long index=traversal.at(next.visited());int x=x(index),z=z(index);
                        var found=Objects.requireNonNull(qualifier.qualify(x,z));
                        var best=next.selected();long bestIndex=next.selectionIndex();long visited=next.visited()+1;
                        if(found.isPresent()){
                            var selected=found.get();validateSelection(selected,x,z);
                            if(best==null||rank(selected)<rank(best)){best=selected;bestIndex=next.visited();}
                        }
                        boolean boundary=preference==null||visited%preference.window()==0||visited==window.columns();
                        var status=best!=null&&(rank(best)==0||boundary)?Status.SELECTED:
                                visited==window.columns()?Status.UNFITTED:Status.SEARCHING;
                        next=new Progress(visited,status,best,bestIndex);
                    }
                }
            }catch(IOException|RuntimeException|Error failure){
                // Commit successful reads only; the failing site remains the next candidate.
                if(!next.equals(before))try{write(next);}catch(IOException persistence){failure.addSuppressed(persistence);}
                throw failure;
            }
            if(!next.equals(before))write(next);return next;
        });
    }
    private int x(long index){return Math.toIntExact(window.minX()+index%window.width());}
    private int z(long index){return Math.toIntExact(window.minZ()+index/window.width());}
    private int rank(NativeCoalCandidateQualifier.Selection s){return preference==null?0:preference.rank(s.biome());}
    private void validateSelection(NativeCoalCandidateQualifier.Selection selected,int x,int z)throws IOException{
        if(selected.x()!=x||selected.z()!=z||selected.cells()!=request.deposit().oreBlocks()
                ||selected.geometrySeed()!=request.geometrySeed(x,z)||selected.biome()==null||!selected.biome().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
            throw new IOException("Coal selection differs from exact saved request/location");
    }
    private void validate(Progress p)throws IOException{
        if(p.visited()<0||p.visited()>window.columns()||p.status()==null)throw new IOException("Invalid coal cursor");
        if(p.status()==Status.SEARCHING&&(p.visited()>=window.columns()||preference==null&&p.selected()!=null)
                ||p.status()==Status.UNFITTED&&(p.visited()!=window.columns()||p.selected()!=null))throw new IOException("Invalid coal terminal/cursor state");
        if((p.status()==Status.SELECTED||p.status()==Status.HELD_CHANGED_SELECTION)&&p.selected()==null)throw new IOException("Missing coal selection");
        if(p.selected()!=null){
            if(p.selectionIndex()<0||p.selectionIndex()>=p.visited())throw new IOException("Invalid coal selection index");
            long index=traversal.at(p.selectionIndex());validateSelection(p.selected(),x(index),z(index));int rank=rank(p.selected());
            if(preference==null&&p.selectionIndex()!=p.visited()-1)throw new IOException("Legacy selection index changed");
            if(preference!=null&&(p.selectionIndex()/preference.window()!=(p.visited()-1)/preference.window()
                    ||rank==0&&p.selectionIndex()!=p.visited()-1))throw new IOException("Coal selection lies outside its committed preference window");
            if(preference!=null&&p.status()==Status.SEARCHING&&(rank==0||p.visited()%preference.window()==0
                    ||p.selectionIndex()/preference.window()!=(p.visited()-1)/preference.window()))throw new IOException("Invalid pending habitat preference");
        }else if(p.selectionIndex()!=-1)throw new IOException("Selection index without coal selection");
        if(preference!=null&&p.status()==Status.SELECTED&&rank(p.selected())!=0
                &&p.visited()%preference.window()!=0&&p.visited()!=window.columns()){
            throw new IOException("Coal fallback selected before fixed preference window ended");
        }
    }
    private Path marker(){return path.resolveSibling(path.getFileName()+".started");}
    private void noPending()throws IOException{
        try(var files=Files.newDirectoryStream(path.getParent(),path.getFileName()+".pending-*")){
            if(files.iterator().hasNext())throw new IOException("Unresolved coal search write; explicit recovery required");
        }
    }
    private void verifyMarker()throws IOException{
        byte[] bytes;try(var in=Files.newInputStream(marker(),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(33);}
        if(!Arrays.equals(bytes,HexFormat.of().parseHex(request.fingerprint())))throw new IOException("Coal search commissioning differs");
    }
    private Progress read()throws IOException{
        request.verify();verifyMarker();noPending();byte[] bytes;
        try(var in=Files.newInputStream(path,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(MAX_BYTES+1);}
        if(bytes.length<40||bytes.length>MAX_BYTES)throw new IOException("Coal search size");byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Coal search checksum");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||in.readInt()!=(preference==null?VERSION:2)||!in.readUTF().equals(request.fingerprint())
                    ||!window.equals(new GeographicColumnSurvey.Window(in.readInt(),in.readInt(),in.readInt(),in.readInt())))throw new IOException("Coal search identity/window changed");
            if(preference!=null&&!preference.fingerprint().equals(in.readUTF()))throw new IOException("Coal preference changed");
            long visited=in.readLong();var status=Status.valueOf(in.readUTF());int flag=in.readUnsignedByte();if(flag>1)throw new IOException("Invalid coal selected flag");
            var selection=flag==0?null:new NativeCoalCandidateQualifier.Selection(in.readInt(),in.readInt(),in.readInt(),in.readLong(),in.readInt(),in.readUTF());
            long selectedIndex=preference==null?(selection==null?-1:visited-1):in.readLong();
            if(in.available()!=0)throw new IOException("Trailing coal search data");var result=new Progress(visited,status,selection,selectedIndex);validate(result);return result;
        }catch(IllegalArgumentException e){throw new IOException("Invalid saved coal search",e);}
    }
    private void write(Progress progress)throws IOException{
        request.verify();verifyMarker();noPending();validate(progress);var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(preference==null?VERSION:2);out.writeUTF(request.fingerprint());out.writeInt(window.minX());out.writeInt(window.minZ());out.writeInt(window.maxX());out.writeInt(window.maxZ());
        if(preference!=null)out.writeUTF(preference.fingerprint());
        out.writeLong(progress.visited());out.writeUTF(progress.status().name());out.writeBoolean(progress.selected()!=null);
        if(progress.selected()!=null){var s=progress.selected();out.writeInt(s.x());out.writeInt(s.y());out.writeInt(s.z());out.writeLong(s.geometrySeed());out.writeInt(s.cells());out.writeUTF(s.biome());}
        if(preference!=null)out.writeLong(progress.selectionIndex());
        out.flush();byte[] body=bytes.toByteArray();if(body.length+32>MAX_BYTES)throw new IOException("Coal search oversized");
        Path pending=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            for(byte[] value:new byte[][]{body,hash(body)}){var buffer=ByteBuffer.wrap(value);while(buffer.hasRemaining())channel.write(buffer);}channel.force(true);
        }
        Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        if(!read().equals(progress))throw new IOException("Coal search readback differs");
    }
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            java.nio.channels.FileLock lock;try{lock=channel.tryLock();}catch(java.nio.channels.OverlappingFileLockException e){throw new IOException("Coal search busy",e);}
            if(lock==null)throw new IOException("Coal search busy");try(lock){return action.run();}
        }
    }
    private static byte[] hash(byte[] value){try{return MessageDigest.getInstance("SHA-256").digest(value);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
