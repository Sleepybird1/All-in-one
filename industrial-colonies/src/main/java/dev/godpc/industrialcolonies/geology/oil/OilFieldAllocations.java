package dev.godpc.industrialcolonies.geology.oil;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Immutable field budgets. Callers must separately qualify native field identity.
 * This journal neither allocates per pump nor debits extraction, and is not registered. */
public final class OilFieldAllocations {
    private final Path directory;
    private final long world;
    private final String dimension,preset,binding;
    private OilFieldAllocations(Path path,OilFieldBudget.Key key) {
        directory=path.toAbsolutePath().normalize();world=key.worldSeed();dimension=key.dimension();preset=key.presetSha256();
        binding=HexFormat.of().formatHex(hash(("IC_OIL_ALLOCATION_V1\n"+world+"\n"+dimension+"\n"+preset).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
    }
    public static OilFieldAllocations create(Path path,OilFieldBudget.Key key)throws IOException {
        var result=new OilFieldAllocations(path,key);Files.createDirectory(result.directory);
        result.force(result.directory.resolve("identity"),HexFormat.of().parseHex(result.binding));result.verify();return result;
    }
    public static OilFieldAllocations open(Path path,OilFieldBudget.Key key)throws IOException {
        var result=new OilFieldAllocations(path,key);result.verify();return result;
    }
    public OilFieldBudget.Budget reserve(OilFieldBudget.Key key)throws IOException {
        return locked(()->{
            check(key);String field=key.fieldIdentity();noPending(field);
            Path record=directory.resolve(field+".bin");
            if(Files.exists(record,LinkOption.NOFOLLOW_LINKS))return read(key);
            // CREATE_NEW preserves a missing-record hold instead of replenishing a lost allocation.
            force(directory.resolve(field+".started"),HexFormat.of().parseHex(binding));
            byte[] body=encode(OilFieldBudget.select(key));var bytes=new ByteArrayOutputStream();bytes.write(body);bytes.write(hash(body));
            Path pending=directory.resolve(field+".pending-"+UUID.randomUUID());force(pending,bytes.toByteArray());
            Files.move(pending,record,StandardCopyOption.ATOMIC_MOVE);return read(key);
        });
    }
    public OilFieldBudget.Budget existing(OilFieldBudget.Key key)throws IOException {return locked(()->read(key));}
    public record CommissionReceipt(OilFieldBudget.Budget budget,long nativeReservoirId) {}
    /** Issued only by a fresh forced commissioning write, never reconstructed from a receipt. */
    public static final class CommissionPermit {
        private final CommissionReceipt receipt;private boolean consumed;
        private CommissionPermit(CommissionReceipt receipt){this.receipt=receipt;}
        synchronized OilFieldBudget.Budget take(OilFieldBudget.Key key,long nativeId)throws IOException {
            if(consumed||!receipt.budget().key().equals(key)||receipt.nativeReservoirId()!=nativeId)throw new IOException("Oil commissioning permit unavailable or mismatched");
            consumed=true;return receipt.budget();
        }
    }
    public CommissionPermit commissionNew(OilFieldBudget.Key key,long nativeId)throws IOException {
        return locked(()->{
            var budget=read(key);String field=key.fieldIdentity();commissionPending(field);
            Path record=directory.resolve(field+".commission");
            if(Files.exists(record,LinkOption.NOFOLLOW_LINKS))throw new IOException("Oil field already commissioned; recovery required");
            force(directory.resolve(field+".commission-started"),HexFormat.of().parseHex(binding));
            var receipt=new CommissionReceipt(budget,nativeId);byte[] body=commissionBytes(receipt);
            var bytes=new ByteArrayOutputStream();bytes.write(body);bytes.write(hash(body));
            Path pending=directory.resolve(field+".commission-pending-"+UUID.randomUUID());force(pending,bytes.toByteArray());
            Files.move(pending,record,StandardCopyOption.ATOMIC_MOVE);
            if(!readCommission(key,nativeId).equals(receipt))throw new IOException("Oil commissioning readback mismatch");
            return new CommissionPermit(receipt);
        });
    }
    /** Read-only evidence for recovery; this never grants a fresh budget application. */
    public CommissionReceipt commissioned(OilFieldBudget.Key key,long nativeId)throws IOException {return locked(()->readCommission(key,nativeId));}
    private byte[] commissionBytes(CommissionReceipt receipt)throws IOException {
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeUTF("IC_OIL_COMMISSION_V1");out.write(encode(receipt.budget()));out.writeLong(receipt.nativeReservoirId());out.flush();return bytes.toByteArray();
    }
    private CommissionReceipt readCommission(OilFieldBudget.Key key,long nativeId)throws IOException {
        var budget=read(key);String field=key.fieldIdentity();commissionPending(field);identity(directory.resolve(field+".commission-started"));
        byte[] bytes=bounded(directory.resolve(field+".commission"),2048);
        if(bytes.length<40)throw new IOException("Truncated oil commissioning record");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        var expected=new CommissionReceipt(budget,nativeId);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length))||!Arrays.equals(body,commissionBytes(expected)))throw new IOException("Oil commissioning identity or checksum mismatch");
        return expected;
    }
    private void commissionPending(String field)throws IOException {
        try(var files=Files.newDirectoryStream(directory,field+".commission-pending-*")){
            if(files.iterator().hasNext())throw new IOException("Unresolved oil commissioning write");
        }
    }
    private void check(OilFieldBudget.Key key)throws IOException {
        if(key.worldSeed()!=world||!key.dimension().equals(dimension)||!key.presetSha256().equals(preset))throw new IOException("Oil allocation environment changed");
    }
    private byte[] encode(OilFieldBudget.Budget budget)throws IOException {
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(0x49434f41);out.writeInt(1);out.writeUTF(binding);out.writeUTF(budget.key().fieldIdentity());
        out.writeUTF(budget.key().kind().name());out.writeLong(budget.totalMb());out.writeUTF(budget.fingerprint());out.flush();return bytes.toByteArray();
    }
    private OilFieldBudget.Budget read(OilFieldBudget.Key key)throws IOException {
        check(key);String field=key.fieldIdentity();noPending(field);identity(directory.resolve(field+".started"));
        byte[] bytes=bounded(directory.resolve(field+".bin"),1024);
        if(bytes.length<40)throw new IOException("Truncated oil allocation");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Oil allocation checksum changed");
        var expected=OilFieldBudget.select(key);
        // Exact canonical encoding checks version, category, environment, amount and fingerprint.
        if(!Arrays.equals(body,encode(expected)))throw new IOException("Oil allocation identity or budget changed");
        return expected;
    }
    private void verify()throws IOException {
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid oil allocation directory");identity(directory.resolve("identity"));
    }
    private void identity(Path path)throws IOException {
        if(!MessageDigest.isEqual(bounded(path,32),HexFormat.of().parseHex(binding)))throw new IOException("Oil allocation authority changed");
    }
    private byte[] bounded(Path path,int limit)throws IOException {
        try(var in=Files.newInputStream(path,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
            byte[] bytes=in.readNBytes(limit+1);if(bytes.length>limit)throw new IOException("Oversized oil allocation");return bytes;
        }
    }
    private void noPending(String field)throws IOException {
        try(var files=Files.newDirectoryStream(directory,field+".pending-*")){
            if(files.iterator().hasNext())throw new IOException("Unresolved oil allocation write");
        }
    }
    private void force(Path path,byte[] bytes)throws IOException {
        try(var channel=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
        }
    }
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException {
        verify();
        try(var channel=FileChannel.open(directory.resolve("allocation.lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            FileLock lock;try{lock=channel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Oil directory busy",e);}
            if(lock==null)throw new IOException("Oil directory busy");try(lock){verify();return action.run();}
        }
    }
    private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
