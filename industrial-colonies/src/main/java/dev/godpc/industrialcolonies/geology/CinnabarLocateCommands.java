package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.QuartPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.*;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;

/** Full requested-radius prediction, paged off-thread; paused queries retain their exact column. */
final class CinnabarLocateCommands {
 private static final Map<MinecraftServer,Map<String,Job>> JOBS=new IdentityHashMap<>();
 private static final int PAGE_COLUMNS=64,INVOCATION_COLUMNS=131072;
 private static final class Job {
  final CinnabarSearchCursor cursor;final ServerLevel level;final Object randomState;final com.google.gson.JsonObject config;final int x,z,radius;
  Supplier<Page> work;volatile boolean stop;boolean running;long started,initialChecked;
  Job(CinnabarSearchCursor cursor,ServerLevel level,Object randomState,com.google.gson.JsonObject config,int x,int z,int radius){this.cursor=cursor;this.level=level;this.randomState=randomState;this.config=config;this.x=x;this.z=z;this.radius=radius;}
 }
 private record Result(int x,int y,int z) {}
 private record Page(Result result,boolean exhausted) {}
 private static String owner(CommandSourceStack s){return s.getEntity()==null?"console":s.getEntity().getUUID().toString();}
 static boolean hasJob(CommandSourceStack s){return JOBS.getOrDefault(s.getServer(),Map.of()).containsKey(owner(s));}
 static void forgetPaused(CommandSourceStack s){var jobs=JOBS.get(s.getServer());if(jobs!=null){var j=jobs.get(owner(s));if(j!=null&&!j.running)jobs.remove(owner(s));}}
 static boolean active(CommandSourceStack s){var j=JOBS.getOrDefault(s.getServer(),Map.of()).get(owner(s));return j!=null&&j.running;}
 static int status(CommandSourceStack s){var j=JOBS.getOrDefault(s.getServer(),Map.of()).get(owner(s));if(j==null)return 0;VeinLocateFeedback.text(s,(j.running?"Running: ":"Paused: ")+j.cursor.checked()+" spots checked.");return 1;}
 static int cancel(CommandSourceStack s){var j=JOBS.getOrDefault(s.getServer(),Map.of()).get(owner(s));if(j==null)return 0;j.stop=true;VeinLocateFeedback.text(s,"Paused: "+j.cursor.checked()+" spots checked. Run again to continue.");return 1;}
 static void stop(MinecraftServer server){var jobs=JOBS.remove(server);if(jobs!=null)jobs.values().forEach(j->j.stop=true);}
 static int start(CommandSourceStack source,int radius){
  if(source.getLevel().dimension()!=Level.OVERWORLD||!WorldStartCinnabarRuntime.localBiomeMode()){source.sendFailure(Component.literal("Cinnabar lookup is unavailable here."));return 0;}
  var server=source.getServer();var jobs=JOBS.computeIfAbsent(server,s->new HashMap<>());var key=owner(source);var old=jobs.get(key);
  if(old!=null&&old.running||old==null&&jobs.size()>=4){source.sendFailure(Component.literal("Search already running or capacity reached."));return 0;}
  try{
   var level=source.getLevel();var generator=level.getChunkSource().getGenerator();var state=level.getChunkSource().randomState();
   var config=GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar").deepCopy();
   int ox=(int)Math.floor(source.getPosition().x),oz=(int)Math.floor(source.getPosition().z);
   Job job;
   if(old!=null&&old.level==level&&old.randomState==state&&old.radius==radius&&old.config.equals(config)&&Math.hypot((double)old.x-ox,(double)old.z-oz)<=16)job=old;
   else{
    var lookup=NativeAccurateTerrain.lookup(state);var height=LevelHeightAccessor.create(level.getMinBuildHeight(),level.getHeight());
    var eligible=new HashSet<String>();level.registryAccess().registryOrThrow(Registries.BIOME).holders().forEach(h->{String id=h.key().location().toString();if(h.is(BiomeTags.IS_MOUNTAIN)||GeologyConfig.families(id).contains("mountain_highland"))eligible.add(id);});Set<String> biomes=Set.copyOf(eligible);
    int spacing=GeologyConfig.integer(config,"localSpacing",512);double chance=GeologyConfig.number(config,"localChance",.25),coverage=GeologyConfig.number(config,"coverage",.7);
    if(GeologyConfig.integer(config,"minimumY",200)!=200||GeologyConfig.integer(config,"maximumY",300)!=300)throw new IllegalArgumentException("Invalid cinnabar policy");
    job=new Job(new CinnabarSearchCursor(level.getSeed(),ox,oz,radius,spacing,chance,coverage),level,state,config,ox,oz,radius);
    var current=job;
    job.work=()->{
     for(int count=0;count<PAGE_COLUMNS&&!current.stop&&System.nanoTime()-current.started<120_000_000_000L&&current.cursor.checked()-current.initialChecked<INVOCATION_COLUMNS;count++){
      var p=current.cursor.peek(4096);if(p==null)return new Page(null,current.cursor.exhausted());
       try{if(CinnabarCapPlans.knownRejected(level,p.x(),p.z())){current.cursor.commit();continue;}}
       catch(java.io.IOException error){throw new java.io.UncheckedIOException(error);}
       var found=NativeAccurateTerrain.queryLookup(lookup,()->{
       int y=generator.getBaseHeight(p.x(),p.z(),Heightmap.Types.WORLD_SURFACE_WG,height,state)-1;if(y<200||y>304)return (Result)null;
       var column=generator.getBaseColumn(p.x(),p.z(),height,state);
       for(int snow=0;snow<4&&y>=200;snow++){var block=column.getBlock(y);if(!block.is(Blocks.SNOW)&&!block.is(Blocks.SNOW_BLOCK)&&!block.is(Blocks.POWDER_SNOW))break;y--;}
       if(y<200||y>300||!GeologyFeature.replaceable(column.getBlock(y)))return (Result)null;
       var biome=generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(p.x()),QuartPos.fromBlock(y),QuartPos.fromBlock(p.z()),state.sampler());String id=biome.unwrapKey().map(k->k.location().toString()).orElse("");return biomes.contains(id)?new Result(p.x(),y,p.z()):null;
      });
      if(current.stop)return new Page(null,false);current.cursor.commit();if(found!=null)return new Page(found,false);
     }
     return new Page(null,false);
    };
   }
   jobs.put(key,job);job.stop=false;job.running=true;job.started=System.nanoTime();job.initialChecked=job.cursor.checked();
   VeinLocateFeedback.text(source,"Running task…");pump(source,key,jobs,job);return 1;
  }catch(Exception error){org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinLocate").error("Cannot start cinnabar search",error);source.sendFailure(Component.literal("Cannot start search. See server log."));return 0;}
 }
 private static void pump(CommandSourceStack source,String key,Map<String,Job> jobs,Job job){
  var server=source.getServer();CompletableFuture.supplyAsync(job.work,net.minecraft.Util.ioPool()).whenComplete((page,error)->server.execute(()->{
   if(JOBS.get(server)!=jobs||jobs.get(key)!=job)return;
   if(!source.hasPermission(4)||!WorldStartCinnabarRuntime.localBiomeMode()||job.level.getChunkSource().randomState()!=job.randomState||!job.config.equals(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartCinnabar"))||source.getEntity() instanceof ServerPlayer player&&(server.getPlayerList().getPlayer(player.getUUID())!=player||player.serverLevel()!=job.level)){jobs.remove(key);return;}
   if(error!=null){job.running=false;job.stop=true;org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinLocate").error("Cinnabar search paused at retained column",error);VeinLocateFeedback.text(source,"Search failed after "+job.cursor.checked()+" spots. Progress kept.");return;}
   if(job.stop){job.running=false;return;}
   if(page.result()!=null){jobs.remove(key);var result=page.result();VeinLocateFeedback.found(source,"Cinnabar",result.x(),result.y(),result.z(),job.cursor.checked(),"Predicted local pocket; actual blocks and remaining ore unverified.");return;}
   if(page.exhausted()){jobs.remove(key);VeinLocateFeedback.none(source,job.cursor.checked(),"All deterministic mask columns within the radius were checked against native prediction; existing blocks may differ.");return;}
   if(job.cursor.checked()-job.initialChecked>=INVOCATION_COLUMNS||System.nanoTime()-job.started>=120_000_000_000L){job.running=false;job.stop=true;VeinLocateFeedback.text(source,"Paused: "+job.cursor.checked()+" spots checked. Run again to continue.");return;}
   pump(source,key,jobs,job);
  }));
 }
}
