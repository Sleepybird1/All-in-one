package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;

/** A committed optional occurrence identity, separate from historical regional mine scopes.
 * This identifies a reservation; only actual successful writes can confer natural provenance. */
public final class ContinentOreProvenance {
    public static String key(ContinentOccurrenceLedger.Request request){
        Objects.requireNonNull(request);var k=request.key();var c=request.candidate();
        try{
            var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
            out.writeUTF("IC_CONTINENT_NATURAL_ORE_V1");out.writeLong(k.worldSeed());
            out.writeUTF(k.dimension());out.writeUTF(k.presetSha256());
            out.writeInt(k.continent().centerX());out.writeInt(k.continent().centerZ());out.writeInt(k.continent().identityBits());
            out.writeUTF(k.family());out.writeUTF(k.policySha256());
            out.writeInt(c.x());out.writeInt(c.y());out.writeInt(c.z());out.writeLong(c.geometrySeed());out.writeInt(c.cells());
            out.writeUTF(c.biome());out.writeDouble(request.chance());out.flush();
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray()));
        }catch(IOException|NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
    private ContinentOreProvenance(){}
}
