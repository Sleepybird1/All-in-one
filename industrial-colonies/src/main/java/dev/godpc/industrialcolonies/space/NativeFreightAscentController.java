package dev.godpc.industrialcolonies.space;

import java.util.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.service.AutomatedLogisticsServices;
import dev.godpc.industrialcolonies.space.FreightJourneyJournal.*;

/** Native vertical-ascent command boundary, extracted from the qualified lab
 * flight. The enclosing adapter still verifies cargo, physical resources,
 * clearance and completion before every call. No admission, phase advancement,
 * hardware installation, destination creation or automatic resume occurs here. */
public final class NativeFreightAscentController {
 private final MinecraftServer server;
 private final FreightJourneyJournal journal;
 private final UUID journey;
 private final NativeFreightSourceRoute.Contract contract;
 private NativeFreightSourceRoute.Live commanded;
 private ServerLevel commandedLevel;
 private long lastTick=-1;
 public NativeFreightAscentController(MinecraftServer server,UUID journey)throws Exception{
  this.server=Objects.requireNonNull(server);thread();this.journey=Objects.requireNonNull(journey);
  journal=FreightJourneyControl.journal(server);var entry=journal.get(journey);
  contract=NativeFreightSourceRoute.parse(entry.plan());
  NativeFreightSourceRoute.resolveForSourcePhase(server,entry,contract);
 }
 public NativeFreightSourceRoute.Contract contract(){return contract;}
 public void step(Entry entry,Permit permit){
  thread();
  require(entry.plan().journey().equals(journey)&&journal.get(journey).equals(entry)
   &&permit.journey().equals(journey)&&journal.admits(permit)&&entry.phase()==Phase.ASCENT,
   "Exact current ASCENT entry and permit required");
  require(!AutonomousShipControl.get(server).disabled(contract.transponder()),"Ship automation disabled");
  require(!AutomatedLogisticsServices.SCHEDULES.isRunning(contract.transponder())
   &&!AutomatedLogisticsServices.PLAYBACK.isRunning(contract.routeId()),"Competing native flight controller");
  long now=server.getTickCount();require(now>=0&&now>lastTick,"Duplicate or nonmonotonic ascent command");
  var live=NativeFreightSourceRoute.resolveForSourcePhase(server,entry,contract);
  var position=live.controller().position();
  require(Math.abs(position.x-contract.destination().x)<8&&Math.abs(position.z-contract.destination().z)<8
   &&position.y>=contract.start().y-8&&position.y<contract.destination().y+80,"Outside qualified ascent corridor");
  // Remember only the original actuator actually commanded. Stop must work
  // after a permit is revoked, and must never target a replacement body.
  commanded=live;commandedLevel=server.getLevel(contract.dimension());lastTick=now;
  var result=live.controller().moveToward(commandedLevel,contract.destination(),160.0,8.0);
  require(result.successful(),"Native source movement refused: "+result.failureReason());
 }
 public void stop(){
  thread();
  if(commanded!=null&&!commanded.body().isRemoved())commanded.controller().stop(commandedLevel);
  commanded=null;commandedLevel=null;
 }
 private void thread(){require(server.isSameThread(),"Ascent commands require server thread");}
 private static void require(boolean value,String reason){if(!value)throw new IllegalStateException(reason);}
}
