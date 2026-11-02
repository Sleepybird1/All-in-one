package dev.godpc.industrialcolonies.space.enemy;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Durable bounded encounter metadata, never spawning or actuator authority.
 * Native adapters must independently verify identities and complete custody.
 * Reload is always held; even a successful audit never creates a live permit.
 * Forced file writes/atomic rename are not an OS power-loss guarantee. */
public final class EnemyEncounterJournal implements AutoCloseable {
 public enum Phase { APPROACH,ATTACK,RETREAT,COMPLETE,HELD;
  public boolean terminal(){return this==COMPLETE||this==HELD;}
 }
 public record Plan(UUID session,UUID source,UUID sourceEncounter,UUID sourceRoot,
                    UUID target,UUID targetAuthority,UUID targetRoot,String dimension,
                    int mountX,int mountY,int mountZ) {
  public Plan {
   for(var id:List.of(session,source,sourceEncounter,sourceRoot,target,targetAuthority,targetRoot))Objects.requireNonNull(id);
   if(source.equals(target)||sourceEncounter.equals(targetAuthority)||dimension==null||dimension.length()>256
       ||!dimension.matches("[a-z0-9_.-]+:[a-z0-9_/.-]+"))throw new IllegalArgumentException("Invalid encounter identities/dimension");
  }
 }
 public record Entry(Plan plan,Phase phase,int emissions,long revision,String reason,String sourceProof,String targetProof) {
  public Entry {
   Objects.requireNonNull(plan);Objects.requireNonNull(phase);Objects.requireNonNull(reason);
   if(emissions<0||emissions>1||revision<1||reason.isEmpty()||reason.length()>512||reason.chars().anyMatch(Character::isISOControl))throw new IllegalArgumentException("Invalid finite encounter state");
   if((phase==Phase.APPROACH||phase==Phase.ATTACK)&&emissions!=0||phase==Phase.RETREAT&&emissions!=1||phase==Phase.COMPLETE&&emissions!=1)throw new IllegalArgumentException("Phase/emission conflict");
   if(sourceProof==null||targetProof==null||sourceProof.isEmpty()!=targetProof.isEmpty()
       ||!sourceProof.isEmpty()&&(!phase.terminal()||!digest(sourceProof)||!digest(targetProof)))throw new IllegalArgumentException("Invalid held custody checkpoint");
  }
  public boolean checkpointed(){return !sourceProof.isEmpty();}
 }
 public record Permit(UUID session,UUID epoch,long revision){}
 private static final int MAGIC=0x45434a31,MAX_FILE=8192,MAX_ENTRIES=128;
 private final Path directory;
 private final UUID epoch=UUID.randomUUID();
 private final Map<UUID,Entry> entries=new HashMap<>();
 private final Set<UUID> issued=new HashSet<>(),active=new HashSet<>();
 private FileChannel lockChannel;private FileLock lock;
 private String fault="";private boolean closed;
 public EnemyEncounterJournal(Path directory) {
  this.directory=Objects.requireNonNull(directory).toAbsolutePath().normalize();
  try {
   Files.createDirectories(this.directory);if(Files.isSymbolicLink(this.directory))throw new IOException("Linked journal directory refused");
   var lockPath=this.directory.resolve("writer.lock");if(Files.isSymbolicLink(lockPath))throw new IOException("Linked journal lock refused");
   lockChannel=FileChannel.open(lockPath,StandardOpenOption.CREATE,StandardOpenOption.WRITE);lock=lockChannel.tryLock();if(lock==null)throw new IOException("Journal already owned");
   try(var stream=Files.list(this.directory)) {
    var files=stream.sorted().toList();if(files.size()>512)throw new IOException("Journal directory budget exceeded");
    var sources=new HashSet<UUID>();
    for(var file:files){var name=file.getFileName().toString();if(name.endsWith(".pending"))throw new IOException("Interrupted journal write preserved");if(!name.endsWith(".dat"))continue;
     if(entries.size()>=MAX_ENTRIES)throw new IOException("Encounter record capacity exceeded");var entry=decode(read(file));
     if(!name.equals(entry.plan().session()+".dat")||entries.putIfAbsent(entry.plan().session(),entry)!=null||!sources.add(entry.plan().source()))throw new IOException("Duplicate or renamed encounter authority");
    }
   }
  }catch(Exception failure){fault=failure.toString();}
 }
 public synchronized String fault(){return fault;}
 public synchronized List<Entry> entries(){return entries.values().stream().sorted(Comparator.comparing(e->e.plan().session().toString())).toList();}
 public synchronized Entry get(UUID id){valid();return Objects.requireNonNull(entries.get(id),"Unknown encounter");}
 public synchronized boolean held(UUID id){return closed||!fault.isEmpty()||!active.contains(id);}
 public synchronized boolean current(Permit permit){return !closed&&fault.isEmpty()&&permit!=null&&epoch.equals(permit.epoch())&&active.contains(permit.session())&&entries.get(permit.session())!=null&&entries.get(permit.session()).revision()==permit.revision();}
 public synchronized Permit begin(Plan plan)throws IOException {
  valid();if(entries.size()>=MAX_ENTRIES||entries.containsKey(plan.session())||entries.values().stream().anyMatch(e->e.plan().source().equals(plan.source())))throw new IllegalStateException("Encounter identity/source already recorded or journal full");
  var entry=new Entry(plan,Phase.APPROACH,0,1,"ADMITTED","","");persist(entry,null);entries.put(plan.session(),entry);issued.add(plan.session());active.add(plan.session());return permit(entry);
 }
 public synchronized Permit observe(Permit permit,Phase phase,int emissions,String reason)throws IOException {
  var old=owned(permit);if(!current(permit)||old.phase().terminal())throw new IllegalStateException("Held or stale encounter permit");
  boolean transition=phase==old.phase()||phase==Phase.HELD||old.phase()==Phase.APPROACH&&phase==Phase.ATTACK
      ||old.phase()==Phase.ATTACK&&phase==Phase.RETREAT||old.phase()==Phase.APPROACH&&phase==Phase.RETREAT
      ||old.phase()==Phase.RETREAT&&phase==Phase.COMPLETE;
  if(!transition||emissions<old.emissions()||emissions-old.emissions()>1||emissions>old.emissions()&&phase!=Phase.RETREAT&&phase!=Phase.HELD)throw new IllegalArgumentException("Unsafe phase or emission transition");
  var next=new Entry(old.plan(),phase,emissions,Math.addExact(old.revision(),1),reason,"","");persist(next,old);entries.put(next.plan().session(),next);if(phase.terminal())active.remove(next.plan().session());return permit(next);
 }
 public synchronized Permit checkpointHeld(Permit permit,String sourceProof,String targetProof)throws IOException {
  var old=owned(permit);if(!old.phase().terminal()||old.checkpointed())throw new IllegalStateException("Explicit stopped uncheckpointed encounter required");
  if(!digest(sourceProof)||!digest(targetProof))throw new IllegalArgumentException("Complete native custody digests required");
  var next=new Entry(old.plan(),old.phase(),old.emissions(),Math.addExact(old.revision(),1),old.reason(),sourceProof,targetProof);persist(next,old);entries.put(next.plan().session(),next);return permit(next);
 }
 /** Read-only equality audit. Native recovery/budget reconstruction is separate. */
 public synchronized Entry auditHeld(UUID id,Plan observed,String sourceProof,String targetProof) {
  var entry=get(id);if(!held(id)||!entry.checkpointed()||!entry.plan().equals(observed)||!entry.sourceProof().equals(sourceProof)||!entry.targetProof().equals(targetProof))throw new IllegalStateException("Uncheckpointed or changed native custody; remain held");return entry;
 }
 private Permit permit(Entry entry){return new Permit(entry.plan().session(),epoch,entry.revision());}
 /** A failed driver may invalidate its runtime token without rewriting evidence. */
 public synchronized void abandon(Permit permit){var entry=owned(permit);active.remove(entry.plan().session());}
 private Entry owned(Permit p){valid();if(p==null||!epoch.equals(p.epoch())||!issued.contains(p.session()))throw new IllegalStateException("Foreign or reopened permit");var e=entries.get(p.session());if(e==null||e.revision()!=p.revision())throw new IllegalStateException("Stale encounter revision");return e;}
 private void valid(){if(closed||!fault.isEmpty())throw new IllegalStateException("Journal held: "+fault);}
 private static boolean digest(String s){return s!=null&&s.matches("[0-9a-f]{64}");}
 private Path file(UUID id){return directory.resolve(id+".dat");}
 private void persist(Entry next,Entry old)throws IOException {
  try {
   var target=file(next.plan().session());if(old==null){if(Files.exists(target))throw new IOException("Existing native journal file refused");}
   else if(!Arrays.equals(read(target),encode(old)))throw new IOException("Journal changed outside current writer");
   var pending=directory.resolve(next.plan().session()+".dat.pending");var bytes=encode(next);
   try(var out=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())out.write(buffer);out.force(true);}
   Files.move(pending,target,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
  }catch(IOException failure){fault=failure.toString();active.clear();throw failure;}
 }
 private static byte[] read(Path path)throws IOException {long size=Files.size(path);if(Files.isSymbolicLink(path)||size<40||size>MAX_FILE)throw new IOException("Invalid bounded journal file");var bytes=Files.readAllBytes(path);if(bytes.length!=size)throw new IOException("Journal changed during read");return bytes;}
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
 private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
 private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
 private static byte[] encode(Entry e)throws IOException {
  var payload=new ByteArrayOutputStream();try(var out=new DataOutputStream(payload)){var p=e.plan();for(var id:List.of(p.session(),p.source(),p.sourceEncounter(),p.sourceRoot(),p.target(),p.targetAuthority(),p.targetRoot()))uuid(out,id);out.writeUTF(p.dimension());out.writeInt(p.mountX());out.writeInt(p.mountY());out.writeInt(p.mountZ());out.writeUTF(e.phase().name());out.writeInt(e.emissions());out.writeLong(e.revision());out.writeUTF(e.reason());out.writeUTF(e.sourceProof());out.writeUTF(e.targetProof());}
  var bytes=payload.toByteArray();var framed=new ByteArrayOutputStream();try(var out=new DataOutputStream(framed)){out.writeInt(MAGIC);out.writeInt(bytes.length);out.write(bytes);out.write(hash(bytes));}if(framed.size()>MAX_FILE)throw new IOException("Journal payload exceeded bound");return framed.toByteArray();
 }
 private static Entry decode(byte[] bytes)throws IOException {
  try(var envelope=new DataInputStream(new ByteArrayInputStream(bytes))){if(envelope.readInt()!=MAGIC)throw new IOException("Unknown encounter journal format");int count=envelope.readInt();if(count<1||count>MAX_FILE-40||count!=bytes.length-40)throw new IOException("Incomplete/extra journal framing");var body=envelope.readNBytes(count);var expected=envelope.readNBytes(32);if(!MessageDigest.isEqual(expected,hash(body))||envelope.read()!=-1)throw new IOException("Journal checksum/framing mismatch");
   try(var in=new DataInputStream(new ByteArrayInputStream(body))){var p=new Plan(uuid(in),uuid(in),uuid(in),uuid(in),uuid(in),uuid(in),uuid(in),in.readUTF(),in.readInt(),in.readInt(),in.readInt());var result=new Entry(p,Phase.valueOf(in.readUTF()),in.readInt(),in.readLong(),in.readUTF(),in.readUTF(),in.readUTF());if(in.read()!=-1)throw new IOException("Unknown journal payload fields");return result;}
  }catch(IllegalArgumentException|NullPointerException invalid){throw new IOException("Invalid journal semantics",invalid);}
 }
 @Override public synchronized void close(){active.clear();closed=true;try{if(lock!=null)lock.release();if(lockChannel!=null)lockChannel.close();}catch(IOException error){fault=error.toString();}}
}
