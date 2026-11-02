package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import net.minecraft.server.level.ServerLevel;

/** Explicit per-level optional-mineral lifecycle. Not registered in production.
 * Callers hold a lease across asynchronous generation and close this runtime on level teardown.
 * Owner groups sample every column; point lookup alone is not a border-routing query. */
public final class NativeContinentRuntime implements AutoCloseable {
 @FunctionalInterface public interface Families {
  List<NativeContinentCoordinator.Family> forContinent(ReTerraForgedGeography.ContinentKey key);
 }
 private final ServerLevel level;private final Path directory;private final String preset;
 private final Families families;private final int spacing,capacity;private final CoalRuntimePolicy coalPolicy;
 private final ReTerraForgedGeography geography;
 private final ContinentCoordinatorCache<ReTerraForgedGeography.ContinentKey,Entry> cache;
 private final String identity;
 private ContinentCoordinatorDirectory storage;
 private String rolloutFingerprint;private Families rolloutFamilies;
 /** Configure once before any continent is admitted; baseline root identity remains unchanged. */
 public void configureRollout(String fingerprint,Families supplied){
  thread();if(rolloutFingerprint!=null||cache.residentCount()!=0)throw new IllegalStateException("Rollout must precede continent admission");
  if(fingerprint==null||!fingerprint.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Explicit rollout policy required");
  rolloutFingerprint=fingerprint;rolloutFamilies=Objects.requireNonNull(supplied);
 }
 private NativeContinentRuntime(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families){
  this(root,level,preset,policy,spacing,capacity,families,null);
 }
 private NativeContinentRuntime(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families,CoalRuntimePolicy coalPolicy){
  this.level=Objects.requireNonNull(level);thread();
  if(!level.dimension().location().toString().equals("minecraft:overworld")||preset==null||!preset.matches("[a-f0-9]{64}")||policy==null||!policy.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Explicit Earth preset and policy fingerprints required");
  new ContinentSpacing(spacing,List.of());
  this.directory=root.toAbsolutePath().normalize();this.preset=preset;this.spacing=spacing;this.capacity=capacity;this.families=Objects.requireNonNull(families);this.coalPolicy=coalPolicy;
  if(coalPolicy!=null)coalPolicy.checkHeight(level.getMinBuildHeight(),level.getMaxBuildHeight());
  identity="IC_CONTINENT_RUNTIME_V1\n"+level.getSeed()+"\n"+level.dimension().location()+"\n"+level.getMinBuildHeight()+"\n"+level.getMaxBuildHeight()+"\n"+preset+"\n"+policy+"\n"+spacing+"\n"+(coalPolicy==null?"":"COAL_V1\n"+coalPolicy.fingerprint()+"\n");
  geography=ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState());
  cache=new ContinentCoordinatorCache<>(capacity,level.getServer()::isSameThread,this::load);
 }
 public static NativeContinentRuntime create(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families)throws IOException{
  var runtime=new NativeContinentRuntime(root,level,preset,policy,spacing,capacity,families);
  runtime.storage=ContinentCoordinatorDirectory.create(runtime.directory,runtime.identity);
  return runtime;
 }
 public static NativeContinentRuntime open(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families)throws IOException{
  var runtime=new NativeContinentRuntime(root,level,preset,policy,spacing,capacity,families);runtime.storage=ContinentCoordinatorDirectory.open(runtime.directory,runtime.identity);return runtime;
 }
 public static NativeContinentRuntime createWithCoal(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families,CoalRuntimePolicy coal)throws IOException{
  var runtime=new NativeContinentRuntime(root,level,preset,policy,spacing,capacity,families,Objects.requireNonNull(coal));
  runtime.storage=ContinentCoordinatorDirectory.create(runtime.directory,runtime.identity);return runtime;
 }
 public static NativeContinentRuntime openWithCoal(Path root,ServerLevel level,String preset,String policy,int spacing,int capacity,Families families,CoalRuntimePolicy coal)throws IOException{
  var runtime=new NativeContinentRuntime(root,level,preset,policy,spacing,capacity,families,Objects.requireNonNull(coal));
  runtime.storage=ContinentCoordinatorDirectory.open(runtime.directory,runtime.identity);return runtime;
 }
 private void thread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");}
 private void checkIdentity()throws IOException{
  thread();storage.check();
 }
 private Entry load(ReTerraForgedGeography.ContinentKey key)throws IOException{
  checkIdentity();
  String name=String.format(Locale.ROOT,"continent-%08x-%08x-%08x",key.centerX(),key.centerZ(),key.identityBits());
  if(geography.skipped(key)){
   if(Files.exists(directory.resolve(name),LinkOption.NOFOLLOW_LINKS)||Files.exists(directory.resolve(name+".started"),LinkOption.NOFOLLOW_LINKS)||Files.exists(directory.resolve(name+".policy"),LinkOption.NOFOLLOW_LINKS))
    throw new IOException("Native skipped region has existing saved commissioning; explicit recovery required, no deletion or reroll");
   return new Entry(key,directory.resolve(name),NativeContinentCoordinator.skipped(directory.resolve(name),level,key,preset,spacing),null);
  }
  ContinentCoordinatorDirectory.Entry entry;Families selectedPolicy=families;
  if(rolloutFingerprint==null)entry=storage.commission(name);
  else {var selection=storage.commission(name,rolloutFingerprint);entry=selection.entry();if(selection.rollout())selectedPolicy=rolloutFamilies;}
  var selected=List.copyOf(selectedPolicy.forContinent(key));
  var optional=entry.existing()?NativeContinentCoordinator.open(entry.path(),level,key,preset,selected,spacing):NativeContinentCoordinator.create(entry.path(),level,key,preset,selected,spacing);
  CoalRuntimeCommission coalIntent=null;
  if(coalPolicy!=null){var scope=new ContinentResourceDecision.Scope(level.getSeed(),level.dimension().location().toString(),preset);coalIntent=entry.existing()?CoalRuntimeCommission.open(entry.path(),coalPolicy,scope,key):CoalRuntimeCommission.create(entry.path(),coalPolicy,scope,key);}
  return new Entry(key,entry.path(),optional,coalIntent);
 }
 private final class Entry {
  final ReTerraForgedGeography.ContinentKey key;final Path path;final NativeContinentCoordinator optional;final CoalRuntimeCommission coalIntent;
  NativeCoalCoordinator coal;CoalDiscoveryCoordinator.Progress coalProgress;
  Entry(ReTerraForgedGeography.ContinentKey key,Path path,NativeContinentCoordinator optional,CoalRuntimeCommission coalIntent){this.key=key;this.path=path;this.optional=optional;this.coalIntent=coalIntent;}
  boolean ready()throws IOException{
   if(optional.skipped()){optional.ownerIndex();return true;}
   if(coalIntent!=null&&coalIntent.started()==0&&coal!=null)throw new IOException("Coal commissioning regressed");
   if(optional.progress().status()==NativeContinentCoordinator.Status.HELD)throw new IllegalStateException("Optional continent discovery held");
   if(coalProgress!=null&&(coalProgress.status()==CoalDiscoveryCoordinator.Status.HELD||coalProgress.status()==CoalDiscoveryCoordinator.Status.UNFITTED))throw new IllegalStateException("Required coal layout cannot release generation");
   return optional.progress().status()==NativeContinentCoordinator.Status.READY&&(coalPolicy==null||coalProgress!=null&&coalProgress.status()==CoalDiscoveryCoordinator.Status.READY);
  }
  void advance(int budget)throws IOException {
   if(optional.skipped()){optional.advance(budget);return;}
   if(optional.progress().status()!=NativeContinentCoordinator.Status.READY){optional.advance(budget);return;}
   if(coalPolicy==null)return;
   if(coal==null){
    var admitted=coalIntent.admit();boolean existing=admitted.existing();var allocation=admitted.allocation();
    var ownSpacing=new ContinentSpacing(coalPolicy.spacing(),List.of());var others=new ContinentSpacing(spacing,optional.selectedCenters());
    coal=existing?NativeCoalCoordinator.open(admitted.searchDirectory(),level,allocation,preset,coalPolicy,ownSpacing,others):NativeCoalCoordinator.create(admitted.searchDirectory(),level,allocation,preset,coalPolicy,ownSpacing,others);
   }
   coalProgress=coal.advance(budget);
  }
  List<MiningScanScope> mineScopes()throws IOException {
   if(!ready())throw new IllegalStateException("Complete optional and coal discovery required");
   var all=new ArrayList<>(optional.mineScopes());if(coal!=null)all.addAll(coal.mineScopes());
   return ContinentMineshafts.validated(all,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight());
  }
 }
 /** Exact native geography lookup; no artificial grid or search reroll. */
 public Lease acquireAt(int x,int z)throws IOException{checkIdentity();return acquire(geography.continent(x,z));}
 public Lease acquire(ReTerraForgedGeography.ContinentKey key)throws IOException{checkIdentity();return new Lease(cache.acquire(key));}
 public int residentCount(){return cache.residentCount();}
 /** Acquire all represented continents without yielding; failure releases this group's partial leases. */
 public Owner acquireOwner(net.minecraft.world.level.ChunkPos chunk)throws IOException{
  return prepareOwner(chunk).acquire();
 }
 /** Capture geography once; a ticket holds no resident coordinator lease between mailbox slices. */
 public OwnerTicket prepareOwner(net.minecraft.world.level.ChunkPos chunk)throws IOException{
  checkIdentity();var coverage=ContinentOwnerCoverage.sample(chunk.x,chunk.z,(x,z)->geography.continent(x,z));
  if(coverage.keys().size()>capacity)throw new IllegalStateException("Owner continent count exceeds runtime capacity");
  return new OwnerTicket(coverage);
 }
 public final class OwnerTicket {
  private final ContinentOwnerCoverage coverage;
  private OwnerTicket(ContinentOwnerCoverage coverage){this.coverage=coverage;}
  public Owner acquire()throws IOException{return acquireCovered(coverage);}
 }
 private Owner acquireCovered(ContinentOwnerCoverage coverage)throws IOException{
  checkIdentity();
  var leases=new ArrayList<Lease>();
  try{for(var key:coverage.keys())leases.add(acquire(key));return new Owner(coverage,List.copyOf(leases));}
  catch(IOException|RuntimeException|Error failure){leases.forEach(Lease::close);throw failure;}
 }
 public void requireLevel(ServerLevel supplied)throws IOException{checkIdentity();if(supplied!=level)throw new IllegalArgumentException("Different native generation level");}
 public final class Owner implements AutoCloseable {
  private final ContinentOwnerCoverage coverage;private final List<Lease> leases;private boolean released;private int next;
  private Owner(ContinentOwnerCoverage coverage,List<Lease> leases){this.coverage=coverage;this.leases=leases;}
  private List<Entry> current()throws IOException{
   checkIdentity();if(released)throw new IllegalStateException("Owner generation lease released");
   // One identity read per server-thread operation, not thousands of disk reads per discovery slice.
   return leases.stream().map(l->l.lease.value()).toList();
  }
  /** Shared bounded discovery budget; no multiply-by-continent hidden work allowance. */
  public boolean advance(int budget)throws IOException{
   var coordinators=current();if(budget<1||budget>4096)throw new IllegalArgumentException("Owner discovery budget1..4096");
   if(coalPolicy!=null){
    // One batched stage per slice, so selected coal seams are revalidated at most once
    // per slot, not once per new column. Both phases share the same search budget.
    for(var c:coordinators)if(!c.ready()){c.advance(budget);break;}
    for(var c:coordinators)if(!c.ready())return false;return true;
   }
   // A slice gives its existing total budget to one unready coordinator. Its search journal
   // durably commits the whole bounded prefix, including a prefix interrupted by a failed read.
   // Round-robin fairness remains across owner continents, without one fsync per candidate.
   for(int i=0;i<coordinators.size();i++){
    var c=coordinators.get(next);next=(next+1)%coordinators.size();
    if(!c.ready()){c.advance(budget);break;}
   }
   for(var c:coordinators)if(!c.ready())return false;return true;
  }
  public List<MiningScanScope> mineScopes()throws IOException{
   var coordinators=current();var scopes=new ArrayList<MiningScanScope>();for(var c:coordinators)scopes.addAll(c.mineScopes());
   return ContinentMineshafts.validatedAcrossContinents(scopes,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight());
  }
  public int place(net.minecraft.server.level.WorldGenRegion region,net.minecraft.world.level.chunk.ChunkAccess chunk)throws IOException{
   return placeInternal(region,chunk,null);
  }
  public int placeForSurface(net.minecraft.server.level.WorldGenRegion region,net.minecraft.world.level.chunk.ChunkAccess chunk,CinnabarOwnerPlacement.Intent intent)throws IOException{
   return placeInternal(region,chunk,Objects.requireNonNull(intent));
  }
  private int placeInternal(net.minecraft.server.level.WorldGenRegion region,net.minecraft.world.level.chunk.ChunkAccess chunk,CinnabarOwnerPlacement.Intent surface)throws IOException{
   var coordinators=current();
   for(var c:coordinators)if(!c.ready())throw new IllegalStateException("Complete owner discovery required");
   return NativeContinentCoordinator.placeOwners(region,chunk,coordinators.stream().map(c->c.optional).toList(),coverage,coalPolicy==null?List.of():coordinators.stream().map(c->c.coal).filter(Objects::nonNull).toList(),surface);
  }
  public List<ReTerraForgedGeography.ContinentKey> continents()throws IOException{current();return coverage.keys();}
  @Override public void close(){thread();if(!released){released=true;leases.forEach(Lease::close);}}
 }
 public final class Lease implements AutoCloseable {
  private final ContinentCoordinatorCache<ReTerraForgedGeography.ContinentKey,Entry>.Lease lease;
  private Lease(ContinentCoordinatorCache<ReTerraForgedGeography.ContinentKey,Entry>.Lease lease){this.lease=lease;}
  private Entry entry()throws IOException{checkIdentity();return lease.value();}
  private NativeContinentCoordinator current()throws IOException{if(coalPolicy!=null)throw new IllegalStateException("Combined runtime requires owner admission, not optional-only access");return entry().optional;}
  public NativeContinentCoordinator.Progress advance(int budget)throws IOException{return current().advance(budget);}
  /** Optional-family lookup only; coal's separate commissioning is never implied by this observation. */
  public NativeContinentCoordinator.LocateResult locate(String family)throws IOException{return entry().optional.locate(family);}
  public NativeContinentCoordinator.Progress advanceOptionalLocate(int budget)throws IOException{return entry().optional.advance(budget);}
  public Map<String,ContinentOccurrenceLedger.Candidate> surveyLocations()throws IOException{return entry().optional.surveyLocations();}
  /** Observation only: no terrain reads, cursor advancement or new occurrence decisions. */
  public Map<String,NativeContinentCoordinator.SearchDiagnostics> diagnostics()throws IOException{return current().diagnostics();}
  public List<MiningScanScope> mineScopes()throws IOException{return entry().mineScopes();}
  public Map<Long,List<String>> ownerIndex()throws IOException{return current().ownerIndex();}
  public MiningScanScope miningScope(String family)throws IOException{return current().miningScope(family);}
  public Map<String,List<net.minecraft.core.BlockPos>> ownerReservations(net.minecraft.world.level.ChunkPos owner)throws IOException{return current().ownerReservations(owner);}
  public Map<String,String> ownerProvenanceKeys(net.minecraft.world.level.ChunkPos owner)throws IOException{return current().ownerProvenanceKeys(owner);}
  public int placeOwner(net.minecraft.server.level.WorldGenRegion region,net.minecraft.world.level.chunk.ChunkAccess owner)throws IOException{return current().placeOwner(region,owner);}
  @Override public void close(){lease.close();}
 }
 @Override public void close(){cache.close();}
}
