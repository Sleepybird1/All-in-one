package dev.godpc.industrialcolonies.space.enemy;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Staged durable intent/receipt log, not physical destruction authority.
 * Native observers must prove every candidate's original identity and actual
 * destruction. Reopening is read-only/held even for committed receipts. No
 * replay, reward, resume, or OS/power-loss guarantee is provided here. */
public final class EnemyBossDestructionJournal implements AutoCloseable {
 public enum Kind { DESTROY, RELOCATE }
 public record Entry(long revision, UUID mutation, Set<String> candidates, String before,
                     String after, String evidence, Kind kind) {
  public Entry(long revision,UUID mutation,Set<String> candidates,String before,String after,String evidence){
   this(revision,mutation,candidates,before,after,evidence,Kind.DESTROY);
  }
  public Entry {
   Objects.requireNonNull(mutation);Objects.requireNonNull(kind);candidates=Set.copyOf(candidates);
   if(revision<1||candidates.isEmpty()||candidates.size()>128
       ||candidates.stream().anyMatch(s->s.isBlank()||s.length()>128||s.chars().anyMatch(Character::isISOControl))
       ||!digest(before)||after==null||evidence==null||after.isEmpty()!=evidence.isEmpty()
       ||!after.isEmpty()&&(!digest(after)||!digest(evidence)||before.equals(after)))
    throw new IllegalArgumentException("Invalid destruction record");
  }
  public boolean committed(){return !after.isEmpty();}
 }
 public record Permit(UUID epoch, UUID mutation, long revision) {}
 private static final int LEGACY_MAGIC=0x42444a31, MAGIC=0x42444a32, MAX=262144;
 private int format=MAGIC;
 private final UUID encounter, authority, epoch=UUID.randomUUID();
 private final Path file,pending;
 private final FileChannel lockChannel;
 private final FileLock lock;
 private final List<Entry> entries=new ArrayList<>();
 private byte[] durable;
 private boolean held,closed;

 public EnemyBossDestructionJournal(Path directory,UUID encounter,UUID authority)throws IOException {
  this.encounter=Objects.requireNonNull(encounter);this.authority=Objects.requireNonNull(authority);
  var dir=directory.toAbsolutePath().normalize();Files.createDirectories(dir);
  if(Files.isSymbolicLink(dir))throw new IOException("Linked directory refused");
  file=dir.resolve("destruction.dat");pending=dir.resolve("destruction.pending");var lockPath=dir.resolve("writer.lock");
  if(Files.isSymbolicLink(lockPath))throw new IOException("Linked lock refused");
  lockChannel=FileChannel.open(lockPath,StandardOpenOption.CREATE,StandardOpenOption.WRITE);
  FileLock acquired=null;
  try {
   try{acquired=lockChannel.tryLock();}catch(OverlappingFileLockException e){throw new IOException("Writer already owned",e);}
   if(acquired==null)throw new IOException("Writer already owned");
   if(Files.exists(pending,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unresolved pending write retained");
   if(Files.exists(file,LinkOption.NOFOLLOW_LINKS)){durable=read(file);decode(durable);held=true;}
  }catch(Throwable failure){if(acquired!=null)acquired.release();lockChannel.close();throw failure;}
  lock=acquired;
 }
 public synchronized Permit begin(Set<String> candidates,String before)throws IOException {
  return begin(Kind.DESTROY,candidates,before);
 }
 /** Records movement intent, never a destruction claim. Native observation
  * must commit the exact surviving constituent transition separately. */
 public synchronized Permit beginRelocation(Set<String> candidates,String before)throws IOException {
  return begin(Kind.RELOCATE,candidates,before);
 }
 private Permit begin(Kind kind,Set<String> candidates,String before)throws IOException {
  writable();
  if(entries.size()>=128)throw new IllegalStateException("Mutation budget exhausted");
  if(!entries.isEmpty()){
   var last=entries.getLast();
   if(!last.committed())throw new IllegalStateException("Unresolved destruction intent");
   if(!last.after().equals(before))throw new IllegalArgumentException("Changed source custody");
   var prior=new HashSet<String>();for(var e:entries)if(e.kind()==Kind.DESTROY)prior.addAll(e.candidates());
   if(candidates.stream().anyMatch(prior::contains))throw new IllegalArgumentException("Constituent destruction already recorded");
  }
  var next=new Entry(entries.size()+1L,UUID.randomUUID(),candidates,before,"","",kind);
  var proposed=new ArrayList<>(entries);proposed.add(next);persist(proposed);entries.add(next);
  return new Permit(epoch,next.mutation(),next.revision());
 }
 public synchronized Entry commit(Permit token,String after,String evidence)throws IOException {
  writable();
  if(token==null||!epoch.equals(token.epoch())||entries.isEmpty())throw new IllegalStateException("Foreign permit");
  var old=entries.getLast();
  if(old.committed()||old.revision()!=token.revision()||!old.mutation().equals(token.mutation()))throw new IllegalStateException("Stale permit");
  var next=new Entry(old.revision(),old.mutation(),old.candidates(),old.before(),after,evidence,old.kind());
  if(!next.committed())throw new IllegalArgumentException("Complete native evidence required");
  var proposed=new ArrayList<>(entries);proposed.set(proposed.size()-1,next);persist(proposed);entries.set(entries.size()-1,next);return next;
 }
 public synchronized List<Entry> inspectHeld(){return List.copyOf(entries);}
 public boolean belongsTo(UUID encounter,UUID authority){return this.encounter.equals(encounter)&&this.authority.equals(authority);}
 /** Fresh immutable disk observation only. This does not certify physical defeat.
  * Call again at each admission boundary; a returned snapshot is not a permit. */
 public record CommittedObservation(UUID encounter, UUID authority, List<Entry> entries,
                                    String chainDigest) {
  public CommittedObservation { entries=List.copyOf(entries); }
 }
 public synchronized CommittedObservation observeCommitted()throws IOException {
  try {
   if(closed||!lock.isValid()||durable==null||entries.isEmpty())
    throw new IOException("No owned durable destruction chain");
   if(Files.exists(pending,LinkOption.NOFOLLOW_LINKS))
    throw new IOException("Pending destruction write");
   if(entries.stream().anyMatch(e->!e.committed()))
    throw new IOException("Unresolved destruction intent");
   if(!Arrays.equals(read(file),durable)||!Arrays.equals(encode(entries),durable))
    throw new IOException("Changed destruction evidence");
   // A concurrent external write must not be hidden by a cached in-memory view.
   if(Files.exists(pending,LinkOption.NOFOLLOW_LINKS)||!Arrays.equals(read(file),durable))
    throw new IOException("Destruction evidence changed during observation");
   var digest=MessageDigest.getInstance("SHA-256");
   digest.update("IC_DESTRUCTION_COMMITTED_V1".getBytes(java.nio.charset.StandardCharsets.UTF_8));
   digest.update(durable);
   return new CommittedObservation(encounter,authority,entries,HexFormat.of().formatHex(digest.digest()));
  }catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
   catch(IOException failure){held=true;throw failure;}
 }
 public synchronized boolean held(){return held||closed;}
 public synchronized void hold(){held=true;}
 private void writable(){if(held||closed)throw new IllegalStateException("Destruction journal held");}
 private void persist(List<Entry> proposed)throws IOException {
  try {
   if(durable==null){if(Files.exists(file,LinkOption.NOFOLLOW_LINKS))throw new IOException("Unexpected existing record");}
   else if(!Arrays.equals(read(file),durable))throw new IOException("External journal change");
   byte[] next=encode(proposed);
   try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
    var buffer=ByteBuffer.wrap(next);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
   }
   Files.move(pending,file,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);durable=next;
  }catch(IOException failure){held=true;throw failure;}
 }
 private byte[] encode(List<Entry> records)throws IOException {
  var body=new ByteArrayOutputStream();
  try(var out=new DataOutputStream(body)){
   uuid(out,encounter);uuid(out,authority);out.writeInt(records.size());
   for(var e:records){out.writeLong(e.revision());uuid(out,e.mutation());
    if(format==MAGIC)out.writeByte(e.kind().ordinal());
    out.writeInt(e.candidates().size());
    for(var p:new TreeSet<>(e.candidates()))out.writeUTF(p);
    out.writeUTF(e.before());out.writeUTF(e.after());out.writeUTF(e.evidence());}
  }
  var bytes=body.toByteArray();var framed=new ByteArrayOutputStream();
  try(var out=new DataOutputStream(framed)){out.writeInt(format);out.writeInt(bytes.length);out.write(bytes);out.write(hash(bytes));}
  if(framed.size()>MAX)throw new IOException("Journal size budget");return framed.toByteArray();
 }
 private void decode(byte[] raw)throws IOException {
  try(var in=new DataInputStream(new ByteArrayInputStream(raw))){
   format=in.readInt();if(format!=MAGIC&&format!=LEGACY_MAGIC)throw new IOException("Unknown journal format");int length=in.readInt();
   if(length<36||length!=raw.length-40)throw new IOException("Invalid framing");
   byte[] payload=in.readNBytes(length),checksum=in.readNBytes(32);
   if(!MessageDigest.isEqual(hash(payload),checksum)||in.read()!=-1)throw new IOException("Changed journal checksum");
   try(var data=new DataInputStream(new ByteArrayInputStream(payload))){
    if(!encounter.equals(uuid(data))||!authority.equals(uuid(data)))throw new IOException("Foreign journal authority");
    int count=data.readInt();if(count<1||count>128)throw new IOException("Invalid record count");
    var mutations=new HashSet<UUID>();var destroyed=new HashSet<String>();Entry last=null;
    for(int i=0;i<count;i++){
     long rev=data.readLong();UUID mutation=uuid(data);
     int kindId=format==MAGIC?data.readUnsignedByte():0;
     if(kindId>=Kind.values().length)throw new IOException("Unknown mutation kind");
     Kind kind=Kind.values()[kindId];int n=data.readInt();
     if(n<1||n>128)throw new IOException("Invalid part count");var candidates=new HashSet<String>();
     for(int j=0;j<n;j++)if(!candidates.add(data.readUTF()))throw new IOException("Duplicate part");
     var e=new Entry(rev,mutation,candidates,data.readUTF(),data.readUTF(),data.readUTF(),kind);
     if(rev!=i+1L||!mutations.add(mutation)||last!=null&&(!last.committed()||!last.after().equals(e.before()))
        ||candidates.stream().anyMatch(destroyed::contains))throw new IOException("Broken destruction chain");
     if(kind==Kind.DESTROY)destroyed.addAll(candidates);entries.add(e);last=e;
    }
    if(data.read()!=-1)throw new IOException("Trailing payload");
   }
  }catch(IllegalArgumentException invalid){throw new IOException("Invalid destruction record",invalid);}
 }
 private static byte[] read(Path p)throws IOException {
  if(Files.isSymbolicLink(p))throw new IOException("Linked record refused");long size=Files.size(p);
  if(size<76||size>MAX)throw new IOException("Invalid bounded record");var bytes=Files.readAllBytes(p);
  if(bytes.length!=size)throw new IOException("Record changed during read");return bytes;
 }
 private static boolean digest(String s){return s!=null&&s.matches("[0-9a-f]{64}");}
 private static byte[] hash(byte[] b){try{return MessageDigest.getInstance("SHA-256").digest(b);}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
 private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
 public synchronized void close()throws IOException{if(closed)return;closed=true;held=true;try{lock.release();}finally{lockChannel.close();}}
}
