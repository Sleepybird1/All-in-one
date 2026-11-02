package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Past stationary-local to moving-local frame conversion evidence only.
 * Does not authorize conversion, resume, or journal repair. Native auditors
 * must separately establish identity, custody, rotation, cell and orbit state. */
public record OrbitalDistinctCoastRecoveryRecord(OrbitalEncounterRecoveryRecord baseline,
 V receivingVelocity,long preparedUniverseTick,String proofDigest,String destinationDigest,OrbitalDistinctCoastState coasts){
 public static final String PREFIX="IC_ORBITAL_ENCOUNTER_V1\nDISTINCT_COAST_RECOVERY_V1\n";
 public enum Outcome{UNAPPLIED,APPLIED}
 public OrbitalDistinctCoastRecoveryRecord{
  Objects.requireNonNull(baseline);Objects.requireNonNull(receivingVelocity);Objects.requireNonNull(coasts);
  if(coasts.sourceVelocity().sub(coasts.targetVelocity()).sub(receivingVelocity).length()>1e-6)throw new IllegalArgumentException("Receiving velocity disagrees with recorded frames");
  if(!receivingVelocity.finite()||receivingVelocity.length()<=1e-3||receivingVelocity.length()>.08
   ||preparedUniverseTick<0||proofDigest==null||!proofDigest.matches("[0-9a-f]{64}")
   ||destinationDigest==null||!destinationDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid distinct-coast receipt");
  try{OrbitalMotionPrecision.requireResolved(baseline.newPosition(),receivingVelocity,2,18);}
  catch(IllegalStateException invalid){throw new IllegalArgumentException("Unresolved receiving motion",invalid);}
 }
 public Outcome classify(long sourceCell,long targetCell,V sourcePosition,V targetPosition,V sourceNow,V targetNow,long universeTick){
  return classify(sourceCell,targetCell,sourcePosition,targetPosition,sourceNow,targetNow,universeTick,false);
 }
 /** Only for a durably acknowledged successful conversion. Allows an exactly
  * stopped body on its bounded represented coast segment; never repairs motion
  * or proves that a pending conversion completed. Caller keeps the journey held. */
 public Outcome classifyAcknowledged(long sourceCell,long targetCell,V sourcePosition,V targetPosition,V sourceNow,V targetNow,long universeTick){
  return classify(sourceCell,targetCell,sourcePosition,targetPosition,sourceNow,targetNow,universeTick,true);
 }
 private Outcome classify(long sourceCell,long targetCell,V sourcePosition,V targetPosition,V sourceNow,V targetNow,long universeTick,boolean acknowledged){
  if(universeTick<preparedUniverseTick||universeTick-preparedUniverseTick>600)throw new IllegalStateException("Distinct coast recovery exceeds30second audit window");
  for(V v:List.of(sourcePosition,targetPosition,sourceNow,targetNow))if(!v.finite())throw new IllegalStateException("Nonfinite recovery state");
  if(targetCell!=baseline.targetCell()||targetNow.length()!=0||targetPosition.sub(baseline.targetPosition()).length()>1e-3)throw new IllegalStateException("Destination moved or changed cell");
  if(sourceCell==baseline.sourceCell()){
   if(sourceNow.length()!=0||sourcePosition.sub(baseline.oldPosition()).length()>1e-3)throw new IllegalStateException("Unapplied source changed");
   return Outcome.UNAPPLIED;
  }
  boolean stopped=acknowledged&&sourceNow.length()==0;
  if(sourceCell!=baseline.targetCell()||!stopped&&sourceNow.sub(receivingVelocity).length()>1e-6)throw new IllegalStateException("Applied source cell or velocity changed");
  var nativeMotion=OrbitalMotionPrecision.requireResolved(baseline.newPosition(),receivingVelocity,2,18);
  var effective=nativeMotion.representedVelocity();var drift=sourcePosition.sub(nativeMotion.representedPosition());
  double seconds=drift.dot(effective)/effective.dot(effective);
  if(!Double.isFinite(seconds)||seconds<0||seconds>(universeTick-preparedUniverseTick)*.05+.05
   ||drift.sub(effective.mul(seconds)).length()>1e-3)throw new IllegalStateException("Applied source is not bounded represented coasting");
  // Refuse changes in float resolution along the observed path.
  if(OrbitalMotionPrecision.requireResolved(sourcePosition,receivingVelocity,2,18).representedVelocity().sub(effective).length()>1e-9)throw new IllegalStateException("Native float velocity changed across path");
  return Outcome.APPLIED;
 }
 public String encode(){
  try{var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434431);out.writeUTF(baseline.encode());out.writeDouble(receivingVelocity.x());out.writeDouble(receivingVelocity.y());out.writeDouble(receivingVelocity.z());out.writeLong(preparedUniverseTick);out.writeUTF(proofDigest);out.writeUTF(destinationDigest);coasts.write(out);
  }return PREFIX+Base64.getEncoder().encodeToString(bytes.toByteArray());}catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static OrbitalDistinctCoastRecoveryRecord decode(String text)throws IOException{
  if(text==null||text.length()>16384||!text.startsWith(PREFIX))throw new IOException("Unsupported distinct coast receipt");
  try(var in=new DataInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(text.substring(PREFIX.length()))))){
   if(in.readInt()!=0x49434431)throw new IOException("Unknown distinct coast schema");
   var result=new OrbitalDistinctCoastRecoveryRecord(OrbitalEncounterRecoveryRecord.decode(in.readUTF()),new V(in.readDouble(),in.readDouble(),in.readDouble()),in.readLong(),in.readUTF(),in.readUTF(),OrbitalDistinctCoastState.read(in));
   if(in.available()!=0||!result.encode().equals(text))throw new IOException("Trailing or noncanonical receipt");return result;
  }catch(IllegalArgumentException|NullPointerException bad){throw new IOException("Malformed distinct coast receipt",bad);}
 }
}
