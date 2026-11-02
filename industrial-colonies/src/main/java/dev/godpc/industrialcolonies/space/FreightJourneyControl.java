package dev.godpc.industrialcolonies.space;

import java.util.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.storage.LevelResource;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;
import net.sprocketgames.create_aeronautics_automated_logistics.service.AutomatedLogisticsServices;

/** Admission boundary for the staged journey driver; no route or propulsion starts here. */
public final class FreightJourneyControl {
 private static final Map<MinecraftServer,FreightJourneyJournal> JOURNALS=new WeakHashMap<>();
 private FreightJourneyControl(){}
 public static synchronized FreightJourneyJournal journal(MinecraftServer server){
  return JOURNALS.computeIfAbsent(server,s->new FreightJourneyJournal(s.getWorldPath(LevelResource.ROOT).resolve("data/industrial_colonies_journeys")));
 }
 /** Native recorded playback cannot compete with an unfinished physical journey. */
 public static boolean blocks(MinecraftServer server,UUID transponder){return journal(server).unfinished(transponder);}
 public static boolean holdsBody(MinecraftServer server,UUID body){
  var journal=journal(server);if(!journal.fault().isEmpty())return true;
  return journal.entries().stream().anyMatch(e->!e.phase().terminal()&&journal.held(e.plan().journey())&&(e.body().equals(body)||e.plan().sourceBody().equals(body)));
 }
 public static boolean blocksBody(MinecraftServer server,UUID body){
  var journal=journal(server);if(!journal.fault().isEmpty())return true;
  return journal.entries().stream().anyMatch(e->!e.phase().terminal()&&(e.body().equals(body)||e.plan().sourceBody().equals(body)));
 }
 public static boolean blocksRoute(MinecraftServer server,Route route){
  var journal=journal(server);if(!journal.fault().isEmpty())return true;
  return route.linkedController().vehicleId().filter(id->blocksBody(server,id)).isPresent();
 }
 public static boolean blocksPlayback(MinecraftServer server,RouteId route){
  if(!journal(server).fault().isEmpty())return true;
  return AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server).stream().anyMatch(r->r.routeId().equals(route)&&
   (r.transponderId().filter(id->blocks(server,id)).isPresent()||r.vehicleId().filter(id->blocksBody(server,id)).isPresent()));
 }
 public static void enforce(MinecraftServer server){
  var journal=journal(server);var controls=AutonomousShipControl.get(server);
  for(var entry:journal.entries())if(!entry.phase().terminal()&&!journal.held(entry.plan().journey())&&controls.disabled(entry.plan().transponder())){
   try{journal.hold(entry.plan().journey(),"Operator disabled ship automation");}
   catch(java.io.IOException failure){break;} // Journal fault revokes every permit and fails admission closed.
  }
  boolean fault=!journal.fault().isEmpty();if(!fault&&journal.entries().stream().allMatch(e->e.phase().terminal()))return;
  for(var run:AutomatedLogisticsServices.SCHEDULES.runtimeScheduleSummaries())if(fault||blocks(server,run.transponderId())){
   var level=server.getLevel(run.dimension());if(level!=null)AutomatedLogisticsServices.SCHEDULES.stop(level,run.transponderId());
  }
  for(var run:AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server))if(fault||run.transponderId().filter(id->blocks(server,id)).isPresent()||run.vehicleId().filter(id->blocksBody(server,id)).isPresent())
   AutomatedLogisticsServices.PLAYBACK.stopRuntimePlayback(server,run.routeId(),FailureReason.NONE);
 }
}
