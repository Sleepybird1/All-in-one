package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.storage.LevelResource;

/** Explicit opt-in commissioning. No count/density default, installation or implicit old-world repair. */
public final class WorldStartCinnabarRuntime {
 private static final Map<ServerLevel,Binding> LEVELS=new ConcurrentHashMap<>();
 private WorldStartCinnabarRuntime(){}
 public static boolean enabled(){return GeologyConfig.bool(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar"),"enabled",false);}
 public static boolean localBiomeMode(){return enabled()&&GeologyConfig.string(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar"),"mode", "connected-range-v1").equals("local-biome-v1");}
 public static Optional<Binding> find(ServerLevel level){return Optional.ofNullable(LEVELS.get(level));}
 public static void load(ServerLevel level){
  // Superflat has no ReTerraForged context or continent-based ore ownership.
  if(level.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return;
  if(localBiomeMode())return; // New local decorator never commissions or reopens legacy range journals.
  if(!enabled()||!level.dimension().location().toString().equals("minecraft:overworld"))return;
  if(!level.getServer().isSameThread())throw new IllegalStateException("Cinnabar commissioning requires server thread");
  if(NativeContinentLevels.find(level).isEmpty())throw new IllegalStateException("Cinnabar requires shared native resource ownership");
  var config=GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar");
  for(String key:List.of("concentrationsPerRange","minimumY","coverage","maximumThickness","maximumWidth","maximumAnchors","maximumObservations","terrainArtifactSHA256"))
   if(!config.has(key))throw new IllegalArgumentException("Explicit cinnabar policy required: "+key);
  if(config.get("minimumY").getAsInt()!=200)throw new IllegalArgumentException("Selected cinnabar minimum isY200");
  var policy=new CinnabarConcentrations.Policy(config.get("concentrationsPerRange").getAsInt(),200,config.get("coverage").getAsDouble(),config.get("maximumThickness").getAsInt(),config.get("maximumWidth").getAsInt(),config.get("maximumAnchors").getAsInt());
  String artifact=config.get("terrainArtifactSHA256").getAsString();if(!artifact.matches("[a-f0-9]{64}"))throw new IllegalArgumentException("Independently verified terrain artifact identity required");
  var binding=new Binding(level,policy,config.get("maximumObservations").getAsInt(),artifact);
  if(LEVELS.putIfAbsent(level,binding)!=null)throw new IllegalStateException("Cinnabar already commissioned");
 }
 public static void unload(ServerLevel level){LEVELS.remove(level);}
 public static void stop(MinecraftServer server){LEVELS.keySet().removeIf(level->level.getServer()==server);}
 public static final class Binding {
  private final ServerLevel level;
  private final GeologyConfig.Config config;
  private final CinnabarConcentrations.Policy policy;
  private final String preset,artifact;
  private final int observations;
  private final Map<ChunkAccess,MountainCinnabarSources.Ticket> tickets=new WeakHashMap<>();
  private MountainCinnabarSources sources;
  private ContinentCoordinatorDirectory directory;
  private boolean failed;
  private Binding(ServerLevel level,CinnabarConcentrations.Policy policy,int observations,String artifact){
   this.level=level;this.policy=policy;this.observations=observations;this.artifact=artifact;preset=WorldStartPresetIdentity.fingerprint(level);
   new MountainRangeSurvey(new MountainRangeSurvey.Column(0,0),observations);
   var current=GeologyConfig.get();config=new GeologyConfig.Config(current.settings().deepCopy(),current.biomes().deepCopy(),current.deposits().deepCopy());
  }
  private void check()throws IOException{
   if(!level.getServer().isSameThread()||failed||!config.equals(GeologyConfig.get()))throw new IOException("Cinnabar context changed or held");
   if(directory!=null)directory.check();
  }
  public MountainCinnabarSources.Ticket ticket(ChunkAccess owner)throws IOException{
   check();try{
    if(sources==null){
     var parent=level.getServer().getWorldPath(LevelResource.ROOT).resolve("data/industrial_colonies");Files.createDirectories(parent);
     var root=parent.resolve("world-start-cinnabar-v1");
     String identity="IC_AUTOMATIC_CINNABAR_V1\n"+level.getSeed()+"\n"+level.dimension().location()+"\n"+preset+"\n"+artifact+"\n"+policy.fingerprint()+"\n"+observations;
     directory=Files.exists(root,LinkOption.NOFOLLOW_LINKS)?ContinentCoordinatorDirectory.open(root,identity):ContinentCoordinatorDirectory.create(root,identity);
     sources=new MountainCinnabarSources(level,root,preset,artifact,observations,policy);
    }
    return tickets.computeIfAbsent(owner,c->sources.owner(c.getPos()));
   }catch(IOException|RuntimeException|Error error){failed=true;throw error;}
  }
  public void release(ChunkAccess owner){
   if(!level.getServer().isSameThread())throw new IllegalStateException("Cinnabar release requires server thread");
   var ticket=tickets.remove(owner);if(ticket!=null&&sources!=null)sources.release(ticket);
  }
 }
}
