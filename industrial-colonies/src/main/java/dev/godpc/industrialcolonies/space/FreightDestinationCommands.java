package dev.godpc.industrialcolonies.space;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import net.minecraft.commands.*;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;

/** Explicit operator setup. Binding never prepares, admits or moves a journey. */
public final class FreightDestinationCommands {
 private FreightDestinationCommands(){}
 private interface Action {String run()throws Exception;}
 private static int execute(CommandSourceStack source,Action action){
  try{String result=action.run();source.sendSuccess(()->Component.literal(result),false);return 1;}
  catch(Exception failure){String reason=String.valueOf(failure.getMessage());source.sendFailure(Component.literal("Destination refused: "+reason.substring(0,Math.min(reason.length(),240))));return 0;}
 }
 public static LiteralArgumentBuilder<CommandSourceStack> branch(){
  var root=Commands.literal("destination").requires(s->s.hasPermission(4));
  root.then(Commands.literal("bind").then(Commands.argument("name",StringArgumentType.word()).then(Commands.argument("pos",BlockPosArgument.blockPos()).executes(c->execute(c.getSource(),()->{
   var source=c.getSource();var server=source.getServer();var owner=source.getPlayerOrException().getUUID();String name=StringArgumentType.getString(c,"name");FreightDestinationBook.name(name);
   var pos=BlockPosArgument.getLoadedBlockPos(c,"pos");var book=FreightDestinationBook.get(server);var old=book.find(name);
   if(old.isPresent()){
    var resolved=NativeFreightDestination.resolve(server,old.get(),owner);
    if(resolved.body().getLevel()!=source.getLevel()||!resolved.port().equals(pos))throw new IllegalStateException("Name already identifies a different physical dock");
   }
   var ref=NativeFreightDestination.capture(source.getLevel(),pos,owner);book.bind(name,ref);
   return "Bound destination "+name+" to dock "+ref.endpoint()+". No journey was started.";
  })))));
  root.then(Commands.literal("status").then(Commands.argument("name",StringArgumentType.word()).executes(c->execute(c.getSource(),()->{
   var ref=FreightDestinationBook.get(c.getSource().getServer()).find(StringArgumentType.getString(c,"name")).orElseThrow(()->new IllegalArgumentException("Unknown destination"));
   NativeFreightDestination.resolve(c.getSource().getServer(),ref,ref.owner());return "Destination available: "+ref.endpoint()+" | body="+ref.body()+" | dimension="+ref.dimension()+" | owner="+ref.owner();
  }))));
  root.then(Commands.literal("list").executes(c->execute(c.getSource(),()->"Destinations: "+String.join(", ",FreightDestinationBook.get(c.getSource().getServer()).entries().keySet()))));
  root.then(Commands.literal("forget").then(Commands.argument("name",StringArgumentType.word()).executes(c->execute(c.getSource(),()->{
   var source=c.getSource();String name=StringArgumentType.getString(c,"name");FreightDestinationBook.get(source.getServer()).forget(name,source.getPlayerOrException().getUUID(),FreightJourneyControl.journal(source.getServer()));
   return "Forgot destination name "+name+". Physical dock and stored journey references are unchanged.";
  }))));
  return root;
 }
}
