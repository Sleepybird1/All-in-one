package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Persisted bounded discovery, separate from occurrence and block-placement custody.
 * Each advance rereads under its writer lock; failed native reads retain the committed
 * prefix and retry the same next location. A changed selected site stays held. */
public final class ContinentSearchJournal {
    private static final int MAGIC=0x49435331,MAGIC_V2=0x49435332,MAX_BYTES=16384;
    private final Path path;
    private final ContinentCandidateSearch.Key key;
    private final GeographicColumnSurvey.Window window;
    private final double chance;
    private final ContinentCandidateSearch.Traversal traversal;
    private ContinentSearchJournal(Path path,ContinentCandidateSearch.Key key,GeographicColumnSurvey.Window window,double chance,ContinentCandidateSearch.Traversal traversal) {
        this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();this.key=Objects.requireNonNull(key);
        this.window=Objects.requireNonNull(window);this.chance=chance;
        this.traversal=Objects.requireNonNull(traversal);
        if(!Double.isFinite(chance)||chance<0||chance>1)throw new IllegalArgumentException("Probability0..1");
    }
    public static ContinentSearchJournal create(Path path,ContinentCandidateSearch.Key key,GeographicColumnSurvey.Window window,double chance)throws IOException {
        return create(path,key,window,chance,ContinentCandidateSearch.Traversal.LINEAR_V1);
    }
    public static ContinentSearchJournal create(Path path,ContinentCandidateSearch.Key key,GeographicColumnSurvey.Window window,double chance,ContinentCandidateSearch.Traversal traversal)throws IOException {
        var journal=new ContinentSearchJournal(path,key,window,chance,traversal);
        Files.createDirectories(journal.path.getParent());
        return journal.locked(()->{
            if(Files.exists(journal.path))throw new IOException("Search journal already exists");
            try(var pending=Files.newDirectoryStream(journal.path.getParent(),journal.path.getFileName()+".pending-*")){
                if(pending.iterator().hasNext())throw new IOException("Unresolved first search write");
            }
            journal.write(new ContinentCandidateSearch(key,window,(x,z)->false,traversal).checkpoint());
            journal.read();return journal;
        });
    }
    public static ContinentSearchJournal open(Path path,ContinentCandidateSearch.Key key,GeographicColumnSurvey.Window window,double chance)throws IOException {
        return open(path,key,window,chance,ContinentCandidateSearch.Traversal.LINEAR_V1);
    }
    public static ContinentSearchJournal open(Path path,ContinentCandidateSearch.Key key,GeographicColumnSurvey.Window window,double chance,ContinentCandidateSearch.Traversal traversal)throws IOException {
        var journal=new ContinentSearchJournal(path,key,window,chance,traversal);journal.read();return journal;
    }
    public ContinentCandidateSearch.Checkpoint snapshot()throws IOException{return read();}
    public ContinentCandidateSearch.Checkpoint advance(int budget,ContinentCandidateSearch.Qualifier qualifier)throws IOException {
        if(budget<1||budget>4096)throw new IllegalArgumentException("Search budget1..4096");Objects.requireNonNull(qualifier);
        return locked(()->{
            var before=read();var search=ContinentCandidateSearch.restore(key,window,qualifier,before,traversal);
            try{return search.advance(budget);}
            finally{if(!before.equals(search.checkpoint()))write(search.checkpoint());}
        });
    }
    @FunctionalInterface private interface IOAction<T>{T run()throws IOException;}
    private <T>T locked(IOAction<T> action)throws IOException {
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE)){
            java.nio.channels.FileLock lock;
            try{lock=channel.tryLock();}catch(java.nio.channels.OverlappingFileLockException e){throw new IOException("Search journal busy",e);}
            if(lock==null)throw new IOException("Search journal busy");
            try(lock){return action.run();}
        }
    }
    private ContinentCandidateSearch.Checkpoint read()throws IOException {
        long size=Files.size(path);if(size<36||size>MAX_BYTES)throw new IOException("Search record size");
        byte[] bytes;try(var in=Files.newInputStream(path)){bytes=in.readNBytes(MAX_BYTES+1);}
        if(bytes.length<36||bytes.length>MAX_BYTES)throw new IOException("Search record bytes");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(digest(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Search checksum");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            int magic=in.readInt();
            var savedTraversal=magic==MAGIC?ContinentCandidateSearch.Traversal.LINEAR_V1:
                    magic==MAGIC_V2?ContinentCandidateSearch.Traversal.valueOf(in.readUTF()):null;
            if(savedTraversal!=traversal)throw new IOException("Search traversal changed or unknown format");
            long seed=in.readLong();String dimension=in.readUTF(),preset=in.readUTF();
            var continent=new ReTerraForgedGeography.ContinentKey(in.readInt(),in.readInt(),in.readInt());
            var savedKey=new ContinentCandidateSearch.Key(seed,dimension,preset,continent,in.readUTF(),in.readUTF());
            var savedWindow=new GeographicColumnSurvey.Window(in.readInt(),in.readInt(),in.readInt(),in.readInt());
            double savedChance=in.readDouble();
            if(!key.equals(savedKey)||!window.equals(savedWindow)||Double.doubleToLongBits(chance)!=Double.doubleToLongBits(savedChance))throw new IOException("Search configuration changed");
            long visited=in.readLong();var status=ContinentCandidateSearch.Status.valueOf(in.readUTF());
            int hasSelected=in.readUnsignedByte();if(hasSelected>1)throw new IOException("Invalid selected flag");
            var selected=hasSelected==1?new ContinentCandidateSearch.Site(in.readInt(),in.readInt()):null;
            if(in.available()!=0)throw new IOException("Trailing search data");
            var checkpoint=new ContinentCandidateSearch.Checkpoint(key,window,visited,status,selected);
            // Structural validation only. Native revalidation is performed by advance.
            ContinentCandidateSearch.restore(key,window,(x,z)->true,checkpoint,traversal);
            return checkpoint;
        }catch(IllegalArgumentException e){throw new IOException("Invalid search checkpoint",e);}
    }
    private void write(ContinentCandidateSearch.Checkpoint checkpoint)throws IOException {
        var bytes=new ByteArrayOutputStream();
        try(var out=new DataOutputStream(bytes)){
            out.writeInt(traversal==ContinentCandidateSearch.Traversal.LINEAR_V1?MAGIC:MAGIC_V2);
            if(traversal!=ContinentCandidateSearch.Traversal.LINEAR_V1)out.writeUTF(traversal.name());
            out.writeLong(key.worldSeed());out.writeUTF(key.dimension());out.writeUTF(key.presetSha256());
            out.writeInt(key.continent().centerX());out.writeInt(key.continent().centerZ());out.writeInt(key.continent().identityBits());
            out.writeUTF(key.family());out.writeUTF(key.policySha256());
            out.writeInt(window.minX());out.writeInt(window.minZ());out.writeInt(window.maxX());out.writeInt(window.maxZ());out.writeDouble(chance);
            out.writeLong(checkpoint.visited());out.writeUTF(checkpoint.status().name());out.writeBoolean(checkpoint.selected()!=null);
            if(checkpoint.selected()!=null){out.writeInt(checkpoint.selected().x());out.writeInt(checkpoint.selected().z());}
        }
        byte[] body=bytes.toByteArray();if(body.length+32>MAX_BYTES)throw new IOException("Search record too large");
        Path pending=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        try(var out=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
            for(byte[] data:new byte[][]{body,digest(body)}){var buffer=ByteBuffer.wrap(data);while(buffer.hasRemaining())out.write(buffer);}
            out.force(true);
        }
        Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        try(var out=FileChannel.open(path,StandardOpenOption.WRITE)){out.force(true);}
        if(!read().equals(checkpoint))throw new IOException("Search readback differs");
    }
    private static byte[] digest(byte[] bytes){
        try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
}
