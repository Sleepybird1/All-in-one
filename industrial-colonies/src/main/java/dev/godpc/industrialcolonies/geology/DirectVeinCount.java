package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ChunkPos;

/** Read-only association and observation of a naturally owned vein, with no extraction node required. */
final class DirectVeinCount {
 private static final Map<MinecraftServer,Map<UUID,Job>> JOBS=new IdentityHashMap<>();
 private DirectVeinCount(){}
 static boolean active(ServerPlayer player){return JOBS.getOrDefault(player.getServer(),Map.of()).containsKey(player.getUUID());}
 static int activeCount(MinecraftServer server){return JOBS.getOrDefault(server,Map.of()).size();}
 static boolean cancel(ServerPlayer player){var job=JOBS.getOrDefault(player.getServer(),Map.of()).get(player.getUUID());if(job==null)return false;job.cancelled.set(true);return true;}
 static void stop(MinecraftServer server){var jobs=JOBS.remove(server);if(jobs!=null)jobs.values().forEach(j->j.cancelled.set(true));}
 private static void tell(CommandSourceStack source,String text){source.sendSuccess(()->Component.literal(text),false);}
 static int start(CommandSourceStack source,ServerPlayer player,BlockPos target){
  var level=source.getLevel();var binding=NativeContinentLevels.find(level).orElse(null);if(binding==null)return 0;
  var chunk=level.getChunkSource().getChunkNow(target.getX()>>4,target.getZ()>>4);
  if(chunk==null||!chunk.hasData(MiningOreOwnership.LEDGER)){source.sendFailure(Component.literal("No saved vein ownership at that block."));return 0;}
  var ledger=chunk.getData(MiningOreOwnership.LEDGER);
  if(!ledger.sealed()||ledger.failed()){source.sendFailure(Component.literal("Vein generation is unfinished at that block."));return 0;}
  var owner=ledger.ownerAt(target.getX(),target.getY(),target.getZ());
  if(owner.isEmpty()){source.sendFailure(Component.literal("Aim at the main vein; this block has no natural vein ownership."));return 0;}
  var jobs=JOBS.computeIfAbsent(source.getServer(),s->new LinkedHashMap<>());
  if(jobs.containsKey(player.getUUID())||jobs.size()>=4){source.sendFailure(Component.literal("A count is active or capacity reached."));return 0;}
  try{var job=new Job(source,player,target,owner.get(),binding);jobs.put(player.getUUID(),job);tell(source,"Counting vein…");return 1;}
  catch(Exception error){org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinCount").error("Cannot start direct vein count",error);source.sendFailure(Component.literal("Cannot start count. See server log."));return 0;}
 }
 static void tick(MinecraftServer server){
  var jobs=JOBS.get(server);if(jobs==null)return;
  for(var entry:List.copyOf(jobs.entrySet())){
   var job=entry.getValue();try{if(job.poll())jobs.remove(entry.getKey());}
   catch(Exception error){jobs.remove(entry.getKey());job.cancelled.set(true);org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinCount").error("Direct vein count stopped",error);job.source.sendFailure(Component.literal("Count failed; no complete total. See server log."));}
  }
  if(jobs.isEmpty())JOBS.remove(server);
 }
 private static final class Job {
  final CommandSourceStack source;final ServerPlayer player;final BlockPos target;final String owner;
  final NativeContinentLevels.Binding binding;final AtomicBoolean cancelled=new AtomicBoolean();
  final CompletableFuture<Optional<MiningScanScope>> lookup;
  MiningScanScope scope;MiningScanCursor cursor;final Map<String,Long> counts=new TreeMap<>();
  final Set<Long> missing=new HashSet<>(),untracked=new HashSet<>();final Map<Long,byte[]> before=new HashMap<>();
  long total;boolean changed;
  Job(CommandSourceStack source,ServerPlayer player,BlockPos target,String owner,NativeContinentLevels.Binding binding){
   this.source=source;this.player=player;this.target=target.immutable();this.owner=owner;this.binding=binding;var descriptor=binding.recordedLookup();int minY=source.getLevel().getMinBuildHeight(),maxY=source.getLevel().getMaxBuildHeight();
   lookup=CompletableFuture.supplyAsync(()->{
    try{return RecordedVeinScopeLookup.find(descriptor.directory(),owner,cancelled::get,file->{
     String[] parts=file.getParent().getFileName().toString().substring("continent-".length()).split("-");
     var continent=new ReTerraForgedGeography.ContinentKey(Integer.parseUnsignedInt(parts[0],16),Integer.parseUnsignedInt(parts[1],16),Integer.parseUnsignedInt(parts[2],16));
     return ContinentOccurrenceLedger.open(file,descriptor.scope(),continent).snapshot().values();
    }).map(request->MiningScanScope.continent(request,minY,maxY));}catch(java.io.IOException error){throw new CompletionException(error);}
   },net.minecraft.Util.ioPool());
  }
  boolean poll()throws Exception{
   var level=source.getLevel();
   if(cancelled.get())return lookup.isDone();
   if(!source.hasPermission(4)||player.isRemoved()||player.serverLevel()!=level||source.getServer().getPlayerList().getPlayer(player.getUUID())!=player||NativeContinentLevels.find(level).orElse(null)!=binding){cancelled.set(true);return lookup.isDone();}
   if(scope==null){
    if(!lookup.isDone())return false;var request=lookup.join();
    if(request.isEmpty()){source.sendFailure(Component.literal("No matching saved continent vein. This may be a legacy deposit."));return true;}
    scope=request.get();
    if(!scope.key().equals(owner)||!scope.contains(target.getX(),target.getY(),target.getZ()))throw new IllegalStateException("Saved vein ownership/geometry mismatch");
    var anchor=level.getChunkSource().getChunkNow(target.getX()>>4,target.getZ()>>4);
    if(anchor==null||!anchor.hasData(MiningOreOwnership.LEDGER)||!anchor.getData(MiningOreOwnership.LEDGER).owns(owner,target.getX(),target.getY(),target.getZ()))throw new IllegalStateException("Selected vein block unloaded or changed");
    cursor=scope.cursor(0);if(cursor.totalCandidates()>64000000L)throw new IllegalStateException("Vein inspection envelope limit");
   }
   for(int budget=0;budget<4096&&!cursor.exhausted();budget++){
    var p=cursor.current();long next=cursor.nextIndex();
    if(scope.contains(p.x(),p.y(),p.z())){
     long key=ChunkPos.asLong(p.x()>>4,p.z()>>4);var chunk=level.getChunkSource().getChunkNow(p.x()>>4,p.z()>>4);
     if(chunk==null)missing.add(key);
     else if(!chunk.hasData(MiningOreOwnership.LEDGER))untracked.add(key);
     else{
      var ledger=chunk.getData(MiningOreOwnership.LEDGER);if(!before.containsKey(key))before.put(key,ledger.encode());
      if(!ledger.sealed()||ledger.failed())untracked.add(key);
      else if(ledger.owns(owner,p.x(),p.y(),p.z())){
       var state=chunk.getBlockState(new BlockPos(p.x(),p.y(),p.z()));
       if(state.isAir())changed=true;else{total++;counts.merge(BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString(),1L,Long::sum);}
      }
     }
    }
    cursor.advance(next);
   }
   if(!cursor.exhausted())return false;
   for(var entry:before.entrySet()){
    var chunk=level.getChunkSource().getChunkNow(ChunkPos.getX(entry.getKey()),ChunkPos.getZ(entry.getKey()));
    if(chunk==null||!chunk.hasData(MiningOreOwnership.LEDGER)||!Arrays.equals(entry.getValue(),chunk.getData(MiningOreOwnership.LEDGER).encode()))changed=true;
   }
   boolean complete=missing.isEmpty()&&untracked.isEmpty()&&!changed;
   tell(source,scope.family()+": "+total+" natural blocks"+(complete?".":" observed (incomplete: "+missing.size()+" unloaded chunks, "+untracked.size()+" untracked chunks"+(changed?", changed during count":"")+")."));
   counts.forEach((id,count)->tell(source,id+": "+count));return true;
  }
 }
}
