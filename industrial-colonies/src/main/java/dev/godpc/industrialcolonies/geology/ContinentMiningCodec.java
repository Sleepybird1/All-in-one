package dev.godpc.industrialcolonies.geology;
import java.io.*;
import java.security.*;
import java.util.*;

/** Bounded exact-scope encoding; saved geometry fingerprints refuse algorithm drift. */
public final class ContinentMiningCodec {
 private static final int MAGIC=0x49434d43,VERSION=1,MAX_BYTES=4096;
 public static byte[] encode(MiningScanScope s)throws IOException{
  if(s.isCoal()){
   var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeInt(MAGIC);out.writeInt(2);
   s.coalReservation().write(out);out.writeInt(s.minBuildY());out.writeInt(s.maxBuildYExclusive());out.writeUTF(s.geometryFingerprint());
   out.flush();out.write(hash(bytes.toByteArray()));out.flush();if(bytes.size()>MAX_BYTES)throw new IOException("Coal scope too large");return bytes.toByteArray();
  }
  var r=s.occurrence();var k=r.key();var c=r.candidate();var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
  out.writeInt(MAGIC);out.writeInt(VERSION);out.writeLong(k.worldSeed());out.writeUTF(k.dimension());out.writeUTF(k.presetSha256());out.writeInt(k.continent().centerX());out.writeInt(k.continent().centerZ());out.writeInt(k.continent().identityBits());out.writeUTF(k.family());out.writeUTF(k.policySha256());
  out.writeInt(c.x());out.writeInt(c.y());out.writeInt(c.z());out.writeLong(c.geometrySeed());out.writeInt(c.cells());out.writeUTF(c.biome());out.writeDouble(r.chance());out.writeInt(s.minBuildY());out.writeInt(s.maxBuildYExclusive());out.writeUTF(s.geometryFingerprint());out.flush();out.write(hash(bytes.toByteArray()));out.flush();
  byte[] result=bytes.toByteArray();if(result.length>MAX_BYTES)throw new IOException("Continent scope too large");return result;
 }
 public static MiningScanScope decode(byte[] bytes)throws IOException{
  if(bytes==null||bytes.length<64||bytes.length>MAX_BYTES)throw new IOException("Invalid continent scope length");byte[] payload=Arrays.copyOf(bytes,bytes.length-32);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Continent scope checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=MAGIC)throw new IOException("Unknown continent scope magic");int version=in.readInt();
   if(version==2){
    var coal=CoalMiningReservation.read(in);int min=in.readInt(),max=in.readInt();String geometry=in.readUTF();
    if(in.available()!=0)throw new IOException("Trailing coal scope");var s=MiningScanScope.coal(coal,min,max);
    if(!geometry.equals(s.geometryFingerprint()))throw new IOException("Saved coal geometry changed; migration required");return s;
   }
   if(version!=VERSION)throw new IOException("Unknown continent scope format");long seed=in.readLong();String dim=in.readUTF(),preset=in.readUTF();var continent=new ReTerraForgedGeography.ContinentKey(in.readInt(),in.readInt(),in.readInt());
   var key=new ContinentCandidateSearch.Key(seed,dim,preset,continent,in.readUTF(),in.readUTF());var c=new ContinentOccurrenceLedger.Candidate(in.readInt(),in.readInt(),in.readInt(),in.readLong(),in.readInt(),in.readUTF());
   var r=new ContinentOccurrenceLedger.Request(key,c,in.readDouble());int min=in.readInt(),max=in.readInt();String geometry=in.readUTF();if(in.available()!=0)throw new IOException("Trailing continent scope");
   var s=MiningScanScope.continent(r,min,max);if(!geometry.equals(s.geometryFingerprint()))throw new IOException("Saved continent geometry changed; migration required");return s;
  }catch(IllegalArgumentException|ArithmeticException e){throw new IOException("Invalid continent scope",e);}
 }
 private static byte[] hash(byte[] data){try{return MessageDigest.getInstance("SHA-256").digest(data);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 private ContinentMiningCodec(){}
}
