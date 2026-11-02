package dev.godpc.industrialcolonies.geology;

import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.util.*;

/** Physical observation of one saved deposit, never a reserve estimate or mining action. */
public final class VeinCountCommands {
 private static final Map<MinecraftServer,Map<UUID,Job>> JOBS=new IdentityHashMap<>();
 private VeinCountCommands(){}
 private static void tell(CommandSourceStack source,String text){source.sendSuccess(()->Component.literal(text),false);}
 public static void register(RegisterCommandsEvent event){
  event.getDispatcher().register(Commands.literal("icveins").requires(s->s.hasPermission(4))
   .then(Commands.literal("count").executes(c->{
    var source=c.getSource();var player=source.getPlayerOrException();var target=pick(source,player);
    if(target==null){source.sendFailure(Component.literal("No loaded vein material within 128 blocks along your view, or an unloaded chunk blocks selection. Specify block coordinates with /icveins count at <x> <y> <z>."));return 0;}
    return start(source,target);
   }).then(Commands.literal("at").then(Commands.argument("node",BlockPosArgument.blockPos()).executes(c->start(c.getSource(),BlockPosArgument.getBlockPos(c,"node")))))
    .then(Commands.literal("cancel").executes(c->{var source=c.getSource();var player=source.getPlayerOrException();var jobs=JOBS.get(source.getServer());boolean removed=jobs!=null&&jobs.remove(player.getUUID())!=null;removed=LegacyVeinCount.cancel(player)||removed;removed=DirectVeinCount.cancel(player)||removed;tell(source,removed?"Vein count cancelled; no blocks or mining progress changed.":"No active vein count.");return removed?1:0;}))));
 }
 /** Ignore hidden surrounding terrain, but stop at the first unloaded chunk. No world chunk requests. */
 private static BlockPos pick(CommandSourceStack source,ServerPlayer player){
  var materials=new HashSet<Block>();materials.add(MiningNodes.NODE.get());
  for(var element:GeologyConfig.get().deposits().getAsJsonArray("deposits")){
   var row=element.getAsJsonObject();materials.add(GeologyFeature.state(row.get("hostRock").getAsString()).getBlock());
   for(String field:List.of("richOres","associated"))for(var item:GeologyConfig.array(row,field))materials.add(GeologyFeature.state(item.getAsJsonObject().get("block").getAsString()).getBlock());
  }
  record Pick(BlockPos pos){}
  var vibranium=net.minecraft.resources.ResourceLocation.parse(WorldStartVeridiumPolicy.ORE);if(BuiltInRegistries.BLOCK.containsKey(vibranium))materials.add(BuiltInRegistries.BLOCK.get(vibranium));
  var start=player.getEyePosition();var end=start.add(player.getLookAngle().scale(128));
  Pick result=net.minecraft.world.level.BlockGetter.traverseBlocks(start,end,source.getLevel(),(level,pos)->{
   var chunk=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4);
   if(chunk==null)return new Pick(null);
   return materials.contains(chunk.getBlockState(pos).getBlock())?new Pick(pos.immutable()):null;
  },level->new Pick(null));
  return result.pos();
 }
 private static int start(CommandSourceStack source,BlockPos position){
  if(!(source.getEntity() instanceof ServerPlayer player)){source.sendFailure(Component.literal("A player is required for vein counting."));return 0;}
  if(JOBS.getOrDefault(source.getServer(),Map.of()).containsKey(player.getUUID())||LegacyVeinCount.active(player)||DirectVeinCount.active(player)){source.sendFailure(Component.literal("A vein count is already active; use /icveins count cancel."));return 0;}
  if(JOBS.getOrDefault(source.getServer(),Map.of()).size()+LegacyVeinCount.activeCount(source.getServer())+DirectVeinCount.activeCount(source.getServer())>=4){source.sendFailure(Component.literal("All four vein-count slots are occupied."));return 0;}
  var level=source.getLevel();var chunk=level.getChunkSource().getChunkNow(position.getX()>>4,position.getZ()>>4);
  if(chunk==null){source.sendFailure(Component.literal("The selected chunk is not loaded; no chunk was requested."));return 0;}
  if(!(chunk.getBlockEntity(position) instanceof MiningNodes.NodeEntity node)||!node.bound()){
   if(NativeContinentLevels.find(level).isPresent()){
    if(LegacyVeinCount.legacyCoalTarget(level,chunk.getBlockState(position).getBlock()))return LegacyVeinCount.startBoundCoal(source,player,position);
    return DirectVeinCount.start(source,player,position);
   }
   if(level.dimension()!=net.minecraft.world.level.Level.OVERWORLD){source.sendFailure(Component.literal("Regional vein identification is Overworld-only."));return 0;}
   return LegacyVeinCount.start(source,player,position);
  }
  var jobs=JOBS.computeIfAbsent(source.getServer(),s->new LinkedHashMap<>());
  if(jobs.containsKey(player.getUUID())||jobs.size()>=4){source.sendFailure(Component.literal("A count is already active or all four counting slots are occupied."));return 0;}
  var job=new Job(source,player,node,position);jobs.put(player.getUUID(),job);
  tell(source,"Counting the saved "+job.scope.family()+" deposit in bounded tick slices. This reads loaded blocks only, changes no mining progress, and reports unloaded areas explicitly. Pause extraction for a stable whole-deposit count.");return 1;
 }
 public static void tick(ServerTickEvent.Post event){
  LegacyVeinCount.tick(event.getServer());DirectVeinCount.tick(event.getServer());
  var jobs=JOBS.get(event.getServer());if(jobs==null)return;
  for(var entry:List.copyOf(jobs.entrySet()))try{if(entry.getValue().poll())jobs.remove(entry.getKey());}
  catch(RuntimeException error){jobs.remove(entry.getKey());entry.getValue().source.sendFailure(Component.literal("Vein count stopped: "+error.getMessage()+". No final total is certified."));}
  if(jobs.isEmpty())JOBS.remove(event.getServer());
 }
 public static void stop(MinecraftServer server){JOBS.remove(server);LegacyVeinCount.stop(server);DirectVeinCount.stop(server);}
 private static final class Job {
  final CommandSourceStack source;final ServerPlayer player;final MiningNodes.NodeEntity node;final BlockPos anchor;
  final MiningScanScope scope;final Set<Block> palette;final MiningScanCursor cursor;
  final Map<String,Long> blocks=new TreeMap<>();final Set<Long> missing=new HashSet<>(),untracked=new HashSet<>();
  long material,owned,other,covered,visited;boolean changing;
  final Map<Long,byte[]> ledgerBefore=new HashMap<>();
  Job(CommandSourceStack source,ServerPlayer player,MiningNodes.NodeEntity node,BlockPos anchor){
   this.source=source;this.player=player;this.node=node;this.anchor=anchor.immutable();scope=node.scope();palette=Set.copyOf(node.ores());cursor=scope.cursor(0);
   if(cursor.totalCandidates()>64000000L)throw new IllegalArgumentException("Deposit envelope exceeds bounded inspection capacity; no partial count started.");
  }
  boolean poll(){
   var level=source.getLevel();
   if(!source.hasPermission(4)||player.isRemoved()||player.serverLevel()!=level||source.getServer().getPlayerList().getPlayer(player.getUUID())!=player)return true;
   var anchorChunk=level.getChunkSource().getChunkNow(anchor.getX()>>4,anchor.getZ()>>4);
   if(anchorChunk==null||anchorChunk.getBlockEntity(anchor)!=node||!node.bound()||!scope.equals(node.scope())||!palette.equals(node.ores()))throw new IllegalStateException("Selected node unloaded or changed");
   for(int budget=0;budget<4096&&!cursor.exhausted();budget++){
    var p=cursor.current();long next=cursor.nextIndex();visited++;
    if(scope.contains(p.x(),p.y(),p.z())){
     var chunk=level.getChunkSource().getChunkNow(p.x()>>4,p.z()>>4);long key=net.minecraft.world.level.ChunkPos.asLong(p.x()>>4,p.z()>>4);
     if(chunk==null)missing.add(key);
     else{
      covered++;var pos=new BlockPos(p.x(),p.y(),p.z());var state=chunk.getBlockState(pos);
      if(chunk.hasData(MiningOreOwnership.LEDGER)){
       var ledger=chunk.getData(MiningOreOwnership.LEDGER);
       if(!ledgerBefore.containsKey(key))try{ledgerBefore.put(key,ledger.encode());}catch(java.io.IOException e){throw new IllegalStateException("Cannot observe provenance",e);}
       if(!ledger.sealed()||ledger.failed())untracked.add(key);
      }else untracked.add(key);
      if(palette.contains(state.getBlock())){
       material++;blocks.merge(BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString(),1L,Long::sum);
       if(MiningOreOwnership.owns(chunk,scope,pos))owned++;else other++;
      }
     }
    }
    cursor.advance(next);
   }
   if(!cursor.exhausted())return false;
   for(var entry:ledgerBefore.entrySet()){
    var chunk=level.getChunkSource().getChunkNow(net.minecraft.world.level.ChunkPos.getX(entry.getKey()),net.minecraft.world.level.ChunkPos.getZ(entry.getKey()));
    if(chunk==null||!chunk.hasData(MiningOreOwnership.LEDGER)){changing=true;continue;}
    try{if(!Arrays.equals(entry.getValue(),chunk.getData(MiningOreOwnership.LEDGER).encode()))changing=true;}
    catch(java.io.IOException e){throw new IllegalStateException("Cannot recheck provenance",e);}
   }
   boolean complete=missing.isEmpty()&&untracked.isEmpty()&&!changing;
   tell(source,(complete?"Whole saved deposit observed":"INCOMPLETE deposit observation")+": "+scope.family()+"; "+material+" matching material blocks observed, "+owned+" with this vein's natural ownership, "+other+" without verified matching ownership. "+covered+" shape cells read; "+missing.size()+" unloaded owner chunks, "+untracked.size()+" chunks with missing/unfinished provenance; changed provenance="+changing+". This is a multi-tick observation, not an atomic inventory or finished-ingot yield.");
   blocks.forEach((id,count)->tell(source,id+": "+count+" observed blocks"));return true;
  }
 }
}
