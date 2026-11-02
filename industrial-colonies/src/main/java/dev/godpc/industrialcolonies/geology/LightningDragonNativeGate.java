package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.QuartPos;
import net.minecraft.tags.BiomeTags;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import dev.godpc.industrialcolonies.worldgen.SurfaceStructureTerrain;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;

/** Opt-in, native-generator candidate allocation. A candidate allocation is not successful placement.
 * No chunks, entities, orbit state or saved terrain are written by this gate. */
public final class LightningDragonNativeGate {
 private static final Set<String> IDS=Set.of("iceandfire:lightning_dragon_cave","iceandfire:lightning_dragon_roost");
 private static final Map<RandomState,Binding> LEVELS=new ConcurrentHashMap<>();
 private static final class LocalPolicy {static final com.google.gson.JsonObject DATA=GeologyConfig.externalOrBundled("lightning_spawn_rules.json");}
 private static com.google.gson.JsonObject localRules(){return GeologyConfig.bool(LocalPolicy.DATA,"enabled",false)?LocalPolicy.DATA:GeologyConfig.object(GeologyConfig.get().settings(),"worldStartDragons");}
 private LightningDragonNativeGate(){}
 public static boolean enabled(){return GeologyConfig.bool(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartDragons"),"enabled",false);}
 public static void load(ServerLevel level){
  if(level.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return;
  if(!enabled()||!level.dimension().location().toString().equals("minecraft:overworld"))return;
  if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread native dragon binding required");
  var binding=new Binding(level);
  if(LEVELS.putIfAbsent(level.getChunkSource().randomState(),binding)!=null)throw new IllegalStateException("Dragon native level already bound");
 }
 public static void unload(ServerLevel level){LEVELS.remove(level.getChunkSource().randomState());}
 public static void clear(){LEVELS.clear();}
 public record AllocationView(ReTerraForgedGeography.ContinentKey continent,int allowance,Set<String> selectedSites) {}
 public record PlanDiagnostics(long examined,long mountainCandidates,long nativePlacement,long stubRejected,long pieceRejected,long terrainRejected,String firstRejected){}
 public static PlanDiagnostics inspectDiagnostics(ServerLevel level,int x,int z){
  var binding=LEVELS.get(level.getChunkSource().randomState());
  if(binding==null||binding.level!=level)throw new IllegalStateException("Exact bound native level required");
  var key=binding.geography.continent(x,z);if(binding.localBiomeMode()){binding.localPlan(key);return new PlanDiagnostics(0,0,0,0,0,0,"local biome mode: no remote viability probes");}binding.plan(key);return binding.diagnostics.get(key);
 }
 /** Read-only observability; does not admit an arbitrary supplied candidate or change the allowance. */
 public static AllocationView inspect(ServerLevel level,int x,int z){
  var binding=LEVELS.get(level.getChunkSource().randomState());
  if(binding==null||binding.level!=level)throw new IllegalStateException("Exact bound native level required");
  var key=binding.geography.continent(x,z);
  var scope=new WorldStartAllocation.Scope(level.getSeed(),level.dimension().location().toString(),binding.preset,key);
  return new AllocationView(key,WorldStartAllocation.lightningCount(scope),binding.localBiomeMode()?binding.localPlan(key):binding.plan(key));
 }
 public static boolean allows(Structure structure,RegistryAccess access,RandomState random,ChunkPos chunk){
  if(!enabled())return true;
  var id=access.registryOrThrow(Registries.STRUCTURE).getKey(structure);
  if(id==null||!IDS.contains(id.toString()))return true;
  var binding=LEVELS.get(random);
  // Deliberately do not manufacture Earth identity in another dimension or before lifecycle admission.
  if(binding==null)return false;
  if(binding.localBiomeMode()){
   int x=chunk.getMiddleBlockX(),z=chunk.getMiddleBlockZ();
   var generator=binding.level.getChunkSource().getGenerator();
   var rules=localRules();
   int minimum=GeologyConfig.integer(rules,"minimumSurfaceY",500);
   if(minimum<200||minimum>=binding.level.getMaxBuildHeight())throw new IllegalArgumentException("Dragon minimum surface height outside native build range");
   int surface=NativeAccurateTerrain.query(binding.level,()->generator.getBaseHeight(x,z,net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE_WG,binding.level,random))-1;
   if(surface<minimum)return false;
   var biome=generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(x),QuartPos.fromBlock(surface+1),QuartPos.fromBlock(z),random.sampler());
   String biomeId=biome.unwrapKey().map(k->k.location().toString()).orElse("");
   double maximum=GeologyConfig.number(rules,"maximumBaseTemperature",1.0);
   if(!Double.isFinite(maximum)||maximum<0||maximum>1.0)throw new IllegalArgumentException("Cold/temperate dragon temperature must be0..1");
   if((!biome.is(BiomeTags.IS_MOUNTAIN)&&!GeologyConfig.families(biomeId).contains("mountain_highland"))||biome.value().getBaseTemperature()>maximum)return false;
   return binding.localPlan(binding.geography.continent(x,z)).contains(identity(id.toString(),chunk));
  }
  var geography=binding.geography.sample(chunk.getMiddleBlockX(),chunk.getMiddleBlockZ());
  if(!geography.mountain())return false;
  return binding.plan(geography.continent()).contains(identity(id.toString(),chunk));
 }
 private static String identity(String id,ChunkPos pos){return id+"/"+pos.x+"/"+pos.z;}
 private static final class Binding {
  final ServerLevel level;final ReTerraForgedGeography geography;final ContinentEnvelope.Parameters envelope;final String preset;
  final Map<ReTerraForgedGeography.ContinentKey,Set<String>> plans=new ConcurrentHashMap<>();
  final Map<ReTerraForgedGeography.ContinentKey,PlanDiagnostics> diagnostics=new ConcurrentHashMap<>();
  Binding(ServerLevel level){
   this.level=level;var state=level.getChunkSource().randomState();
   geography=ReTerraForgedGeography.fromRandomState(state);envelope=ReTerraForgedContinentEnvelope.read(state);
   preset=WorldStartPresetIdentity.fingerprint(level);
  }
  boolean localBiomeMode(){return GeologyConfig.string(localRules(),"mode","native-mountain-v1").equals("biome-climate-v1");}
  /** Stable potential-site ranking only. No remote terrain, biome or native-start probes.
   * The unchanged native structure pipeline and local climate decide actual placement.
   * Thus the allowance is a cap, never a guarantee that all allocated sites are viable. */
  Set<String> localPlan(ReTerraForgedGeography.ContinentKey key){
   var known=plans.get(key);if(known!=null)return known;
   var scope=new WorldStartAllocation.Scope(level.getSeed(),level.dimension().location().toString(),preset,key);
   int allowance=WorldStartAllocation.lightningCount(scope);
   if(allowance==0){plans.putIfAbsent(key,Set.of());return Set.of();}
   var window=ContinentEnvelope.around(key,envelope);
   var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
   var candidates=new HashMap<String,ChunkPos>();long examined=0;
   for(var set:registry){
    var entries=set.structures().stream().filter(e->e.structure().unwrapKey().map(k->IDS.contains(k.location().toString())).orElse(false)).toList();
    if(entries.isEmpty())continue;
    if(!(set.placement() instanceof RandomSpreadStructurePlacement p))throw new IllegalStateException("Unqualified Lightning placement type");
    int firstX=Math.floorDiv(Math.floorDiv(window.minX(),16),p.spacing()),lastX=Math.floorDiv(Math.floorDiv(window.maxX(),16),p.spacing());
    int firstZ=Math.floorDiv(Math.floorDiv(window.minZ(),16),p.spacing()),lastZ=Math.floorDiv(Math.floorDiv(window.maxZ(),16),p.spacing());
    long count=((long)lastX-firstX+1)*((long)lastZ-firstZ+1);
    if(count<0||(examined+=count)>65536)throw new IllegalStateException("Dragon potential grid exceeds work bound");
    for(int rz=firstZ;rz<=lastZ;rz++)for(int rx=firstX;rx<=lastX;rx++){
     var pos=p.getPotentialStructureChunk(level.getSeed(),Math.multiplyExact(rx,p.spacing()),Math.multiplyExact(rz,p.spacing()));
     int x=pos.getMiddleBlockX(),z=pos.getMiddleBlockZ();
     if(!window.contains(x,z)||!geography.continent(x,z).equals(key))continue;
     for(var entry:entries){String id=entry.structure().unwrapKey().orElseThrow().location().toString();
      if(candidates.putIfAbsent(identity(id,pos),pos)!=null)throw new IllegalStateException("Duplicate Lightning potential site");
     }
    }
   }
   var ordered=new ArrayList<>(candidates.keySet());ordered.sort(Comparator.<String>comparingDouble(id->WorldStartAllocation.unit(scope,"lightning-site",id)).thenComparing(id->id));
   var selected=new HashSet<String>();var occupied=new HashSet<Long>();
   for(var id:ordered){if(selected.size()==allowance)break;if(occupied.add(candidates.get(id).toLong()))selected.add(id);}
   if(plans.size()>512){plans.clear();diagnostics.clear();}
   var result=Set.copyOf(selected);plans.putIfAbsent(key,result);return plans.get(key);
  }
  Set<String> plan(ReTerraForgedGeography.ContinentKey key){
   var known=plans.get(key);if(known!=null)return known;
   var scope=new WorldStartAllocation.Scope(level.getSeed(),level.dimension().location().toString(),preset,key);
   if(WorldStartAllocation.lightningCount(scope)==0){diagnostics.putIfAbsent(key,new PlanDiagnostics(0,0,0,0,0,0,""));plans.putIfAbsent(key,Set.of());return Set.of();}
   var window=ContinentEnvelope.around(key,envelope);var sites=new ArrayList<WorldStartAllocation.DragonSite>();
   var stats=new Stats();
   var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
   Set<String> seen=new HashSet<>();long examined=0;
   for(var set:registry){
    var entries=set.structures().stream().filter(e->e.structure().unwrapKey().map(k->IDS.contains(k.location().toString())).orElse(false)).toList();
    if(entries.isEmpty())continue;
    if(!(set.placement() instanceof RandomSpreadStructurePlacement p))throw new IllegalStateException("Unqualified Lightning placement type");
    int firstX=Math.floorDiv(Math.floorDiv(window.minX(),16),p.spacing()),lastX=Math.floorDiv(Math.floorDiv(window.maxX(),16),p.spacing());
    int firstZ=Math.floorDiv(Math.floorDiv(window.minZ(),16),p.spacing()),lastZ=Math.floorDiv(Math.floorDiv(window.maxZ(),16),p.spacing());
    long count=((long)lastX-firstX+1)*((long)lastZ-firstZ+1);
    if(count<0||examined+count>65536)throw new IllegalStateException("Dragon native candidate envelope exceeds qualified work budget: set="+registry.getKey(set)+", spacing="+p.spacing()+", count="+count+", previous="+examined+", radius="+window.unclippedRadius());
    examined+=count;
    for(int rz=firstZ;rz<=lastZ;rz++)for(int rx=firstX;rx<=lastX;rx++){
     var pos=p.getPotentialStructureChunk(level.getSeed(),Math.multiplyExact(rx,p.spacing()),Math.multiplyExact(rz,p.spacing()));
     int x=pos.getMiddleBlockX(),z=pos.getMiddleBlockZ();if(!window.contains(x,z))continue;
     // The qualified identity-only reader excludes foreign continents without
     // creating their processed terrain tiles. Retain full native terrain checks
     // for every candidate belonging to this exact continent.
     if(!geography.continent(x,z).equals(key))continue;
     var sample=geography.sample(x,z);if(!sample.mountain()||!sample.continent().equals(key))continue;
     stats.mountainCandidates++;
     // Native village-exclusion scans are expensive. Apply the cheap exact geography filters first;
     // this changes evaluation order only, never candidate eligibility or the quota.
     if(!p.isStructureChunk(level.getChunkSource().getGeneratorState(),pos.x,pos.z))continue;
     stats.nativePlacement++;
     for(var entry:entries){String id=entry.structure().unwrapKey().orElseThrow().location().toString(),identity=identity(id,pos);
      if(!seen.add(identity))throw new IllegalStateException("Duplicate Lightning candidate from independent structure sets");
      sites.add(new WorldStartAllocation.DragonSite(identity,x,z,true,key));
     }
    }
   }
   var selected=new HashSet<String>();for(var site:WorldStartAllocation.lightningSites(scope,sites,site->eligibleStart(site,stats)))selected.add(site.identity());
   var result=Set.copyOf(selected);
   if(plans.size()>512){plans.clear();diagnostics.clear();}
   diagnostics.putIfAbsent(key,new PlanDiagnostics(examined,stats.mountainCandidates,stats.nativePlacement,stats.stubRejected,stats.pieceRejected,stats.terrainRejected,stats.firstRejected));
   plans.putIfAbsent(key,result);return plans.getOrDefault(key,result);
  }
  static final class Stats {long mountainCandidates,nativePlacement,stubRejected,pieceRejected,terrainRejected;String firstRejected="";void reject(String id){if(firstRejected.isEmpty())firstRejected=id;}}
  boolean eligibleStart(WorldStartAllocation.DragonSite site,Stats stats){
   String[] parts=site.identity().split("/");var chunk=new ChunkPos(Integer.parseInt(parts[1]),Integer.parseInt(parts[2]));
   var access=level.registryAccess();var structure=access.registryOrThrow(Registries.STRUCTURE).get(ResourceLocation.parse(parts[0]));
   if(structure==null)throw new IllegalStateException("Selected native dragon structure disappeared");
   var generator=level.getChunkSource().getGenerator();var random=level.getChunkSource().randomState();
   var context=new Structure.GenerationContext(access,generator,generator.getBiomeSource(),random,level.getStructureManager(),level.getSeed(),chunk,level,structure.biomes()::contains);
   var stub=structure.findValidGenerationPoint(context);if(stub.isEmpty()){stats.stubRejected++;stats.reject(site.identity());return false;}
   var start=new StructureStart(structure,chunk,0,stub.get().getPiecesBuilder().build());
   if(!start.isValid()){stats.pieceRejected++;stats.reject(site.identity());return false;}
   boolean allowed=!SurfaceStructureTerrain.shouldCheck(structure,access)
       ||SurfaceStructureTerrain.fits(start,generator,random,level)&&SurfaceStructureTerrain.summitFits(start,access,generator,random,level);
   if(!allowed){stats.terrainRejected++;stats.reject(site.identity());}return allowed;
  }
 }
}
