package dev.godpc.industrialcolonies.space;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;

/** Durable admission for one physical journey. Never moves bodies, fuel or cargo.
 * Native adapters must verify physical facts before supplying evidence digests. */
public final class FreightJourneyJournal {
 public enum Phase { READY, ASCENT, HANDOFF, ORBIT, APPROACH, UNLOAD, COMPLETE, CANCELLED;
  public boolean terminal(){return this==COMPLETE||this==CANCELLED;}
 }
 public record Plan(UUID journey, UUID transponder, UUID owner, UUID sourceBody,
                    String sourceDimension, String destinationDimension,
                    String sourceRoute, String destinationRoute,
                    String controllerDigest, String cargoDigest) {
  public Plan {
   Objects.requireNonNull(journey);Objects.requireNonNull(transponder);Objects.requireNonNull(owner);Objects.requireNonNull(sourceBody);
   for(String value:List.of(sourceDimension,destinationDimension,sourceRoute,destinationRoute))
    if(value.isBlank()||value.length()>MAX_TEXT)throw new IllegalArgumentException("Incomplete or oversized journey plan");
   if(sourceDimension.equals(destinationDimension))throw new IllegalArgumentException("Distinct handoff dimensions required");
   digestField(controllerDigest);digestField(cargoDigest);
  }
 }
 public record Entry(Plan plan, Phase phase, UUID body, long revision, String evidenceDigest, String holdReason, String encounterIntent, String encounterReceipt) {
  public Entry(Plan plan,Phase phase,UUID body,long revision,String evidenceDigest,String holdReason){this(plan,phase,body,revision,evidenceDigest,holdReason,"","");}
  public Entry(Plan plan,Phase phase,UUID body,long revision,String evidenceDigest,String holdReason,String encounterIntent){this(plan,phase,body,revision,evidenceDigest,holdReason,encounterIntent,"");}
  public Entry {
   Objects.requireNonNull(plan);Objects.requireNonNull(phase);Objects.requireNonNull(body);Objects.requireNonNull(holdReason);Objects.requireNonNull(encounterIntent);Objects.requireNonNull(encounterReceipt);
   if(revision<0||holdReason.length()>MAX_TEXT)throw new IllegalArgumentException("Invalid journey revision or reason");
   digestField(evidenceDigest);
   if(!encounterIntent.isEmpty()&&(phase!=Phase.ORBIT||!validIntent(encounterIntent)||!evidenceDigest.equals(intentDigest(encounterIntent))))throw new IllegalArgumentException("Invalid pending encounter intent");
   if(!encounterReceipt.isEmpty()&&(!validIntent(encounterReceipt)||!encounterIntent.isEmpty()||phase.ordinal()<Phase.APPROACH.ordinal()))throw new IllegalArgumentException("Invalid acknowledged encounter receipt");
   boolean sourcePhase=phase==Phase.READY||phase==Phase.ASCENT||phase==Phase.HANDOFF;
   if(sourcePhase&&!body.equals(plan.sourceBody()))throw new IllegalArgumentException("Pre-handoff body changed");
   if(!sourcePhase&&phase!=Phase.CANCELLED&&body.equals(plan.sourceBody()))throw new IllegalArgumentException("Native destination body required");
  }
 }
 /** A permit is valid only within this journal instance and current revision. */
 public record Permit(UUID journey, UUID epoch, long revision) {}
 private static final int LEGACY_MAGIC=0x49434a31,INTENT_MAGIC=0x49434a32,MAGIC=0x49434a33,MAX_TEXT=1_000_000,MAX_FILE=9_000_000;
 private final Path directory;
 private final UUID epoch=UUID.randomUUID();
 private final Map<UUID,Entry> entries=new HashMap<>();
 private final Set<UUID> active=new HashSet<>();
 private final Set<UUID> verifiedReceipts=new HashSet<>();
 private String fault="";
 public FreightJourneyJournal(Path directory){
  this.directory=directory;
  try{
   Files.createDirectories(directory);
   if(Files.isSymbolicLink(directory))throw new IOException("Journey directory is a symbolic link");
   try(var stream=Files.list(directory)){
    var files=stream.sorted().toList();if(files.size()>10_000)throw new IOException("Too many journey records");
    for(var file:files){
     String name=file.getFileName().toString();
     if(name.endsWith(".pending"))throw new IOException("Interrupted journey write: "+name);
     if(!name.endsWith(".dat"))continue;
     Entry entry=decode(read(file));
     if(!name.equals(entry.plan().journey()+".dat")||entries.putIfAbsent(entry.plan().journey(),entry)!=null)throw new IOException("Journey identity conflict");
    }
   }
   var owners=new HashSet<UUID>();
   for(var entry:entries.values())if(!entry.phase().terminal()&&!owners.add(entry.plan().transponder()))throw new IOException("Multiple unfinished journeys for one ship");
   // Every reopened nonterminal record is held, even if its saved reason is empty.
  }catch(Exception error){fault=error.toString();}
 }
 public synchronized String fault(){return fault;}
 public synchronized List<Entry> entries(){return List.copyOf(entries.values());}
 public synchronized Entry get(UUID id){return Objects.requireNonNull(entries.get(id),"Unknown journey");}
 public synchronized boolean held(UUID id){return !fault.isEmpty()||!active.contains(id);}
 public synchronized boolean unfinished(UUID transponder){return !fault.isEmpty()||entries.values().stream().anyMatch(e->!e.phase().terminal()&&e.plan().transponder().equals(transponder));}
 /** Hardware may already be installed during ascent. An unfinished journey
  * grants native departure only after its exact source HANDOFF is durable and
  * actively admitted. Unassigned craft retain the existing hardware policy. */
 public synchronized boolean nativeHandoffAllowed(UUID body,String dimension){
  Objects.requireNonNull(body);Objects.requireNonNull(dimension);
  if(!fault.isEmpty())return false;
  var matches=entries.values().stream().filter(e->!e.phase().terminal()&&(e.body().equals(body)||e.plan().sourceBody().equals(body))).toList();
  // Cancelling a source leg above the native threshold must not accidentally
  // authorize departure by removing its unfinished record. A newly verified
  // assigned journey takes precedence and can explicitly rearm HANDOFF.
  if(matches.isEmpty())return entries.values().stream().noneMatch(e->e.phase()==Phase.CANCELLED&&(e.body().equals(body)||e.plan().sourceBody().equals(body)));
  if(matches.size()!=1)return false;
  var entry=matches.getFirst();
  return entry.phase()==Phase.HANDOFF&&entry.body().equals(body)&&entry.plan().sourceBody().equals(body)
   &&entry.plan().sourceDimension().equals(dimension)&&active.contains(entry.plan().journey())&&entry.holdReason().isEmpty();
 }
 /** Independent power sources can survive restart. Authorize fluid movement at
  * the dock operation itself, not just at the driver's motor command. */
 public synchronized boolean nativeFluidTransferAllowed(UUID body){
  return nativeTransferAllowed(body,false);
 }
 /** Native capture can exchange items during APPROACH before powered unloading. */
 public synchronized boolean nativeItemTransferAllowed(UUID body){
  return nativeTransferAllowed(body,true);
 }
 private boolean nativeTransferAllowed(UUID body,boolean passiveItems){
  Objects.requireNonNull(body);
  if(!fault.isEmpty())return false;
  var matches=entries.values().stream().filter(e->!e.phase().terminal()&&(e.body().equals(body)||e.plan().sourceBody().equals(body))).toList();
  if(matches.isEmpty())return entries.values().stream().noneMatch(e->e.phase()==Phase.CANCELLED&&(e.body().equals(body)||e.plan().sourceBody().equals(body)));
  if(matches.size()!=1)return false;
  var entry=matches.getFirst();
  return (entry.phase()==Phase.UNLOAD||(passiveItems&&entry.phase()==Phase.APPROACH))&&entry.body().equals(body)&&active.contains(entry.plan().journey())&&entry.holdReason().isEmpty();
 }
 public synchronized Entry prepare(Plan plan,String evidence)throws IOException{
  healthy();if(entries.containsKey(plan.journey())||unfinished(plan.transponder()))throw new IllegalStateException("Journey identity already used or ship already assigned");
  var entry=new Entry(plan,Phase.READY,plan.sourceBody(),0,evidence,"Explicit verified start required");write(entry);return entry;
 }
 /** Caller must recheck native stored/live identity, exact cargo and actuator ownership. */
 public synchronized Permit resume(UUID id,long expectedRevision,String physicalEvidence)throws IOException{
  healthy();Entry old=get(id);checkRevision(old,expectedRevision);
  if(old.phase().terminal()||active.contains(id)||!old.encounterIntent().isEmpty())throw new IllegalStateException("Journey terminal, active or encounter requires reconciliation");
  if(!old.encounterReceipt().isEmpty()&&!verifiedReceipts.contains(id))throw new IllegalStateException("Acknowledged encounter requires fresh native reconciliation");
  var next=new Entry(old.plan(),old.phase(),old.body(),Math.incrementExact(old.revision()),physicalEvidence,"","",old.encounterReceipt());
  write(next);active.add(id);return permit(next);
 }
 public synchronized boolean admits(Permit permit){
  if(permit==null||!fault.isEmpty()||!epoch.equals(permit.epoch())||!active.contains(permit.journey()))return false;
  var entry=entries.get(permit.journey());return entry!=null&&!entry.phase().terminal()&&entry.revision()==permit.revision()&&entry.holdReason().isEmpty();
 }
 /** Sequential physical phases only. HANDOFF -> ORBIT alone may replace the body. */
 public synchronized Permit advance(Permit permit,Phase nextPhase,UUID observedBody,String evidence)throws IOException{
  healthy();if(!admits(permit))throw new IllegalStateException("Stale or held journey permit");Entry old=get(permit.journey());
  if(!old.encounterIntent().isEmpty())throw new IllegalStateException("Pending encounter requires verified completion");
  if(nextPhase==Phase.CANCELLED||nextPhase.ordinal()!=old.phase().ordinal()+1)throw new IllegalStateException("Journey phase cannot skip or replay");
  boolean transfer=old.phase()==Phase.HANDOFF&&nextPhase==Phase.ORBIT;
  if(transfer?observedBody.equals(old.body()):!observedBody.equals(old.body()))throw new IllegalArgumentException("Unexpected physical body transition");
  var next=new Entry(old.plan(),nextPhase,observedBody,Math.incrementExact(old.revision()),evidence,"","",old.encounterReceipt());write(next);
  if(nextPhase.terminal())active.remove(permit.journey());return permit(next);
 }
 /** Persist exact native intent BEFORE any body change. The native adapter must
  * encode/verify identities, coordinates, orientation, cargo and controller state.
  * This journal preserves those bytes; it does not certify their physical truth. */
 public synchronized Permit beginEncounter(Permit permit,String nativeIntent)throws IOException{
  healthy();if(!admits(permit))throw new IllegalStateException("Stale or held encounter permit");var old=get(permit.journey());
  if(old.phase()!=Phase.ORBIT||!old.encounterIntent().isEmpty()||!validIntent(nativeIntent))throw new IllegalStateException("Encounter requires orbital phase and one complete new intent");
  var next=new Entry(old.plan(),old.phase(),old.body(),Math.incrementExact(old.revision()),intentDigest(nativeIntent),"",nativeIntent);write(next);return permit(next);
 }
 /** Only a same-process, still-admitted operation may acknowledge its observed result. */
 public synchronized Permit finishEncounter(Permit permit,UUID observedBody,String evidence)throws IOException{
  healthy();if(!admits(permit))throw new IllegalStateException("Stale or held encounter completion");var old=get(permit.journey());
  if(old.encounterIntent().isEmpty()||!old.body().equals(observedBody))throw new IllegalStateException("Missing encounter or changed body authority");
  var next=new Entry(old.plan(),Phase.APPROACH,old.body(),Math.incrementExact(old.revision()),evidence,"","",old.encounterIntent());write(next);verifiedReceipts.add(permit.journey());return permit(next);
 }
 /** After interruption, a native adapter must inspect actual old/new state.
  * Resolving an intent never restarts propulsion or grants a permit. */
 public synchronized Entry reconcileEncounter(UUID id,long expectedRevision,UUID observedBody,boolean applied,String evidence)throws IOException{
  healthy();var old=get(id);checkRevision(old,expectedRevision);
  if(active.contains(id)||old.encounterIntent().isEmpty()||!old.body().equals(observedBody))throw new IllegalStateException("Reconciliation requires held intent and unchanged body authority");
  var next=new Entry(old.plan(),applied?Phase.APPROACH:Phase.ORBIT,old.body(),Math.incrementExact(old.revision()),evidence,"Encounter reconciled; explicit verified start required","",applied?old.encounterIntent():"");write(next);if(applied)verifiedReceipts.add(id);return next;
 }
 /** Retained acknowledgement is audit evidence, never permission to replay.
  * Only a native verifier may supply the observed stationary old/new outcome.
  * Later moving phases require a separate physical recovery protocol. */
 public synchronized Entry reconcileAcknowledgedEncounter(UUID id,long expectedRevision,UUID observedBody,boolean applied,String evidence)throws IOException{
  healthy();var old=get(id);checkRevision(old,expectedRevision);
  if(active.contains(id)||old.phase()!=Phase.APPROACH||old.encounterReceipt().isEmpty()||!old.body().equals(observedBody))throw new IllegalStateException("Held acknowledged approach and unchanged authority required");
  var next=new Entry(old.plan(),applied?Phase.APPROACH:Phase.ORBIT,old.body(),Math.incrementExact(old.revision()),evidence,"Acknowledged encounter reconciled; explicit verified start required","",applied?old.encounterReceipt():"");
  write(next);if(applied)verifiedReceipts.add(id);else verifiedReceipts.remove(id);return next;
 }
 /** A native verifier may checkpoint a deliberately held later phase only when
  * this process already reconciled its encounter. Never creates authority from
  * an unknown fresh-process state; the original receipt is retained verbatim. */
 public synchronized FreightHeldPhaseRecord prepareHeldPhaseRecovery(UUID id,long expectedRevision,UUID target,String nativeState)throws IOException{
  healthy();var old=get(id);checkRevision(old,expectedRevision);
  if(active.contains(id)||!verifiedReceipts.contains(id)||old.holdReason().isBlank())throw new IllegalStateException("Deliberately held and already verified encounter required");
  return FreightHeldPhaseRecord.capture(old,target,nativeState);
 }
 /** Read-only snapshot of an already admitted UNLOAD. This grants no new
  * authority and must never be used to baseline an unknown restarted state. */
 public synchronized FreightHeldPhaseRecord prepareActiveUnloadRecovery(UUID id,long expectedRevision,UUID target,String nativeState)throws IOException{
  healthy();var old=get(id);checkRevision(old,expectedRevision);
  if(!active.contains(id)||!verifiedReceipts.contains(id)||old.phase()!=Phase.UNLOAD||!old.holdReason().isBlank())throw new IllegalStateException("Already admitted verified active UNLOAD required");
  return FreightHeldPhaseRecord.capture(old,target,nativeState);
 }
 /** Exact native checkpoint comparison only. No phase rewind, motion, cargo
  * write, encounter replay or automatic resume follows this journal repair. */
 public synchronized Entry reconcileHeldPhaseRecovery(FreightHeldPhaseRecord saved,UUID observedBody,UUID observedTarget,String nativeState)throws IOException{
  healthy();Objects.requireNonNull(saved);var old=get(saved.journey());
  if(active.contains(saved.journey()))throw new IllegalStateException("Current journey must remain held");
  saved.verify(old,observedBody,observedTarget,nativeState);
  var next=new Entry(old.plan(),old.phase(),old.body(),Math.incrementExact(old.revision()),FreightHeldPhaseRecord.hash(saved.encode()),"Current held phase reconciled; explicit verified start required","",old.encounterReceipt());
  write(next);verifiedReceipts.add(saved.journey());return next;
 }
 /** Explicitly separate from ordinary checkpoint recovery. A fresh process may
  * find the one recorded resume but unchanged before-transfer native storage.
  * Full native audit is mandatory; no later phase/revision or hold is accepted. */
 public synchronized Entry reconcileUnflushedUnloadResume(FreightHeldPhaseRecord saved,UUID observedBody,UUID observedTarget,String nativeState)throws IOException{
  healthy();Objects.requireNonNull(saved);var old=get(saved.journey());
  if(active.contains(saved.journey())||verifiedReceipts.contains(saved.journey()))throw new IllegalStateException("Fresh held process audit required");
  saved.verifyUnflushedResume(old,observedBody,observedTarget,nativeState);
  var next=new Entry(old.plan(),old.phase(),old.body(),Math.incrementExact(old.revision()),FreightHeldPhaseRecord.hash(saved.encode()),"Unflushed UNLOAD resume reconciled; explicit verified start required","",old.encounterReceipt());
  write(next);verifiedReceipts.add(saved.journey());return next;
 }
 public synchronized void hold(UUID id,String reason)throws IOException{
  // Revoke before persistence, so a failed write cannot leave an admitted driver.
  active.remove(id);healthy();Entry old=get(id);
  if(old.phase().terminal())return;
  if(reason.isBlank())throw new IllegalArgumentException("Hold reason required");
  write(new Entry(old.plan(),old.phase(),old.body(),Math.incrementExact(old.revision()),old.evidenceDigest(),reason,old.encounterIntent(),old.encounterReceipt()));
 }
 public synchronized void holdShip(UUID transponder,String reason)throws IOException{
  for(var entry:List.copyOf(entries.values()))if(entry.plan().transponder().equals(transponder)&&!entry.phase().terminal())hold(entry.plan().journey(),reason);
 }
 public synchronized void holdAll(String reason)throws IOException{
  active.clear();healthy();for(var entry:List.copyOf(entries.values()))if(!entry.phase().terminal())hold(entry.plan().journey(),reason);
 }
 public synchronized void cancel(UUID id,long expectedRevision,String reason)throws IOException{
  healthy();Entry old=get(id);checkRevision(old,expectedRevision);
  if(old.phase().terminal()||reason.isBlank())throw new IllegalStateException("Terminal journey or missing cancellation reason");
  if(!old.encounterIntent().isEmpty()){active.remove(id);throw new IllegalStateException("Pending encounter must be reconciled before cancellation");}
  active.remove(id);write(new Entry(old.plan(),Phase.CANCELLED,old.body(),Math.incrementExact(old.revision()),old.evidenceDigest(),reason,"",old.encounterReceipt()));
 }
 private Permit permit(Entry entry){return new Permit(entry.plan().journey(),epoch,entry.revision());}
 private static void checkRevision(Entry entry,long expected){if(entry.revision()!=expected)throw new IllegalStateException("Journey revision changed");}
 private void healthy()throws IOException{if(!fault.isEmpty())throw new IOException("Journey journal held: "+fault);}
 private static void digestField(String value){if(value==null||!value.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("SHA-256 evidence required");}
 private static boolean validIntent(String value){return value!=null&&value.startsWith("IC_ORBITAL_ENCOUNTER_V1\n")&&value.length()>"IC_ORBITAL_ENCOUNTER_V1\n".length()&&value.length()<=MAX_TEXT;}
 private static String intentDigest(String value){return HexFormat.of().formatHex(hash(value.getBytes(StandardCharsets.UTF_8)));}
 private static byte[] read(Path file)throws IOException{
  if(!Files.isRegularFile(file,LinkOption.NOFOLLOW_LINKS)||Files.size(file)>MAX_FILE)throw new IOException("Invalid journey file");return Files.readAllBytes(file);
 }
 private void write(Entry entry)throws IOException{
  Path pending=directory.resolve(entry.plan().journey()+".pending"),target=directory.resolve(entry.plan().journey()+".dat");
  try{
   byte[] bytes=encode(entry);if(bytes.length>MAX_FILE)throw new IOException("Journey record too large");
   try(var channel=FileChannel.open(pending,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)){
    var buffer=ByteBuffer.wrap(bytes);while(buffer.hasRemaining())channel.write(buffer);channel.force(true);
   }
   Files.move(pending,target,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
   if(!decode(read(target)).equals(entry))throw new IOException("Journey readback mismatch");entries.put(entry.plan().journey(),entry);
  }catch(Exception error){active.clear();fault=error.toString();throw new IOException("Journey write failed; all journey admission held",error);}
 }
 private static byte[] encode(Entry e)throws IOException{
  Plan p=e.plan();var raw=new ByteArrayOutputStream();
  try(var out=new DataOutputStream(raw)){
   out.writeInt(MAGIC);out.writeLong(e.revision());
   for(String value:List.of(p.journey().toString(),p.transponder().toString(),p.owner().toString(),p.sourceBody().toString(),p.sourceDimension(),p.destinationDimension(),p.sourceRoute(),p.destinationRoute(),p.controllerDigest(),p.cargoDigest(),e.phase().name(),e.body().toString(),e.evidenceDigest(),e.holdReason(),e.encounterIntent(),e.encounterReceipt())){
    byte[] bytes=value.getBytes(StandardCharsets.UTF_8);out.writeInt(bytes.length);out.write(bytes);
   }
  }
  byte[] payload=raw.toByteArray();raw.write(hash(payload));return raw.toByteArray();
 }
 private static Entry decode(byte[] bytes)throws IOException{
  if(bytes.length<44||bytes.length>MAX_FILE)throw new IOException("Invalid journey record length");
  byte[] payload=Arrays.copyOf(bytes,bytes.length-32);
  if(!MessageDigest.isEqual(hash(payload),Arrays.copyOfRange(bytes,bytes.length-32,bytes.length)))throw new IOException("Journey checksum mismatch");
  try(var in=new DataInputStream(new ByteArrayInputStream(payload))){
   int magic=in.readInt();if(magic!=MAGIC&&magic!=INTENT_MAGIC&&magic!=LEGACY_MAGIC)throw new IOException("Unsupported journey format");long revision=in.readLong();String[] s=new String[magic==MAGIC?16:magic==INTENT_MAGIC?15:14];
   for(int i=0;i<s.length;i++){int count=in.readInt();if(count<0||count>MAX_TEXT*4||count>in.available())throw new IOException("Invalid journey field length");s[i]=new String(in.readNBytes(count),StandardCharsets.UTF_8);}
   if(in.available()!=0)throw new IOException("Trailing journey data");
   return new Entry(new Plan(UUID.fromString(s[0]),UUID.fromString(s[1]),UUID.fromString(s[2]),UUID.fromString(s[3]),s[4],s[5],s[6],s[7],s[8],s[9]),Phase.valueOf(s[10]),UUID.fromString(s[11]),revision,s[12],s[13],magic==LEGACY_MAGIC?"":s[14],magic==MAGIC?s[15]:"");
  }catch(RuntimeException error){throw new IOException("Invalid journey record",error);}
 }
 private static byte[] hash(byte[] bytes){try{return MessageDigest.getInstance("SHA-256").digest(bytes);}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
