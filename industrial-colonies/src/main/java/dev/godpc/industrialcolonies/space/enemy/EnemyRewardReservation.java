package dev.godpc.industrialcolonies.space.enemy;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** One immutable reservation per encounter in a world-scoped trusted directory.
 * Existing records are held, never replayed, overwritten or interpreted as
 * delivered rewards. Partial failed writes deliberately block retries. This is
 * not atomic with world saves or inventory delivery and grants no items. */
public final class EnemyRewardReservation {
 public record HeldClaim(UUID encounter,UUID root,UUID beneficiary,long revision,String defeatDigest,String rewardPlanDigest){}
 public record HeldAcknowledgement(HeldClaim claim,String inventoryEvidenceDigest){}
 private static final int MAGIC=0x49435231,MAX=1024;
 private EnemyRewardReservation(){}
 private static Path path(Path directory,UUID encounter)throws IOException{
  Objects.requireNonNull(encounter);var dir=directory.toAbsolutePath().normalize();
  if(!Files.isDirectory(dir,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(dir))throw new IOException("Existing trusted world claim directory required");
  return dir.resolve(encounter+".claim");
 }
 public static HeldClaim reserve(Path directory,EnemyRewardAdmission.Evidence evidence,String rewardPlanDigest)throws IOException{
  if(EnemyRewardAdmission.assess(evidence)!=EnemyRewardAdmission.Decision.ALLOW_RESERVATION||!digest(rewardPlanDigest))
   throw new IOException("Reward reservation not admitted");
  var claim=new HeldClaim(evidence.encounter(),evidence.root(),evidence.beneficiary(),evidence.revision(),evidence.verifiedDestructionDigest(),rewardPlanDigest);
  var file=path(directory,claim.encounter());var bytes=encode(claim);
  if(!Files.notExists(file,LinkOption.NOFOLLOW_LINKS))throw new FileAlreadyExistsException(file.toString());
  EnemyRootDisposition.reserve(directory,new EnemyRootDisposition.Held(claim.root(),claim.encounter(),claim.beneficiary(),EnemyRootDisposition.Kind.REWARD));
  // CREATE_NEW arbitrates racing JVMs and different beneficiaries. Never remove
  // an existing file here, even if its contents are unreadable or incomplete.
  try(var channel=FileChannel.open(file,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
  }
  if(!claim.equals(inspectHeld(directory,claim.encounter())))throw new IOException("Reservation readback changed");
  return claim;
 }
 public static HeldClaim inspectHeld(Path directory,UUID encounter)throws IOException{
  var file=path(directory,encounter);
  if(Files.isSymbolicLink(file))throw new IOException("Linked reservation refused");
  byte[] bytes;
  try(var channel=FileChannel.open(file,StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
   long length=channel.size();if(length<32||length>MAX)throw new IOException("Invalid reservation length");
   var buffer=ByteBuffer.allocate((int)length);while(buffer.hasRemaining())if(channel.read(buffer)<0)throw new EOFException("Truncated claim");
   if(channel.size()!=length)throw new IOException("Claim changed while reading");bytes=buffer.array();
  }
  var payload=Arrays.copyOf(bytes,bytes.length-32);var checksum=Arrays.copyOfRange(bytes,bytes.length-32,bytes.length);
  if(!MessageDigest.isEqual(hash(payload),checksum))throw new IOException("Reservation checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=MAGIC)throw new IOException("Unknown claim format");
   var claim=new HeldClaim(uuid(in),uuid(in),uuid(in),in.readLong(),in.readUTF(),in.readUTF());
   if(in.available()!=0||!claim.encounter().equals(encounter)||claim.revision()<1||!digest(claim.defeatDigest())||!digest(claim.rewardPlanDigest()))
    throw new IOException("Invalid or foreign claim");
   return claim;
  }
 }
 static HeldAcknowledgement acknowledge(Path directory,HeldClaim claim,String evidence)throws IOException{
  if(!digest(evidence)||!claim.equals(inspectHeld(directory,claim.encounter())))throw new IOException("Acknowledgement claim mismatch");
  EnemyRootDisposition.require(directory,new EnemyRootDisposition.Held(claim.root(),claim.encounter(),claim.beneficiary(),EnemyRootDisposition.Kind.REWARD));
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434131);var encoded=encode(claim);out.writeInt(encoded.length);out.write(encoded);out.writeUTF(evidence);
  }
  bytes.write(hash(bytes.toByteArray()));var file=ackPath(directory,claim.encounter());
  try(var channel=FileChannel.open(file,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var buffer=ByteBuffer.wrap(bytes.toByteArray());while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
  }
  var saved=inspectAcknowledgementHeld(directory,claim.encounter());
  if(!saved.equals(new HeldAcknowledgement(claim,evidence)))throw new IOException("Acknowledgement readback changed");
  return saved;
 }
 private static Path ackPath(Path directory,UUID encounter)throws IOException{return path(directory,encounter).resolveSibling(encounter+".ack");}
 /** Presence is not proof that the corresponding Minecraft save retained items.
  * This inspection never returns permission to deliver or automatically repair. */
 public static HeldAcknowledgement inspectAcknowledgementHeld(Path directory,UUID encounter)throws IOException{
  var claim=inspectHeld(directory,encounter);byte[] bytes;
  try(var channel=FileChannel.open(ackPath(directory,encounter),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
   long size=channel.size();if(size<40||size>MAX)throw new IOException("Invalid acknowledgement length");
   var buffer=ByteBuffer.allocate((int)size);while(buffer.hasRemaining())if(channel.read(buffer)<0)throw new EOFException();
   if(channel.size()!=size)throw new IOException("Acknowledgement changed");bytes=buffer.array();
  }
  var payload=Arrays.copyOf(bytes,bytes.length-32);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Acknowledgement checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=0x49434131)throw new IOException("Unknown acknowledgement format");
   int length=in.readInt();var expected=encode(claim);
   if(length!=expected.length||!Arrays.equals(in.readNBytes(length),expected))throw new IOException("Acknowledgement bound to different claim");
   var evidence=in.readUTF();if(!digest(evidence)||in.available()!=0)throw new IOException("Invalid acknowledgement evidence");
   return new HeldAcknowledgement(claim,evidence);
  }
 }
 private static byte[] encode(HeldClaim c)throws IOException{
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(MAGIC);uuid(out,c.encounter());uuid(out,c.root());uuid(out,c.beneficiary());out.writeLong(c.revision());out.writeUTF(c.defeatDigest());out.writeUTF(c.rewardPlanDigest());
  }
  var payload=bytes.toByteArray();bytes.write(hash(payload));return bytes.toByteArray();
 }
 private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
 private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
 private static boolean digest(String s){return s!=null&&s.matches("[0-9a-f]{64}");}
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
