package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;

/** Deterministic cross-pool candidate separation, independent of chunk request order.
 * Within-band native spacing remains authoritative. Mixed bands use the smaller band's minimum.
 * Candidate rejection can increase realized gaps; no maximum or successful terrain fit is promised. */
public final class WorldStartStructureSpacing {
 private static final Map<String,Integer> MINIMUM=Map.of("villages",800,"small",1000,"medium",2000,"large",4000,"ships",1000);
 private static final Map<RandomState,Binding> LEVELS=new ConcurrentHashMap<>();
 private WorldStartStructureSpacing(){}
 public static boolean enabled(){return GeologyConfig.bool(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartStructures"),"enabled",false);}
 public static void load(ServerLevel level){
  if(!enabled()||!level.dimension().location().toString().equals("minecraft:overworld"))return;
  var binding=new Binding(level);
  if(LEVELS.putIfAbsent(level.getChunkSource().randomState(),binding)!=null)throw new IllegalStateException("Structure spacing already bound");
 }
 public static void unload(ServerLevel level){LEVELS.remove(level.getChunkSource().randomState());}
 public static void clear(){LEVELS.clear();}
 public static boolean allows(Structure structure,RandomState random,ChunkPos chunk){
  var binding=LEVELS.get(random);if(binding==null)return true;
  String band=binding.membership.get(structure);return band==null||binding.allows(band,chunk);
 }
 /** Native fixture/operator inspection; does not create or change structure starts. */
 public static boolean inspect(ServerLevel level,String band,ChunkPos chunk){
  var binding=LEVELS.get(level.getChunkSource().randomState());
  if(binding==null||binding.level!=level||!MINIMUM.containsKey(band))throw new IllegalArgumentException("Exact bound native band required");
  return binding.allows(band,chunk);
 }
 private record Band(String name,int minimum,RandomSpreadStructurePlacement placement){}
 private static final class Binding {
  final ServerLevel level;final Map<String,Band> bands=new TreeMap<>();final Map<Structure,String> membership=new IdentityHashMap<>();
  Binding(ServerLevel level){
   this.level=level;var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
   for(var entry:MINIMUM.entrySet()){
    var set=registry.get(ResourceLocation.parse("industrial_colonies:world_start_"+entry.getKey()));
    if(set==null||!(set.placement() instanceof RandomSpreadStructurePlacement p)||(p.separation()+1)*16<entry.getValue())
     throw new IllegalStateException("Missing or insufficient native structure band: "+entry.getKey());
    bands.put(entry.getKey(),new Band(entry.getKey(),entry.getValue(),p));
    for(var row:set.structures())if(membership.put(row.structure().value(),entry.getKey())!=null)throw new IllegalStateException("Duplicate active structure band membership");
   }
   if(membership.size()!=103)throw new IllegalStateException("Expected103preserved landmark entries");
  }
  boolean allows(String name,ChunkPos here){
   var own=Objects.requireNonNull(bands.get(name));
   if(!own.placement().isStructureChunk(level.getChunkSource().getGeneratorState(),here.x,here.z))return false;
   long priority=priority(name,here);
   for(var other:bands.values()){
    if(other==own)continue;
    int distance=Math.min(own.minimum(),other.minimum()),reach=(distance+15)/16;
    var p=other.placement();
    int lx=Math.floorDiv(here.x-reach,p.spacing()),hx=Math.floorDiv(here.x+reach,p.spacing());
    int lz=Math.floorDiv(here.z-reach,p.spacing()),hz=Math.floorDiv(here.z+reach,p.spacing());
    if((long)(hx-lx+1)*(hz-lz+1)>256)throw new IllegalStateException("Cross-pool neighbor work bound exceeded");
    for(int rz=lz;rz<=hz;rz++)for(int rx=lx;rx<=hx;rx++){
     var neighbor=p.getPotentialStructureChunk(level.getSeed(),rx*p.spacing(),rz*p.spacing());
     long dx=((long)neighbor.x-here.x)*16,dz=((long)neighbor.z-here.z)*16;
     if(dx*dx+dz*dz>=(long)distance*distance||!p.isStructureChunk(level.getChunkSource().getGeneratorState(),neighbor.x,neighbor.z))continue;
     int order=Long.compareUnsigned(priority(other.name(),neighbor),priority);
     if(order<0||order==0&&other.name().compareTo(name)<0)return false;
    }
   }
   return true;
  }
  long priority(String name,ChunkPos pos){return GeologyMath.seed(level.getSeed(),pos.x,pos.z,0x5753545255435455L^name.hashCode());}
 }
}
