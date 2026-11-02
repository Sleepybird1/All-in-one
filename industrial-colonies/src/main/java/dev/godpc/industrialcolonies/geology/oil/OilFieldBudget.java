package dev.godpc.industrialcolonies.geology.oil;

import java.io.*;
import java.security.*;
import java.util.*;

/** Conditional reserve selection for a previously qualified field, never an occurrence roll.
 * No pump/well coordinates enter the budget: all wells must share the saved field allocation.
 * This is an unregistered policy; native field authority and allocation persistence are separate. */
public final class OilFieldBudget {
    public enum Kind { ONSHORE, OFFSHORE }
    public record Key(long worldSeed,String dimension,String presetSha256,String fieldIdentity,Kind kind) {
        public Key {
            if(dimension==null||dimension.length()>256||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")
                    ||presetSha256==null||!presetSha256.matches("[a-f0-9]{64}")
                    ||fieldIdentity==null||!fieldIdentity.matches("[a-f0-9]{64}")||kind==null)
                throw new IllegalArgumentException("Qualified oil field identity required");
        }
    }
    public record Budget(Key key,long totalMb,String fingerprint) {}
    private OilFieldBudget() {}
    /** The approved conditional80/18/2table. Does not choose whether a field exists. */
    public static long onshoreReserveForRoll(int roll) {
        if(roll<0||roll>=10000)throw new IllegalArgumentException("Reserve roll0..9999 required");
        return roll<8000?5_000_000L:roll<9800?25_000_000L:100_000_000L;
    }
    public static Budget select(Key key) {
        Objects.requireNonNull(key);
        byte[] identity=identity(key);
        long seed=java.nio.ByteBuffer.wrap(digest(identity)).getLong();
        long amount=key.kind()==Kind.OFFSHORE?100_000_000L:onshoreReserveForRoll((int)Math.floorMod(seed,10000L));
        try {
            var bytes=new ByteArrayOutputStream();bytes.write(identity);var out=new DataOutputStream(bytes);out.writeLong(amount);out.flush();
            return new Budget(key,amount,HexFormat.of().formatHex(digest(bytes.toByteArray())));
        } catch(IOException impossible){throw new AssertionError(impossible);}
    }
    private static byte[] identity(Key key) {
        try {
            var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
            out.writeUTF("IC_OIL_FIELD_BUDGET_V1");out.writeLong(key.worldSeed());out.writeUTF(key.dimension());
            out.writeUTF(key.presetSha256());out.writeUTF(key.fieldIdentity());out.writeUTF(key.kind().name());out.flush();return bytes.toByteArray();
        }catch(IOException impossible){throw new AssertionError(impossible);}
    }
    private static byte[] digest(byte[] bytes) {
        try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
    }
}
