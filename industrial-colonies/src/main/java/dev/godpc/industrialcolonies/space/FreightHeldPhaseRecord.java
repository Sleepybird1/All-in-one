package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Separate deliberately-held checkpoint, not a reinterpretation of an encounter.
 * Native callers must fingerprint complete current bodies, cargo, dock, pose,
 * authority and disarmed controls. An opaque digest alone proves none of these.
 * Unknown active-crash state cannot be blessed by creating a fresh checkpoint. */
public record FreightHeldPhaseRecord(UUID journey,long revision,Phase phase,UUID body,UUID target,
 String planDigest,String receiptDigest,String nativeStateDigest) {
 private static final String PREFIX="ic-held-phase-v1:";
 public FreightHeldPhaseRecord {
  Objects.requireNonNull(journey);Objects.requireNonNull(body);Objects.requireNonNull(target);
  if(revision<0||body.equals(target)||(phase!=Phase.APPROACH&&phase!=Phase.UNLOAD))throw new IllegalArgumentException("Distinct held approach/unload pair required");
  for(String d:new String[]{planDigest,receiptDigest,nativeStateDigest})if(d==null||!d.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Exact checkpoint digests required");
 }
 static FreightHeldPhaseRecord capture(Entry entry,UUID target,String nativeState){
  var ref=FreightDestinationReference.decode(entry.plan().destinationRoute());ref.requirePlan(entry.plan());
  if(!ref.body().equals(target)||entry.encounterReceipt().isEmpty()||!entry.encounterIntent().isEmpty())throw new IllegalStateException("Acknowledged exact commissioned destination required");
  return new FreightHeldPhaseRecord(entry.plan().journey(),entry.revision(),entry.phase(),entry.body(),target,hash(entry.plan().toString()),hash(entry.encounterReceipt()),nativeState);
 }
 void verify(Entry entry,UUID observedBody,UUID observedTarget,String nativeState){
  if(entry.revision()!=revision)throw new IllegalStateException("Held checkpoint revision "+revision+" differs from journal "+entry.revision());
  if(!body.equals(observedBody)||!target.equals(observedTarget)||!equals(capture(entry,observedTarget,nativeState)))throw new IllegalStateException("Held checkpoint differs from current journey or native state");
 }
 /** A single durable resume can precede an unflushed native rollback. Admit
  * only that exact UNLOAD successor, with the full original native state. */
 void verifyUnflushedResume(Entry entry,UUID observedBody,UUID observedTarget,String nativeState){
  if(phase!=Phase.UNLOAD||entry.phase()!=Phase.UNLOAD||!entry.holdReason().isEmpty()||revision==Long.MAX_VALUE||entry.revision()!=revision+1)throw new IllegalStateException("Exact single UNLOAD resume successor required");
  new FreightHeldPhaseRecord(journey,revision+1,phase,body,target,planDigest,receiptDigest,nativeStateDigest).verify(entry,observedBody,observedTarget,nativeState);
 }
 public String encode(){
  try{var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeInt(1);out.writeLong(revision);
   for(String s:List.of(journey.toString(),phase.name(),body.toString(),target.toString(),planDigest,receiptDigest,nativeStateDigest))out.writeUTF(s);
   out.flush();byte[] payload=bytes.toByteArray();bytes.write(digest(payload));return PREFIX+Base64.getUrlEncoder().withoutPadding().encodeToString(bytes.toByteArray());
  }catch(IOException impossible){throw new AssertionError(impossible);}
 }
 public static FreightHeldPhaseRecord decode(String text){
  if(text==null||text.length()>2048||!text.startsWith(PREFIX))throw new IllegalArgumentException("Bounded held checkpoint required");
  try{byte[] raw=Base64.getUrlDecoder().decode(text.substring(PREFIX.length()));if(raw.length<44)throw new IllegalArgumentException("Truncated held checkpoint");
   byte[] payload=Arrays.copyOf(raw,raw.length-32);if(!MessageDigest.isEqual(digest(payload),Arrays.copyOfRange(raw,raw.length-32,raw.length)))throw new IllegalArgumentException("Held checkpoint checksum");
   var in=new DataInputStream(new ByteArrayInputStream(payload));if(in.readInt()!=1)throw new IllegalArgumentException("Unknown held checkpoint version");long revision=in.readLong();
   var result=new FreightHeldPhaseRecord(UUID.fromString(in.readUTF()),revision,Phase.valueOf(in.readUTF()),UUID.fromString(in.readUTF()),UUID.fromString(in.readUTF()),in.readUTF(),in.readUTF(),in.readUTF());
   if(in.available()!=0||!result.encode().equals(text))throw new IllegalArgumentException("Noncanonical held checkpoint");return result;
  }catch(IOException|IllegalArgumentException failure){throw new IllegalArgumentException("Invalid held checkpoint",failure);}
 }
 static String hash(String text){return HexFormat.of().formatHex(digest(text.getBytes(StandardCharsets.UTF_8)));}
 private static byte[] digest(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
