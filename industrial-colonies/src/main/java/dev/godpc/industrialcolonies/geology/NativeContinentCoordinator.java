package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.io.*;
import java.util.*;

/** Staged optional-family generation barrier. No event registration or automatic commissioning.
 * Resolve in a fixed seeded order; no owner index is visible until all specified families finish.
 * Coal/cinnabar must be coordinated separately before a production generation barrier can release. */
public final class NativeContinentCoordinator {
    public record Family(String id,int reserve,int initialY,long shapeSalt,double chance,
            ContinentReservePolicy.BiomeChances biomeChances,String sourcePolicy){
        public Family(String id,int reserve,int initialY,long shapeSalt,double chance){this(id,reserve,initialY,shapeSalt,chance,null,"");}
        public Family {
            if(id==null||!id.matches("[a-z0-9_]+")||id.equals("coal")||id.equals("cinnabar")
                    ||reserve<1||reserve>FiniteOreLimits.MAX_BLOCKS||!Double.isFinite(chance)||chance<0||chance>1)
                throw new IllegalArgumentException("Explicit optional family and finite reserve/probability required");
            Objects.requireNonNull(sourcePolicy);
            if(!sourcePolicy.isEmpty()&&!sourcePolicy.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Source policy fingerprint");
        }
    }
    /** No implicit biome mapping or fitting height. Catalog and every caller choice bind the saved scope. */
    public static List<Family> catalogFamilies(ContinentResourceCatalog catalog,ContinentResourceDecision.Scope scope,
            ReTerraForgedGeography.ContinentKey continent,Map<String,ContinentReservePolicy.BiomeChances> chances,
            Map<String,Integer> initialHeights){
        var heights=Map.copyOf(initialHeights);
        if(!heights.keySet().equals(catalog.familyIds()))throw new IllegalArgumentException("Exact initial-height coverage required");
        return catalog.requests(scope,continent,chances).stream().map(r->{var s=r.reserve();
            return new Family(s.family(),s.oreBlocks(),heights.get(s.family()),s.shapeSalt(),0,r.chances(),catalog.policySha256());}).toList();
    }
    public enum Status { SEARCHING, READY, HELD }
    public record Progress(Status status,int resolved,int families,Map<String,NativeContinentDiscovery.Status> decisions){}
    public record SearchDiagnostics(long reads,long foreignContinent,long habitatRejected,long formationRejected){}
    private final ServerLevel level;private final Path directory;private final ReTerraForgedGeography.ContinentKey continent;
    private final String preset,scope;private final List<Family> families;private final int spacing;
    private final GeologyConfig.Config config;
    private ContinentCoordinatorManifest manifest;private ContinentOccurrenceLedger ledger;
    private final Map<String,NativeContinentDiscovery> discoveries=new LinkedHashMap<>();
    private final Map<String,NativeContinentCandidateQualifier> qualifiers=new LinkedHashMap<>();
    private final Map<String,NativeContinentDiscovery.Progress> resolved=new LinkedHashMap<>();
    private final Map<String,MiningScanScope> mineScopeCache=new HashMap<>();
    private final List<ContinentSpacing.Center> centers=new ArrayList<>();
    private Map<Long,List<String>> ownerIndex;private boolean held;
    private final boolean nativeSkipped;
    private final Object originalRandomState;
    private final ReTerraForgedGeography skipProof;

    private NativeContinentCoordinator(Path directory,ServerLevel level,ReTerraForgedGeography.ContinentKey continent,
            String preset,List<Family> supplied,int spacing){
        this(directory,level,continent,preset,supplied,spacing,false);
    }
    private NativeContinentCoordinator(Path directory,ServerLevel level,ReTerraForgedGeography.ContinentKey continent,
            String preset,List<Family> supplied,int spacing,boolean nativeSkipped){
        this.directory=directory.toAbsolutePath().normalize();this.level=Objects.requireNonNull(level);checkThread();
        this.continent=Objects.requireNonNull(continent);this.preset=preset;this.spacing=spacing;
        if(!"minecraft:overworld".equals(level.dimension().location().toString())||preset==null||!preset.matches("[a-f0-9]{64}")
                ||supplied.isEmpty()!=nativeSkipped||supplied.size()>128)throw new IllegalArgumentException("Earth coordinator scope required");
        this.nativeSkipped=nativeSkipped;originalRandomState=level.getChunkSource().randomState();
        skipProof=nativeSkipped?ReTerraForgedGeography.fromRandomState(originalRandomState):null;
        if(nativeSkipped&&!skipProof.skipped(continent))throw new IllegalArgumentException("Native generator did not skip this region");
        new ContinentSpacing(spacing,List.of());
        var sorted=new ArrayList<>(supplied);
        sorted.sort((a,b)->{int c=Long.compareUnsigned(GeologyMath.mix(level.getSeed()^a.id().hashCode()),GeologyMath.mix(level.getSeed()^b.id().hashCode()));return c!=0?c:a.id().compareTo(b.id());});
        families=List.copyOf(sorted);
        if(families.stream().map(Family::id).distinct().count()!=families.size())throw new IllegalArgumentException("Duplicate family");
        var source=GeologyConfig.get();config=new GeologyConfig.Config(source.settings().deepCopy(),source.biomes().deepCopy(),source.deposits().deepCopy());
        Set<String> known=new HashSet<>();for(var d:GeologyConfig.array(config.deposits(),"deposits"))known.add(d.getAsJsonObject().get("id").getAsString());
        for(var f:families)if(!known.contains(f.id())||f.initialY()<level.getMinBuildHeight()||f.initialY()>=level.getMaxBuildHeight())throw new IllegalArgumentException("Unknown family or invalid initial height");
        scope=hash("native-continent-coordinator/v4\n"+level.getSeed()+"\n"+preset+"\n"+continent+"\n"+spacing+"\n"+families+"\n"+config);
        if(nativeSkipped)ownerIndex=Map.of();
    }
    /** Empty in-memory routing only after native branch proof. Never commissions or rewrites saved decisions. */
    static NativeContinentCoordinator skipped(Path directory,ServerLevel level,ReTerraForgedGeography.ContinentKey key,String preset,int spacing){
        return new NativeContinentCoordinator(directory,level,key,preset,List.of(),spacing,true);
    }
    boolean skipped(){return nativeSkipped;}
    public static NativeContinentCoordinator create(Path directory,ServerLevel level,ReTerraForgedGeography.ContinentKey continent,
            String preset,List<Family> families,int spacing)throws IOException{
        var c=new NativeContinentCoordinator(directory,level,continent,preset,families,spacing);
        Files.createDirectory(c.directory); // Existing or interrupted commissioning must not reset.
        c.ledger=ContinentOccurrenceLedger.create(c.directory.resolve("occurrences.bin"),c.ledgerScope(),continent);
        c.manifest=ContinentCoordinatorManifest.create(c.directory.resolve("coordinator.bin"),c.scope,c.families.size());return c;
    }
    public static NativeContinentCoordinator open(Path directory,ServerLevel level,ReTerraForgedGeography.ContinentKey continent,
            String preset,List<Family> families,int spacing)throws IOException{
        var c=new NativeContinentCoordinator(directory,level,continent,preset,families,spacing);
        c.manifest=ContinentCoordinatorManifest.open(c.directory.resolve("coordinator.bin"),c.scope,c.families.size());
        c.ledger=ContinentOccurrenceLedger.open(c.directory.resolve("occurrences.bin"),c.ledgerScope(),continent);return c;
    }
    private ContinentResourceDecision.Scope ledgerScope(){return new ContinentResourceDecision.Scope(level.getSeed(),level.dimension().location().toString(),preset);}
    private void checkThread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");}
    private void checkScope()throws IOException{
        checkThread();if(!config.equals(GeologyConfig.get()))throw new IOException("Coordinator configuration changed");
        if(nativeSkipped){
            if(originalRandomState!=level.getChunkSource().randomState()||!skipProof.skipped(continent))throw new IOException("Native skipped-region authority changed");
            return;
        }
        int started=manifest.started();var saved=ledger.snapshot();Set<String> commissioned=new HashSet<>();
        for(int i=0;i<started;i++)commissioned.add(families.get(i).id());
        if(!commissioned.containsAll(saved.keySet()))throw new IOException("Occurrence outside commissioned family prefix");
        for(var e:resolved.entrySet()){
            var old=e.getValue().occurrence().orElse(null);
            if(!Objects.equals(old,saved.get(e.getKey())))throw new IOException("Resolved occurrence changed");
            if(!Files.isRegularFile(journal(e.getKey())))throw new IOException("Resolved search journal missing");
        }
    }
    private Path journal(String family){return directory.resolve("search-"+family+".bin");}
    public Progress advance(int budget)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Coordinator budget1..4096");
        checkScope();if(held)return progress();
        int remaining=budget;
        while(remaining>0&&resolved.size()<families.size()){
            int index=resolved.size();Family family=families.get(index);
            NativeContinentDiscovery discovery=discoveries.get(family.id());
            if(discovery==null){
                var qualifier=new NativeContinentCandidateQualifier(level,continent,preset,family.id(),family.reserve(),family.initialY(),family.shapeSalt(),new ContinentSpacing(spacing,centers),ContinentCandidateSearch.Traversal.LOCAL_V3,family.biomeChances(),family.sourcePolicy());
                int started=manifest.started();Path path=journal(family.id());
                if(started==index){
                    if(Files.exists(path))throw new IOException("Uncommissioned family journal already exists");
                    manifest.start(index); // Durable intent before first cursor file; missing started files hold.
                    discovery=NativeContinentDiscovery.create(path,qualifier,ledger,family.chance());
                }else{
                    if(started<index)throw new IOException("Commissioning prefix is behind resolved families");
                    discovery=NativeContinentDiscovery.open(path,qualifier,ledger,family.chance());
                }
                discoveries.put(family.id(),discovery);
                qualifiers.put(family.id(),qualifier);
            }
            long before=discovery.visited();
            var result=discovery.advance(remaining);
            long consumed=result.search().visited()-before;
            if(consumed<0||consumed>remaining)throw new IllegalStateException("Native discovery exceeded shared candidate budget");
            // Reopening a terminal selection revalidates one original site without advancing its cursor.
            remaining-=Math.max(1,(int)consumed);
            if(result.status()==NativeContinentDiscovery.Status.HELD){held=true;break;}
            if(result.status()==NativeContinentDiscovery.Status.SEARCHING)break;
            resolved.put(family.id(),result);
            if(result.status()==NativeContinentDiscovery.Status.PRESENT){var p=result.plan().orElseThrow().candidate();centers.add(new ContinentSpacing.Center(family.id(),p.x(),p.z()));}
        }
        if(!held&&resolved.size()==families.size()&&ownerIndex==null)ownerIndex=buildIndex();
        return progress();
    }
    /** Read-only committed selection observation. Does not expose owner/placement authority. */
    public record LocateResult(String state,ContinentOccurrenceLedger.Candidate candidate) {}
    /** One scope validation for the automatic survey; observations are committed plans only. */
    public Map<String,ContinentOccurrenceLedger.Candidate> surveyLocations()throws IOException{
        checkScope();if(held)throw new IOException("Continent discovery held");
        var result=new TreeMap<String,ContinentOccurrenceLedger.Candidate>();
        for(var e:resolved.entrySet())if(e.getValue().status()==NativeContinentDiscovery.Status.PRESENT)
            result.put(e.getKey(),e.getValue().occurrence().orElseThrow().request().candidate());
        return Map.copyOf(result);
    }
    public LocateResult locate(String family)throws IOException{
        checkScope();if(held)throw new IOException("Continent discovery held; locate refuses stale results");
        if(families.stream().noneMatch(f->f.id().equals(family)))return new LocateResult("NO_ALLOCATION",null);
        var result=resolved.get(family);if(result==null)return new LocateResult("SEARCHING",null);
        if(result.status()==NativeContinentDiscovery.Status.PRESENT)return new LocateResult("PRESENT",result.occurrence().orElseThrow().request().candidate());
        return new LocateResult(result.status().name(),null);
    }
    public Progress progress(){
        checkThread();var states=new LinkedHashMap<String,NativeContinentDiscovery.Status>();resolved.forEach((k,v)->states.put(k,v.status()));
        return new Progress(held?Status.HELD:ownerIndex!=null?Status.READY:Status.SEARCHING,resolved.size(),families.size(),Collections.unmodifiableMap(states));
    }
    public Map<String,SearchDiagnostics> diagnostics(){
        checkThread();var result=new LinkedHashMap<String,SearchDiagnostics>();
        qualifiers.forEach((id,q)->result.put(id,new SearchDiagnostics(q.reads(),q.foreign(),q.habitat(),q.noFit())));
        return Map.copyOf(result);
    }
    /** Immutable family IDs only; mutable caller plans can never change owner routing. */
    public Map<Long,List<String>> ownerIndex()throws IOException{
        checkScope();if(held||ownerIndex==null)throw new IllegalStateException("All optional families must finish before owner routing");return ownerIndex;
    }
    /** Frozen resolved centers for the later guaranteed-coal spacing stage. */
    public List<ContinentSpacing.Center> selectedCenters()throws IOException {ownerIndex();return List.copyOf(centers);}
    public int placeOwner(WorldGenRegion region,ChunkAccess owner)throws IOException{
        return placeOwners(region,owner,List.of(this),null);
    }
    /** One chunk ledger for all admitted border continents; no coordinator may seal it prematurely. */
    static int placeOwners(WorldGenRegion region,ChunkAccess owner,List<NativeContinentCoordinator> coordinators,
            ContinentOwnerCoverage coverage)throws IOException{
        return placeOwners(region,owner,coordinators,coverage,List.of());
    }
    /** Explicit combined admission: all border continents must supply their entire ready coal layout. */
    static int placeOwners(WorldGenRegion region,ChunkAccess owner,List<NativeContinentCoordinator> coordinators,
            ContinentOwnerCoverage coverage,List<NativeCoalCoordinator> coalCoordinators)throws IOException{
        return placeOwners(region,owner,coordinators,coverage,coalCoordinators,null);
    }
    /** Explicit deferred surface phase. Old callers keep immediate sealing and byte formats. */
    static int placeOwners(WorldGenRegion region,ChunkAccess owner,List<NativeContinentCoordinator> coordinators,
            ContinentOwnerCoverage coverage,List<NativeCoalCoordinator> coalCoordinators,CinnabarOwnerPlacement.Intent surface)throws IOException{
        if(coordinators.isEmpty()||coordinators.size()>64)throw new IllegalArgumentException("Bounded coordinator group required");
        if(!coalCoordinators.isEmpty()&&(coverage==null||coalCoordinators.size()!=coordinators.stream().filter(c->!c.skipped()).count()))throw new IllegalArgumentException("Complete coal/optional owner coverage required");
        if(coverage!=null&&(owner.getPos().x!=coverage.chunkX()||owner.getPos().z!=coverage.chunkZ()))throw new IllegalArgumentException("Coverage belongs to another owner");
        record Placement(NativeContinentCoordinator coordinator,List<String> families){}
        var work=new ArrayList<Placement>();var continents=new HashSet<ReTerraForgedGeography.ContinentKey>();
        var occupied=new HashSet<BlockPos>();var provenance=new HashSet<String>();
        for(var c:coordinators){
            var index=c.ownerIndex();
            if(region.getLevel()!=c.level||!continents.add(c.continent))throw new IllegalArgumentException("Wrong level or duplicate continent");
            var assigned=index.getOrDefault(owner.getPos().toLong(),List.of());
            if(coverage!=null){
                var reservations=c.ownerReservations(owner.getPos());
                for(var cells:reservations.values())for(var cell:cells)
                    if(!coverage.contains(c.continent,cell.getX(),cell.getZ())||!occupied.add(cell))throw new IllegalStateException("Owner reservation crosses admitted geography or overlaps");
                for(var key:c.ownerProvenanceKeys(owner.getPos()).values())if(!provenance.add(key))throw new IllegalStateException("Duplicate owner provenance");
            }
            if(!assigned.isEmpty())work.add(new Placement(c,assigned));
        }
        if(coverage!=null&&!continents.equals(new HashSet<>(coverage.keys())))throw new IllegalStateException("Incomplete owner continent coverage");
        record CoalPlacement(NativeCoalCoordinator coordinator,List<String> slots){}
        var coalWork=new ArrayList<CoalPlacement>();var coalContinents=new HashSet<ReTerraForgedGeography.ContinentKey>();
        var coalOwners=coordinators.stream().filter(c->!c.skipped()).map(c->c.continent).collect(java.util.stream.Collectors.toSet());
        for(var coal:coalCoordinators){
            coal.requireLevel(region.getLevel());
            if(!coalOwners.contains(coal.continent())||!coalContinents.add(coal.continent()))throw new IllegalArgumentException("Wrong or duplicate coal continent");
            var reservations=coal.ownerReservations().getOrDefault(owner.getPos().toLong(),Map.of());
            for(var cells:reservations.values())for(var cell:cells)
                if(!coverage.contains(coal.continent(),cell.getX(),cell.getZ())||!occupied.add(cell))throw new IllegalStateException("Coal owner reservation crosses geography or overlaps minerals");
            for(String key:coal.ownerProvenanceKeys(owner.getPos()).values())if(!provenance.add(key))throw new IllegalStateException("Duplicate coal provenance");
            if(!reservations.isEmpty())coalWork.add(new CoalPlacement(coal,List.copyOf(reservations.keySet())));
        }
        if(!coalCoordinators.isEmpty()&&!coalContinents.equals(coalOwners))throw new IllegalStateException("Incomplete coal owner coverage");
        if(surface!=null){
            if(surface.chunkX()!=owner.getPos().x||surface.chunkZ()!=owner.getPos().z)throw new IllegalArgumentException("Foreign surface reservation owner");
            for(var voxel:surface.targets().keySet())if(!occupied.add(new BlockPos(voxel.x(),voxel.y(),voxel.z())))throw new IllegalStateException("Surface reservation overlaps underground resource");
            for(String key:surface.provenanceKeys())if(!provenance.add(key))throw new IllegalStateException("Duplicate surface provenance");
        }
        if(provenance.size()>128)throw new IllegalStateException("Owner provenance capacity exceeded before placement");
        if(work.isEmpty()&&coalWork.isEmpty()&&surface==null)return 0;
        if(owner.isUpgrading()||!owner.getPersistedStatus().isBefore(net.minecraft.world.level.chunk.status.ChunkStatus.CARVERS)
                ||!region.getCenter().equals(owner.getPos()))throw new IllegalStateException("Fresh native owner required");
        if(MassiveDeposits.enabled(GeologyConfig.get()))throw new IllegalStateException("Continent and massive generation ownership must not overlap");
        if(!MiningOreOwnership.begin(owner))throw new IllegalStateException("Existing natural provenance must not be overwritten");
        try{
            if(surface!=null){owner.getData(MiningOreOwnership.LEDGER).deferSurface(surface.identity());owner.setUnsaved(true);}
            int count=0;
            for(var p:work)for(String family:p.families())count+=GeologyFeature.placeContinentOwner(region,owner,p.coordinator().discoveries.get(family),
                    (request,actual)->MiningOreOwnership.recordContinent(owner,request,actual));
            for(var p:coalWork)for(String slot:p.slots())count+=GeologyFeature.placeCoalOwner(region,owner,p.coordinator(),slot);
            if(owner.getData(MiningOreOwnership.LEDGER).remaining()!=count)throw new IllegalStateException("Placed/provenance counts differ");
            // Nodes use one deterministic unowned position outside the finite ore geometry.
            // All overlapping resource reservations were checked above; no node requires a mineshaft.
            for(var p:work)for(String family:p.families())MiningNodes.placeIndependent(region,owner,p.coordinator().miningScope(family),occupied);
            for(var p:coalWork)for(var scope:p.coordinator().mineScopes())MiningNodes.placeIndependent(region,owner,scope,occupied);
            if(surface==null)MiningOreOwnership.seal(owner);return count;
        }catch(IOException|RuntimeException|Error failure){MiningOreOwnership.abort(owner);throw failure;}
    }
    /** Read-only finite reservations. No mutable plan/configuration escapes the coordinator. */
    public Map<String,List<BlockPos>> ownerReservations(ChunkPos owner)throws IOException{
        var index=ownerIndex();var result=new LinkedHashMap<String,List<BlockPos>>();
        var world=GeologyWorld.of(level);
        for(String family:index.getOrDefault(owner.toLong(),List.of())){
            var cells=world.shape(resolved.get(family).plan().orElseThrow()).stream()
                    .filter(p->new ChunkPos(p).equals(owner)).map(BlockPos::immutable).toList();
            if(cells.isEmpty())throw new IOException("Indexed owner has no reserved cells");
            result.put(family,cells);
        }
        return Collections.unmodifiableMap(result);
    }
    public Map<String,String> ownerProvenanceKeys(ChunkPos owner)throws IOException{
        var index=ownerIndex();var result=new LinkedHashMap<String,String>();
        for(String family:index.getOrDefault(owner.toLong(),List.of()))
            result.put(family,ContinentOreProvenance.key(resolved.get(family).occurrence().orElseThrow().request()));
        return Collections.unmodifiableMap(result);
    }
    /** Admission only; this does not create a node, authorize a drill or certify physical reserves. */
    public MiningScanScope miningScope(String family)throws IOException{
        ownerIndex();var result=resolved.get(family);
        if(result==null||result.status()!=NativeContinentDiscovery.Status.PRESENT)throw new IllegalArgumentException("Present committed family required");
        // ownerIndex() above retains thread/config/held checks; only immutable geometry is cached.
        return mineScopeCache.computeIfAbsent(family,ignored->MiningScanScope.continent(result.occurrence().orElseThrow().request(),level.getMinBuildHeight(),level.getMaxBuildHeight()));
    }
    /** Immutable snapshot for future structure-generation admission; no disk/world access is needed by fitting. */
    public List<MiningScanScope> mineScopes()throws IOException{
        ownerIndex();var scopes=new ArrayList<MiningScanScope>();
        for(var e:resolved.entrySet())if(e.getValue().status()==NativeContinentDiscovery.Status.PRESENT)scopes.add(miningScope(e.getKey()));
        return ContinentMineshafts.validated(scopes,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight());
    }
    private record Body(List<BlockPos> cells,int minX,int minY,int minZ,int maxX,int maxY,int maxZ){
        boolean overlaps(Body b){return minX<=b.maxX&&maxX>=b.minX&&minY<=b.maxY&&maxY>=b.minY&&minZ<=b.maxZ&&maxZ>=b.minZ;}
    }
    private Map<Long,List<String>> buildIndex()throws IOException{
        var result=new HashMap<Long,List<String>>();var bodies=new ArrayList<Body>();var world=GeologyWorld.of(level);
        for(var entry:resolved.entrySet())if(entry.getValue().status()==NativeContinentDiscovery.Status.PRESENT){
            var cells=world.shape(entry.getValue().plan().orElseThrow());
            if(cells.isEmpty()||cells.size()>FiniteOreLimits.MAX_BLOCKS||new HashSet<>(cells).size()!=cells.size())throw new IOException("Invalid reserved body");
            int minX=Integer.MAX_VALUE,minY=minX,minZ=minX,maxX=Integer.MIN_VALUE,maxY=maxX,maxZ=maxX;
            var owners=new HashSet<Long>();for(var p:cells){minX=Math.min(minX,p.getX());minY=Math.min(minY,p.getY());minZ=Math.min(minZ,p.getZ());maxX=Math.max(maxX,p.getX());maxY=Math.max(maxY,p.getY());maxZ=Math.max(maxZ,p.getZ());owners.add(new ChunkPos(p).toLong());}
            var body=new Body(cells,minX,minY,minZ,maxX,maxY,maxZ);
            for(var prior:bodies)if(body.overlaps(prior)){
                var seen=new HashSet<>(prior.cells());if(cells.stream().anyMatch(seen::contains))throw new IOException("Optional mineral bodies overlap");
            }
            bodies.add(body);for(long owner:owners)result.computeIfAbsent(owner,k->new ArrayList<>()).add(entry.getKey());
        }
        result.replaceAll((k,v)->List.copyOf(v));return Map.copyOf(result);
    }
    private static String hash(String text){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
}
