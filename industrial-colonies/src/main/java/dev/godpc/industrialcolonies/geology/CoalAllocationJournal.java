package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** One immutable coal-layout request per explicitly commissioned native continent.
 * Incomplete writes remain on disk and refuse reopen; never reset or draw another layout.
 * This persists requests, not physical placement or a guaranteed usable reserve. */
public final class CoalAllocationJournal {
    private static final int MAGIC=0x49434341,VERSION=1,MAX_BYTES=8192;
    private final Path path;
    private final CoalLayoutPolicy policy;
    private final ContinentResourceDecision.Scope scope;
    private final ReTerraForgedGeography.ContinentKey continent;
    private CoalAllocationJournal(Path path,CoalLayoutPolicy policy,ContinentResourceDecision.Scope scope,
                                  ReTerraForgedGeography.ContinentKey continent){
        this.path=Objects.requireNonNull(path).toAbsolutePath().normalize();this.policy=Objects.requireNonNull(policy);
        this.scope=Objects.requireNonNull(scope);this.continent=Objects.requireNonNull(continent);
    }
    public ContinentResourceDecision.Scope scope(){return scope;}
    public ReTerraForgedGeography.ContinentKey continent(){return continent;}
    public static CoalAllocationJournal create(Path path,CoalLayoutPolicy policy,ContinentResourceDecision.Scope scope,
                                               ReTerraForgedGeography.ContinentKey continent)throws IOException{
        var journal=new CoalAllocationJournal(path,policy,scope,continent);
        var selected=policy.select(scope,continent);byte[] encoded=journal.encode(selected);
        Files.createDirectories(journal.path.getParent());
        if(!Files.isDirectory(journal.path.getParent(),LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid coal journal parent");
        // CREATE_NEW also arbitrates competing initial writers; no replace/delete path exists.
        try(var channel=FileChannel.open(journal.path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            var buffer=ByteBuffer.wrap(encoded);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
        }
        if(!journal.snapshot().equals(selected))throw new IOException("Coal allocation readback differs");
        return journal;
    }
    public static CoalAllocationJournal open(Path path,CoalLayoutPolicy policy,ContinentResourceDecision.Scope scope,
                                             ReTerraForgedGeography.ContinentKey continent)throws IOException{
        var journal=new CoalAllocationJournal(path,policy,scope,continent);journal.snapshot();return journal;
    }
    /** Re-read before use so removed, corrupted or replaced authority cannot survive in a cache. */
    public CoalLayoutPolicy.Plan snapshot()throws IOException{
        byte[] data;
        try(var in=Files.newInputStream(path,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){data=in.readNBytes(MAX_BYTES+1);}
        if(data.length<40||data.length>MAX_BYTES)throw new IOException("Invalid coal allocation length");
        byte[] body=Arrays.copyOf(data,data.length-32);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(data,data.length-32,data.length)))throw new IOException("Coal allocation checksum mismatch");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||in.readInt()!=VERSION||in.readLong()!=scope.worldSeed()
                    ||!in.readUTF().equals(scope.dimension())||!in.readUTF().equals(scope.presetSha256())
                    ||in.readInt()!=continent.centerX()||in.readInt()!=continent.centerZ()||in.readInt()!=continent.identityBits())
                throw new IOException("Coal allocation scope/version mismatch");
            String identity=in.readUTF(),fingerprint=in.readUTF();
            var layout=CoalLayoutPolicy.Layout.valueOf(in.readUTF());var minimum=CoalLayoutPolicy.Minimum.valueOf(in.readUTF());
            int total=in.readInt(),count=in.readInt();if(count<1||count>6)throw new IOException("Invalid coal deposit count");
            var deposits=new ArrayList<CoalLayoutPolicy.Deposit>();
            for(int i=0;i<count;i++)deposits.add(new CoalLayoutPolicy.Deposit(in.readUTF(),CoalLayoutPolicy.Size.valueOf(in.readUTF()),in.readInt(),in.readLong()));
            if(in.available()!=0)throw new IOException("Trailing coal allocation data");
            var plan=new CoalLayoutPolicy.Plan(identity,fingerprint,layout,minimum,deposits,total);
            policy.verify(scope,continent,plan);return plan;
        }catch(IllegalArgumentException|IllegalStateException e){throw new IOException("Changed or invalid coal allocation",e);}
    }
    private byte[] encode(CoalLayoutPolicy.Plan plan)throws IOException{
        policy.verify(scope,continent,plan);
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(VERSION);out.writeLong(scope.worldSeed());out.writeUTF(scope.dimension());out.writeUTF(scope.presetSha256());
        out.writeInt(continent.centerX());out.writeInt(continent.centerZ());out.writeInt(continent.identityBits());
        out.writeUTF(plan.identity());out.writeUTF(plan.policySha256());out.writeUTF(plan.layout().name());out.writeUTF(plan.minimum().name());
        out.writeInt(plan.requestedTotal());out.writeInt(plan.deposits().size());
        for(var d:plan.deposits()){out.writeUTF(d.slot());out.writeUTF(d.size().name());out.writeInt(d.oreBlocks());out.writeLong(d.shapeSalt());}
        out.flush();byte[] body=bytes.toByteArray();out.write(hash(body));out.flush();
        if(bytes.size()>MAX_BYTES)throw new IOException("Coal allocation too large");return bytes.toByteArray();
    }
    private static byte[] hash(byte[] body){try{return MessageDigest.getInstance("SHA-256").digest(body);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
