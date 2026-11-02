package dev.godpc.industrialcolonies.space.enemy;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Immutable evidence before an ownership mutation, not authority to mutate.
 * Keyed by original physical root so changing claimant/session cannot retry it.
 * Existing and partial files remain held. No replay, deletion or world-save
 * atomicity is provided; a new process must audit actual native ownership. */
public final class EnemyCaptureTransferIntent {
 public record Held(UUID session,UUID encounter,UUID root,UUID target,UUID claimant,UUID transponder,
     long revision,String dimension,int x,int y,int z,String sourceProof,String targetProof,String comparableCustody) {
  public Held {
   for(var id:Arrays.asList(session,encounter,root,target,claimant,transponder))Objects.requireNonNull(id);
   if(root.equals(target)||revision<1||dimension==null||dimension.length()>256
       ||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_/.-]+")||!digest(sourceProof)||!digest(targetProof)||!digest(comparableCustody))
    throw new IllegalArgumentException("Invalid capture intent");
  }
 }
 private static final int MAGIC=0x49434331,MAX=2048;
 public record Applied(Held intent,String sourceCustody,String targetCustody,String sourceMetadata,String targetMetadata){
  public Applied {
   Objects.requireNonNull(intent);
   if(!digest(sourceCustody)||!digest(targetCustody)||!digest(sourceMetadata)||!digest(targetMetadata))throw new IllegalArgumentException("Invalid applied capture evidence");
  }
 }
 private EnemyCaptureTransferIntent(){}
 private static Path path(Path directory,UUID root)throws IOException{
  Objects.requireNonNull(root);var dir=directory.toAbsolutePath().normalize();
  if(!Files.isDirectory(dir,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(dir))throw new IOException("Existing trusted world capture directory required");
  return dir.resolve(root+".capture-intent");
 }
 public static Held persist(Path directory,Held intent)throws IOException{
  Objects.requireNonNull(intent);var file=path(directory,intent.root());var bytes=encode(intent);
  EnemyRootDisposition.reserve(directory,new EnemyRootDisposition.Held(intent.root(),intent.encounter(),intent.claimant(),EnemyRootDisposition.Kind.CAPTURE));
  try(var channel=FileChannel.open(file,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
  }
  if(!intent.equals(inspectHeld(directory,intent.root())))throw new IOException("Capture intent readback changed");
  return intent;
 }
 public static Held inspectHeld(Path directory,UUID root)throws IOException{
  byte[] bytes;
  try(var channel=FileChannel.open(path(directory,root),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
   long size=channel.size();if(size<32||size>MAX)throw new IOException("Invalid capture intent length");
   var buffer=ByteBuffer.allocate((int)size);while(buffer.hasRemaining())if(channel.read(buffer)<0)throw new EOFException("Incomplete capture intent");
   if(channel.size()!=size)throw new IOException("Capture intent changed during read");bytes=buffer.array();
  }
  var payload=Arrays.copyOf(bytes,bytes.length-32);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Capture intent checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=MAGIC)throw new IOException("Unknown capture intent format");
   var result=new Held(uuid(in),uuid(in),uuid(in),uuid(in),uuid(in),uuid(in),in.readLong(),in.readUTF(),
       in.readInt(),in.readInt(),in.readInt(),in.readUTF(),in.readUTF(),in.readUTF());
   if(in.available()!=0||!result.root().equals(root))throw new IOException("Foreign/trailing capture intent");
   return result;
  }catch(IllegalArgumentException ex){throw new IOException("Invalid capture intent fields",ex);}
 }
 /** Called only after native owner-only and registry/cargo checks. This receipt
  * does not force the Minecraft save or release the held body. */
 static Applied acknowledge(Path directory,Applied applied)throws IOException{
  if(!applied.intent().equals(inspectHeld(directory,applied.intent().root())))throw new IOException("Capture acknowledgement intent mismatch");
  var intentValue=applied.intent();EnemyRootDisposition.require(directory,new EnemyRootDisposition.Held(intentValue.root(),intentValue.encounter(),intentValue.claimant(),EnemyRootDisposition.Kind.CAPTURE));
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434341);var intent=encode(applied.intent());out.writeInt(intent.length);out.write(intent);
   out.writeUTF(applied.sourceCustody());out.writeUTF(applied.targetCustody());out.writeUTF(applied.sourceMetadata());out.writeUTF(applied.targetMetadata());
  }
  bytes.write(hash(bytes.toByteArray()));if(bytes.size()>MAX)throw new IOException("Capture acknowledgement too large");
  var file=ackPath(directory,applied.intent().root());
  try(var channel=FileChannel.open(file,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var buffer=ByteBuffer.wrap(bytes.toByteArray());while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
  }
  if(!Optional.of(applied).equals(inspectAppliedHeld(directory,applied.intent().root())))throw new IOException("Capture acknowledgement readback changed");
  return applied;
 }
 private static Path ackPath(Path directory,UUID root)throws IOException{return path(directory,root).resolveSibling(root+".capture-applied");}
 /** Stable binding for roster references; includes the complete original intent. */
 public static String appliedDigest(Applied value)throws IOException{
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeUTF("IC_CAPTURE_ROSTER_RECEIPT_V1");out.write(encode(value.intent()));
   out.writeUTF(value.sourceCustody());out.writeUTF(value.targetCustody());out.writeUTF(value.sourceMetadata());out.writeUTF(value.targetMetadata());
  }
  return HexFormat.of().formatHex(hash(bytes.toByteArray()));
 }
 /** Only an absent acknowledgement is pending. Corrupt, linked or inaccessible
  * records refuse; they must never be treated as permission to retry. */
 public static Optional<Applied> inspectAppliedHeld(Path directory,UUID root)throws IOException{
  var intent=inspectHeld(directory,root);byte[] bytes;
  try(var channel=FileChannel.open(ackPath(directory,root),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
   long size=channel.size();if(size<40||size>MAX)throw new IOException("Invalid capture acknowledgement length");
   var buffer=ByteBuffer.allocate((int)size);while(buffer.hasRemaining())if(channel.read(buffer)<0)throw new EOFException();
   if(channel.size()!=size)throw new IOException("Capture acknowledgement changed");bytes=buffer.array();
  }catch(NoSuchFileException absent){return Optional.empty();}
  var payload=Arrays.copyOf(bytes,bytes.length-32);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Capture acknowledgement checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=0x49434341)throw new IOException("Unknown capture acknowledgement format");
   var expected=encode(intent);int length=in.readInt();
   if(length!=expected.length||!Arrays.equals(in.readNBytes(length),expected))throw new IOException("Capture acknowledgement belongs to different intent");
   var result=new Applied(intent,in.readUTF(),in.readUTF(),in.readUTF(),in.readUTF());
   if(in.available()!=0)throw new IOException("Trailing capture acknowledgement");return Optional.of(result);
  }catch(IllegalArgumentException ex){throw new IOException("Invalid capture acknowledgement",ex);}
 }
 private static byte[] encode(Held value)throws IOException{
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(MAGIC);for(var id:List.of(value.session(),value.encounter(),value.root(),value.target(),value.claimant(),value.transponder()))uuid(out,id);
   out.writeLong(value.revision());out.writeUTF(value.dimension());out.writeInt(value.x());out.writeInt(value.y());out.writeInt(value.z());
   out.writeUTF(value.sourceProof());out.writeUTF(value.targetProof());out.writeUTF(value.comparableCustody());
  }
  bytes.write(hash(bytes.toByteArray()));if(bytes.size()>MAX)throw new IOException("Capture intent too large");return bytes.toByteArray();
 }
 private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
 private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
 private static boolean digest(String value){return value!=null&&value.matches("[0-9a-f]{64}");}
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException ex){throw new AssertionError(ex);}}
}
