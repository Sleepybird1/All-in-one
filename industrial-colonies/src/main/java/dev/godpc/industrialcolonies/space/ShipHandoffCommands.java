package dev.godpc.industrialcolonies.space;

import java.util.*;
import net.minecraft.commands.*;
import net.minecraft.commands.arguments.*;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.TagParser;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.*;
import net.sprocketgames.create_aeronautics_automated_logistics.identity.ShipTransponderRegistry;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;

/** Staged operator interface; all coordinates are native station coordinates in the command dimension. */
public final class ShipHandoffCommands {
 private ShipHandoffCommands(){}
 private interface Operation {String run()throws Exception;}
 private static int execute(CommandSourceStack source,Operation action){try{String text=action.run();source.sendSuccess(()->Component.literal(text),true);return 1;}catch(Exception error){source.sendFailure(Component.literal("Handoff held/refused: "+error.getMessage()));return 0;}}
 public static void commands(RegisterCommandsEvent event){
  var root=Commands.literal("ichandoff").requires(s->s.hasPermission(4));
  root.then(Commands.literal("status").executes(c->execute(c.getSource(),()->{
   var j=ShipHandoffCoordinator.journal(c.getSource().getServer());
   for(var e:j.entries())c.getSource().sendSuccess(()->Component.literal(e.transaction()+" | ship="+e.transponder()+" | "+e.phase()+" | restart audit="+j.recoveryRequired(e.transaction())+" | "+e.reason()),false);
   return "Journal fault: "+(j.fault().isEmpty()?"none":j.fault())+". Release never auto-starts a route.";
  })));
  root.then(Commands.literal("prepare").then(Commands.argument("ship",UuidArgument.uuid()).then(Commands.argument("station",BlockPosArgument.blockPos()).then(Commands.argument("destination",DimensionArgument.dimension()).executes(c->execute(c.getSource(),()->{
   var source=c.getSource();var level=source.getLevel();var station=station(level,BlockPosArgument.getLoadedBlockPos(c,"station"));
   UUID ship=UuidArgument.getUuid(c,"ship");var snap=ShipTransponderRegistry.snapshot(ship).orElseThrow(()->new IllegalStateException("Unknown transponder"));
   require(snap.dimension().equals(level.dimension()),"Source ship must be in command dimension");
   require(level.hasChunkAt(snap.transponderPos()),"Source transponder chunk is unloaded");
   require(level.getBlockEntity(snap.transponderPos()) instanceof ShipTransponderBlockEntity,"Source transponder missing");
   var transponder=(ShipTransponderBlockEntity)level.getBlockEntity(snap.transponderPos());require(transponder.transponderId().equals(ship),"Source identity changed");
   require(station.ownerId().equals(transponder.ownerId())&&transponder.ownerId().isPresent(),"Station and ship owners must match");
   require(!station.isRecording(),"Station still recording");
   var route=station.recordedRoute().orElseThrow(()->new IllegalStateException("Source station has no saved route"));
   UUID tx=ShipHandoffCoordinator.prepare(source.getServer(),transponder,route,DimensionArgument.getDimension(c,"destination").dimension());
   return "Prepared "+tx+". Automation stopped; native physical transition remains independent.";
  }))))));
  root.then(Commands.literal("arrive").then(Commands.argument("transaction",UuidArgument.uuid()).executes(c->execute(c.getSource(),()->{
   ShipHandoffCoordinator.reconcileArrival(c.getSource().getServer(),UuidArgument.getUuid(c,"transaction"));return "Native arrival verified. Bind an existing destination-local station route next.";
  }))));
  root.then(Commands.literal("recover").then(Commands.argument("transaction",UuidArgument.uuid()).executes(c->execute(c.getSource(),()->{
   ShipHandoffCoordinator.recover(c.getSource().getServer(),UuidArgument.getUuid(c,"transaction"));return "Stored and live native custody reconciled. Automation remains held; run arrive, bind and release explicitly.";
  }))));
  for(boolean release:new boolean[]{false,true})root.then(Commands.literal(release?"release":"bind").then(Commands.argument("transaction",UuidArgument.uuid()).then(Commands.argument("station",BlockPosArgument.blockPos()).executes(c->execute(c.getSource(),()->{
   var source=c.getSource();UUID tx=UuidArgument.getUuid(c,"transaction");var entry=ShipHandoffCoordinator.journal(source.getServer()).get(tx);
   var station=station(source.getLevel(),BlockPosArgument.getLoadedBlockPos(c,"station"));
   require(station.ownerId().equals(Optional.of(entry.owner())),"Destination station owner mismatch");
   require(!station.isRecording()&&!station.isPlaybackRunning()&&station.activeRouteId().isEmpty(),"Destination station must be idle");
   var route=station.recordedRoute().orElseThrow(()->new IllegalStateException("Destination station has no saved local leg"));
   if(release){
    require(source.getLevel().dimension().location().toString().equals(entry.destinationDimension()),"Wrong station dimension");
    var saved=RouteNbtSerializer.read(TagParser.parseTag(entry.destinationRoute())).orElseThrow();require(route.equals(saved),"Station leg changed after binding");
    ShipHandoffCoordinator.release(source.getServer(),tx);return "Released. Start the verified destination leg explicitly using native station controls.";
   }
   require(route.dimension().equals(source.getLevel().dimension()),"Destination leg does not belong to this station dimension");
   var bound=ShipHandoffCoordinator.bindDestinationLeg(source.getServer(),tx,route);station.linkController(bound.linkedController());station.finishRecording(bound);
   require(station.recordedRoute().equals(Optional.of(bound)),"Native station route write failed");
   return "Bound and journaled native destination leg. Automation remains held until explicit release.";
  })))));
  event.getDispatcher().register(root);
 }
 private static AirshipStationBlockEntity station(ServerLevel level,BlockPos position){require(level.getBlockEntity(position) instanceof AirshipStationBlockEntity,"An actual native airship station is required");return (AirshipStationBlockEntity)level.getBlockEntity(position);}
 private static void require(boolean value,String message){if(!value)throw new IllegalStateException(message);}
}
