package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.security.*;
import java.util.*;

/** Read-only binding of a terrain search to one slot of an existing coal allocation. */
public final class CoalPlacementRequest {
    private final CoalAllocationJournal journal;
    private final CoalLayoutPolicy.Plan allocation;
    private final CoalLayoutPolicy.Deposit deposit;
    private final String fingerprint;
    private CoalPlacementRequest(CoalAllocationJournal journal,String slot,String terrainPolicy)throws IOException{
        this.journal=Objects.requireNonNull(journal);
        if(terrainPolicy==null||!terrainPolicy.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Terrain policy fingerprint required");
        allocation=journal.snapshot();
        deposit=allocation.deposits().stream().filter(d->d.slot().equals(slot)).findFirst().orElseThrow(()->new IllegalArgumentException("Slot absent from saved coal allocation"));
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeUTF("industrial-colonies/coal-placement/v1");out.writeUTF(allocation.identity());out.writeUTF(deposit.slot());out.writeUTF(terrainPolicy);out.flush();
        fingerprint=HexFormat.of().formatHex(hash(bytes.toByteArray()));
    }
    public static CoalPlacementRequest bind(CoalAllocationJournal journal,String slot,String terrainPolicy)throws IOException{
        return new CoalPlacementRequest(journal,slot,terrainPolicy);
    }
    public CoalLayoutPolicy.Deposit deposit(){return deposit;}
    public String fingerprint(){return fingerprint;}
    public ContinentResourceDecision.Scope scope(){return journal.scope();}
    public ReTerraForgedGeography.ContinentKey continent(){return journal.continent();}
    /** Re-read saved authority before querying terrain or exposing a selected plan. */
    public void verify()throws IOException{
        if(!journal.snapshot().equals(allocation))throw new IOException("Saved coal allocation changed");
    }
    public long geometrySeed(int x,int z){
        if(Math.abs((long)x)>=ContinentEnvelope.LIMIT||Math.abs((long)z)>=ContinentEnvelope.LIMIT)
            throw new IllegalArgumentException("Coal center outside native precision domain");
        long policySalt=ByteBuffer.wrap(HexFormat.of().parseHex(fingerprint)).getLong();
        return GeologyMath.seed(scope().worldSeed(),x,z,deposit.shapeSalt()^policySalt);
    }
    private static byte[] hash(byte[] value){try{return MessageDigest.getInstance("SHA-256").digest(value);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
