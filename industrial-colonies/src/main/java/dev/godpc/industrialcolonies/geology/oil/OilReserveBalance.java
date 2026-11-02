package dev.godpc.industrialcolonies.geology.oil;

import java.io.*;
import java.util.Objects;
import java.util.Arrays;
import java.security.*;

/** Exact depletion state, to be saved with its owning native reservoir.
 * Not registered: the caller must couple accepted tank fill and persistence. */
public record OilReserveBalance(String fieldIdentity,long remainingMb) {
    public static final long MAX_MB=(long)Integer.MAX_VALUE*1000;
    public OilReserveBalance {
        if(fieldIdentity==null||!fieldIdentity.matches("[a-f0-9]{64}")||remainingMb<0||remainingMb>MAX_MB)
            throw new IllegalArgumentException("Invalid exact oil balance");
    }
    /** Only an explicitly classified legacy record may enter this path. Never a missing new record. */
    public static OilReserveBalance migrateLegacy(String field,int nativeBuckets) {
        if(nativeBuckets<0)throw new IllegalArgumentException("Negative legacy reserves");
        return new OilReserveBalance(field,(long)nativeBuckets*1000);
    }
    /** Ceiling retains a live native reservoir until its final fractional bucket is consumed. */
    public int nativeBuckets(){return (int)((remainingMb+999)/1000);}
    public int available(int requestedMb,int tankCapacityMb) {
        if(requestedMb<0||tankCapacityMb<0)throw new IllegalArgumentException("Negative extraction request");
        return (int)Math.min(remainingMb,Math.min(requestedMb,tankCapacityMb));
    }
    public OilReserveBalance consume(int acceptedMb) {
        if(acceptedMb<0||acceptedMb>remainingMb)throw new IllegalArgumentException("Extraction exceeds reserve");
        return new OilReserveBalance(fieldIdentity,remainingMb-acceptedMb);
    }
    public byte[] encode() {
        try {
            var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
            out.writeInt(0x49434f42);out.writeInt(1);out.writeUTF(fieldIdentity);out.writeLong(remainingMb);out.flush();
            byte[] body=bytes.toByteArray();bytes.write(hash(body));return bytes.toByteArray();
        }catch(IOException impossible){throw new AssertionError(impossible);}
    }
    /** Missing, changed-identity, malformed or mirror-mismatched state must hold, never remigrate. */
    public static OilReserveBalance decode(byte[] bytes,String expectedField,int nativeBuckets)throws IOException {
        if(bytes==null||bytes.length!=114)throw new IOException("Missing or malformed exact oil balance");
        byte[] body=Arrays.copyOf(bytes,82);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,82,114)))throw new IOException("Exact oil balance checksum changed");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=0x49434f42||in.readInt()!=1)throw new IOException("Unsupported exact oil balance");
            var result=new OilReserveBalance(in.readUTF(),in.readLong());
            if(in.available()!=0||!Objects.equals(result.fieldIdentity(),expectedField)||result.nativeBuckets()!=nativeBuckets)
                throw new IOException("Exact oil balance identity/mirror mismatch");
            return result;
        }catch(IllegalArgumentException e){throw new IOException("Invalid exact oil balance",e);}
    }
    private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
