package dev.godpc.industrialcolonies.geology;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.function.Supplier;

/** One checksummed committed fit per cap. Chunk order/restart cannot choose a new body.
 * Unresolved/corrupt records are retained and refused, never regenerated. */
public final class CinnabarCapStore {
 public record Request(long key,int tileX,int tileZ,int reserve){}
 private final Path root;private final byte[] identity;
 public CinnabarCapStore(Path root,String identity)throws IOException{
  this.root=root;this.identity=hash(identity.getBytes(java.nio.charset.StandardCharsets.UTF_8));
  Files.createDirectories(root);Path owner=root.resolve("identity.bin");
  if(Files.exists(owner,LinkOption.NOFOLLOW_LINKS)){if(!Files.isRegularFile(owner,LinkOption.NOFOLLOW_LINKS)||!Arrays.equals(Files.readAllBytes(owner),this.identity))throw new IOException("Cap policy identity changed");}
  else {try(var out=Files.newOutputStream(owner,StandardOpenOption.CREATE_NEW)){out.write(this.identity);}}
 }
 public synchronized List<SummitCinnabarCap.Cell> select(Request request,Supplier<List<SummitCinnabarCap.Cell>> fit)throws IOException{
  String name="cap_"+request.tileX()+"_"+request.tileZ();Path target=root.resolve(name+".bin"),marker=root.resolve(name+".started"),pending=root.resolve(name+".pending");
  if(Files.exists(pending,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unresolved cap write retained");
  if(Files.exists(target,LinkOption.NOFOLLOW_LINKS)){
   if(!Files.isRegularFile(target,LinkOption.NOFOLLOW_LINKS)||!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)||Files.size(marker)!=0)throw new IOException("Invalid cap authority");
   if(Files.size(target)>800000)throw new IOException("Cap record bounds");return decode(Files.readAllBytes(target),request);
  }
  if(Files.exists(marker,LinkOption.NOFOLLOW_LINKS))throw new IOException("Missing committed cap retained");
  var cells=List.copyOf(fit.get());byte[] bytes=encode(cells,request);
  Files.createFile(marker);
  try(var out=new FileOutputStream(pending.toFile())){out.write(bytes);out.flush();out.getFD().sync();}
  Files.move(pending,target,StandardCopyOption.ATOMIC_MOVE);
  return decode(Files.readAllBytes(target),request);
 }
 public synchronized Optional<List<SummitCinnabarCap.Cell>> existing(Request r)throws IOException{
  String name="cap_"+r.tileX()+"_"+r.tileZ();Path file=root.resolve(name+".bin"),marker=root.resolve(name+".started");
  if(Files.exists(root.resolve(name+".pending"),LinkOption.NOFOLLOW_LINKS))throw new IOException("Unresolved cap write retained");
  if(!Files.exists(file,LinkOption.NOFOLLOW_LINKS)){if(Files.exists(marker,LinkOption.NOFOLLOW_LINKS))throw new IOException("Missing committed cap retained");return Optional.empty();}
  if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)>800000||!Files.isRegularFile(marker,LinkOption.NOFOLLOW_LINKS)||Files.size(marker)!=0)throw new IOException("Invalid cap authority");
  return Optional.of(decode(Files.readAllBytes(file),r));
 }
 private byte[] encode(List<SummitCinnabarCap.Cell> cells,Request r)throws IOException{
  validate(cells,r);var buffer=new ByteArrayOutputStream();var out=new DataOutputStream(buffer);
  out.writeInt(0x49434333);out.write(identity);out.writeLong(r.key());out.writeInt(r.tileX());out.writeInt(r.tileZ());out.writeInt(r.reserve());out.writeInt(cells.size());
  for(var c:cells){out.writeInt(c.x());out.writeInt(c.y());out.writeInt(c.z());out.writeInt(c.surfaceY());}out.flush();out.write(hash(buffer.toByteArray()));return buffer.toByteArray();
 }
 private List<SummitCinnabarCap.Cell> decode(byte[] bytes,Request r)throws IOException{
  if(bytes.length<92||bytes.length>800000)throw new IOException("Cap record bounds");
  byte[] body=Arrays.copyOf(bytes,bytes.length-32);if(!MessageDigest.isEqual(hash(body),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Cap checksum");
  var in=new DataInputStream(new ByteArrayInputStream(body));
  if(in.readInt()!=0x49434333||!Arrays.equals(in.readNBytes(32),identity)||in.readLong()!=r.key()||in.readInt()!=r.tileX()||in.readInt()!=r.tileZ()||in.readInt()!=r.reserve())throw new IOException("Cap request changed");
  int count=in.readInt();if(count<0||count>15000||count!=0&&count!=r.reserve())throw new IOException("Cap count");
  var cells=new ArrayList<SummitCinnabarCap.Cell>();for(int i=0;i<count;i++)cells.add(new SummitCinnabarCap.Cell(in.readInt(),in.readInt(),in.readInt(),in.readInt()));
  if(in.available()!=0)throw new IOException("Trailing cap bytes");validate(cells,r);return List.copyOf(cells);
 }
 private static void validate(List<SummitCinnabarCap.Cell> cells,Request r)throws IOException{
  if(r.reserve()!=1000&&r.reserve()!=5000&&r.reserve()!=15000||cells.size()!=0&&cells.size()!=r.reserve()||new HashSet<>(cells).size()!=cells.size())throw new IOException("Invalid cap reserve");
  for(var c:cells)if(Math.floorDiv(c.x(),32)*2!=r.tileX()||Math.floorDiv(c.z(),32)*2!=r.tileZ()||c.y()<200||c.y()>300||c.surfaceY()<c.y()||c.surfaceY()-c.y()>=24)throw new IOException("Cap cell outside fitted tile/band");
 }
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
