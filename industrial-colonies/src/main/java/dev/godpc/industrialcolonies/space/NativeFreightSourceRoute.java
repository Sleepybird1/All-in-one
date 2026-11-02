package dev.godpc.industrialcolonies.space;

import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.TagParser;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;
import net.sprocketgames.create_aeronautics_automated_logistics.vehicle.SableSubLevelVehicleController;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Read-only extraction of the currently qualified two-point vertical ascent.
 * Does not certify clearance/fuel, acquire actuators, start playback or hand off.
 * Unsupported native route features are refused rather than silently ignored. */
public final class NativeFreightSourceRoute {
 private NativeFreightSourceRoute(){}
 public record Contract(RouteId routeId,ResourceKey<Level> dimension,UUID owner,UUID body,
                        UUID transponder,BlockPos controller,Vec3 start,Vec3 destination,
                        long recordedTicks,String canonical,String digest){}
 public record Live(ServerSubLevel body,ShipTransponderBlockEntity transponder,SableSubLevelVehicleController controller){}
 public static Contract parse(Plan plan)throws Exception{
  Objects.requireNonNull(plan);var tag=TagParser.parseTag(plan.sourceRoute());
  var route=RouteNbtSerializer.read(tag).orElseThrow(()->new IllegalArgumentException("Unreadable saved native source route"));
  var canonical=RouteNbtSerializer.write(route);
  require(canonical.equals(tag),"Unknown, omitted or migrated native route fields");
  require(route.ownerId().equals(Optional.of(plan.owner()))&&route.dimension().location().toString().equals(plan.sourceDimension()),"Source route owner or dimension differs from commitment");
  var linked=route.linkedController();
  require(linked.dimension().equals(route.dimension())&&linked.vehicleId().equals(Optional.of(plan.sourceBody()))&&linked.controllerPos().isPresent()
   &&linked.controllerType().toString().equals("create_aeronautics_automated_logistics:sable_sublevel"),"Source route controller/body differs from commitment");
  require(tag.getString("transportMode").equals("airship")&&tag.getString("playbackMode").equals("ONE_WAY")&&route.stops().isEmpty()&&route.points().size()==2,"Only one-way two-point ascent without stops is qualified");
  var first=route.points().getFirst();var last=route.points().getLast();
  for(var point:route.points())require(point.dimension().equals(route.dimension())&&point.yaw().isEmpty()&&point.rotation().isEmpty()&&finite(point.position()),"Mixed dimensions, nonfinite points or orientation commands are unqualified");
  require(first.tickOffset()==0&&last.tickOffset()>0,"Recorded source clocks must start at zero and increase");
  var a=first.position();var b=last.position();
  require(b.y>a.y&&Math.abs(a.x-b.x)<=1e-3&&Math.abs(a.z-b.z)<=1e-3,"Saved source route must be an upward vertical ascent");
  String text=canonical.toString();return new Contract(route.id(),route.dimension(),plan.owner(),plan.sourceBody(),plan.transponder(),linked.controllerPos().orElseThrow().immutable(),a,b,last.tickOffset(),text,hash(text));
 }
 /** Live source identity only. A complete adapter must separately verify cargo,
  * actuator ownership, loaded collision bounds, resources and phase completion. */
 public static Live resolveForSourcePhase(MinecraftServer server,Entry entry,Contract route){
  require(server.isSameThread(),"Source-route lookup requires server thread");
  require((entry.phase()==Phase.READY||entry.phase()==Phase.ASCENT)&&entry.body().equals(route.body())&&entry.plan().sourceBody().equals(route.body())
   &&entry.plan().owner().equals(route.owner())&&entry.plan().transponder().equals(route.transponder())&&entry.plan().sourceDimension().equals(route.dimension().location().toString()),"Exact pre-handoff source phase and identity required");
  try{require(parse(entry.plan()).equals(route),"Saved source contract changed");}catch(Exception invalid){throw new IllegalStateException("Saved source contract unavailable or changed",invalid);}
  var level=server.getLevel(route.dimension());require(level!=null&&level.hasChunkAt(route.controller()),"Source controller dimension/chunk unavailable");
  var be=level.getBlockEntity(route.controller());require(be instanceof ShipTransponderBlockEntity,"Recorded source controller is not a transponder");var transponder=(ShipTransponderBlockEntity)be;
  require(!transponder.isRemoved()&&transponder.transponderId().equals(route.transponder())&&transponder.ownerId().equals(Optional.of(route.owner())),"Recorded physical source transponder or owner changed");
  var containing=Sable.HELPER.getContaining(be);require(containing instanceof ServerSubLevel&&!containing.isRemoved()&&containing.getUniqueId().equals(route.body()),"Original source body unavailable or replaced");
  var controller=SableSubLevelVehicleController.resolveControllerBlock(level,route.body(),route.controller()).orElseThrow(()->new IllegalStateException("Original native source controller unavailable"));
  require(finite(controller.position()),"Nonfinite source controller position");return new Live((ServerSubLevel)containing,transponder,controller);
 }
 private static boolean finite(Vec3 p){return Double.isFinite(p.x)&&Double.isFinite(p.y)&&Double.isFinite(p.z);}
 private static String hash(String text){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
 private static void require(boolean valid,String why){if(!valid)throw new IllegalArgumentException(why);}
}
