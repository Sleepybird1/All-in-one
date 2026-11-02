package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.util.*;

/** Separate stationary numerical-coast receipt. This records a past check;
 * it never authorizes movement or substitutes for fresh live admission.
 * Recovery may audit a held physical outcome after the proof window expires. */
public record OrbitalCoastRecoveryRecord(OrbitalEncounterRecoveryRecord baseline,
 long preparedUniverseTick,double positionBound,double velocityBound,String destinationDigest) {
 public static final String PREFIX="IC_ORBITAL_ENCOUNTER_V1\nCOAST_AGREEMENT_RECOVERY_V1\n";
 public OrbitalCoastRecoveryRecord {
  Objects.requireNonNull(baseline);
  if(preparedUniverseTick<0||!Double.isFinite(positionBound)||positionBound<=0||positionBound>.0005
    ||!Double.isFinite(velocityBound)||velocityBound<=0||velocityBound>1e-6
    ||destinationDigest==null||!destinationDigest.matches("[0-9a-f]{64}"))
   throw new IllegalArgumentException("Invalid stationary coast receipt");
 }
 public String encode(){
  try{var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434331);out.writeUTF(baseline.encode());out.writeLong(preparedUniverseTick);
   out.writeDouble(positionBound);out.writeDouble(velocityBound);out.writeUTF(destinationDigest);
  }return PREFIX+Base64.getEncoder().encodeToString(bytes.toByteArray());}
  catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static OrbitalCoastRecoveryRecord decode(String text)throws IOException{
  if(text==null||text.length()>16384||!text.startsWith(PREFIX))throw new IOException("Unsupported coast receipt");
  try(var in=new DataInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(text.substring(PREFIX.length()))))){
   if(in.readInt()!=0x49434331)throw new IOException("Unknown coast receipt schema");
   var result=new OrbitalCoastRecoveryRecord(OrbitalEncounterRecoveryRecord.decode(in.readUTF()),in.readLong(),in.readDouble(),in.readDouble(),in.readUTF());
   if(in.available()!=0||!result.encode().equals(text))throw new IOException("Trailing or noncanonical coast receipt");
   return result;
  }catch(IllegalArgumentException|NullPointerException invalid){throw new IOException("Malformed coast receipt",invalid);}
 }
}
