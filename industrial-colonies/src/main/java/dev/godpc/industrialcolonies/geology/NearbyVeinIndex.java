package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.util.*;

/** Prospecting hints only, never extraction authority. Exact observed X/Z columns,
 * indexed in16block buckets. A query examines at most252004buckets, no terrain reads. */
public final class NearbyVeinIndex {
 private final Map<String,Map<Long,BitSet>> families=new TreeMap<>();
 private static long key(int x,int z){return ((long)x<<32)^(z&0xffffffffL);}
 private static void family(String id){if(id==null||!id.matches("[a-z0-9_]{1,80}"))throw new IllegalArgumentException("Invalid clue mineral family");}
 public synchronized boolean record(String family,int x,int z){
  family(family);var columns=families.computeIfAbsent(family,k->new HashMap<>()).computeIfAbsent(key(x>>4,z>>4),k->new BitSet(256));
  int bit=(x&15)+16*(z&15);boolean added=!columns.get(bit);columns.set(bit);return added;
 }
 private static Iterable<Map.Entry<Long,BitSet>> candidates(Map<Long,BitSet> buckets,long minX,long maxX,long minZ,long maxZ){
  long cells=(maxX-minX+1)*(maxZ-minZ+1);
  if(buckets.size()<=cells)return buckets.entrySet();
  var result=new ArrayList<Map.Entry<Long,BitSet>>();
  for(long cx=minX;cx<=maxX;cx++)for(long cz=minZ;cz<=maxZ;cz++){
   long k=key((int)cx,(int)cz);var bits=buckets.get(k);if(bits!=null)result.add(Map.entry(k,bits));
  }
  return result;
 }
 public synchronized boolean nearby(String family,int x,int z,int radius){
  family(family);if(radius<0||radius>4000)throw new IllegalArgumentException("Clue radius must be0..4000");
  var buckets=families.get(family);if(buckets==null)return false;
  long minimumX=(long)x-radius,maximumX=(long)x+radius,minimumZ=(long)z-radius,maximumZ=(long)z+radius;
  if(minimumX<Integer.MIN_VALUE||maximumX>Integer.MAX_VALUE||minimumZ<Integer.MIN_VALUE||maximumZ>Integer.MAX_VALUE)return false;
  long limit=(long)radius*radius;
  for(var entry:candidates(buckets,Math.floorDiv(minimumX,16),Math.floorDiv(maximumX,16),Math.floorDiv(minimumZ,16),Math.floorDiv(maximumZ,16))){
   int cx=(int)(entry.getKey()>>32),cz=(int)(long)entry.getKey();
   if(cx<Math.floorDiv(minimumX,16)||cx>Math.floorDiv(maximumX,16)||cz<Math.floorDiv(minimumZ,16)||cz>Math.floorDiv(maximumZ,16))continue;
   var columns=entry.getValue();
   for(int bit=columns.nextSetBit(0);bit>=0;bit=columns.nextSetBit(bit+1)){
    long dx=(long)cx*16+(bit&15)-x,dz=(long)cz*16+(bit>>4)-z;
    if(dx*dx+dz*dz<=limit)return true;
   }
  }
  return false;
 }
 public record Observation(int x,int z,long distanceSquared) {}
 /** Closest recorded matching source in a bounded circle; no terrain access or new discovery. */
 public synchronized Optional<Observation> nearest(String family,int x,int z,int radius){
  family(family);if(radius<0||radius>4000)throw new IllegalArgumentException("Prospecting radius0..4000");
  var buckets=families.get(family);if(buckets==null)return Optional.empty();
  Observation best=null;long limit=(long)radius*radius;
  long minCX=Math.floorDiv((long)x-radius,16),maxCX=Math.floorDiv((long)x+radius,16);
  long minCZ=Math.floorDiv((long)z-radius,16),maxCZ=Math.floorDiv((long)z+radius,16);
  for(var entry:candidates(buckets,minCX,maxCX,minCZ,maxCZ)){
    long cx=(int)(entry.getKey()>>32),cz=(int)(long)entry.getKey();
    if(cx<minCX||cx>maxCX||cz<minCZ||cz>maxCZ)continue;
    var bits=entry.getValue();
    for(int bit=bits.nextSetBit(0);bit>=0;bit=bits.nextSetBit(bit+1)){
     long px=cx*16+(bit&15),pz=cz*16+(bit>>4),dx=px-x,dz=pz-z,d=dx*dx+dz*dz;
     if(px<Integer.MIN_VALUE||px>Integer.MAX_VALUE||pz<Integer.MIN_VALUE||pz>Integer.MAX_VALUE||d>limit)continue;
     if(best==null||d<best.distanceSquared()||(d==best.distanceSquared()&&(px<best.x()||(px==best.x()&&pz<best.z()))))
      best=new Observation((int)px,(int)pz,d);
    }
   }
  return Optional.ofNullable(best);
 }
 /** Actual source columns in this owner, not a regional prediction or proximity guess. */
 public synchronized Set<String> familiesInChunk(int chunkX,int chunkZ){
  var result=new TreeSet<String>();long bucket=key(chunkX,chunkZ);
  families.forEach((family,columns)->{var bits=columns.get(bucket);if(bits!=null&&!bits.isEmpty())result.add(family);});
  return Set.copyOf(result);
 }
 /** Families with a real observed source within radius of any point in this chunk.
  * Broad phase only: each chosen clue coordinate must still pass nearby(). */
 public synchronized Set<String> familiesNearChunk(int chunkX,int chunkZ,int radius){
  return familiesNearChunk(chunkX,chunkZ,radius,Map.of());
 }
 public synchronized Set<String> familiesNearChunk(int chunkX,int chunkZ,int radius,Map<String,Integer> overrides){
  if(radius<0||radius>4000)throw new IllegalArgumentException("Clue radius0..4000");
  long minX=(long)chunkX*16,minZ=(long)chunkZ*16,maxX=minX+15,maxZ=minZ+15;
  var result=new TreeSet<String>();
  for(var family:families.entrySet()){
   int reach=overrides.getOrDefault(family.getKey(),radius);
   if(reach<0||reach>4000)throw new IllegalArgumentException("Clue override radius0..4000");
   long limit=(long)reach*reach;
   outer:for(var entry:candidates(family.getValue(),Math.floorDiv(minX-reach,16),Math.floorDiv(maxX+reach,16),Math.floorDiv(minZ-reach,16),Math.floorDiv(maxZ+reach,16))){
     long cx=(int)(entry.getKey()>>32),cz=(int)(long)entry.getKey();
     if(cx<Math.floorDiv(minX-reach,16)||cx>Math.floorDiv(maxX+reach,16)||cz<Math.floorDiv(minZ-reach,16)||cz>Math.floorDiv(maxZ+reach,16))continue;
     var bits=entry.getValue();
     for(int bit=bits.nextSetBit(0);bit>=0;bit=bits.nextSetBit(bit+1)){
      long x=cx*16+(bit&15),z=cz*16+(bit>>4),dx=Math.max(0,Math.max(minX-x,x-maxX)),dz=Math.max(0,Math.max(minZ-z,z-maxZ));
      if(dx*dx+dz*dz<=limit){result.add(family.getKey());break outer;}
     }
    }
  }
  return Set.copyOf(result);
 }
 public synchronized byte[] encode()throws IOException{
  var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeInt(0x49435643);out.writeInt(1);out.writeInt(families.size());
  for(var family:families.entrySet()){
   out.writeUTF(family.getKey());out.writeInt(family.getValue().size());
   for(var entry:new TreeMap<>(family.getValue()).entrySet()){
    out.writeLong(entry.getKey());long[] words=entry.getValue().toLongArray();out.writeInt(words.length);for(long word:words)out.writeLong(word);
   }
  }
  out.flush();byte[] payload=bytes.toByteArray();
  try{out.write(java.security.MessageDigest.getInstance("SHA-256").digest(payload));}catch(java.security.NoSuchAlgorithmException e){throw new AssertionError(e);}
  out.flush();return bytes.toByteArray();
 }
 public static NearbyVeinIndex decode(byte[] bytes)throws IOException{
  if(bytes.length<44||bytes.length>64*1024*1024)throw new IOException("Clue index exceeds safety bound");
  byte[] payload=Arrays.copyOf(bytes,bytes.length-32),footer=Arrays.copyOfRange(bytes,bytes.length-32,bytes.length);
  try{if(!java.security.MessageDigest.isEqual(footer,java.security.MessageDigest.getInstance("SHA-256").digest(payload)))throw new IOException("Clue index checksum mismatch");}
  catch(java.security.NoSuchAlgorithmException e){throw new AssertionError(e);}
  var index=new NearbyVeinIndex();var in=new DataInputStream(new ByteArrayInputStream(payload));
  if(in.readInt()!=0x49435643||in.readInt()!=1)throw new IOException("Unknown clue index format");
  int count=in.readInt();if(count<0||count>256)throw new IOException("Clue family count");int total=0;
  for(int i=0;i<count;i++){
   String id=in.readUTF();try{family(id);}catch(IllegalArgumentException e){throw new IOException(e);}
   if(index.families.containsKey(id))throw new IOException("Duplicate clue family");
   int size=in.readInt();if(size<0||size>1000000||(total+=size)>1000000)throw new IOException("Clue bucket count");
   var map=new HashMap<Long,BitSet>();index.families.put(id,map);
   for(int j=0;j<size;j++){
    long key=in.readLong();int words=in.readInt();if(words<1||words>4)throw new IOException("Clue column words");
    long[] value=new long[words];for(int k=0;k<words;k++)value[k]=in.readLong();var bits=BitSet.valueOf(value);
    if(bits.isEmpty()||map.putIfAbsent(key,bits)!=null)throw new IOException("Empty/duplicate clue bucket");
   }
  }
  if(in.available()!=0)throw new IOException("Trailing clue bytes");return index;
 }
}
