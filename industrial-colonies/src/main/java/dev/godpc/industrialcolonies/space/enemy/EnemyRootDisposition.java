package dev.godpc.industrialcolonies.space.enemy;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Capture and reward APIs MUST share the same trusted world directory.
 * First original-root disposition wins; never remove it after a failed second
 * write. No live ownership, defeat, delivery or world-save atomicity implied. */
public final class EnemyRootDisposition {
 public enum Kind { CAPTURE, REWARD }
 public record Held(UUID root,UUID encounter,UUID beneficiary,Kind kind){
  public Held{Objects.requireNonNull(root);Objects.requireNonNull(encounter);Objects.requireNonNull(beneficiary);Objects.requireNonNull(kind);}
 }
 private EnemyRootDisposition(){}
 private static Path file(Path directory,UUID root)throws IOException{
  var dir=directory.toAbsolutePath().normalize();
  if(!Files.isDirectory(dir,LinkOption.NOFOLLOW_LINKS)||Files.isSymbolicLink(dir))throw new IOException("Trusted common world disposition directory required");
  return dir.resolve(root+".disposition");
 }
 static void reserve(Path directory,Held value)throws IOException{
  var path=file(directory,value.root());
  // Legacy records have no disposition, but are never evidence of availability.
  var capture=directory.resolve(value.root()+".capture-intent");
  if(!Files.notExists(capture,LinkOption.NOFOLLOW_LINKS))throw new FileAlreadyExistsException(capture.toString());
  try(var stream=Files.newDirectoryStream(directory,"*.claim")){
   int scanned=0;for(var claim:stream){
    if(++scanned>512)throw new IOException("Legacy reward census exceeded");
    UUID encounter;try{var name=claim.getFileName().toString();encounter=UUID.fromString(name.substring(0,name.length()-6));}
    catch(IllegalArgumentException failure){throw new IOException("Unknown legacy reward record",failure);}
    if(EnemyRewardReservation.inspectHeld(directory,encounter).root().equals(value.root()))throw new FileAlreadyExistsException(claim.toString());
   }
  }
  byte[] bytes=encode(value);
  try(var channel=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
   var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
  }
  require(directory,value);
 }
 public static void require(Path directory,Held expected)throws IOException{
  if(!expected.equals(inspectHeld(directory,expected.root())))throw new IOException("Original ship disposition changed");
 }
 public static Held inspectHeld(Path directory,UUID root)throws IOException{
  byte[] bytes;
  try(var channel=FileChannel.open(file(directory,root),StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS)){
   if(channel.size()!=85)throw new IOException("Incomplete/unknown root disposition");
   var buffer=ByteBuffer.allocate(85);while(buffer.hasRemaining())if(channel.read(buffer)<0)throw new EOFException();
   if(channel.size()!=85)throw new IOException("Root disposition changed");bytes=buffer.array();
  }
  var payload=Arrays.copyOf(bytes,53);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,53,85)))throw new IOException("Root disposition checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=0x49434431)throw new IOException("Unknown root disposition");
   var recordedRoot=uuid(in);var encounter=uuid(in);var beneficiary=uuid(in);int kind=in.readUnsignedByte();
   if(!recordedRoot.equals(root)||kind>=Kind.values().length||in.available()!=0)throw new IOException("Foreign root disposition");
   return new Held(recordedRoot,encounter,beneficiary,Kind.values()[kind]);
  }
 }
 private static byte[] encode(Held value)throws IOException{
  var bytes=new ByteArrayOutputStream();try(var out=new DataOutputStream(bytes)){
   out.writeInt(0x49434431);for(var id:List.of(value.root(),value.encounter(),value.beneficiary())){out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}out.writeByte(value.kind().ordinal());
  }
  bytes.write(hash(bytes.toByteArray()));return bytes.toByteArray();
 }
 private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException ex){throw new AssertionError(ex);}}
}
