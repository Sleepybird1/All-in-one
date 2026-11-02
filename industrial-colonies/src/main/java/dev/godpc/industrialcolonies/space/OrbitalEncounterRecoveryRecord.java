package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Exact bounded recovery evidence, never instructions to replay a movement.
 * A native verifier must match the observed old or new state before journal
 * reconciliation. This codec alone establishes no ownership or cargo facts.
 */
public record OrbitalEncounterRecoveryRecord(UUID journey,UUID owner,UUID body,UUID target,
 UUID transponder,UUID targetTransponder,UUID retiredSource,UUID retiredTarget,
 long preparedRevision,long serverTick,long sourceCell,long targetCell,String dimension,String frame,
 V oldPosition,V newPosition,V targetPosition,Rotation sourceRotation,Rotation targetRotation,
 String sourceDigest,String targetDigest) {
 private static final String PREFIX="IC_ORBITAL_ENCOUNTER_V1\nSTATIONARY_RECOVERY_V1\n";
 public record Rotation(double x,double y,double z,double w){
  public Rotation{double norm=x*x+y*y+z*z+w*w;if(!Double.isFinite(norm)||Math.abs(norm-1)>1e-6)throw new IllegalArgumentException("Finite normalized rotation required");}
 }
 public OrbitalEncounterRecoveryRecord {
  for(UUID id:List.of(journey,owner,body,target,transponder,targetTransponder,retiredSource,retiredTarget))Objects.requireNonNull(id);
  if(body.equals(target)||transponder.equals(targetTransponder)||body.equals(retiredSource)||target.equals(retiredTarget)
    ||sourceCell==targetCell||preparedRevision<0||serverTick<0)throw new IllegalArgumentException("Conflicting encounter identities or clocks");
  for(String label:List.of(dimension,frame))if(label.isBlank()||label.length()>256)throw new IllegalArgumentException("Invalid encounter frame label");
  for(V p:List.of(oldPosition,newPosition,targetPosition))if(!p.finite()||Math.abs(p.x())>=30000000||Math.abs(p.y())>=30000000||Math.abs(p.z())>=30000000)throw new IllegalArgumentException("Invalid native encounter position");
  Objects.requireNonNull(sourceRotation);Objects.requireNonNull(targetRotation);
  for(String digest:List.of(sourceDigest,targetDigest))if(!digest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Exact recovery digest required");
 }
 public String encode(){
  try{var buffer=new ByteArrayOutputStream();try(var out=new DataOutputStream(buffer)){
   out.writeInt(0x49434531);
   for(UUID id:List.of(journey,owner,body,target,transponder,targetTransponder,retiredSource,retiredTarget)){out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
   for(long n:new long[]{preparedRevision,serverTick,sourceCell,targetCell})out.writeLong(n);
   out.writeUTF(dimension);out.writeUTF(frame);
   for(V p:List.of(oldPosition,newPosition,targetPosition)){out.writeDouble(p.x());out.writeDouble(p.y());out.writeDouble(p.z());}
   for(Rotation q:List.of(sourceRotation,targetRotation)){out.writeDouble(q.x());out.writeDouble(q.y());out.writeDouble(q.z());out.writeDouble(q.w());}
   out.writeUTF(sourceDigest);out.writeUTF(targetDigest);
  }return PREFIX+Base64.getEncoder().encodeToString(buffer.toByteArray());}catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static OrbitalEncounterRecoveryRecord decode(String text)throws IOException{
  if(text==null||text.length()>8192||!text.startsWith(PREFIX))throw new IOException("Unsupported native encounter recovery record");
  try{
   byte[] bytes=Base64.getDecoder().decode(text.substring(PREFIX.length()));
   try(var in=new DataInputStream(new ByteArrayInputStream(bytes))){
    if(in.readInt()!=0x49434531)throw new IOException("Unknown encounter recovery schema");
    UUID[] id=new UUID[8];for(int i=0;i<id.length;i++)id[i]=new UUID(in.readLong(),in.readLong());
    long revision=in.readLong(),tick=in.readLong(),source=in.readLong(),target=in.readLong();String dimension=in.readUTF(),frame=in.readUTF();
    V[] p=new V[3];for(int i=0;i<p.length;i++)p[i]=new V(in.readDouble(),in.readDouble(),in.readDouble());
    Rotation[] q=new Rotation[2];for(int i=0;i<q.length;i++)q[i]=new Rotation(in.readDouble(),in.readDouble(),in.readDouble(),in.readDouble());
    var result=new OrbitalEncounterRecoveryRecord(id[0],id[1],id[2],id[3],id[4],id[5],id[6],id[7],revision,tick,source,target,dimension,frame,p[0],p[1],p[2],q[0],q[1],in.readUTF(),in.readUTF());
    if(in.available()!=0||!result.encode().equals(text))throw new IOException("Trailing or noncanonical encounter recovery data");return result;
   }
  }catch(IllegalArgumentException|NullPointerException invalid){throw new IOException("Malformed encounter recovery data",invalid);}
 }
}
