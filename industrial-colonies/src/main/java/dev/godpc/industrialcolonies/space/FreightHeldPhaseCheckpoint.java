package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;

/** Fresh held-phase coast baseline, separate from the original encounter window.
 * Native persistence re-epochs its orbit; compare propagated physical state
 * within the existing30second/1mm/1micrometer-per-second coast tolerances. */
public record FreightHeldPhaseCheckpoint(FreightHeldPhaseRecord phase,long universeTick,OrbitalDistinctCoastState coasts,FreightHeldPose sourcePose,FreightHeldPose targetPose,String sourceStorage,String targetStorage,boolean pumpFlowSamples) {
 private static final String PREFIX="ic-held-coast-v1:";
 public FreightHeldPhaseCheckpoint{Objects.requireNonNull(phase);if(pumpFlowSamples&&(phase.phase()!=FreightJourneyJournal.Phase.UNLOAD||sourceStorage==null))throw new IllegalArgumentException("Pump-flow profile requires UNLOAD and full witnesses");Objects.requireNonNull(coasts);if(universeTick<0)throw new IllegalArgumentException("Nonnegative held coast tick required");if((sourcePose==null)!=(targetPose==null))throw new IllegalArgumentException("Both pose witnesses required");
  if((sourceStorage==null)!=(targetStorage==null))throw new IllegalArgumentException("Both storage witnesses required");
  if(sourceStorage!=null){if(sourcePose==null||sourceStorage.equals(targetStorage))throw new IllegalArgumentException("Distinct storage and complete pose witnesses required");storage(sourceStorage);storage(targetStorage);}
 }
 public FreightHeldPhaseCheckpoint(FreightHeldPhaseRecord phase,long universeTick,OrbitalDistinctCoastState coasts,FreightHeldPose source,FreightHeldPose target,String sourceStorage,String targetStorage){this(phase,universeTick,coasts,source,target,sourceStorage,targetStorage,false);}
 public FreightHeldPhaseCheckpoint(FreightHeldPhaseRecord phase,long universeTick,OrbitalDistinctCoastState coasts){this(phase,universeTick,coasts,null,null,null,null);}
 public FreightHeldPhaseCheckpoint(FreightHeldPhaseRecord phase,long universeTick,OrbitalDistinctCoastState coasts,FreightHeldPose source,FreightHeldPose target){this(phase,universeTick,coasts,source,target,null,null);}
 private static void storage(String value){if(value.length()>256||value.startsWith("/")||value.contains("..")||!value.matches("[A-Za-z0-9_./-]+\\.slvls#[0-9]{1,4}")||Integer.parseInt(value.substring(value.lastIndexOf('#')+1))>1023)throw new IllegalArgumentException("Bounded original relative native storage location required");}
 /** Carries candidate original poses, never changes the original digest. Native
  * audit must authenticate them against that digest before granting recovery. */
 public FreightHeldPhaseCheckpoint withPoseWitness(FreightHeldPose source,FreightHeldPose target){
  if(source==null||target==null)throw new IllegalArgumentException("Both original pose witnesses required");
  if(sourcePose!=null&&(!sourcePose.equals(source)||!targetPose.equals(target)))throw new IllegalStateException("Cannot replace existing pose witnesses");
  return new FreightHeldPhaseCheckpoint(phase,universeTick,coasts,source,target,sourceStorage,targetStorage,pumpFlowSamples);
 }
 public FreightHeldPhaseCheckpoint withStorageWitness(String source,String target){
  if(source==null||target==null)throw new IllegalArgumentException("Both original storage witnesses required");
  if(sourceStorage!=null&&(!sourceStorage.equals(source)||!targetStorage.equals(target)))throw new IllegalStateException("Cannot replace original storage witnesses");
  return new FreightHeldPhaseCheckpoint(phase,universeTick,coasts,sourcePose,targetPose,source,target,pumpFlowSamples);
 }
 public static String bind(String nativeState,long tick,OrbitalDistinctCoastState coasts){
  if(nativeState==null||!nativeState.matches("[0-9a-f]{64}")||tick<0||coasts==null)throw new IllegalArgumentException("Complete held native baseline required");
  return FreightHeldPhaseRecord.hash("IC_HELD_PHASE_COAST_V1\n"+nativeState+"\n"+tick+"\n"+coasts);
 }
 public void verifyCoast(long now,OrbitalDistinctCoastState current){
  if(now<universeTick||now-universeTick>600)throw new IllegalStateException("Held-phase coast checkpoint outside30second window");
  coasts.verify(current.sourcePosition(),current.sourceVelocity(),current.targetPosition(),current.targetVelocity(),current.mu(),(now-universeTick)*.05);
 }
 public String encode(){try{
  var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeInt(pumpFlowSamples?4:sourceStorage!=null?3:sourcePose==null?1:2);out.writeUTF(phase.encode());out.writeLong(universeTick);coasts.write(out);if(sourcePose!=null){sourcePose.write(out);targetPose.write(out);}if(sourceStorage!=null){out.writeUTF(sourceStorage);out.writeUTF(targetStorage);}out.flush();
  return PREFIX+Base64.getUrlEncoder().withoutPadding().encodeToString(bytes.toByteArray());
 }catch(IOException impossible){throw new AssertionError(impossible);}}
 public static FreightHeldPhaseCheckpoint decode(String text){
  if(text==null||text.length()>4096||!text.startsWith(PREFIX))throw new IllegalArgumentException("Bounded held coast checkpoint required");
  try{var in=new DataInputStream(new ByteArrayInputStream(Base64.getUrlDecoder().decode(text.substring(PREFIX.length()))));
   int version=in.readInt();if(version<1||version>4)throw new IllegalArgumentException("Unknown held coast version");
   var phase=FreightHeldPhaseRecord.decode(in.readUTF());long tick=in.readLong();var coasts=OrbitalDistinctCoastState.read(in);
   var checkpoint=new FreightHeldPhaseCheckpoint(phase,tick,coasts,version>=2?FreightHeldPose.read(in):null,version>=2?FreightHeldPose.read(in):null,version>=3?in.readUTF():null,version>=3?in.readUTF():null,version==4);
   if(in.available()!=0||!checkpoint.encode().equals(text))throw new IllegalArgumentException("Noncanonical held coast checkpoint");return checkpoint;
  }catch(IOException|IllegalArgumentException failure){throw new IllegalArgumentException("Invalid held coast checkpoint",failure);}
 }
}
