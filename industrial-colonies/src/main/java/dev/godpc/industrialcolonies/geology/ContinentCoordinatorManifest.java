package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Durable commissioning prefix: a missing started family journal must never be recreated. */
public final class ContinentCoordinatorManifest {
    private static final int MAGIC=0x49434d31;
    private final Path path;private final String scope;private final int families;
    private ContinentCoordinatorManifest(Path path,String scope,int families){
        this.path=path.toAbsolutePath().normalize();this.scope=scope;this.families=families;
        if(scope==null||!scope.matches("[a-f0-9]{64}")||families<1||families>128)throw new IllegalArgumentException("Bounded scoped family manifest required");
    }
    public static ContinentCoordinatorManifest create(Path path,String scope,int families)throws IOException{
        var m=new ContinentCoordinatorManifest(path,scope,families);Files.createDirectories(m.path.getParent());
        return m.locked(()->{
            if(Files.exists(m.path))throw new IOException("Coordinator manifest already exists");
            try(var pending=Files.newDirectoryStream(m.path.getParent(),m.path.getFileName()+".pending-*")){
                if(pending.iterator().hasNext())throw new IOException("Unresolved first coordinator write");
            }
            m.write(0);return m;
        });
    }
    public static ContinentCoordinatorManifest open(Path path,String scope,int families)throws IOException{
        var m=new ContinentCoordinatorManifest(path,scope,families);m.started();return m;
    }
    public int started()throws IOException{
        if(Files.size(path)!=110)throw new IOException("Coordinator manifest size");
        byte[] all;try(var in=Files.newInputStream(path)){all=in.readNBytes(111);}
        if(all.length!=110)throw new IOException("Coordinator manifest truncated or grew");
        byte[] body=Arrays.copyOf(all,78);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(all,78,110)))throw new IOException("Coordinator checksum");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||!in.readUTF().equals(scope)||in.readInt()!=families)throw new IOException("Coordinator scope changed");
            int value=in.readInt();if(value<0||value>families||in.available()!=0)throw new IOException("Invalid commissioning prefix");return value;
        }
    }
    public void start(int index)throws IOException{
        if(index<0||index>=families)throw new IllegalArgumentException("Family index outside manifest");
        locked(()->{if(started()!=index)throw new IOException("Started family prefix changed");write(index+1);return null;});
    }
    private void write(int started)throws IOException{
        var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
            out.writeInt(MAGIC);out.writeUTF(scope);out.writeInt(families);out.writeInt(started);
        }
        byte[] body=bytes.toByteArray();Path pending=path.resolveSibling(path.getFileName()+".pending-"+UUID.randomUUID());
        try(var out=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
            for(byte[] b:new byte[][]{body,hash(body)}){var buffer=ByteBuffer.wrap(b);while(buffer.hasRemaining())out.write(buffer);}out.force(true);
        }
        Files.move(pending,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        try(var out=FileChannel.open(path,StandardOpenOption.WRITE)){out.force(true);}
        if(started()!=started)throw new IOException("Coordinator readback mismatch");
    }
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        try(var channel=FileChannel.open(path.resolveSibling(path.getFileName()+".lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE)){
            FileLock lock;try{lock=channel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Coordinator busy",e);}
            if(lock==null)throw new IOException("Coordinator busy");try(lock){return action.run();}
        }
    }
    private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
