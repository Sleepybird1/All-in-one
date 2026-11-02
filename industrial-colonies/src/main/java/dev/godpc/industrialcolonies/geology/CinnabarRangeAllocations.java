package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Immutable finite requests per audited connected range. Not placement or proof of available ore. */
public final class CinnabarRangeAllocations {
    private static final int MAGIC=0x49434341, VERSION=1, MAX_SLOTS=64, MAX_RESERVE=100_000;
    public record Plan(List<Integer> concentrationReserves) {
        public Plan {
            concentrationReserves=List.copyOf(concentrationReserves);
            if(concentrationReserves.isEmpty()||concentrationReserves.size()>MAX_SLOTS)
                throw new IllegalArgumentException("Cinnabar requires1..64 concentration requests");
            for(int reserve:concentrationReserves)if(reserve<1||reserve>MAX_RESERVE)
                throw new IllegalArgumentException("Invalid finite concentration reserve");
        }
        public long totalReserve(){return concentrationReserves.stream().mapToLong(Integer::longValue).sum();}
    }
    public record Allocation(String componentIdentity,Plan plan) {
        public Allocation {validHash(componentIdentity);Objects.requireNonNull(plan);}
        /** Stable names for later terrain qualification and owner placement, never entry-seed based. */
        public String concentrationIdentity(int slot){
            if(slot<0||slot>=plan.concentrationReserves().size())throw new IndexOutOfBoundsException(slot);
            return componentIdentity+"/cinnabar/"+slot;
        }
    }
    private final Path directory;
    private final String environment,policy,binding;
    private CinnabarRangeAllocations(Path directory,String environment,String policy){
        this.directory=Objects.requireNonNull(directory).toAbsolutePath().normalize();
        validHash(environment);validHash(policy);this.environment=environment;this.policy=policy;
        binding=HexFormat.of().formatHex(hash(("IC_CINNABAR_RANGE_DIRECTORY_V1\n"+environment+"\n"+policy).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
    }
    /** Explicitly commission an empty owned directory. Existing/missing authority is never recreated. */
    public static CinnabarRangeAllocations create(Path directory,String environment,String policy)throws IOException{
        var result=new CinnabarRangeAllocations(directory,environment,policy);
        Files.createDirectory(result.directory);
        try(var channel=FileChannel.open(result.directory.resolve("identity"),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            put(channel,HexFormat.of().parseHex(result.binding));channel.force(true);
        }
        result.verify();return result;
    }
    public static CinnabarRangeAllocations open(Path directory,String environment,String policy)throws IOException{
        var result=new CinnabarRangeAllocations(directory,environment,policy);result.verify();return result;
    }
    /** First caller pins the whole plan; subsequent callers must present the same plan and audited range. */
    public Allocation reserve(MountainRangeJournal survey,Plan plan)throws IOException{
        return reserveAudited(()->audited(survey),plan);
    }
    public Allocation reserve(PagedMountainRangeJournal survey,Plan plan)throws IOException{
        return reserveAudited(()->audited(survey),plan);
    }
    @FunctionalInterface private interface AuditedComponent {String get()throws IOException;}
    private Allocation reserveAudited(AuditedComponent audited,Plan plan)throws IOException{
        Objects.requireNonNull(plan);
        return locked(()->{
            String component=audited.get();Path record=directory.resolve(component+".bin");
            noPending(component);
            if(Files.exists(record,LinkOption.NOFOLLOW_LINKS)){
                Allocation saved=read(component);
                if(!saved.plan().equals(plan))throw new IOException("Cinnabar range already has a different finite plan");
                return saved;
            }
            // Persist intent before allocation bytes. A lost record cannot be silently allocated again.
            try(var channel=FileChannel.open(marker(component),StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
                put(channel,HexFormat.of().parseHex(binding));channel.force(true);
            }
            var allocation=new Allocation(component,plan);byte[] body=encode(allocation);
            Path pending=directory.resolve(component+".pending-"+UUID.randomUUID());
            try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
                put(channel,body);put(channel,hash(body));channel.force(true);
            }
            Files.move(pending,record,StandardCopyOption.ATOMIC_MOVE);
            Allocation saved=read(component);if(!saved.equals(allocation))throw new IOException("Allocation readback differs");return saved;
        });
    }
    /** Reopening the directory does not bypass the survey's fresh-session terrain audit. */
    public Allocation existing(MountainRangeJournal survey)throws IOException{return locked(()->read(audited(survey)));}
    public Allocation existing(PagedMountainRangeJournal survey)throws IOException{return locked(()->read(audited(survey)));}
    private String audited(PagedMountainRangeJournal survey)throws IOException{
        Objects.requireNonNull(survey);
        if(!survey.identity().environmentFingerprint().equals(environment))throw new IOException("Mountain allocation environment changed");
        return survey.completedIdentity();
    }
    private String audited(MountainRangeJournal survey)throws IOException{
        Objects.requireNonNull(survey);
        if(!survey.identity().environmentFingerprint().equals(environment))throw new IOException("Mountain allocation environment changed");
        return survey.completedIdentity();
    }
    private Path marker(String component){return directory.resolve(component+".started");}
    private void verify()throws IOException{
        if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))throw new IOException("Invalid allocation directory");
        verifyIdentity(directory.resolve("identity"));
    }
    private void verifyIdentity(Path file)throws IOException{
        byte[] bytes;try(var in=Files.newInputStream(file,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(33);}
        if(!MessageDigest.isEqual(bytes,HexFormat.of().parseHex(binding)))throw new IOException("Cinnabar allocation policy/environment identity changed");
    }
    private void noPending(String component)throws IOException{
        try(var stream=Files.newDirectoryStream(directory,component+".pending-*")){
            if(stream.iterator().hasNext())throw new IOException("Unresolved cinnabar allocation write");
        }
    }
    private byte[] encode(Allocation allocation)throws IOException{
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        out.writeInt(MAGIC);out.writeInt(VERSION);out.writeUTF(binding);out.writeUTF(allocation.componentIdentity());
        out.writeInt(allocation.plan().concentrationReserves().size());for(int reserve:allocation.plan().concentrationReserves())out.writeInt(reserve);
        out.flush();return bytes.toByteArray();
    }
    private Allocation read(String component)throws IOException{
        validHash(component);noPending(component);verifyIdentity(marker(component));byte[] bytes;
        try(var in=Files.newInputStream(directory.resolve(component+".bin"),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){bytes=in.readNBytes(4097);}
        if(bytes.length<40||bytes.length>4096)throw new IOException("Invalid allocation record length");
        byte[] body=Arrays.copyOf(bytes,bytes.length-32);
        if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Allocation checksum mismatch");
        try(var in=new DataInputStream(new ByteArrayInputStream(body))){
            if(in.readInt()!=MAGIC||in.readInt()!=VERSION||!in.readUTF().equals(binding)||!in.readUTF().equals(component))throw new IOException("Allocation record identity changed");
            int count=in.readInt();if(count<1||count>MAX_SLOTS)throw new IOException("Invalid concentration count");
            var reserves=new ArrayList<Integer>(count);for(int i=0;i<count;i++)reserves.add(in.readInt());
            if(in.available()!=0)throw new IOException("Trailing allocation data");return new Allocation(component,new Plan(reserves));
        }catch(IllegalArgumentException e){throw new IOException("Invalid saved concentration budget",e);}
    }
    @FunctionalInterface private interface Action<T>{T run()throws IOException;}
    private <T>T locked(Action<T> action)throws IOException{
        verify();
        try(var channel=FileChannel.open(directory.resolve("allocation.lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS)){
            FileLock lock;try{lock=channel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Cinnabar directory busy",e);}
            if(lock==null)throw new IOException("Cinnabar directory busy");try(lock){verify();return action.run();}
        }
    }
    private static void put(FileChannel channel,byte[] bytes)throws IOException{var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);}
    private static void validHash(String value){if(value==null||!value.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Expected SHA256 identity");}
    private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
