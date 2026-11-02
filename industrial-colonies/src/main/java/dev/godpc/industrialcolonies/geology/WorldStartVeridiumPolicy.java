package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.WorldGenLevel;

/** Optional giant host inside the existing finite owner, never a second recoverable reserve. */
public final class WorldStartVeridiumPolicy {
 public static final String FAMILY="veridium";
 public static final String ORE="allthemodium:vibranium_ore";
 private WorldStartVeridiumPolicy(){}
 public static boolean enabled(GeologyConfig.Config config){
  return GeologyConfig.bool(GeologyConfig.object(config.settings(),"worldStartVeridium"),"enabled",false);
 }
 public static void validate(GeologyConfig.Config config){
  var definitions=GeologyConfig.array(config.deposits(),"deposits").asList().stream().map(e->e.getAsJsonObject())
    .filter(d->GeologyConfig.string(d,"id","").equals(FAMILY)).toList();
  if(definitions.size()!=1)throw new IllegalArgumentException("Exactly one giant Veridium definition required");
  var d=definitions.getFirst();
  if(!GeologyConfig.string(d,"hostRock","").equals("create:veridium")
    ||GeologyConfig.number(d,"baseWeight",-1)!=0
    ||GeologyConfig.integer(d,"normalSizeMin",0)!=50000||GeologyConfig.integer(d,"normalSizeMax",0)!=100000
    ||!d.has("canSpawnMineshaft")||!d.get("canSpawnMineshaft").isJsonPrimitive()
    ||!d.getAsJsonPrimitive("canSpawnMineshaft").isBoolean()||d.get("canSpawnMineshaft").getAsBoolean()
    ||!GeologyConfig.array(d,"richOres").isEmpty()||!GeologyConfig.array(d,"associated").isEmpty()
    ||!GeologyConfig.array(d,"hardBiomeExclusions").isEmpty()||!GeologyConfig.array(d,"hardTerrainExclusions").isEmpty()
    ||!GeologyConfig.object(d,"biomeWeights").entrySet().isEmpty()
    ||!GeologyConfig.array(GeologyConfig.object(d,"placement"),"requiredSurfaceFamilies").isEmpty()
    ||GeologyConfig.bool(GeologyConfig.object(d,"micro"),"enabled",true))
   throw new IllegalArgumentException("Giant Veridium needs its exact host, no mines/micro/rich/associated fallback");
 }
 public static Optional<NativeContinentCoordinator.Family> family(long seed,String dimension,String preset,
   ReTerraForgedGeography.ContinentKey continent){
  var allocation=WorldStartAllocation.veridium(new WorldStartAllocation.Scope(seed,dimension,preset,continent));
  // The deterministic allocation is already bound to seed/preset/continent. An absent host
  // has no second occurrence roll or search, and is excluded from the legacy writer globally.
  if(!allocation.present())return Optional.empty();
  return Optional.of(new NativeContinentCoordinator.Family(FAMILY,allocation.hostBlocks(),0,0x564552494449554dL,1));
 }
 public static void bindDefinition(JsonObject definition,long seed,String dimension,String preset,
   ReTerraForgedGeography.ContinentKey continent,int cells){
  var selected=WorldStartAllocation.veridium(new WorldStartAllocation.Scope(seed,dimension,preset,continent));
  if(!selected.present()||selected.hostBlocks()!=cells)throw new IllegalArgumentException("Giant host differs from saved scope allocation");
  definition.addProperty("worldStartVeridiumOreBlocks",selected.oreBlocks());
 }
 public static boolean isPlan(GeologyPlanner.Plan plan){return plan.id().equals(FAMILY)&&plan.definition().has("worldStartVeridiumOreBlocks");}
 public static int placeOre(WorldGenLevel level,GeologyPlanner.Plan plan,List<BlockPos> geometry,List<BlockPos> actual){
  int quota=plan.definition().get("worldStartVeridiumOreBlocks").getAsInt();
  if(quota<0||quota>5||geometry.size()!=plan.intendedSize()||geometry.size()<50000||geometry.size()>100000)
   throw new IllegalArgumentException("Bounded giant host and whole-formation ore quota required");
  var id=ResourceLocation.parse(ORE);
  if(!BuiltInRegistries.BLOCK.containsKey(id))throw new IllegalStateException("Missing actual Vibranium ore block");
  var ore=BuiltInRegistries.BLOCK.get(id).defaultBlockState();
  var written=Set.copyOf(actual);
  // Rank the complete saved geometry, never round an ore quota independently per chunk.
  var order=Comparator.<BlockPos>comparingLong(p->GeologyMath.mix(p.asLong()^plan.candidate().seed()^0x56494252414e4955L))
    .thenComparingInt(BlockPos::getX).thenComparingInt(BlockPos::getY).thenComparingInt(BlockPos::getZ);
  int placed=0;
  for(var p:geometry.stream().sorted(order).limit(quota).toList())if(written.contains(p)){
   if(!level.setBlock(p,ore,2))throw new IllegalStateException("Failed selected finite Vibranium ore write");
   placed++;
  }
  return placed;
 }
}
