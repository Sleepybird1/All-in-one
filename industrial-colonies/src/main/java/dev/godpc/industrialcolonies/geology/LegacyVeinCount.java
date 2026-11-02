package dev.godpc.industrialcolonies.geology;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import java.util.*;

/** Current regional geometry plus observed blocks; never claims missing historical ownership. */
final class LegacyVeinCount {
 private static final Map<MinecraftServer,Map<UUID,Job>> JOBS=new IdentityHashMap<>();
 private LegacyVeinCount(){}
 static boolean active(ServerPlayer p){return JOBS.getOrDefault(p.getServer(),Map.of()).containsKey(p.getUUID());}
 static int activeCount(MinecraftServer server){return JOBS.getOrDefault(server,Map.of()).size();}
 static boolean cancel(ServerPlayer p){var jobs=JOBS.get(p.getServer());return jobs!=null&&jobs.remove(p.getUUID())!=null;}
 static void stop(MinecraftServer server){JOBS.remove(server);}
 private static void tell(CommandSourceStack source,String text){source.sendSuccess(()->Component.literal(text),false);}
 static boolean legacyCoalTarget(net.minecraft.server.level.ServerLevel level,Block block){
  if(NativeContinentLevels.find(level).isEmpty()||NativeContinentLevels.excludedFamilies(level).contains("coal"))return false;
  return GeologyConfig.array(GeologyConfig.get().deposits(),"deposits").asList().stream().map(e->e.getAsJsonObject()).filter(d->GeologyConfig.string(d,"id","").equals("coal")).anyMatch(d->palette(d).contains(block));
 }
 static int startBoundCoal(CommandSourceStack source,ServerPlayer player,BlockPos target){return start(source,player,target,true);}
 static int start(CommandSourceStack source,ServerPlayer player,BlockPos target){return start(source,player,target,false);}
 private static int start(CommandSourceStack source,ServerPlayer player,BlockPos target,boolean boundCoal){
  var jobs=JOBS.computeIfAbsent(source.getServer(),s->new LinkedHashMap<>());
  if(jobs.size()>=2||jobs.containsKey(player.getUUID())){source.sendFailure(Component.literal("A regional vein count is active or its two slots are occupied."));return 0;}
  try{jobs.put(player.getUUID(),new Job(source,player,target,boundCoal));}
  catch(RuntimeException error){source.sendFailure(Component.literal("Cannot identify vein: "+error.getMessage()));return 0;}
  tell(source,"Identifying the targeted regional vein, one candidate region per tick, then counting actual loaded blocks throughout its geometry. No chunks are requested. Current-plan matching cannot prove old generation settings or original natural ownership.");return 1;
 }
 static void tick(MinecraftServer server){
  var jobs=JOBS.get(server);if(jobs==null)return;
  for(var e:List.copyOf(jobs.entrySet()))try{if(NativeTerrainYield.during(e.getValue()::poll))jobs.remove(e.getKey());}
  catch(NativeTerrainYield.Pending pending){/* Retry the exact same regional query on a later tick; native tile work is shared. */}
  catch(Exception error){jobs.remove(e.getKey());e.getValue().source.sendFailure(Component.literal("Vein count stopped: "+error.getMessage()+"; no complete count."));}
  if(jobs.isEmpty())JOBS.remove(server);
 }
 private static Set<Block> palette(GeologyPlanner.Plan plan){return palette(plan.definition());}
 private static Set<Block> palette(com.google.gson.JsonObject d){
  var result=new HashSet<Block>();
  result.add(GeologyFeature.state(d.get("hostRock").getAsString()).getBlock());
  for(String field:List.of("richOres","associated"))for(var e:GeologyConfig.array(d,field))result.add(GeologyFeature.state(e.getAsJsonObject().get("block").getAsString()).getBlock());
  return Set.copyOf(result);
 }
 private static final class Match {
  final GeologyPlanner.Plan plan;final Set<BlockPos> points;final MassiveDepositGeometry.Body body;final Set<Block> blocks;final MassiveDepositGeometry.Bounds bounds;
  Match(GeologyPlanner.Plan plan,GeologyWorld world,MassiveDeposits.Settings settings){
   this.plan=plan;blocks=palette(plan);
   if(settings!=null){body=MassiveDeposits.body(plan,settings);points=Set.of();bounds=body.bounds();}
   else{
    body=null;points=Set.copyOf(world.shape(plan));if(points.isEmpty())throw new IllegalStateException("Empty regional formation");
    int lx=Integer.MAX_VALUE,ly=lx,lz=lx,hx=Integer.MIN_VALUE,hy=hx,hz=hx;
    for(var p:points){lx=Math.min(lx,p.getX());ly=Math.min(ly,p.getY());lz=Math.min(lz,p.getZ());hx=Math.max(hx,p.getX());hy=Math.max(hy,p.getY());hz=Math.max(hz,p.getZ());}
    bounds=new MassiveDepositGeometry.Bounds(lx,ly,lz,hx,hy,hz);
   }
  }
  boolean contains(int x,int y,int z){return body!=null?body.contains(x,y,z):points.contains(new BlockPos(x,y,z));}
 }
 private static final class Job {
  final CommandSourceStack source;final ServerPlayer player;final BlockPos target;final Block targetBlock;final GeologyWorld world;
  final GeologyConfig.Config config;final Object randomState;final MassiveDeposits.Settings massive;
  final NativeContinentLevels.Binding binding;final boolean boundCoal;
  final int minRx,maxRx,minRz,maxRz,reach;int rx,rz,regions;Match match;MiningScanCursor cursor;
  final Map<String,Long> counts=new TreeMap<>();final Set<Long> missing=new HashSet<>();long covered,material;
  Job(CommandSourceStack source,ServerPlayer player,BlockPos target,boolean boundCoal){
   this.source=source;this.player=player;this.target=target.immutable();var level=source.getLevel();
   var chunk=level.getChunkSource().getChunkNow(target.getX()>>4,target.getZ()>>4);if(chunk==null)throw new IllegalArgumentException("Target chunk unloaded");
   targetBlock=chunk.getBlockState(target).getBlock();this.boundCoal=boundCoal;binding=NativeContinentLevels.find(level).orElse(null);if(boundCoal&&!legacyCoalTarget(level,targetBlock))throw new IllegalArgumentException("Not an active legacy coal block");world=GeologyWorld.of(level);randomState=level.getChunkSource().randomState();
   var c=GeologyConfig.get();config=new GeologyConfig.Config(c.settings().deepCopy(),c.biomes().deepCopy(),c.deposits().deepCopy());
   if(world.planner.definitions().stream().noneMatch(d->palette(d).contains(targetBlock)))throw new IllegalArgumentException("Target is not a configured vein material");
   int region=world.planner.regionSize();massive=MassiveDeposits.enabled(c)?MassiveDeposits.settings(c):null;
   if(massive!=null){reach=massive.maxReach();minRx=Math.floorDiv(target.getX()-reach,region);maxRx=Math.floorDiv(target.getX()+reach,region);minRz=Math.floorDiv(target.getZ()-reach,region);maxRz=Math.floorDiv(target.getZ()+reach,region);}
   else{var geometry=GeologyConfig.object(c.settings(),"geometry");reach=(int)Math.ceil(6*Math.cbrt(GeologyConfig.integer(geometry,"maxIntendedBlocks",50000)));int search=Math.max(GeologyConfig.integer(geometry,"regionSearchRadius",1),(int)Math.ceil((double)reach/region));int x=Math.floorDiv(target.getX(),region),z=Math.floorDiv(target.getZ(),region);minRx=x-search;maxRx=x+search;minRz=z-search;maxRz=z+search;}
   if(((long)maxRx-minRx+1)*((long)maxRz-minRz+1)>4096)throw new IllegalArgumentException("Regional identification exceeds bounded scope");rx=minRx;rz=minRz;
  }
  boolean poll(){
   var level=source.getLevel();
   if(!source.hasPermission(4)||player.isRemoved()||player.serverLevel()!=level||source.getServer().getPlayerList().getPlayer(player.getUUID())!=player)return true;
   if((boundCoal?NativeContinentLevels.find(level).orElse(null)!=binding||!legacyCoalTarget(level,targetBlock):NativeContinentLevels.find(level).isPresent())||!config.equals(GeologyConfig.get())||randomState!=level.getChunkSource().randomState())throw new IllegalStateException("Generation context changed; no regional fallback allowed");
   if(cursor==null){
    if(rx<=maxRx){
     int x=rx,z=rz;
     if(world.planner.mayReach(x,z,target.getX(),target.getZ(),target.getX(),target.getZ(),reach)){
      var plan=world.planner.decide(x,z).plan();
      if(plan!=null&&(!boundCoal||plan.id().equals("coal"))&&palette(plan).contains(targetBlock)){
       var found=new Match(plan,world,massive);
       if(found.contains(target.getX(),target.getY(),target.getZ())){
        if(match!=null)throw new IllegalStateException("Target belongs to overlapping current regional geometries; do not combine deposits");match=found;
       }
      }
     }
     regions++;if(++rz>maxRz){rz=minRz;rx++;}
     return false;
    }
    if(match==null){tell(source,"No matching main-vein geometry at the selected block. It may be a small pocket, mineshaft-specific body or older generation; no vein total was invented.");return true;}
    cursor=new MiningScanCursor(match.bounds,level.getMinBuildHeight(),level.getMaxBuildHeight(),0);
    if(cursor.totalCandidates()>64000000L)throw new IllegalStateException("Matched envelope exceeds bounded counting capacity");
   }
   for(int budget=0;budget<4096&&!cursor.exhausted();budget++){
    var p=cursor.current();long next=cursor.nextIndex();
    if(match.contains(p.x(),p.y(),p.z())){
     var chunk=level.getChunkSource().getChunkNow(p.x()>>4,p.z()>>4);
     if(chunk==null)missing.add(ChunkPos.asLong(p.x()>>4,p.z()>>4));
     else{covered++;var state=chunk.getBlockState(new BlockPos(p.x(),p.y(),p.z()));if(match.blocks.contains(state.getBlock())){material++;counts.merge(BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString(),1L,Long::sum);}}
    }
    cursor.advance(next);
   }
   if(!cursor.exhausted())return false;
   tell(source,(missing.isEmpty()?"Whole current regional geometry observed":"INCOMPLETE regional vein count")+": "+match.plan.id()+"; "+material+" matching material blocks currently observed; "+covered+" shape cells read, "+missing.size()+" unloaded chunks. Current-plan geometry, not original-generation proof; multi-tick read can change during mining. No ingot yield or original natural reserve inferred.");
   counts.forEach((id,count)->tell(source,id+": "+count+" blocks"));return true;
  }
 }
}
