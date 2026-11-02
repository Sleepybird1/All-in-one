package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Separate moving-recovery envelope around immutable identity/custody/pose
 * evidence. V2 uses persisted DeepSpaceData universe ticks; V1 dimension game
 * clocks are deliberately not reinterpreted or accepted. The embedded baseline is data, never a stationary recovery request.
 * A native auditor must additionally verify ownership, unique stored/live bodies,
 * rotations, controls, cargo, orbital frames and current resolved motion. */
public record OrbitalCommonMotionRecoveryRecord(OrbitalEncounterRecoveryRecord baseline,
 V commonVelocity,long preparedUniverseTick,String proofDigest) {
 public static final String PREFIX="IC_ORBITAL_ENCOUNTER_V1\nCOMMON_MOTION_RECOVERY_V2\n";
 public enum Outcome { UNAPPLIED, APPLIED }
 public OrbitalCommonMotionRecoveryRecord {
  Objects.requireNonNull(baseline);Objects.requireNonNull(commonVelocity);
  if(!commonVelocity.finite()||commonVelocity.length()<=.1||commonVelocity.length()>1||preparedUniverseTick<0
    ||proofDigest==null||!proofDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid bounded common-motion recovery evidence");
 }
 /** Never treats a stored intent as an instruction to move. Ten-minute maximum
  * coasting window; loading pauses may shorten actual motion within that window. */
 public Outcome classify(long sourceCell,long targetCell,V sourcePosition,V targetPosition,
                         V sourceVelocity,V targetVelocity,long universeTick){
  if(universeTick<preparedUniverseTick||universeTick-preparedUniverseTick>12000)throw new IllegalStateException("Moving recovery clock outside qualified window");
  for(V v:List.of(sourcePosition,targetPosition,sourceVelocity,targetVelocity))if(!v.finite())throw new IllegalStateException("Nonfinite moving recovery state");
  if(!sourceVelocity.equals(commonVelocity)||!targetVelocity.equals(commonVelocity)||targetCell!=baseline.targetCell())throw new IllegalStateException("Moving recovery velocity or destination cell changed");
  V drift=targetPosition.sub(baseline.targetPosition());double seconds=drift.dot(commonVelocity)/commonVelocity.dot(commonVelocity);
  if(!Double.isFinite(seconds)||seconds<0||seconds>(universeTick-preparedUniverseTick)*.05+.05
    ||drift.sub(commonVelocity.mul(seconds)).length()>1e-3)throw new IllegalStateException("Destination motion is not bounded common coasting");
  Outcome outcome;V expected;
  if(sourceCell==baseline.sourceCell()){outcome=Outcome.UNAPPLIED;expected=baseline.oldPosition().add(drift);}
  else if(sourceCell==baseline.targetCell()){outcome=Outcome.APPLIED;expected=baseline.newPosition().add(drift);}
  else throw new IllegalStateException("Original cargo body occupies an unexpected cell");
  if(sourcePosition.sub(expected).length()>1e-3)throw new IllegalStateException("Original cargo body disagrees with recorded coasting outcome");
  return outcome;
 }
 public String encode(){
  try{var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434d32);out.writeUTF(baseline.encode());out.writeDouble(commonVelocity.x());out.writeDouble(commonVelocity.y());out.writeDouble(commonVelocity.z());out.writeLong(preparedUniverseTick);out.writeUTF(proofDigest);
  }return PREFIX+Base64.getEncoder().encodeToString(bytes.toByteArray());}catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static OrbitalCommonMotionRecoveryRecord decode(String text)throws IOException{
  if(text==null||text.length()>16384||!text.startsWith(PREFIX))throw new IOException("Unsupported common-motion recovery record");
  try(var in=new DataInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(text.substring(PREFIX.length()))))){
   if(in.readInt()!=0x49434d32)throw new IOException("Unknown common-motion schema");
   var result=new OrbitalCommonMotionRecoveryRecord(OrbitalEncounterRecoveryRecord.decode(in.readUTF()),new V(in.readDouble(),in.readDouble(),in.readDouble()),in.readLong(),in.readUTF());
   if(in.available()!=0||!result.encode().equals(text))throw new IOException("Trailing or noncanonical common-motion record");return result;
  }catch(IllegalArgumentException|NullPointerException invalid){throw new IOException("Malformed common-motion record",invalid);}
 }
}
