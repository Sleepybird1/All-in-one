package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;

/** Chunk-local natural ore provenance. Native generation, mutation and chunk-save hooks are required. */
public final class MiningOreLedger {
    private static final int MAGIC=0x49434f4c,VERSION=1,MAX_OWNERS=128;
    private final int chunkX,chunkZ,minY,maxY,volume;
    private final Map<String,BitSet> owners=new LinkedHashMap<>();
    private final BitSet occupied=new BitSet();
    private boolean sealed,failed;
    // Process-local observation token; never persisted or used as ownership authority.
    private long revision;
    private String surfaceIdentity="";
    private boolean surfaceComplete;
    public MiningOreLedger(int chunkX,int chunkZ,int minY,int maxY){
        long height=(long)maxY-minY;
        if(height<=0||height>4096)throw new IllegalArgumentException("Unsupported provenance height");
        if(chunkX<Integer.MIN_VALUE/16||chunkX>Integer.MAX_VALUE/16||chunkZ<Integer.MIN_VALUE/16||chunkZ>Integer.MAX_VALUE/16)
            throw new IllegalArgumentException("Unrepresentable chunk");
        this.chunkX=chunkX;this.chunkZ=chunkZ;this.minY=minY;this.maxY=maxY;volume=(int)height*256;
    }
    private static void validKey(String key){if(key==null||!key.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid deposit key");}
    private int index(int x,int y,int z){
        if((x>>4)!=chunkX||(z>>4)!=chunkZ||y<minY||y>=maxY)throw new IllegalArgumentException("Foreign provenance position");
        return (y-minY)*256+(z&15)*16+(x&15);
    }
    /** Call only after actual successful geological placement, before generation is sealed. */
    public synchronized void recordGenerated(String key,int x,int y,int z){
        validKey(key);int index=index(x,y,z);
        if(sealed||failed)throw new IllegalStateException("Natural ore generation already sealed or failed");
        if(occupied.get(index))throw new IllegalStateException("Position already has a geological owner");
        if(!owners.containsKey(key)&&owners.size()>=MAX_OWNERS)throw new IllegalStateException("Too many deposit owners");
        owners.computeIfAbsent(key,k->new BitSet()).set(index);occupied.set(index);revision++;
    }
    public record Cell(int x,int y,int z) {}
    /** Validate the entire physical-write batch before adding any ownership.
     * An invalid late cell cannot leave a partially accepted provenance record. */
    public synchronized void recordGeneratedBatch(String key,Collection<Cell> cells){
        validKey(key);Objects.requireNonNull(cells);
        if(sealed||failed)throw new IllegalStateException("Natural ore generation already sealed or failed");
        if(cells.size()>volume)throw new IllegalArgumentException("Batch exceeds owner volume");
        var additions=new BitSet();
        for(var p:cells){Objects.requireNonNull(p);int i=index(p.x(),p.y(),p.z());
            if(additions.get(i)||occupied.get(i))throw new IllegalStateException("Duplicate geological ownership");
            additions.set(i);
        }
        if(additions.isEmpty())return;
        if(!owners.containsKey(key)&&owners.size()>=MAX_OWNERS)throw new IllegalStateException("Too many deposit owners");
        owners.computeIfAbsent(key,k->new BitSet()).or(additions);occupied.or(additions);revision++;
    }
    public synchronized void seal(){
        if(failed)throw new IllegalStateException("Failed generation cannot certify natural ore");
        if(!surfaceIdentity.isEmpty()&&!surfaceComplete)throw new IllegalStateException("Surface generation still pending");
        if(!sealed){sealed=true;revision++;}
    }
    /** Pin the future surface phase before any writes. No existing intent may be replaced. */
    public synchronized void deferSurface(String identity){
        validKey(identity);
        if(sealed||failed||!surfaceIdentity.isEmpty()||!owners.isEmpty())throw new IllegalStateException("Fresh empty generation ledger required for surface intent");
        surfaceIdentity=identity;revision++;
    }
    public synchronized boolean surfacePending(String identity){validKey(identity);return !sealed&&!failed&&!surfaceComplete&&surfaceIdentity.equals(identity);}
    public synchronized boolean surfaceFinished(String identity){validKey(identity);return sealed&&!failed&&surfaceComplete&&surfaceIdentity.equals(identity);}
    /** Caller has verified every expected surface write. This is the only pending-to-sealed transition. */
    public synchronized void finishSurface(String identity){
        if(!surfacePending(identity))throw new IllegalStateException("Surface intent missing, changed, completed or held");
        surfaceComplete=true;sealed=true;revision++;
    }
    /** Preserve partial claims for diagnosis, but never authorize harvest or exhausted completion.
     * This is a terminal hold, not rollback of physical block writes. */
    public synchronized void abort(){
        if(failed)return;
        if(sealed)throw new IllegalStateException("Cannot abort completed natural ore generation");
        failed=true;revision++;
    }
    public synchronized boolean failed(){return failed;}
    public synchronized boolean sealed(){return sealed;}
    /** Placement conflict query only; an unfinished/failed claim never authorizes harvesting. */
    public synchronized boolean claimed(int x,int y,int z){return occupied.get(index(x,y,z));}
    public synchronized boolean owns(String key,int x,int y,int z){
        validKey(key);int index=index(x,y,z);var bits=owners.get(key);
        return sealed&&!failed&&bits!=null&&bits.get(index);
    }
    /** Every post-generation block change must revoke provenance, even replacement with another ore. */
    public synchronized boolean invalidate(int x,int y,int z){
        int index=index(x,y,z);if(!occupied.get(index))return false;
        for(var bits:owners.values())bits.clear(index);occupied.clear(index);revision++;return true;
    }
    public synchronized int remaining(){return occupied.cardinality();}
    public synchronized long revision(){return revision;}
    /** Immutable physical positions for bounded observation; unfinished claims never become an empty count. */
    public synchronized OwnerSnapshot snapshot(String key){
        validKey(key);
        return new OwnerSnapshot(revision,sealed&&!failed,owners.getOrDefault(key,new BitSet()));
    }
    public record OwnerSnapshot(long revision,boolean complete,BitSet cells){
        public OwnerSnapshot {cells=(BitSet)Objects.requireNonNull(cells).clone();}
        @Override public BitSet cells(){return (BitSet)cells.clone();}
    }

    /** Read-only exact natural owner of a selected block; unfinished history grants no association. */
    public synchronized Optional<String> ownerAt(int x,int y,int z){
        int cell=index(x,y,z);if(!sealed||failed||!occupied.get(cell))return Optional.empty();
        return owners.entrySet().stream().filter(e->e.getValue().get(cell)).map(Map.Entry::getKey).findFirst();
    }
    /** -1 means unfinished or failed generation; it cannot authorize a completion decision. */
    public synchronized int remaining(String key){validKey(key);var bits=owners.get(key);return !sealed||failed?-1:bits==null?0:bits.cardinality();}
    public synchronized byte[] encode()throws IOException{
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        // Preserve legacy v1 normal and v2 failed bytes. Only deferred surface work uses v3;
        // old readers refuse it rather than treating incomplete generation as completed ore.
        out.writeInt(MAGIC);out.writeInt(!surfaceIdentity.isEmpty()?3:failed?2:VERSION);out.writeInt(chunkX);out.writeInt(chunkZ);out.writeInt(minY);out.writeInt(maxY);
        out.writeByte(failed?2:sealed?1:0);
        if(!surfaceIdentity.isEmpty()){out.writeUTF(surfaceIdentity);out.writeBoolean(surfaceComplete);}
        out.writeInt(owners.size());
        for(var entry:owners.entrySet()){
            out.writeUTF(entry.getKey());long[] words=entry.getValue().toLongArray();out.writeInt(words.length);
            for(long word:words)out.writeLong(word);
        }
        out.flush();byte[] payload=bytes.toByteArray();out.write(digest(payload));out.flush();return bytes.toByteArray();
    }
    /** Decode against the receiving chunk, never silently rebase foreign or damaged provenance. */
    public static MiningOreLedger decode(byte[] data,int chunkX,int chunkZ,int minY,int maxY)throws IOException{
        var ledger=new MiningOreLedger(chunkX,chunkZ,minY,maxY);
        long maxBytes=131L+MAX_OWNERS*(70L+((ledger.volume+63L)/64)*8);
        if(data==null||data.length<61||data.length>maxBytes)throw new IOException("Invalid provenance length");
        byte[] payload=Arrays.copyOf(data,data.length-32);
        if(!MessageDigest.isEqual(digest(payload),Arrays.copyOfRange(data,data.length-32,data.length)))throw new IOException("Provenance checksum mismatch");
        var in=new DataInputStream(new ByteArrayInputStream(payload));
        if(in.readInt()!=MAGIC)throw new IOException("Provenance magic mismatch");
        int version=in.readInt();
        if((version!=VERSION&&version!=2&&version!=3)||in.readInt()!=chunkX||in.readInt()!=chunkZ||in.readInt()!=minY||in.readInt()!=maxY)
            throw new IOException("Provenance version or chunk scope mismatch");
        int flag=in.readUnsignedByte();
        if(version==VERSION&&flag>1||version==2&&flag!=2||version==3&&flag>2)throw new IOException("Invalid generation state");
        ledger.sealed=flag==1;ledger.failed=flag==2;
        if(version==3){
            ledger.surfaceIdentity=in.readUTF();int complete=in.readUnsignedByte();
            try{validKey(ledger.surfaceIdentity);}catch(IllegalArgumentException e){throw new IOException("Invalid surface identity",e);}
            if(complete>1||(complete==1)!=(flag==1))throw new IOException("Invalid surface completion state");
            ledger.surfaceComplete=complete==1;
        }
        int count=in.readInt();if(count<0||count>MAX_OWNERS)throw new IOException("Invalid owner count");
        for(int i=0;i<count;i++){
            String key=in.readUTF();try{validKey(key);}catch(IllegalArgumentException e){throw new IOException(e);}
            if(ledger.owners.containsKey(key))throw new IOException("Duplicate owner");
            int n=in.readInt();if(n<0||n>(ledger.volume+63)/64||n>(in.available()/8))throw new IOException("Invalid provenance bitmap length");
            long[] words=new long[n];for(int w=0;w<n;w++)words[w]=in.readLong();var bits=BitSet.valueOf(words);
            if(bits.length()>ledger.volume||bits.intersects(ledger.occupied))throw new IOException("Overlapping or foreign provenance");
            ledger.owners.put(key,bits);ledger.occupied.or(bits);
        }
        if(in.available()!=0)throw new IOException("Trailing provenance data");return ledger;
    }
    private static byte[] digest(byte[] data){try{return MessageDigest.getInstance("SHA-256").digest(data);}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
}
