package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/** Persistent historical main-vein observations. Not a reserve, depletion ledger or locator.
 * Unknown/unobserved terrain suppresses clues; no chunk loads or continent discovery. */
public final class NearbyVeinClues extends SavedData {
 private static final Factory<NearbyVeinClues> FACTORY=new Factory<>(NearbyVeinClues::new,NearbyVeinClues::read);
 private static final Map<ServerLevel,NearbyVeinClues> LEVELS=new ConcurrentHashMap<>();
 private NearbyVeinIndex index=new NearbyVeinIndex();private CompoundTag rejected;
 private static final class Policy {static final com.google.gson.JsonObject DATA=GeologyConfig.externalOrBundled("vein_clues.json");}
 public static boolean enabled(){return GeologyConfig.bool(Policy.DATA,"enabled",false);}
 private static int radius(){int r=GeologyConfig.integer(Policy.DATA,"maximumDistance",2000);if(r<1||r>2000)throw new IllegalArgumentException("Matching-vein clues maximum1..2000blocks");return r;}
 private static int cinnabarRadius(){int r=GeologyConfig.integer(Policy.DATA,"cinnabarMaximumDistance",4000);if(r<1||r>4000)throw new IllegalArgumentException("Cinnabar clues maximum1..4000blocks");return r;}
 private static int radius(String family){return "cinnabar".equals(family)?cinnabarRadius():radius();}
 public static boolean scatteredSite(ServerLevel level,String family,int chunkX,int chunkZ,long seed){
  var point=nearest(level,family,chunkX*16+8,chunkZ*16+8);
  return point.isPresent()&&TraceScatterPolicy.accepts(seed,point.get().distanceSquared(),radius(family));
 }
 public static void load(ServerLevel level){
  if(!enabled())return;
  if(!level.getServer().isSameThread())throw new IllegalStateException("Clue index load requires server thread");
  radius();cinnabarRadius();LEVELS.put(level,level.getDataStorage().computeIfAbsent(FACTORY,"industrial_colonies_nearby_vein_clues"));
 }
 public static void unload(ServerLevel level){LEVELS.remove(level);}
 public static void record(ServerLevel level,String family,List<BlockPos> actual){
  if(!enabled()||actual.isEmpty())return;
  var data=LEVELS.get(level);if(data==null||data.rejected!=null)return;boolean changed=false;
  // The synchronized index must be visible before this owner's CARVERS future completes.
  // Only SavedData's dirty notification is marshalled back to the server thread.
  for(var p:actual)changed|=data.index.record(family,p.getX(),p.getZ());
  if(changed){Runnable dirty=()->{if(LEVELS.get(level)==data)data.setDirty();};
   if(level.getServer().isSameThread())dirty.run();else level.getServer().execute(dirty);}
 }
 public static Set<String> familiesInChunk(ServerLevel level,int x,int z){
  var data=LEVELS.get(level);return data==null||data.rejected!=null?Set.of():data.index.familiesInChunk(x,z);
 }
 public static Set<String> familiesNearChunk(ServerLevel level,int x,int z){
  var data=LEVELS.get(level);return data==null||data.rejected!=null?Set.of():data.index.familiesNearChunk(x,z,radius(),Map.of("cinnabar",cinnabarRadius()));
 }
 public static Optional<NearbyVeinIndex.Observation> nearest(ServerLevel level,String family,int x,int z){
  var data=LEVELS.get(level);
  return !enabled()||data==null||data.rejected!=null?Optional.empty():data.index.nearest(family,x,z,radius(family));
 }
 public static boolean allows(ServerLevel level,String family,int x,int z){
  if(!enabled())return true;var data=LEVELS.get(level);
  return data!=null&&data.rejected==null&&data.index.nearby(family,x,z,radius(family));
 }
 public static boolean allowsBlock(ServerLevel level,String block,int x,int z){
  if(!enabled())return true;
  for(var row:GeologyConfig.array(GeologyConfig.get().deposits(),"deposits")){
   var definition=row.getAsJsonObject();
   if(GeologyConfig.string(definition,"hostRock","").equals(block)&&allows(level,definition.get("id").getAsString(),x,z))return true;
  }
  return false;
 }
 private static NearbyVeinClues read(CompoundTag tag,HolderLookup.Provider registries){
  var data=new NearbyVeinClues();
  try{if(!tag.contains("index",7))throw new IllegalArgumentException("Missing clue index");data.index=NearbyVeinIndex.decode(tag.getByteArray("index"));}
  catch(Exception failure){data.rejected=tag.copy();}return data;
 }
 @Override public CompoundTag save(CompoundTag tag,HolderLookup.Provider registries){
  if(rejected!=null)return rejected.copy();
  try{tag.putByteArray("index",index.encode());return tag;}
  catch(java.io.IOException e){throw new IllegalStateException("Cannot encode clue observations",e);}
 }
}
