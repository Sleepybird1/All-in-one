package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Durable observation journal. No inventories, world edits, or automatic recovery replay. */
public final class ShipHandoffJournal {
 public enum Phase { PREPARED, ARRIVED, READY, RELEASED, HELD }
 public record Entry(UUID transaction,UUID transponder,UUID owner,UUID sourceBody,
                     String sourceDimension,String destinationDimension,String sourceRoute,
                     String destinationRoute,String custody,Phase phase,String destinationBody,String reason) {
  public Entry {
   Objects.requireNonNull(transaction);Objects.requireNonNull(transponder);Objects.requireNonNull(owner);Objects.requireNonNull(sourceBody);Objects.requireNonNull(phase);
   for(String s:List.of(sourceDimension,destinationDimension,sourceRoute,destinationRoute,custody,destinationBody,reason))
    if(s.length()>MAX_TEXT)throw new IllegalArgumentException("Journal field too large");
   if(sourceDimension.isBlank()||destinationDimension.isBlank()||sourceDimension.equals(destinationDimension)||sourceRoute.isBlank()||custody.isBlank())throw new IllegalArgumentException("Incomplete handoff identity");
   if(!destinationBody.isEmpty())UUID.fromString(destinationBody);
   if((phase==Phase.ARRIVED||phase==Phase.READY||phase==Phase.RELEASED)&&destinationBody.isEmpty())throw new IllegalArgumentException("Missing destination body");
   if((phase==Phase.READY||phase==Phase.RELEASED)&&destinationRoute.isBlank())throw new IllegalArgumentException("Missing destination leg");
  }
  public Entry advance(Phase phase,String body,String route,String reason){return new Entry(transaction,transponder,owner,sourceBody,sourceDimension,destinationDimension,sourceRoute,route,custody,phase,body,reason);}
 }
 private static final int MAGIC=0x49434831,MAX_TEXT=1_000_000,MAX_FILE=8_000_000;
 private final Path directory;
 private final Map<UUID,Entry> entries=new HashMap<>();
 private final Set<UUID> recovered=new HashSet<>();
 private String fault="";
 public ShipHandoffJournal(Path directory){
  this.directory=directory;
  try{
   Files.createDirectories(directory);
   try(var files=Files.list(directory)){
    for(Path file:files.sorted().toList()){
     if(file.getFileName().toString().endsWith(".pending"))throw new IOException("Interrupted journal write: "+file.getFileName());
     if(!file.getFileName().toString().endsWith(".dat"))continue;
     Entry entry=decode(Files.readAllBytes(bounded(file)));
     if(!file.getFileName().toString().equals(entry.transaction()+".dat")||entries.putIfAbsent(entry.transaction(),entry)!=null)throw new IOException("Journal identity conflict");
     if(entry.phase()!=Phase.RELEASED)recovered.add(entry.transaction());
    }
   }
   var active=new HashSet<UUID>();
   for(Entry entry:entries.values())if(entry.phase()!=Phase.RELEASED&&!active.add(entry.transponder()))throw new IOException("Multiple active handoffs for one transponder");
  }catch(Exception failure){fault=failure.toString();}
 }
 private static Path bounded(Path file)throws IOException{if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)>MAX_FILE)throw new IOException("Invalid journal file");return file;}
 public String fault(){return fault;}
 public Collection<Entry> entries(){return List.copyOf(entries.values());}
 public boolean recoveryRequired(UUID transaction){return recovered.contains(transaction);}
 public boolean blocks(UUID transponder){return !fault.isEmpty()||entries.values().stream().anyMatch(e->e.transponder().equals(transponder)&&e.phase()!=Phase.RELEASED);}
 public Entry get(UUID transaction){return Objects.requireNonNull(entries.get(transaction),"Unknown handoff transaction");}
 public synchronized void prepare(Entry entry)throws IOException{
  requireHealthy();
  if(entry.phase()!=Phase.PREPARED||entries.containsKey(entry.transaction())||blocks(entry.transponder()))throw new IllegalStateException("Handoff already active or invalid initial phase");
  write(entry);
 }
 /** Caller must revalidate actual native state even when resuming after a restart. */
 public synchronized void advance(Entry next,boolean reconciled)throws IOException{
  requireHealthy();Entry old=get(next.transaction());
  if(!old.transponder().equals(next.transponder())||!old.owner().equals(next.owner())||!old.sourceBody().equals(next.sourceBody())||!old.sourceDimension().equals(next.sourceDimension())||!old.destinationDimension().equals(next.destinationDimension())||!old.sourceRoute().equals(next.sourceRoute())||!old.custody().equals(next.custody()))throw new IllegalArgumentException("Immutable handoff identity changed");
  if(old.phase()==Phase.RELEASED)throw new IllegalStateException("Completed handoff cannot replay");
  if(!old.destinationBody().isEmpty()&&!old.destinationBody().equals(next.destinationBody()))throw new IllegalArgumentException("Observed destination body changed");
  if(recovered.contains(old.transaction())&&!reconciled&&next.phase()!=Phase.HELD)throw new IllegalStateException("Restart requires physical reconciliation");
  boolean legal=next.phase()==Phase.HELD||next.phase()==Phase.ARRIVED&&(old.phase()==Phase.PREPARED||old.phase()==Phase.HELD)&&reconciled
   ||next.phase()==Phase.READY&&old.phase()==Phase.ARRIVED&&reconciled
   ||next.phase()==Phase.RELEASED&&old.phase()==Phase.READY&&reconciled;
  if(!legal)throw new IllegalStateException("Illegal handoff phase transition");
  write(next);if(reconciled)recovered.remove(next.transaction());
 }
 private void requireHealthy()throws IOException{if(!fault.isEmpty())throw new IOException("Handoff journal held: "+fault);}
 private void write(Entry entry)throws IOException{
  Path pending=directory.resolve(entry.transaction()+".pending"),target=directory.resolve(entry.transaction()+".dat");
  try{
   byte[] bytes=encode(entry);
   try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
    var buffer=java.nio.ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
   }
   // No non-atomic fallback. A failed replace keeps pending evidence and holds automation.
   Files.move(pending,target,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
   if(!decode(Files.readAllBytes(bounded(target))).equals(entry))throw new IOException("Journal readback mismatch");
   entries.put(entry.transaction(),entry);
  }catch(Exception failure){fault=failure.toString();throw new IOException("Journal write failed; automation held",failure);}
 }
 private static byte[] encode(Entry e)throws IOException{
  var raw=new ByteArrayOutputStream();try(var out=new DataOutputStream(raw)){
   out.writeInt(MAGIC);
   for(String s:List.of(e.transaction().toString(),e.transponder().toString(),e.owner().toString(),e.sourceBody().toString(),e.sourceDimension(),e.destinationDimension(),e.sourceRoute(),e.destinationRoute(),e.custody(),e.phase().name(),e.destinationBody(),e.reason())){
    byte[] b=s.getBytes(java.nio.charset.StandardCharsets.UTF_8);out.writeInt(b.length);out.write(b);
   }
  }
  byte[] payload=raw.toByteArray();raw.write(digest(payload));return raw.toByteArray();
 }
 private static Entry decode(byte[] bytes)throws IOException{
  if(bytes.length<36||bytes.length>MAX_FILE)throw new IOException("Invalid journal length");
  byte[] payload=Arrays.copyOf(bytes,bytes.length-32),checksum=Arrays.copyOfRange(bytes,bytes.length-32,bytes.length);
  if(!MessageDigest.isEqual(checksum,digest(payload)))throw new IOException("Journal checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   if(in.readInt()!=MAGIC)throw new IOException("Unsupported journal format");String[] s=new String[12];
   for(int i=0;i<s.length;i++){int n=in.readInt();if(n<0||n>MAX_TEXT*4||n>in.available())throw new IOException("Invalid journal field length");s[i]=new String(in.readNBytes(n),java.nio.charset.StandardCharsets.UTF_8);}
   if(in.available()!=0)throw new IOException("Trailing journal bytes");
   return new Entry(UUID.fromString(s[0]),UUID.fromString(s[1]),UUID.fromString(s[2]),UUID.fromString(s[3]),s[4],s[5],s[6],s[7],s[8],Phase.valueOf(s[9]),s[10],s[11]);
  }catch(RuntimeException error){throw new IOException("Invalid journal record",error);}
 }
 private static byte[] digest(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
