package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.nbt.*;
import net.minecraft.resources.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.LevelResource;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.FluidStack;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.ShipTransponderRegistry;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;
import net.sprocketgames.create_aeronautics_automated_logistics.service.AutomatedLogisticsServices;
import net.sprocketgames.create_aeronautics_automated_logistics.vehicle.VehicleControllerRef;
import dev.godpc.industrialcolonies.space.ShipHandoffJournal.*;

/** Explicit, conservative handoff API. It observes native transfers; it never warps a ship. */
public final class ShipHandoffCoordinator {
 private static final Map<MinecraftServer,ShipHandoffJournal> JOURNALS=new WeakHashMap<>();
 private ShipHandoffCoordinator(){}
 public static ShipHandoffJournal journal(MinecraftServer server){return JOURNALS.computeIfAbsent(server,s->new ShipHandoffJournal(s.getWorldPath(LevelResource.ROOT).resolve("data/industrial_colonies_handoffs")));}
 private static void require(boolean value,String message){if(!value)throw new IllegalStateException(message);}
 private record Craft(ServerLevel level,ServerSubLevel body,ShipTransponderBlockEntity transponder){}
 private static List<Craft> physical(MinecraftServer server,UUID id){
  var result=new ArrayList<Craft>();
  for(var level:server.getAllLevels()){
   var container=SubLevelContainer.getContainer(level);if(container==null)continue;
   for(var body:container.getAllSubLevels())if(body instanceof ServerSubLevel ship&&!ship.isRemoved())
    for(var holder:ship.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values())
     if(be instanceof ShipTransponderBlockEntity t&&!t.isRemoved()&&t.transponderId().equals(id)&&Sable.HELPER.getContaining(t)==ship)result.add(new Craft(level,ship,t));
  }
  return result;
 }
 public static boolean blocks(MinecraftServer server,UUID transponder){return journal(server).blocks(transponder)||FreightJourneyControl.blocks(server,transponder);}
 public static boolean blocksRoute(MinecraftServer server,Route route){
  if(FreightJourneyControl.blocksRoute(server,route))return true;
  var j=journal(server);if(!j.fault().isEmpty())return true;
  // A completed transfer never authorizes a stale source-body replay/materialization.
  if(j.entries().stream().anyMatch(e->route.linkedController().vehicleId().equals(Optional.of(e.sourceBody()))))return true;
  return j.entries().stream().filter(e->e.phase()!=Phase.RELEASED).anyMatch(e->
   route.linkedController().vehicleId().map(id->id.equals(e.sourceBody())||id.toString().equals(e.destinationBody())).orElse(false)
   ||ShipTransponderRegistry.snapshot(e.transponder()).flatMap(s->s.controllerRef()).filter(ref->ref.matches(route.linkedController())).isPresent()
   ||physical(server,e.transponder()).stream().anyMatch(c->route.linkedController().vehicleId().filter(c.body().getUniqueId()::equals).isPresent()));
 }
 public static boolean blocksPlayback(MinecraftServer server,RouteId id){
  if(FreightJourneyControl.blocksPlayback(server,id))return true;
  if(!journal(server).fault().isEmpty())return true;
  return AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server).stream().anyMatch(r->r.routeId().equals(id)&&(r.transponderId().filter(t->blocks(server,t)).isPresent()||r.vehicleId().filter(b->blockedBody(server,b)).isPresent()));
 }
 private static boolean blockedBody(MinecraftServer server,UUID body){return journal(server).entries().stream().anyMatch(e->e.sourceBody().equals(body)||e.phase()!=Phase.RELEASED&&body.toString().equals(e.destinationBody()));}
 public static void enforce(MinecraftServer server){
  var j=journal(server);if(j.fault().isEmpty()&&j.entries().isEmpty())return;
  boolean fault=!j.fault().isEmpty();var identities=new HashSet<UUID>();var bodies=new HashSet<UUID>();
  for(var entry:j.entries()){
   bodies.add(entry.sourceBody());
   if(entry.phase()!=Phase.RELEASED){identities.add(entry.transponder());if(!entry.destinationBody().isEmpty())bodies.add(UUID.fromString(entry.destinationBody()));}
  }
  // One snapshot per service per tick, rather than rescanning every playback for each route.
  for(var run:AutomatedLogisticsServices.SCHEDULES.runtimeScheduleSummaries())if(fault||identities.contains(run.transponderId())){var level=server.getLevel(run.dimension());if(level!=null)AutomatedLogisticsServices.SCHEDULES.stop(level,run.transponderId());}
  for(var run:AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server))if(fault||run.transponderId().filter(identities::contains).isPresent()||run.vehicleId().filter(bodies::contains).isPresent())AutomatedLogisticsServices.PLAYBACK.stopRuntimePlayback(server,run.routeId(),FailureReason.NONE);
 }
 public static UUID prepare(MinecraftServer server,ShipTransponderBlockEntity transponder,Route sourceRoute,ResourceKey<Level> destination)throws IOException{
  require(server.isSameThread(),"Handoff requires server thread");var crafts=physical(server,transponder.transponderId());
  require(crafts.size()==1&&crafts.getFirst().transponder()==transponder,"One loaded authoritative source transponder required");Craft craft=crafts.getFirst();
  UUID owner=transponder.ownerId().orElseThrow(()->new IllegalStateException("Owned craft required"));
  require(!AutonomousShipControl.get(server).disabled(transponder.transponderId()),"Operator disabled ship");
  requireDetached(craft);
  validateRoute(sourceRoute,craft.level().dimension(),owner);
  require(sourceRoute.linkedController().vehicleId().equals(Optional.of(craft.body().getUniqueId())),"Source route belongs to another body");
  require(server.getLevel(destination)!=null&&!destination.equals(craft.level().dimension()),"Existing distinct destination required");
  Entry entry=new Entry(UUID.randomUUID(),transponder.transponderId(),owner,craft.body().getUniqueId(),craft.level().dimension().location().toString(),destination.location().toString(),RouteNbtSerializer.write(sourceRoute).toString(),"",custody(craft),Phase.PREPARED,"","");
  // Commit the guard before touching runtime state. A crash here is held on restart.
  journal(server).prepare(entry);enforce(server);return entry.transaction();
 }
 private static void validateRoute(Route route,ResourceKey<Level> dimension,UUID owner){
  require(route.dimension().equals(dimension)&&route.linkedController().dimension().equals(dimension),"Route must already belong to destination dimension");
  require(route.ownerId().equals(Optional.of(owner)),"Route owner mismatch");require(route.points().size()>=2,"Recorded route requires at least two points");
  long previous=-1;for(var point:route.points()){
   require(point.dimension().equals(dimension)&&Double.isFinite(point.position().x)&&Double.isFinite(point.position().y)&&Double.isFinite(point.position().z)&&point.tickOffset()>=0&&point.tickOffset()>=previous,"Invalid route point or dimension");previous=point.tickOffset();
  }
 }
 private static Craft verifyDestination(MinecraftServer server,Entry entry){
  return verifyDestination(server,entry,false);
 }
 private static Craft verifyDestination(MinecraftServer server,Entry entry,boolean auditedRestart){
  require(server.isSameThread(),"Handoff requires server thread");
  // Loaded containers do not prove absence from Sable's persisted holding storage.
  // Only the explicit stored/live audit can acknowledge a restart hold.
  require(auditedRestart||!journal(server).recoveryRequired(entry.transaction()),"Restart held: persisted native body custody audit required");
  require(!AutonomousShipControl.get(server).disabled(entry.transponder()),"Operator disabled ship");
  var matches=physical(server,entry.transponder());require(matches.size()==1,"Destination is missing or identity is ambiguous");Craft craft=matches.getFirst();
  requireDetached(craft);
  require(craft.level().dimension().location().toString().equals(entry.destinationDimension())&&!craft.body().getUniqueId().equals(entry.sourceBody()),"Native destination identity not established");
  require(entry.destinationBody().isEmpty()||entry.destinationBody().equals(craft.body().getUniqueId().toString()),"Previously observed destination body changed");
  for(var level:server.getAllLevels()){var c=SubLevelContainer.getContainer(level);require(c==null||c.getSubLevel(entry.sourceBody())==null,"Source body still exists");}
  require(craft.transponder().ownerId().equals(Optional.of(entry.owner())),"Destination owner changed");
  var snapshot=ShipTransponderRegistry.snapshot(entry.transponder()).orElseThrow(()->new IllegalStateException("Missing native registry snapshot"));
  require(snapshot.dimension().equals(craft.level().dimension())&&snapshot.ownerId().equals(Optional.of(entry.owner()))&&snapshot.runtimeShipId().equals(Optional.of(craft.body().getUniqueId()))&&snapshot.transponderPos().equals(craft.transponder().getBlockPos()),"Registry has not converged to actual destination");
  require(entry.custody().equals(custody(craft)),"Linked item/fluid cargo custody changed");
  require(!craft.transponder().dockOutputActive()&&craft.transponder().dockOutputOwner().isEmpty()&&!craft.transponder().scheduleActive(),"Native dock/schedule still owns ship");
  require(AutomatedLogisticsServices.SCHEDULES.runtimeScheduleSummaries().stream().noneMatch(r->r.transponderId().equals(entry.transponder())),"Native schedule runtime still owns handoff");
  var sourceRoute=readRoute(entry.sourceRoute());
  require(AutomatedLogisticsServices.DOCK_RESERVATIONS.snapshots().stream().noneMatch(r->
   java.util.stream.Stream.concat(r.holder().stream(),r.waiting().stream()).anyMatch(request->
    request.transponderId().equals(Optional.of(entry.transponder()))||request.legacyRouteId().equals(sourceRoute.id())
    ||!entry.destinationRoute().isEmpty()&&request.legacyRouteId().equals(readRoute(entry.destinationRoute()).id()))),"Native dock reservation remains held or queued");
  require(AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server).stream().noneMatch(r->r.transponderId().equals(Optional.of(entry.transponder()))||r.vehicleId().equals(Optional.of(craft.body().getUniqueId()))||r.vehicleId().equals(Optional.of(entry.sourceBody()))),"Native playback still owns handoff");
  return craft;
 }
 private static Route readRoute(String encoded){try{return RouteNbtSerializer.read(TagParser.parseTag(encoded)).orElseThrow();}catch(Exception failure){throw new IllegalStateException("Saved native route cannot be decoded",failure);}}
 /** This coordinator owns one detached craft, never a dock or a coupled trailer set. */
 private static void requireDetached(Craft craft){
  for(var holder:craft.body().getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values()){
   if(Sable.HELPER.getContaining(be)!=craft.body())continue;
   if(net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(be.getBlockState().getBlock()).toString().equals("simulated:docking_connector")){
    // Simulated is nested in the installed runtime, not exposed on our compile classpath.
    // Read only its verified public API; absent/changed signatures refuse handoff.
    try{
     boolean locked=(Boolean)be.getClass().getMethod("isLocked").invoke(be);
     boolean paired=(Boolean)be.getClass().getMethod("hasOtherConnector").invoke(be);
     require(!locked&&!paired,"Physical connector must be detached before handoff");
    }catch(ReflectiveOperationException|ClassCastException failure){throw new IllegalStateException("Native physical connector state unavailable",failure);}
   }
  }
  for(var actor:craft.body().getPlot().getBlockEntityActors()){
   var dependencies=actor.sable$getConnectionDependencies();
   if(dependencies!=null)for(var other:dependencies)
    require(other==craft.body(),"Connected body set requires separate handoff support");
  }
 }
 /** Explicit recovery requires both native persisted authority and unchanged live custody. */
 public static void recover(MinecraftServer server,UUID transaction)throws IOException{
  var j=journal(server);var entry=j.get(transaction);require(j.recoveryRequired(transaction),"Transaction does not require restart reconciliation");
  require(entry.phase()!=Phase.RELEASED,"Released transaction cannot replay");enforce(server);
  var audit=SableStoredBodyAudit.inspect(server);
  require(audit.bodies().stream().noneMatch(b->b.id().equals(entry.sourceBody())),"Source body still has native stored custody");
  var candidates=audit.bodies().stream().filter(b->b.transponders().containsKey(entry.transponder())).toList();
  require(candidates.size()==1,"Stored destination transponder missing or duplicated");var stored=candidates.getFirst();
  require(stored.referenced()&&stored.dimension().equals(entry.destinationDimension())&&stored.transponders().get(entry.transponder()).equals(Optional.of(entry.owner())),"Stored destination holding pointer, dimension or owner disagrees");
  var craft=verifyDestination(server,entry,true);require(stored.id().equals(craft.body().getUniqueId()),"Stored and live destination bodies disagree");
  j.advance(entry.advance(Phase.HELD,stored.id().toString(),entry.destinationRoute(),"Explicit native stored/live reconciliation across "+audit.hashes().size()+" unchanged files; arrival/bind/release still required"),true);
 }
 public static void reconcileArrival(MinecraftServer server,UUID transaction)throws IOException{
  var j=journal(server);var entry=j.get(transaction);enforce(server);var craft=verifyDestination(server,entry);
  j.advance(entry.advance(Phase.ARRIVED,craft.body().getUniqueId().toString(),entry.destinationRoute(),"Native identity/custody verified; destination leg required"),true);
 }
 /** Retains the destination leg's exact geometry/stops/id; changes only its controller binding. */
 public static Route bindDestinationLeg(MinecraftServer server,UUID transaction,Route destinationLeg)throws IOException{
  var j=journal(server);var entry=j.get(transaction);var craft=verifyDestination(server,entry);validateRoute(destinationLeg,craft.level().dimension(),entry.owner());
  var actual=craft.transponder().controllerRef(craft.level()).orElseThrow(()->new IllegalStateException("No destination controller"));
  require(destinationLeg.transportMode()==craft.transponder().transportMode(craft.level()),"Transport mode mismatch");
  var bound=new Route(destinationLeg.id(),destinationLeg.name(),destinationLeg.transportMode(),destinationLeg.dimension(),destinationLeg.points(),actual,destinationLeg.playbackMode(),RouteStatus.RECORDED,destinationLeg.stops(),destinationLeg.ownerId());
  var encoded=RouteNbtSerializer.write(bound);require(RouteNbtSerializer.read(encoded).filter(bound::equals).isPresent(),"Native route serialization changed semantics");
  j.advance(entry.advance(Phase.READY,craft.body().getUniqueId().toString(),encoded.toString(),"Destination leg saved; explicit release required"),true);return bound;
 }
 /** Releases admission only. Never starts a route, moves cargo, or claims a native reservation. */
 public static Route release(MinecraftServer server,UUID transaction)throws Exception{
  var j=journal(server);var entry=j.get(transaction);var craft=verifyDestination(server,entry);
  Route route=RouteNbtSerializer.read(TagParser.parseTag(entry.destinationRoute())).orElseThrow();validateRoute(route,craft.level().dimension(),entry.owner());
  require(route.linkedController().equals(craft.transponder().controllerRef(craft.level()).orElseThrow()),"Saved destination controller changed");
  j.advance(entry.advance(Phase.RELEASED,craft.body().getUniqueId().toString(),entry.destinationRoute(),"Explicit release after physical reconciliation; no automatic playback"),true);return route;
 }
 private static String custody(Craft craft){
  var t=craft.transponder();var entries=t.linkedCargo().stream().sorted(Comparator.comparing(e->e.pos().subtract(t.getBlockPos()).toShortString())).toList();
  require(!entries.isEmpty(),"Linked item/fluid cargo manifest required");StringBuilder data=new StringBuilder();var ops=RegistryOps.create(NbtOps.INSTANCE,craft.level().registryAccess());
  var seen=new HashSet<BlockPos>();
  for(var e:entries){
   require(seen.add(e.pos())&&Sable.HELPER.getContaining(craft.level(),e.pos())==craft.body(),"Cargo link is duplicated or outside craft");
   data.append(e.pos().subtract(t.getBlockPos()).toShortString()).append(':').append(e.itemStorage()).append(':').append(e.fluidStorage());
   if(e.itemStorage()){
    var items=craft.level().getCapability(Capabilities.ItemHandler.BLOCK,e.pos(),Direction.UP);require(items!=null,"Linked item handler unavailable");data.append("slots=").append(items.getSlots());
    for(int i=0;i<items.getSlots();i++){var stack=items.getStackInSlot(i);data.append('|').append(i).append('=').append(stack.isEmpty()?"empty":canonical(ItemStack.CODEC.encodeStart(ops,stack).getOrThrow()));}
   }
   if(e.fluidStorage()){
    var fluids=craft.level().getCapability(Capabilities.FluidHandler.BLOCK,e.pos(),Direction.UP);require(fluids!=null,"Linked fluid handler unavailable");data.append("tanks=").append(fluids.getTanks());
    for(int i=0;i<fluids.getTanks();i++){var stack=fluids.getFluidInTank(i);data.append('|').append(i).append('=').append(stack.isEmpty()?"empty":canonical(FluidStack.CODEC.encodeStart(ops,stack).getOrThrow()));}
   }
  }
  try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data.toString().getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 private static String canonical(Tag tag){
  if(tag instanceof CompoundTag compound){var out=new StringBuilder("{");compound.getAllKeys().stream().sorted().forEach(k->out.append(k.length()).append(':').append(k).append('=').append(canonical(compound.get(k))).append(';'));return out.append('}').toString();}
  if(tag instanceof ListTag list){var out=new StringBuilder("[");for(Tag child:list)out.append(canonical(child)).append(';');return out.append(']').toString();}
  return tag.getId()+":"+tag.toString();
 }
}
