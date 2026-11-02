package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.OrbitalBodyCustody;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.io.IOException;
import java.util.*;
import java.nio.file.Path;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.IdentityDirectorySavedData;

/** Explicit per-level custody roster. Loading never grants spawning, movement,
 * weapon authority or automatic encounter restart. Missing/unloaded/changed
 * Schema3 uses the existing controller-verified basic-v1 cache custody profile.
 * Old schema1/schema2 hashes are refused/preserved rather than silently reinterpreted.
 * Survivors refuse recovery; callers must not infer an empty world from it. */
public final class EnemyEncounterRoster extends SavedData {
 public static final String FILE="industrial_colonies_enemy_roster";
 public static final Factory<EnemyEncounterRoster> FACTORY=new Factory<>(EnemyEncounterRoster::new,EnemyEncounterRoster::load);
 public record Entry(UUID body,UUID encounter,UUID root,int blocks,String custodyDigest,List<EnemyMountedCannonCustody.Attachment> attachments) {
  public Entry {
   Objects.requireNonNull(body);Objects.requireNonNull(encounter);Objects.requireNonNull(root);
   if(blocks<1||blocks>65536||custodyDigest==null||!custodyDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid native custody record");
   attachments=List.copyOf(attachments);if(attachments.size()>64)throw new IllegalArgumentException("Attachment capacity exceeded");
   var mounts=new HashSet<net.minecraft.core.BlockPos>();var entities=new HashSet<UUID>();
   for(var row:attachments)if(row.mount()==null||row.entity()==null||row.blocks()<1||row.blocks()>256||row.digest()==null||!row.digest().matches("[0-9a-f]{64}")||!mounts.add(row.mount())||!entities.add(row.entity()))throw new IllegalArgumentException("Invalid duplicate or incomplete native attachment");
  }
 }
 public record HeldRecovery(Map<UUID,UUID> bodies,String reason) {
  public HeldRecovery {bodies=Map.copyOf(bodies);}
 }
 /** Original entry remains intact. A receipt annotation never means free spawn
  * capacity or permission to resume the former NPC. */
 public record Captured(UUID body,UUID claimant,UUID session,UUID target,String receiptDigest){
  public Captured{
   Objects.requireNonNull(body);Objects.requireNonNull(claimant);Objects.requireNonNull(session);Objects.requireNonNull(target);
   if(body.equals(target)||receiptDigest==null||!receiptDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid captured roster binding");
  }
 }
 private final Map<UUID,Entry> entries=new HashMap<>();
 private final Map<UUID,Captured> captured=new HashMap<>();
 private String dimension="";
 private boolean sealed,invalid;
 private CompoundTag rejected;
 public static EnemyEncounterRoster get(ServerLevel level) {
  thread(level);var result=level.getDataStorage().computeIfAbsent(FACTORY,FILE);if(!result.invalid&&result.dimension.isEmpty()){result.dimension=level.dimension().location().toString();result.setDirty();}return result;
 }
 public boolean held(){return true;}
 public boolean sealed(){return sealed&&!invalid;}
 public boolean invalid(){return invalid;}
 public List<Entry> entries(){return entries.values().stream().sorted(Comparator.comparing(e->e.body().toString())).toList();}
 public List<Captured> captured(){return captured.values().stream().sorted(Comparator.comparing(e->e.body().toString())).toList();}
 private static void thread(ServerLevel level){if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread roster required");}
 private void valid(ServerLevel level) {
  thread(level);if(invalid)throw new IllegalStateException("Invalid roster preserved; recovery held");
  if(!dimension.isEmpty()&&!dimension.equals(level.dimension().location().toString()))throw new IllegalStateException("Roster dimension changed");
 }
 /** Records supplied existing native bodies, never commissions or recreates one.
  * Every change invalidates the prior complete-roster seal. No removal API:
  * destruction/capture reconciliation requires separately qualified custody. */
 public void record(ServerSubLevel body)throws IOException {
  var level=body.getLevel();valid(level);
  if(!captured.isEmpty()||EnemyCaptureHold.inhibits(body.getUserDataTag()))throw new IllegalStateException("Capture requires explicit receipt reconciliation");
  var identity=EnemyHullIdentity.read(body);var custody=OrbitalBodyCustody.readForEncounterRecovery(body);
  var next=new Entry(body.getUniqueId(),identity.encounter(),identity.root(),custody.blocks(),custody.digest(),EnemyMountedCannonCustody.readHeld(body).attachments());
  var old=entries.get(next.body());
  if(old!=null&&(!old.encounter().equals(next.encounter())||!old.root().equals(next.root())))throw new IllegalStateException("Recorded physical identity changed");
  if(old==null&&entries.size()>=4096)throw new IllegalStateException("Roster capacity exceeded");
  entries.put(next.body(),next);dimension=level.dimension().location().toString();sealed=false;setDirty();
 }
 private Map<UUID,UUID> audit(ServerLevel level)throws IOException {
  if(!captured.isEmpty())throw new IllegalStateException("Captured roster requires saved receipt audit");
  return audit(level,Map.of());
 }
 private Map<UUID,UUID> audit(ServerLevel level,Map<UUID,Captured> verifiedCaptures)throws IOException {
  valid(level);if(entries.isEmpty())throw new IllegalStateException("Complete nonempty commissioned roster required");
  var container=SubLevelContainer.getContainer(level);if(container==null)throw new IllegalStateException("Native body container unavailable");
  var found=new HashSet<UUID>();var roster=new HashMap<UUID,UUID>();int scanned=0;
  for(var body:container.getAllSubLevels()) {
   if(++scanned>4096)throw new IllegalStateException("Native body scan budget exceeded");
   var expected=entries.get(body.getUniqueId());var tag=body.getUserDataTag();boolean marked=tag!=null&&tag.contains(EnemyHullIdentity.KEY);
   if(!marked){if(expected!=null)throw new IllegalStateException("Recorded body lost NPC identity");continue;}
   if(expected==null||!found.add(body.getUniqueId()))throw new IllegalStateException("Unknown or duplicate native NPC survivor");
   var identity=EnemyHullIdentity.read(body);var custody=OrbitalBodyCustody.readForEncounterRecovery(body);
   if(!expected.encounter().equals(identity.encounter())||!expected.root().equals(identity.root())
       ||expected.blocks()!=custody.blocks()||(!verifiedCaptures.containsKey(expected.body())&&!expected.custodyDigest().equals(custody.digest()))
       ||!expected.attachments().equals(EnemyMountedCannonCustody.readHeld(body).attachments()))throw new IllegalStateException("Recorded native identity or custody changed");
   roster.put(expected.body(),expected.encounter());
  }
  if(!found.equals(entries.keySet()))throw new IllegalStateException("Recorded native survivor not loaded");
  return Map.copyOf(roster);
 }
 private void auditCaptureReferences(ServerLevel level,Map<UUID,Captured> references,Path directory,
     EnemyEncounterJournal journal,IdentityDirectorySavedData identities)throws IOException{
  valid(level);var container=SubLevelContainer.getContainer(level);if(container==null)throw new IOException("Native roster container absent");
  var bodies=new HashMap<UUID,ServerSubLevel>();int count=0;
  for(var body:container.getAllSubLevels()){
   if(++count>4096||bodies.putIfAbsent(body.getUniqueId(),body)!=null)throw new IOException("Duplicate or excessive native roster bodies");
  }
  for(var ref:references.values()){
   var source=bodies.get(ref.body());var target=bodies.get(ref.target());
   if(source==null||target==null||!entries.containsKey(ref.body())||!entries.containsKey(ref.target()))throw new IOException("Captured roster endpoints absent");
   var result=NativeCaptureRestartAudit.inspect(directory,ref.body(),journal,source,target,identities);
   var ack=EnemyCaptureTransferIntent.inspectAppliedHeld(directory,ref.body()).orElseThrow(()->new IOException("Captured receipt absent"));
   if(result.state()!=NativeCaptureRestartAudit.State.APPLIED_HELD||!ref.claimant().equals(result.intent().claimant())
       ||!ref.session().equals(result.intent().session())||!ref.target().equals(result.intent().target())
       ||!ref.receiptDigest().equals(EnemyCaptureTransferIntent.appliedDigest(ack)))throw new IOException("Captured roster receipt changed or unapplied");
  }
 }
 /** Adds only an annotation after native saved-owner/cargo verification. Original
  * custody entry and reservation are retained; failure changes neither roster nor budget. */
 public void reconcileCapturedHeld(ServerLevel level,UUID body,Path directory,EnemyEncounterJournal journal,
     IdentityDirectorySavedData identities)throws IOException{
  valid(level);if(!sealed||captured.containsKey(body))throw new IOException("Sealed original roster required; repeat capture refused");
  var ack=EnemyCaptureTransferIntent.inspectAppliedHeld(directory,body).orElseThrow(()->new IOException("Applied receipt required"));
  var intent=ack.intent();var candidates=new HashMap<>(captured);
  candidates.put(body,new Captured(body,intent.claimant(),intent.session(),intent.target(),EnemyCaptureTransferIntent.appliedDigest(ack)));
  auditCaptureReferences(level,candidates,directory,journal,identities);audit(level,candidates);
  captured.clear();captured.putAll(candidates);setDirty();
 }
 /** Explicit read/audit before budget reconstruction. Captured bodies still
  * count until a separately qualified release policy is implemented. */
 public HeldRecovery recoverCapturedHeld(ServerLevel level,EnemyEncounterBudget budget,Path directory,
     EnemyEncounterJournal journal,IdentityDirectorySavedData identities)throws IOException{
  valid(level);if(!sealed||captured.isEmpty())throw new IOException("Sealed captured roster required");
  auditCaptureReferences(level,captured,directory,journal,identities);var roster=audit(level,captured);
  EnemyNativeBudget.restore(level,roster,budget);return new HeldRecovery(roster,"CAPTURED_HELD_CAPACITY_RETAINED");
 }
 /** Explicit same-thread complete audit; failed reconstruction preserves budget. */
 public HeldRecovery seal(ServerLevel level,EnemyEncounterBudget budget)throws IOException {
  var roster=audit(level);EnemyNativeBudget.restore(level,roster,budget);sealed=true;setDirty();
  return new HeldRecovery(roster,"EXPLICITLY_SEALED_HELD");
 }
 /** Reopened data stays held even after successful audit and budget reconstruction. */
 public HeldRecovery recoverHeld(ServerLevel level,EnemyEncounterBudget budget)throws IOException {
  valid(level);if(!sealed)throw new IllegalStateException("Incomplete roster cannot reconstruct budget");
  var roster=audit(level);EnemyNativeBudget.restore(level,roster,budget);
  return new HeldRecovery(roster,"RESTART_REQUIRES_EXPLICIT_START");
 }
 /** Read-only complete audit: no seal change, saved-data write or budget repair. */
 public HeldRecovery auditSealedReadOnly(ServerLevel level)throws IOException {
  valid(level);if(!sealed)throw new IllegalStateException("Unsealed roster remains held");
  return new HeldRecovery(audit(level),"READ_ONLY_HELD_CUSTODY");
 }
 public static EnemyEncounterRoster load(CompoundTag tag,HolderLookup.Provider registries) {
  var result=new EnemyEncounterRoster();
  try {
   int format=tag.getInt("format");
   if(!tag.getAllKeys().equals(format==4?Set.of("format","dimension","sealed","entries","captured"):Set.of("format","dimension","sealed","entries"))||!tag.contains("format",Tag.TAG_INT)||(format!=3&&format!=4)
      ||!tag.contains("dimension",Tag.TAG_STRING)||!tag.contains("sealed",Tag.TAG_BYTE)||!tag.contains("entries",Tag.TAG_LIST))throw new IllegalArgumentException("Invalid roster schema");
   result.dimension=tag.getString("dimension");if(result.dimension.length()>256||ResourceLocation.tryParse(result.dimension)==null)throw new IllegalArgumentException("Invalid roster dimension");
   var list=tag.getList("entries",Tag.TAG_COMPOUND);if(list.size()!=((ListTag)tag.get("entries")).size()||list.size()>4096)throw new IllegalArgumentException("Invalid roster list");
   var attachmentIds=new HashSet<UUID>();
   for(Tag value:list){var row=(CompoundTag)value;
    if(!row.getAllKeys().equals(Set.of("body","encounter","root","blocks","custody","attachments"))||!row.hasUUID("body")||!row.hasUUID("encounter")||!row.hasUUID("root")
       ||!row.contains("blocks",Tag.TAG_INT)||!row.contains("custody",Tag.TAG_STRING)||!row.contains("attachments",Tag.TAG_LIST))throw new IllegalArgumentException("Invalid roster identity schema");
    var entry=new Entry(row.getUUID("body"),row.getUUID("encounter"),row.getUUID("root"),row.getInt("blocks"),row.getString("custody"),readAttachments(row));
    for(var attachment:entry.attachments())if(!attachmentIds.add(attachment.entity()))throw new IllegalArgumentException("Duplicate native attachment across roster bodies");
    if(result.entries.putIfAbsent(entry.body(),entry)!=null)throw new IllegalArgumentException("Duplicate roster body");
   }
   if(format==4){
    if(!tag.contains("captured",Tag.TAG_LIST))throw new IllegalArgumentException("Captured roster list absent");
    var captures=tag.getList("captured",Tag.TAG_COMPOUND);
    if(captures.size()!=((ListTag)tag.get("captured")).size()||captures.size()>4096)throw new IllegalArgumentException("Invalid captured roster list");
    for(Tag value:captures){var row=(CompoundTag)value;
     if(!row.getAllKeys().equals(Set.of("body","claimant","session","target","receipt"))||!row.hasUUID("body")||!row.hasUUID("claimant")||!row.hasUUID("session")||!row.hasUUID("target")||!row.contains("receipt",Tag.TAG_STRING))throw new IllegalArgumentException("Invalid captured row");
     var ref=new Captured(row.getUUID("body"),row.getUUID("claimant"),row.getUUID("session"),row.getUUID("target"),row.getString("receipt"));
     if(!result.entries.containsKey(ref.body())||!result.entries.containsKey(ref.target())||result.captured.putIfAbsent(ref.body(),ref)!=null)throw new IllegalArgumentException("Foreign or duplicate captured row");
    }
   }
   if(tag.getByte("sealed")!=0&&tag.getByte("sealed")!=1)throw new IllegalArgumentException("Invalid roster seal byte");result.sealed=tag.getBoolean("sealed");if(result.sealed&&result.entries.isEmpty()||!result.sealed&&!result.captured.isEmpty())throw new IllegalArgumentException("Invalid captured/sealed roster");
  }catch(RuntimeException failure){result.invalid=true;result.sealed=false;result.entries.clear();result.captured.clear();result.rejected=tag.copy();}
  return result;
 }
 private static List<EnemyMountedCannonCustody.Attachment> readAttachments(CompoundTag row) {
  var list=row.getList("attachments",Tag.TAG_COMPOUND);if(list.size()!=((ListTag)row.get("attachments")).size()||list.size()>64)throw new IllegalArgumentException("Invalid complete attachment list");
  var result=new ArrayList<EnemyMountedCannonCustody.Attachment>();
  for(Tag value:list){var item=(CompoundTag)value;
   if(!item.getAllKeys().equals(Set.of("x","y","z","entity","blocks","digest"))||!item.contains("x",Tag.TAG_INT)||!item.contains("y",Tag.TAG_INT)||!item.contains("z",Tag.TAG_INT)||!item.hasUUID("entity")||!item.contains("blocks",Tag.TAG_INT)||!item.contains("digest",Tag.TAG_STRING))throw new IllegalArgumentException("Invalid native attachment schema");
   result.add(new EnemyMountedCannonCustody.Attachment(new net.minecraft.core.BlockPos(item.getInt("x"),item.getInt("y"),item.getInt("z")),item.getUUID("entity"),item.getInt("blocks"),item.getString("digest")));
  }return List.copyOf(result);
 }
 private static ListTag writeAttachments(List<EnemyMountedCannonCustody.Attachment> attachments) {
  var result=new ListTag();for(var row:attachments){var item=new CompoundTag();item.putInt("x",row.mount().getX());item.putInt("y",row.mount().getY());item.putInt("z",row.mount().getZ());item.putUUID("entity",row.entity());item.putInt("blocks",row.blocks());item.putString("digest",row.digest());result.add(item);}return result;
 }
 @Override public CompoundTag save(CompoundTag tag,HolderLookup.Provider registries) {
  if(invalid)return rejected.copy();
  tag.putInt("format",captured.isEmpty()?3:4);tag.putString("dimension",dimension.isEmpty()?"minecraft:overworld":dimension);tag.putBoolean("sealed",sealed);
  if(!captured.isEmpty()){var captures=new ListTag();for(var ref:captured()){var row=new CompoundTag();row.putUUID("body",ref.body());row.putUUID("claimant",ref.claimant());row.putUUID("session",ref.session());row.putUUID("target",ref.target());row.putString("receipt",ref.receiptDigest());captures.add(row);}tag.put("captured",captures);}else tag.remove("captured");
  var list=new ListTag();for(var entry:entries()){var row=new CompoundTag();row.putUUID("body",entry.body());row.putUUID("encounter",entry.encounter());row.putUUID("root",entry.root());row.putInt("blocks",entry.blocks());row.putString("custody",entry.custodyDigest());row.put("attachments",writeAttachments(entry.attachments()));list.add(row);}tag.put("entries",list);return tag;
 }
}
