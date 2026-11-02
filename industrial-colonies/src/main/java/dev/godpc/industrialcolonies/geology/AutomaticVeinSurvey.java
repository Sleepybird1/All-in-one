package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/** Silent resumable spawn-outward prospecting survey. Never places ore or requests chunks. */
public final class AutomaticVeinSurvey {
 private static final Map<ServerLevel,Session> SESSIONS=new IdentityHashMap<>();
 private static final Set<ServerLevel> FAILED=Collections.newSetFromMap(new IdentityHashMap<>());
 private static final org.slf4j.Logger LOG=org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinSurvey");
 private AutomaticVeinSurvey(){}
 private static final class Policy {static final com.google.gson.JsonObject DATA=GeologyConfig.externalOrBundled("vein_survey.json");}
 private static boolean enabled(){return WorldStartOreRuntime.enabled()&&GeologyConfig.bool(Policy.DATA,"enabled",false);}
 static final class Data extends SavedData {
  static final Factory<Data> FACTORY=new Factory<>(Data::new,Data::read);
  SpawnSurveyState state;CompoundTag rejected;
  static Data read(CompoundTag tag,HolderLookup.Provider registries){var d=new Data();try{if(!tag.contains("state",7))throw new IllegalStateException("Missing survey state");d.state=SpawnSurveyState.decode(tag.getByteArray("state"));}catch(Exception e){d.rejected=tag.copy();}return d;}
  @Override public CompoundTag save(CompoundTag tag,HolderLookup.Provider registries){if(rejected!=null)return rejected.copy();try{if(state==null)throw new IllegalStateException("Uninitialized survey");tag.putByteArray("state",state.encode());return tag;}catch(java.io.IOException e){throw new IllegalStateException("Cannot save survey progress",e);}}
 }
 private static SpawnSurveyState.Origin spawn(ServerLevel level){var p=level.getSharedSpawnPos();return new SpawnSurveyState.Origin(p.getX(),p.getY(),p.getZ());}
 private static String hash(String text){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 private static final class Session {
  final ServerLevel level;final NativeContinentLevels.Binding binding;final Object randomState;
  final GeologyConfig.Config config;final Set<String> optional,targets;final Data data;final ReTerraForgedGeography geography;
  long nextTick,waitSince;Object waiting;boolean warned;
  Session(ServerLevel level,NativeContinentLevels.Binding binding){
   if(!NativeAccurateTerrain.enabled())throw new IllegalStateException("Automatic survey requires cooperative processed native terrain support");
   this.level=level;this.binding=binding;randomState=level.getChunkSource().randomState();config=GeologyConfig.get();optional=Set.copyOf(binding.locatableFamilies());
   var all=new TreeSet<>(optional);
   for(var value:GeologyConfig.array(config.deposits(),"deposits")){var definition=value.getAsJsonObject();String id=definition.get("id").getAsString();if(!id.equals("cinnabar")&&GeologyConfig.number(definition,"baseWeight",1)>0)all.add(id);}
   if(WorldStartCinnabarRuntime.localBiomeMode())all.add("cinnabar");targets=Set.copyOf(all);
   int stride=GeologyConfig.integer(config.settings(),"regionSize",512);
   String identity=hash("spawn-survey-v1\n"+level.getSeed()+"\n"+level.dimension().location()+"\n"+binding.recordedLookup().scope()+"\n"+config+"\n"+Policy.DATA+"\n"+new TreeSet<>(targets));
   data=level.getDataStorage().computeIfAbsent(Data.FACTORY,"industrial_colonies_automatic_vein_survey");
   if(data.rejected!=null)throw new IllegalStateException("Saved survey is invalid; original bytes retained, no reset");
   if(data.state==null){data.state=new SpawnSurveyState(identity,targets,stride,spawn(level));data.setDirty();}
   data.state.require(identity,targets,stride);geography=ReTerraForgedGeography.fromRandomState(randomState);
  }
  void warn(){if(warned)return;warned=true;String text="Automatic ore survey paused: "+data.state.reason()+". Saved veins retained. Operator survey status/resume commands are available.";LOG.warn(text);for(var player:level.getServer().getPlayerList().getPlayers())if(player.hasPermissions(4))player.sendSystemMessage(Component.literal(text));}
  void pause(String reason){data.state.pause(reason);data.setDirty();warn();}
  void tick(){
   if(data.state.moveSpawn(spawn(level))){warned=false;nextTick=level.getServer().getTickCount()+20;data.setDirty();}
   if(data.state.paused()){warn();return;}if(data.state.complete())return;
   long now=level.getServer().getTickCount();
   if(waiting!=null){if(now-waitSince>1200)pause("Native terrain prerequisite exceeded 60 seconds");return;}
   if(now<nextTick)return;nextTick=now+2;
   if(level.getChunkSource().randomState()!=randomState||NativeContinentLevels.find(level).orElse(null)!=binding||GeologyConfig.get()!=config){pause("Generation context changed");return;}
   long started=System.nanoTime();
   try{
    data.state.beginStep();data.setDirty();if(data.state.paused()){warn();return;}
    NativeTerrainYield.during(()->{advance();return true;});
   }catch(NativeTerrainYield.Pending pending){
    Object token=new Object();waiting=token;waitSince=now;long epoch=data.state.epoch();
    pending.ready().whenComplete((ignored,error)->level.getServer().execute(()->{
     if(SESSIONS.get(level)!=this||waiting!=token)return;waiting=null;if(data.state.epoch()!=epoch)return;
     if(error!=null)pause("Native terrain calculation failed; inspect the server log");
    }));
   }catch(ContinentCoordinatorCache.Busy busy){nextTick=now+20;}
   catch(Exception error){LOG.error("Automatic ore survey stopped without resetting canonical records",error);pause(Objects.toString(error.getMessage(),error.getClass().getSimpleName()));}
   finally{if(System.nanoTime()-started>50_000_000L)nextTick=Math.max(nextTick,now+40);}
  }
  void advance()throws Exception{
   var point=data.state.point();
   switch(data.state.phase()){
    case 0->{
     var continent=geography.continent(point.x(),point.z());String key=continent.centerX()+":"+continent.centerZ()+":"+continent.identityBits();
     if(data.state.seen(key)){data.state.nextPhase();return;}
     try(var lease=binding.runtime().acquire(continent)){
      var progress=lease.advanceOptionalLocate(1);
      for(var e:lease.surveyLocations().entrySet()){var c=e.getValue();data.state.record(new SpawnSurveyState.Site(e.getKey(),c.x(),c.y(),c.z(),"CANONICAL_PLAN"));}
      if(progress.status()==NativeContinentCoordinator.Status.HELD)throw new IllegalStateException("Canonical continent discovery held");
      if(progress.status()==NativeContinentCoordinator.Status.READY){data.state.markSeen(key);data.state.nextPhase();}
     }
    }
    case 1->{
     // Existing non-replaced regional families retain exactly the planner used by generation.
     if(targets.stream().anyMatch(f->!optional.contains(f)&&!f.equals("cinnabar"))){
      var planner=GeologyWorld.of(level).planner;var plan=planner.decide(Math.floorDiv(point.x(),planner.regionSize()),Math.floorDiv(point.z(),planner.regionSize())).plan();
      if(plan!=null&&!optional.contains(plan.id())&&targets.contains(plan.id())&&!plan.id().equals("cinnabar")){var c=plan.candidate();data.state.record(new SpawnSurveyState.Site(plan.id(),c.x(),c.y(),c.z(),"REGIONAL_PREDICTION"));}
     }
     data.state.nextPhase();
    }
    case 2->{
     if(targets.contains("cinnabar"))sampleCinnabar(point);data.state.nextPhase();
    }
    default->throw new IllegalStateException("Survey phase");
   }
   data.setDirty();
  }
  void sampleCinnabar(SpawnSurveyState.Point point){
   var policy=GeologyConfig.object(config.settings(),"worldStartCinnabar");int spacing=GeologyConfig.integer(policy,"localSpacing",512);
   if(spacing!=GeologyConfig.integer(config.settings(),"regionSize",512))throw new IllegalStateException("Survey needs matching local/regional grid stride; policy retained");
   var candidate=LocalCinnabarPattern.at(level.getSeed(),Math.floorDiv(point.x(),spacing),Math.floorDiv(point.z(),spacing),spacing,GeologyConfig.number(policy,"localChance",.25));if(candidate==null)return;
   for(var p:LocalCinnabarPattern.probes(candidate,GeologyConfig.number(policy,"coverage",.7))){
    var result=NativeAccurateTerrain.query(level,()->{
     var generator=level.getChunkSource().getGenerator();var state=level.getChunkSource().randomState();
     int y=generator.getBaseHeight(p.x(),p.z(),Heightmap.Types.WORLD_SURFACE_WG,level,state)-1;if(y<200||y>304)return (SpawnSurveyState.Site)null;
     var column=generator.getBaseColumn(p.x(),p.z(),level,state);
     for(int snow=0;snow<4&&y>=200;snow++){var b=column.getBlock(y);if(!b.is(Blocks.SNOW)&&!b.is(Blocks.SNOW_BLOCK)&&!b.is(Blocks.POWDER_SNOW))break;y--;}
     if(y<200||y>300||!GeologyFeature.replaceable(column.getBlock(y)))return (SpawnSurveyState.Site)null;
     var biome=generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(p.x()),QuartPos.fromBlock(y),QuartPos.fromBlock(p.z()),state.sampler());String id=biome.unwrapKey().map(k->k.location().toString()).orElse("");
     if(!biome.is(BiomeTags.IS_MOUNTAIN)&&!GeologyConfig.families(id).contains("mountain_highland"))return (SpawnSurveyState.Site)null;
     return new SpawnSurveyState.Site("cinnabar",p.x(),y,p.z(),"LOCAL_PREDICTION");
    });
    if(result!=null){data.state.record(result);return;}
   }
  }
 }
 public static void tick(ServerTickEvent.Post event){
  var level=event.getServer().overworld();if(level==null||!enabled()||FAILED.contains(level))return;
  var binding=NativeContinentLevels.find(level).orElse(null);if(binding==null)return;
  try{var session=SESSIONS.get(level);if(session==null){session=new Session(level,binding);SESSIONS.put(level,session);}session.tick();}
  catch(Exception failure){FAILED.add(level);LOG.error("Automatic ore survey admission refused; saved records retained",failure);for(var p:event.getServer().getPlayerList().getPlayers())if(p.hasPermissions(4))p.sendSystemMessage(Component.literal("Automatic ore survey could not start; saved data retained. Check the server log."));}
 }
 public static void unload(ServerLevel level){SESSIONS.remove(level);FAILED.remove(level);}
 public static void stop(MinecraftServer server){SESSIONS.keySet().removeIf(l->l.getServer()==server);FAILED.removeIf(l->l.getServer()==server);}
 public static Optional<SpawnSurveyState.Site> nearest(ServerLevel level,String family,double x,double z,int radius){var s=SESSIONS.get(level);return s==null?Optional.empty():s.data.state.nearest(family,x,z,radius);}
 public static String status(ServerLevel level){var s=SESSIONS.get(level);if(s==null)return FAILED.contains(level)?"Automatic survey admission failed; inspect server log.":"Automatic survey not active.";var state=s.data.state;return "Automatic survey "+(state.paused()?"PAUSED: "+state.reason():state.complete()?"COMPLETE":"RUNNING")+"; missing="+new TreeSet<>(state.missing())+"; points="+state.pointIndex()+"; work="+state.steps()+"; recorded plans="+state.sites().size()+". Locations are plans/predictions, not verified physical stock.";}
 public static boolean resume(ServerLevel level){var s=SESSIONS.get(level);if(s==null||!s.data.state.paused()||s.waiting!=null)return false;s.data.state.resume();s.warned=false;s.data.setDirty();return true;}
}
