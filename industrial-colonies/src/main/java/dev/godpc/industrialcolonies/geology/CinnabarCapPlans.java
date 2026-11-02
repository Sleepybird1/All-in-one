package dev.godpc.industrialcolonies.geology;
import java.io.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.LevelResource;
/** Lifecycle binding; records are written by normal generation, never by an operator migration. */
public final class CinnabarCapPlans {
 private static final Map<ServerLevel,CinnabarCapStore> STORES=new ConcurrentHashMap<>();
 private CinnabarCapPlans(){}
 public static void load(ServerLevel level){
  // Superflat has no ReTerraForged context or continent-based ore ownership.
  if(level.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return;
  if(level.dimension()!=Level.OVERWORLD||!WorldStartCinnabarRuntime.localBiomeMode())return;
  String identity="CINNABAR_CAP_V3_SHARED_24\n"+level.getSeed()+"\n"+WorldStartPresetIdentity.fingerprint(level)+"\n"+GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar");
  try{STORES.put(level,new CinnabarCapStore(level.getServer().getWorldPath(LevelResource.ROOT).resolve("data/industrial_colonies/cinnabar-caps-v3"),identity));}
  catch(IOException e){org.slf4j.LoggerFactory.getLogger("IndustrialColonies/CinnabarCap").error("Cinnabar cap records refused; other chunk generation remains enabled",e);}
 }
 public static void unload(ServerLevel level){STORES.remove(level);}
 /** Suppress predictions only for actual committed generation refusals. */
 public static boolean knownRejected(ServerLevel level,int x,int z)throws IOException{
  var store=STORES.get(level);if(store==null)return false;
  var config=GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar");
  int spacing=GeologyConfig.integer(config,"localSpacing",512);double chance=GeologyConfig.number(config,"localChance",.25);
  for(int gx=Math.floorDiv(x-32,spacing);gx<=Math.floorDiv(x+32,spacing);gx++)for(int gz=Math.floorDiv(z-32,spacing);gz<=Math.floorDiv(z+32,spacing);gz++){
   var c=LocalCinnabarPattern.at(level.getSeed(),gx,gz,spacing,chance);if(c==null||Math.floorDiv(c.x(),32)!=Math.floorDiv(x,32)||Math.floorDiv(c.z(),32)!=Math.floorDiv(z,32))continue;
   var known=store.existing(new CinnabarCapStore.Request(c.key(),Math.floorDiv(c.x(),32)*2,Math.floorDiv(c.z(),32)*2,LocalCinnabarPattern.reserve(c.key())));
   if(known.isPresent())return known.get().isEmpty();
  }
  return false;
 }
 public static List<SummitCinnabarCap.Cell> select(ServerLevel level,CinnabarCapStore.Request request,Supplier<List<SummitCinnabarCap.Cell>> fit)throws IOException{
  var store=STORES.get(level);if(store==null)throw new IOException("Cap store unavailable");return store.select(request,fit);
 }
}
