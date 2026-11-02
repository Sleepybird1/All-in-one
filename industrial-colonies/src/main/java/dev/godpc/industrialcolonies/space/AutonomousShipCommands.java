package dev.godpc.industrialcolonies.space;

import java.util.UUID;
import net.minecraft.commands.*;
import net.minecraft.commands.arguments.UuidArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.sprocketgames.create_aeronautics_automated_logistics.service.AutomatedLogisticsServices;
import net.sprocketgames.create_aeronautics_automated_logistics.route.FailureReason;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.ShipTransponderRegistry;

/** Operator controls stop automation, retain cargo, and never delete or freeze bodies. */
public final class AutonomousShipCommands {
 private AutonomousShipCommands(){}
 public static void register(){NeoForge.EVENT_BUS.addListener(AutonomousShipCommands::commands);NeoForge.EVENT_BUS.addListener(ShipHandoffCommands::commands);NeoForge.EVENT_BUS.addListener(AutonomousShipCommands::tick);}
 public static void commands(RegisterCommandsEvent event){
  var root=Commands.literal("icships").requires(source->source.hasPermission(4));
  root.then(FreightJourneyCommands.branch());
  root.then(FreightDestinationCommands.branch());
  for(boolean disable:new boolean[]{true,false})root.then(Commands.literal(disable?"disable":"enable")
   .then(Commands.literal("all").executes(c->change(c.getSource(),null,disable)))
   .then(Commands.literal("ship").then(Commands.argument("id",UuidArgument.uuid()).executes(c->change(c.getSource(),UuidArgument.getUuid(c,"id"),disable)))));
  root.then(Commands.literal("status").executes(c->{var data=AutonomousShipControl.get(c.getSource().getServer());c.getSource().sendSuccess(()->Component.literal("All automation disabled: "+data.allDisabled()+"; individual disabled transponders: "+data.individuallyDisabled()),false);return 1;}));
  root.then(Commands.literal("list").executes(c->{for(var ship:ShipTransponderRegistry.allShips())c.getSource().sendSuccess(()->Component.literal(ship.transponderId()+" | "+ship.shipName()+" | disabled="+AutonomousShipControl.get(c.getSource().getServer()).disabled(ship.transponderId())),false);return 1;}));
  event.getDispatcher().register(root);
 }
 private static int change(CommandSourceStack source,UUID id,boolean disable){
  var server=source.getServer();var data=AutonomousShipControl.get(server);
  try{if(id==null)data.setAllDisabled(disable);else data.setDisabled(id,disable);}
  catch(IllegalStateException error){source.sendFailure(Component.literal(error.getMessage()));return 0;}
  enforce(server);FreightJourneyControl.enforce(server);server.overworld().getDataStorage().save();net.neoforged.neoforge.common.IOUtilities.waitUntilIOWorkerComplete();
  try{
   var file=server.getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT).resolve("data").resolve(AutonomousShipControl.FILE+".dat");
   var actual=net.minecraft.nbt.NbtIo.readCompressed(file,net.minecraft.nbt.NbtAccounter.create(8L*1024*1024));
   var expected=data.save(new net.minecraft.nbt.CompoundTag(),server.registryAccess());
   if(!actual.getCompound("data").equals(expected))throw new java.io.IOException("Ship-control readback mismatch");
  }catch(Exception failure){data.setDirty();source.sendFailure(Component.literal("Live controls applied, but saving could not be verified: "+failure.getMessage()));return 0;}
  source.sendSuccess(()->Component.literal((disable?"Disabled ":"Enabled ")+(id==null?"global automation switch":"ship "+id)+". Individual restrictions remain independent. Enabling does not restart a stopped route."),true);return 1;
 }
 private static void tick(ServerTickEvent.Pre event){enforce(event.getServer());FreightJourneyControl.enforce(event.getServer());ShipHandoffCoordinator.enforce(event.getServer());}
 public static void enforce(MinecraftServer server){
  dev.godpc.industrialcolonies.space.enemy.EnemyCannonHold.enforce(server);
  var data=AutonomousShipControl.get(server);if(!data.allDisabled()&&data.individuallyDisabled().isEmpty())return;
  for(var run:AutomatedLogisticsServices.SCHEDULES.runtimeScheduleSummaries())if(data.disabled(run.transponderId())){
   var level=server.getLevel(run.dimension());if(level!=null)AutomatedLogisticsServices.SCHEDULES.stop(level,run.transponderId());
  }
  for(var run:AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(server))if(data.allDisabled()||run.transponderId().filter(data::disabled).isPresent()||run.vehicleId().filter(id->AutonomousShipControl.blocksVehicle(server,run.dimension(),id)).isPresent())AutomatedLogisticsServices.PLAYBACK.stopRuntimePlayback(server,run.routeId(),FailureReason.NONE);
 }
}
