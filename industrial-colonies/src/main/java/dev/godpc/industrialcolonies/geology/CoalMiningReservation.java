package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;

/** Immutable finite coal identity. It describes a saved selection, never proves natural ore.
 * Separate from optional occurrence records: there is no probability or absence outcome. */
public record CoalMiningReservation(ContinentResourceDecision.Scope scope,
        ReTerraForgedGeography.ContinentKey continent,String slot,String requestFingerprint,
        NativeCoalCandidateQualifier.Selection selected) {
    public CoalMiningReservation {
        Objects.requireNonNull(scope);Objects.requireNonNull(continent);Objects.requireNonNull(selected);
        if(slot==null||!slot.matches("(?:small_[0-5]|medium_[01]|large_0|minimum_small)")
                ||requestFingerprint==null||!requestFingerprint.matches("[a-f0-9]{64}")
                ||selected.cells()<1||selected.cells()>FiniteOreLimits.MAX_BLOCKS||selected.biome()==null
                ||!selected.biome().matches("[a-z0-9_.-]+:[a-z0-9_./-]+")||selected.biome().length()>256
                ||Math.abs((long)selected.x())>=ContinentEnvelope.LIMIT||Math.abs((long)selected.z())>=ContinentEnvelope.LIMIT)
            throw new IllegalArgumentException("Invalid finite coal reservation");
    }
    public static CoalMiningReservation bind(CoalPlacementRequest request,NativeCoalCandidateQualifier.Selection selected)throws IOException {
        request.verify();Objects.requireNonNull(selected);
        if(request.deposit().oreBlocks()!=selected.cells()||request.geometrySeed(selected.x(),selected.z())!=selected.geometrySeed())
            throw new IllegalArgumentException("Coal selection differs from saved slot");
        return new CoalMiningReservation(request.scope(),request.continent(),request.deposit().slot(),request.fingerprint(),selected);
    }
    void write(DataOutput out)throws IOException {
        out.writeLong(scope.worldSeed());out.writeUTF(scope.dimension());out.writeUTF(scope.presetSha256());
        out.writeInt(continent.centerX());out.writeInt(continent.centerZ());out.writeInt(continent.identityBits());
        out.writeUTF(slot);out.writeUTF(requestFingerprint);out.writeInt(selected.x());out.writeInt(selected.y());out.writeInt(selected.z());
        out.writeLong(selected.geometrySeed());out.writeInt(selected.cells());out.writeUTF(selected.biome());
    }
    static CoalMiningReservation read(DataInput in)throws IOException {
        var scope=new ContinentResourceDecision.Scope(in.readLong(),in.readUTF(),in.readUTF());
        var continent=new ReTerraForgedGeography.ContinentKey(in.readInt(),in.readInt(),in.readInt());
        return new CoalMiningReservation(scope,continent,in.readUTF(),in.readUTF(),new NativeCoalCandidateQualifier.Selection(
                in.readInt(),in.readInt(),in.readInt(),in.readLong(),in.readInt(),in.readUTF()));
    }
    public String key() {
        try {var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeUTF("IC_COAL_NATURAL_ORE_V1");write(out);out.flush();
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray()));
        }catch(IOException|NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
}
