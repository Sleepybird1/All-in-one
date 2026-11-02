package dev.godpc.industrialcolonies.geology;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.util.*;

/** Operator inspection of canonical optional-vein decisions. No chunk requests, block writes or teleport. */
public final class VeinLocateCommands {
 private static final int STEP=4096,MAX_POINTS=4096,MAX_READS=2048,MAX_JOBS=4;
 private static final Map<MinecraftServer,Map<String,Job>> JOBS=new IdentityHashMap<>();
 private static final Map<MinecraftServer,Set<String>> RECORDED_JOBS=new IdentityHashMap<>();
 private record Point(int x,int z) {}
 private VeinLocateCommands(){}
 private static String owner(CommandSourceStack source){return source.getEntity()==null?"console":source.getEntity().getUUID().toString();}
 private static void tell(CommandSourceStack source,String text){source.sendSuccess(()->Component.literal(text),false);}
 public static void register(RegisterCommandsEvent event){
  event.getDispatcher().register(Commands.literal("icveins").requires(s->s.hasPermission(4))
   .then(Commands.literal("survey").then(Commands.literal("status").executes(c->{tell(c.getSource(),AutomaticVeinSurvey.status(c.getSource().getLevel()));return 1;}))
    .then(Commands.literal("resume").executes(c->{boolean resumed=AutomaticVeinSurvey.resume(c.getSource().getLevel());tell(c.getSource(),resumed?"Automatic survey resumed with its existing saved cursor and vein decisions.":"Survey cannot resume now; inspect survey status. No records were reset.");return resumed?1:0;})))
   .then(Commands.literal("nearest").then(Commands.argument("family",StringArgumentType.word())
    .executes(c->recorded(c.getSource(),StringArgumentType.getString(c,"family"),32768))
    .then(Commands.argument("radiusBlocks",IntegerArgumentType.integer(1,131072)).executes(c->recorded(c.getSource(),StringArgumentType.getString(c,"family"),IntegerArgumentType.getInteger(c,"radiusBlocks"))))))
   .then(Commands.literal("locate").then(Commands.argument("family",StringArgumentType.word()).suggests((c,b)->{var binding=NativeContinentLevels.find(c.getSource().getLevel());if(binding.isPresent())for(var family:new TreeSet<>(binding.get().locatableFamilies()))b.suggest(family);if(WorldStartCinnabarRuntime.localBiomeMode())b.suggest("cinnabar");return b.buildFuture();})
    .executes(c->start(c.getSource(),StringArgumentType.getString(c,"family"),32768))
    .then(Commands.argument("radiusBlocks",IntegerArgumentType.integer(1,131072)).executes(c->start(c.getSource(),StringArgumentType.getString(c,"family"),IntegerArgumentType.getInteger(c,"radiusBlocks"))))))
   .then(Commands.literal("status").executes(c->{var source=c.getSource();if(CinnabarLocateCommands.hasJob(source))return CinnabarLocateCommands.status(source);var job=JOBS.getOrDefault(source.getServer(),Map.of()).get(owner(source));tell(source,job==null?"No active vein search.":job.status());return job==null?0:1;}))
   .then(Commands.literal("cancel").executes(c->{var source=c.getSource();if(CinnabarLocateCommands.hasJob(source))return CinnabarLocateCommands.cancel(source);var jobs=JOBS.get(source.getServer());var job=jobs==null?null:jobs.get(owner(source));if(job!=null)job.paused=true;tell(source,job==null?"No active search.":"Paused: "+job.reads+" spots checked. Run again to continue.");return job==null?0:1;})));
 }
 private static int start(CommandSourceStack source,String family,int radius){
  var existing=JOBS.getOrDefault(source.getServer(),Map.of()).get(owner(source));
  if(CinnabarLocateCommands.active(source)||existing!=null&&(!existing.paused||existing.waiting)){source.sendFailure(Component.literal("Search already running."));return 0;}
  if(family.equals("cinnabar")&&existing!=null)JOBS.get(source.getServer()).remove(owner(source));
  if(family.equals("cinnabar"))return CinnabarLocateCommands.start(source,radius);
  if(source.getLevel().dimension()!=Level.OVERWORLD){source.sendFailure(Component.literal("Vein locate is Overworld-only."));return 0;}
  var binding=NativeContinentLevels.find(source.getLevel());if(binding.isEmpty()){source.sendFailure(Component.literal("The new continent vein runtime is not active in this world. The old /icgeology locate is a different regional prediction."));return 0;}
  try{
   if(!binding.get().locatableFamilies().contains(family)){source.sendFailure(Component.literal("No active optional-vein locator for "+family+". Use autocomplete; coal has separate unfinished locator support."));return 0;}
   var jobs=JOBS.computeIfAbsent(source.getServer(),server->new LinkedHashMap<>());var key=owner(source);var old=jobs.get(key);
   if(old==null&&jobs.size()>=MAX_JOBS){source.sendFailure(Component.literal("Search capacity reached."));return 0;}
   CinnabarLocateCommands.forgetPaused(source);
   if(old!=null&&old.family.equals(family)&&old.radius==radius&&old.binding==binding.get()&&Math.hypot(old.ox-source.getPosition().x,old.oz-source.getPosition().z)<=16){old.source=source;old.paused=false;old.invocationReads=old.reads;old.started=System.nanoTime();}
   else jobs.put(key,new Job(source,binding.get(),family,radius));
   tell(source,"Running task…");return 1;
  }catch(Exception error){source.sendFailure(Component.literal("Cannot start vein search: "+error.getMessage()));return 0;}
 }
 public static void tick(ServerTickEvent.Post event){
  var jobs=JOBS.get(event.getServer());if(jobs==null)return;
  for(var entry:List.copyOf(jobs.entrySet())){
   var job=entry.getValue();
   if(job.source.getEntity() instanceof ServerPlayer player&&(event.getServer().getPlayerList().getPlayer(player.getUUID())!=player||player.serverLevel()!=job.source.getLevel())){jobs.remove(entry.getKey());continue;}
   if(job.waiting&&!job.paused&&System.nanoTime()-job.started>=120_000_000_000L){job.paused=true;tell(job.source,"Paused: "+job.reads+" spots checked. Run again to continue.");}
   if(job.paused||job.waiting)continue;
   try{if(NativeTerrainYield.during(job::poll))jobs.remove(entry.getKey());}
   catch(NativeTerrainYield.Pending pending){job.waiting=true;pending.ready().whenComplete((ignored,error)->event.getServer().execute(()->{if(JOBS.get(event.getServer())!=jobs||jobs.get(entry.getKey())!=job)return;job.waiting=false;if(error!=null){job.paused=true;org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinLocate").error("Vein terrain prerequisite failed",error);tell(job.source,"Search failed after "+job.reads+" spots. Progress kept.");}}));}
   catch(ContinentCoordinatorCache.Busy busy){/* Another native generation lease owns capacity; retry on a later tick. */}
   catch(Exception error){job.paused=true;org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinLocate").error("Vein search paused without resetting records",error);tell(job.source,"Search failed after "+job.reads+" spots. Progress kept.");}
  }
  if(jobs.isEmpty())JOBS.remove(event.getServer());
 }
 public static void stop(MinecraftServer server){JOBS.remove(server);RECORDED_JOBS.remove(server);CinnabarLocateCommands.stop(server);}
 private static int recorded(CommandSourceStack source,String family,int radius){
  if(source.getLevel().dimension()==Level.OVERWORLD){
   var cached=AutomaticVeinSurvey.nearest(source.getLevel(),family,source.getPosition().x,source.getPosition().z,radius);
   if(cached.isPresent()){var site=cached.get();VeinLocateFeedback.found(source,family,site.x(),site.y(),site.z(),0,"Survey-recorded "+site.kind()+"; actual remaining ore and global nearest unverified.");return 1;}
  }
  var binding=NativeContinentLevels.find(source.getLevel());
  if(source.getLevel().dimension()!=Level.OVERWORLD||binding.isEmpty()){source.sendFailure(Component.literal("Recorded vein lookup requires the active Overworld vein system."));return 0;}
  try{
   if(!binding.get().locatableFamilies().contains(family)){source.sendFailure(Component.literal("No recorded optional-vein lookup for "+family+"; coal and cinnabar use separate records."));return 0;}
   var server=source.getServer();var key=owner(source);var jobs=RECORDED_JOBS.computeIfAbsent(server,s->new HashSet<>());
   if(jobs.contains(key)||jobs.size()>=MAX_JOBS){source.sendFailure(Component.literal("Recorded vein lookup already running or capacity reached."));return 0;}
   var descriptor=binding.get().recordedLookup();double x=source.getPosition().x,z=source.getPosition().z;jobs.add(key);tell(source,"Running task…");
   java.util.concurrent.CompletableFuture.supplyAsync(()->{
    try{return RecordedVeinLookup.scan(descriptor.directory(),family,x,z,radius,file->{
     String[] parts=file.getParent().getFileName().toString().substring("continent-".length()).split("-");
     var continent=new ReTerraForgedGeography.ContinentKey(Integer.parseUnsignedInt(parts[0],16),Integer.parseUnsignedInt(parts[1],16),Integer.parseUnsignedInt(parts[2],16));
     return ContinentOccurrenceLedger.open(file,descriptor.scope(),continent).snapshot().values().stream().filter(ContinentOccurrenceLedger.Entry::present).map(e->{var c=e.request().candidate();return new RecordedVeinLookup.Site(e.request().key().family(),c.x(),c.y(),c.z(),c.cells(),c.biome());}).toList();
    });}catch(Exception e){throw new java.util.concurrent.CompletionException(e);}
   },net.minecraft.Util.ioPool()).whenComplete((result,error)->server.execute(()->{
    var current=RECORDED_JOBS.get(server);if(current!=jobs||!current.remove(key))return;if(current.isEmpty())RECORDED_JOBS.remove(server);
    if(!source.hasPermission(4)||NativeContinentLevels.find(source.getLevel()).orElse(null)!=binding.get())return;
    if(source.getEntity() instanceof ServerPlayer player&&server.getPlayerList().getPlayer(player.getUUID())!=player)return;
    if(error!=null){org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinLocate").error("Recorded lookup failed",error);source.sendFailure(Component.literal("Search failed. Saved records kept."));return;}
    if(result.nearest().isEmpty()){VeinLocateFeedback.none(source,result.journals(),"Saved journals only; unexplored terrain was not searched.");return;}
    var site=result.nearest().get();VeinLocateFeedback.found(source,family,site.x(),site.y(),site.z(),result.journals(),"Recorded plan; physical stock and unrecorded nearer veins unverified.");
   }));return 1;
  }catch(Exception error){source.sendFailure(Component.literal("Cannot read recorded veins: "+error.getMessage()));return 0;}
 }
 private static final class Job {
  CommandSourceStack source;final NativeContinentLevels.Binding binding;final String family;
  final ReTerraForgedGeography geography;final Object randomState;
  final double ox,oz;final int radius;final List<Point> points;final Set<ReTerraForgedGeography.ContinentKey> seen=new HashSet<>();
  ReTerraForgedGeography.ContinentKey pending;int pointIndex,reads,absent,unfitted,outside,invocationReads;boolean paused,waiting;long started=System.nanoTime();
  Job(CommandSourceStack source,NativeContinentLevels.Binding binding,String family,int radius){
   this.source=source;this.binding=binding;this.family=family;this.radius=radius;ox=source.getPosition().x;oz=source.getPosition().z;randomState=source.getLevel().getChunkSource().randomState();geography=ReTerraForgedGeography.fromRandomState(randomState);
   int x=(int)Math.floor(ox),z=(int)Math.floor(oz);var candidates=new ArrayList<Point>();int rings=(radius+STEP-1)/STEP;
   for(int dx=-rings;dx<=rings;dx++)for(int dz=-rings;dz<=rings;dz++){
    long px=(long)x+(long)dx*STEP,pz=(long)z+(long)dz*STEP;if(Math.abs(px)>=ContinentEnvelope.LIMIT||Math.abs(pz)>=ContinentEnvelope.LIMIT)continue;
    if((double)dx*dx*STEP*STEP+(double)dz*dz*STEP*STEP>(double)radius*radius)continue;candidates.add(new Point((int)px,(int)pz));
   }
   candidates.sort(Comparator.comparingDouble(p->(p.x()-ox)*(p.x()-ox)+(p.z()-oz)*(p.z()-oz)));points=List.copyOf(candidates.subList(0,Math.min(MAX_POINTS,candidates.size())));
  }
  String status(){return (paused?"Paused: ":"Running: ")+reads+" spots checked.";}
  boolean poll()throws Exception{
   if(!source.hasPermission(4)||NativeContinentLevels.find(source.getLevel()).orElse(null)!=binding)return true;
   if(source.getEntity() instanceof ServerPlayer p&&source.getServer().getPlayerList().getPlayer(p.getUUID())!=p)return true;
   if(reads-invocationReads>=MAX_READS||System.nanoTime()-started>=120_000_000_000L){paused=true;tell(source,"Paused: "+reads+" spots checked. Run again to continue.");return false;}
   if(randomState!=source.getLevel().getChunkSource().randomState())throw new IllegalStateException("Native terrain context changed");
   var runtime=binding.runtime();
   if(pending==null){
    if(pointIndex>=points.size()){VeinLocateFeedback.none(source,reads,"Sampled continent scopes only; not exhaustive physical ore coverage.");return true;}
    var point=points.get(pointIndex++);
    pending=geography.continent(point.x(),point.z());
    if(!seen.add(pending)){pending=null;return false;}
   }
   try(var lease=runtime.acquire(pending)){
    var result=lease.locate(family);
    if(result.state().equals("SEARCHING")){lease.advanceOptionalLocate(1);reads++;result=lease.locate(family);}
    if(result.state().equals("SEARCHING"))return false;
    if(result.state().equals("PRESENT")){
     var c=result.candidate();double dx=c.x()-ox,dz=c.z()-oz;
     if(dx*dx+dz*dz<=(double)radius*radius){VeinLocateFeedback.found(source,family,c.x(),c.y(),c.z(),reads,"Canonical vein plan; actual remaining stock unverified.");return true;}outside++;
    }else if(result.state().equals("ABSENT")||result.state().equals("NO_ALLOCATION"))absent++;
    else if(result.state().equals("EXHAUSTED"))unfitted++;
    else throw new IllegalStateException("Unresolved authority "+result.state());
   }
   pending=null;return false;
  }
 }
}
