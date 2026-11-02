package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Durable occurrence decisions only; never places, restores or claims custody of ore.
 * Selection must already be native-qualified. Changing a committed request holds the
 * original result, including absence. Unknown/corrupt records never become a new roll. */
public final class ContinentOccurrenceLedger {
    private static final int MAGIC = 0x49434f31, MAX_BYTES = 1048576, MAX_ROWS = 128;
    public record Candidate(int x,int y,int z,long geometrySeed,int cells,String biome) {
        public Candidate {
            if (Math.abs((long)x)>ContinentEnvelope.LIMIT || Math.abs((long)z)>ContinentEnvelope.LIMIT
                    || cells<1 || cells>FiniteOreLimits.MAX_BLOCKS || biome==null || !biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                throw new IllegalArgumentException("Qualified finite candidate required");
        }
    }
    public record Request(ContinentCandidateSearch.Key key,Candidate candidate,double chance) {
        public Request {
            Objects.requireNonNull(key);Objects.requireNonNull(candidate);
            if (!Double.isFinite(chance)||chance<0||chance>1) throw new IllegalArgumentException("Probability0..1");
        }
    }
    public record Entry(Request request,double roll,boolean present) {}
    public enum Status { RECORDED, EXISTING, HELD_CHANGED_INPUT }
    public record Result(Status status,Entry entry) {}
    private final Path path;
    private final ContinentResourceDecision.Scope scope;
    private final ReTerraForgedGeography.ContinentKey continent;
    private ContinentOccurrenceLedger(Path path,ContinentResourceDecision.Scope scope,ReTerraForgedGeography.ContinentKey continent) {
        this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();
        this.scope=Objects.requireNonNull(scope);this.continent=Objects.requireNonNull(continent);
    }
    /** Explicit first commissioning only. Existing or uncertain state is never reset. */
    public static ContinentOccurrenceLedger create(Path path,ContinentResourceDecision.Scope scope,
            ReTerraForgedGeography.ContinentKey continent) throws IOException {
        var ledger=new ContinentOccurrenceLedger(path,scope,continent);
        Files.createDirectories(ledger.path.getParent());
        try(var channel=FileChannel.open(ledger.path.resolveSibling(ledger.path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE)) {
            java.nio.channels.FileLock lock;
            try { lock=channel.tryLock(); }
            catch(java.nio.channels.OverlappingFileLockException busy) { throw new IOException("Occurrence ledger busy",busy); }
            if(lock==null)throw new IOException("Occurrence ledger busy");
            try(lock) {
                if(Files.exists(ledger.path))throw new IOException("Occurrence ledger already exists");
                try(var pending=Files.newDirectoryStream(ledger.path.getParent(),ledger.path.getFileName()+".pending-*")) {
                    if(pending.iterator().hasNext())throw new IOException("Unresolved occurrence write; explicit recovery required");
                }
                ledger.write(new TreeMap<>());ledger.read();return ledger;
            }
        }
    }
    public static ContinentOccurrenceLedger open(Path path,ContinentResourceDecision.Scope scope,
            ReTerraForgedGeography.ContinentKey continent) throws IOException {
        var ledger=new ContinentOccurrenceLedger(path,scope,continent);ledger.read();return ledger;
    }
    /** Single-writer lock plus reread avoids stale-instance overwrites. Busy writers
     * refuse; callers may retry the same request. Return only after durable file write. */
    public Result decide(Request request) throws IOException {
        requireScope(request);
        Files.createDirectories(path.getParent());
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE)) {
            java.nio.channels.FileLock lock;
            try { lock=channel.tryLock(); }
            catch(java.nio.channels.OverlappingFileLockException busy) { throw new IOException("Occurrence ledger busy",busy); }
            if(lock==null)throw new IOException("Occurrence ledger busy");
            try(lock) {
                var entries=read();var old=entries.get(request.key().family());
                if(old!=null)return new Result(old.request().equals(request)?Status.EXISTING:Status.HELD_CHANGED_INPUT,old);
                if(entries.size()>=MAX_ROWS)throw new IOException("Occurrence ledger capacity");
                double roll=ContinentResourceDecision.presenceRoll(scope,continent,request.key().family());
                var entry=new Entry(request,roll,roll<request.chance());entries.put(request.key().family(),entry);
                write(entries);
                if(!read().equals(entries))throw new IOException("Occurrence readback differs");
                return new Result(Status.RECORDED,entry);
            }
        }
    }
    public Map<String,Entry> snapshot() throws IOException { return Map.copyOf(read()); }
    private void requireScope(Request r) {
        var k=r.key();
        if(k.worldSeed()!=scope.worldSeed()||!k.dimension().equals(scope.dimension())
                ||!k.presetSha256().equals(scope.presetSha256())||!k.continent().equals(continent))
            throw new IllegalArgumentException("Foreign occurrence scope");
    }
    private TreeMap<String,Entry> read() throws IOException {
        var result=new TreeMap<String,Entry>();
        long size=Files.size(path);
        if(size<36||size>MAX_BYTES)throw new IOException("Invalid occurrence file size");
        byte[] bytes;
        try(var in=Files.newInputStream(path)) {bytes=in.readNBytes(MAX_BYTES+1);}
        if(bytes.length<36||bytes.length>MAX_BYTES)throw new IOException("Invalid occurrence bytes");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(digest(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))
            throw new IOException("Occurrence checksum mismatch");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))) {
            if(in.readInt()!=MAGIC||in.readLong()!=scope.worldSeed()||!in.readUTF().equals(scope.dimension())
                    ||!in.readUTF().equals(scope.presetSha256())||in.readInt()!=continent.centerX()
                    ||in.readInt()!=continent.centerZ()||in.readInt()!=continent.identityBits())throw new IOException("Occurrence header/scope mismatch");
            int count=in.readInt();if(count<0||count>MAX_ROWS)throw new IOException("Occurrence row count");
            for(int i=0;i<count;i++) {
                String family=in.readUTF(),policy=in.readUTF();
                var candidate=new Candidate(in.readInt(),in.readInt(),in.readInt(),in.readLong(),in.readInt(),in.readUTF());
                double chance=in.readDouble(),roll=in.readDouble();boolean present=in.readBoolean();
                var key=new ContinentCandidateSearch.Key(scope.worldSeed(),scope.dimension(),scope.presetSha256(),continent,family,policy);
                var request=new Request(key,candidate,chance);
                double expected=ContinentResourceDecision.presenceRoll(scope,continent,family);
                if(Double.doubleToLongBits(roll)!=Double.doubleToLongBits(expected)||present!=(roll<chance)
                        ||result.put(family,new Entry(request,roll,present))!=null)throw new IOException("Invalid or duplicate occurrence decision");
            }
            if(in.available()!=0)throw new IOException("Trailing occurrence data");
        } catch(IllegalArgumentException e) { throw new IOException("Invalid occurrence record",e); }
        return result;
    }
    private void write(TreeMap<String,Entry> entries) throws IOException {
        var bytes=new ByteArrayOutputStream();
        try(var out=new DataOutputStream(bytes)) {
            out.writeInt(MAGIC);out.writeLong(scope.worldSeed());out.writeUTF(scope.dimension());out.writeUTF(scope.presetSha256());
            out.writeInt(continent.centerX());out.writeInt(continent.centerZ());out.writeInt(continent.identityBits());out.writeInt(entries.size());
            for(var e:entries.values()) {
                var r=e.request();var c=r.candidate();out.writeUTF(r.key().family());out.writeUTF(r.key().policySha256());
                out.writeInt(c.x());out.writeInt(c.y());out.writeInt(c.z());out.writeLong(c.geometrySeed());out.writeInt(c.cells());out.writeUTF(c.biome());
                out.writeDouble(r.chance());out.writeDouble(e.roll());out.writeBoolean(e.present());
            }
        }
        byte[] body=bytes.toByteArray();if(body.length+32>MAX_BYTES)throw new IOException("Occurrence file too large");
        Path temporary=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        try(var out=FileChannel.open(temporary,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)) {
            for(byte[] data:new byte[][]{body,digest(body)}) {var b=ByteBuffer.wrap(data);while(b.hasRemaining())out.write(b);}
            out.force(true);
        }
        // Never fall back to a non-atomic replacement. A refused/unknown operation
        // leaves its pending evidence; pending files are never silently admitted.
        Files.move(temporary,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        try(var out=FileChannel.open(path,StandardOpenOption.WRITE)) { out.force(true); }
    }
    private static byte[] digest(byte[] bytes) {
        try { return MessageDigest.getInstance("SHA-256").digest(bytes); }
        catch(NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
}
