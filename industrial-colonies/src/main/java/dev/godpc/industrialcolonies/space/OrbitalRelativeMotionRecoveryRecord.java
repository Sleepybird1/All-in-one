package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Unequal constant local-motion recovery data. Never an instruction to move.
 * A native auditor must verify original identity, cargo, frames, rotation,
 * current resolved velocities and the qualified physical dock separately. */
public record OrbitalRelativeMotionRecoveryRecord(OrbitalEncounterRecoveryRecord baseline,
 V sourceVelocity,V targetVelocity,long preparedUniverseTick,String proofDigest){
 public static final String PREFIX="IC_ORBITAL_ENCOUNTER_V1\nRELATIVE_MOTION_RECOVERY_V1\n";
 public enum Outcome{UNAPPLIED,APPLIED}
 public OrbitalRelativeMotionRecoveryRecord{
  Objects.requireNonNull(baseline);
  for(V v:List.of(sourceVelocity,targetVelocity))if(!v.finite()||v.length()<=.1||v.length()>1)throw new IllegalArgumentException("Invalid persistent bounded velocity");
  double speed=sourceVelocity.sub(targetVelocity).length();
  if(speed<=1e-3||speed>.08||preparedUniverseTick<0||proofDigest==null||!proofDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid relative recovery evidence");
 }
 public Outcome classify(long sourceCell,long targetCell,V sourcePosition,V targetPosition,V sourceNow,V targetNow,long universeTick){
  if(universeTick<preparedUniverseTick||universeTick-preparedUniverseTick>12000)throw new IllegalStateException("Relative recovery clock outside qualified window");
  for(V v:List.of(sourcePosition,targetPosition,sourceNow,targetNow))if(!v.finite())throw new IllegalStateException("Nonfinite relative recovery state");
  if(!sourceNow.equals(sourceVelocity)||!targetNow.equals(targetVelocity)||targetCell!=baseline.targetCell())throw new IllegalStateException("Relative recovery velocity or target cell changed");
  V drift=targetPosition.sub(baseline.targetPosition());double seconds=drift.dot(targetVelocity)/targetVelocity.dot(targetVelocity);
  if(!Double.isFinite(seconds)||seconds<0||seconds>(universeTick-preparedUniverseTick)*.05+.05||drift.sub(targetVelocity.mul(seconds)).length()>1e-3)throw new IllegalStateException("Target motion is not bounded coasting");
  Outcome result;V origin;
  if(sourceCell==baseline.sourceCell()){result=Outcome.UNAPPLIED;origin=baseline.oldPosition();}
  else if(sourceCell==baseline.targetCell()){result=Outcome.APPLIED;origin=baseline.newPosition();}
  else throw new IllegalStateException("Original cargo occupies unexpected cell");
  // Equal elapsed physical coasting is required, even when native loading
  // pauses reduce it below elapsed universe time. Unequal pauses fail closed.
  if(sourcePosition.sub(origin.add(sourceVelocity.mul(seconds))).length()>1e-3)throw new IllegalStateException("Original cargo disagrees with recorded relative coasting");
  return result;
 }
 public String encode(){
  try{var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49435231);out.writeUTF(baseline.encode());
   for(V v:List.of(sourceVelocity,targetVelocity)){out.writeDouble(v.x());out.writeDouble(v.y());out.writeDouble(v.z());}
   out.writeLong(preparedUniverseTick);out.writeUTF(proofDigest);
  }return PREFIX+Base64.getEncoder().encodeToString(bytes.toByteArray());}catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static OrbitalRelativeMotionRecoveryRecord decode(String text)throws IOException{
  if(text==null||text.length()>16384||!text.startsWith(PREFIX))throw new IOException("Unsupported relative-motion record");
  try(var in=new DataInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(text.substring(PREFIX.length()))))){
   if(in.readInt()!=0x49435231)throw new IOException("Unknown relative-motion schema");
   var result=new OrbitalRelativeMotionRecoveryRecord(OrbitalEncounterRecoveryRecord.decode(in.readUTF()),new V(in.readDouble(),in.readDouble(),in.readDouble()),new V(in.readDouble(),in.readDouble(),in.readDouble()),in.readLong(),in.readUTF());
   if(in.available()!=0||!result.encode().equals(text))throw new IOException("Trailing or noncanonical relative-motion record");return result;
  }catch(IllegalArgumentException|NullPointerException invalid){throw new IOException("Malformed relative-motion record",invalid);}
 }
}
