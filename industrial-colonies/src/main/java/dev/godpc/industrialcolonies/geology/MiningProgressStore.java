package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.Arrays;
import java.util.UUID;

/**
 * Exclusive, versioned scan checkpoints. Does not remove blocks or deliver drops.
 * Atomic checkpoint replacement is not a transaction with Minecraft chunk saves;
 * physical mining must add a durable custody protocol before using this store.
 */
public final class MiningProgressStore {
    private static final int MAGIC=0x49434d53,VERSION=1,MAX_BYTES=4096;
    private final Path root;
    public MiningProgressStore(Path root)throws IOException{
        this.root=root.toAbsolutePath().normalize();Files.createDirectories(this.root);
    }
    public Session open(MiningScanScope scope)throws IOException{
        var path=root.resolve(scope.key()+".state");
        var channel=FileChannel.open(root.resolve(scope.key()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);
        FileLock lock=null;
        try {
            try{lock=channel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Deposit already leased",e);}
            if(lock==null)throw new IOException("Deposit already leased");
            long next;
            if(Files.exists(path))next=decode(scope,Files.readAllBytes(checkedSize(path)));
            else {
                if(channel.size()!=0)throw new IOException("Previously initialized deposit state is missing; refusing reset");
                next=0;write(path,scope,next);
            }
            if(channel.size()==0){channel.write(ByteBuffer.wrap(new byte[]{1}),0);channel.force(true);}
            return new Session(scope,path,channel,lock,next);
        }catch(IOException|RuntimeException e){
            try{if(lock!=null)lock.release();}catch(IOException cleanup){e.addSuppressed(cleanup);}
            try{channel.close();}catch(IOException cleanup){e.addSuppressed(cleanup);}throw e;
        }
    }
    private static Path checkedSize(Path p)throws IOException{
        long size=Files.size(p);if(size<40||size>MAX_BYTES)throw new IOException("Invalid mining checkpoint size");return p;
    }
    private static byte[] digest(byte[] data){try{return MessageDigest.getInstance("SHA-256").digest(data);}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
    private static byte[] encode(MiningScanScope s,long next)throws IOException{
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(s.isContinent()?2:VERSION);
        if(s.isContinent()){byte[] scope=ContinentMiningCodec.encode(s);out.writeInt(scope.length);out.write(scope);}
        else {out.writeUTF(s.dimension());out.writeUTF(s.family());out.writeInt(s.regionX());out.writeInt(s.regionZ());out.writeLong(s.body().seed());
            for(double n:new double[]{s.body().cx(),s.body().cy(),s.body().cz(),s.body().rx(),s.body().ry(),s.body().rz()})out.writeDouble(n);
            out.writeInt(s.minBuildY());out.writeInt(s.maxBuildYExclusive());}
        out.writeLong(next);out.flush();
        byte[] payload=bytes.toByteArray();out.write(digest(payload));out.flush();return bytes.toByteArray();
    }
    private static long decode(MiningScanScope expected,byte[] bytes)throws IOException{
        if(bytes.length<40||bytes.length>MAX_BYTES)throw new IOException("Invalid mining checkpoint size");
        byte[] payload=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(digest(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Mining checkpoint checksum mismatch");
        try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
            if(in.readInt()!=MAGIC)throw new IOException("Unsupported mining checkpoint magic");int version=in.readInt();MiningScanScope actual;
            if(version==2){int n=in.readInt();if(n<64||n>4096||n>in.available()-8)throw new IOException("Invalid nested mining scope size");actual=ContinentMiningCodec.decode(in.readNBytes(n));}
            else if(version==VERSION){String dimension=in.readUTF(),family=in.readUTF();int rx=in.readInt(),rz=in.readInt();long seed=in.readLong();
                var body=new MassiveDepositGeometry.Body(seed,in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble());
                actual=new MiningScanScope(dimension,family,rx,rz,body,in.readInt(),in.readInt());}
            else throw new IOException("Unsupported mining checkpoint version");
            long next=in.readLong();
            if(in.available()!=0||!actual.equals(expected))throw new IOException("Mining checkpoint scope changed; explicit migration required");
            actual.cursor(next);return next;
        }catch(IllegalArgumentException|ArithmeticException e){throw new IOException("Invalid mining checkpoint values",e);}
    }
    private static void write(Path path,MiningScanScope scope,long next)throws IOException{
        byte[] data=encode(scope,next);Path temp=path.resolveSibling(path.getFileName()+"."+UUID.randomUUID()+".tmp");
        try{
            try(var output=FileChannel.open(temp,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
                var buffer=ByteBuffer.wrap(data);while(buffer.hasRemaining())output.write(buffer);output.force(true);
            }
            // Never fall back to a non-atomic replace or reset on a failed save.
            Files.move(temp,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        }finally{Files.deleteIfExists(temp);}
    }
    public static final class Session implements AutoCloseable {
        private final MiningScanScope scope;
        private final Path path;
        private final FileChannel channel;
        private final FileLock lock;
        private long next;
        private boolean closed;
        private Session(MiningScanScope s,Path p,FileChannel c,FileLock l,long n){scope=s;path=p;channel=c;lock=l;next=n;}
        private void check(){if(closed||!lock.isValid())throw new IllegalStateException("Mining lease is closed");}
        public synchronized long nextIndex(){check();return next;}
        public synchronized MiningScanCursor snapshotCursor(){check();return scope.cursor(next);}
        /** Checkpoint only after the caller has made its independent block/drop custody durable. */
        public synchronized void commit(long expected,long target)throws IOException{
            check();if(next!=expected||target<=next)throw new IllegalStateException("Stale or regressive mining checkpoint");
            scope.cursor(target);
            try{write(path,scope,target);next=target;}
            catch(IOException e){try{close();}catch(IOException cleanup){e.addSuppressed(cleanup);}throw e;}
        }
        public synchronized void close()throws IOException{
            if(closed)return;closed=true;
            try{lock.release();}finally{channel.close();}
        }
    }
}
