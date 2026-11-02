package dev.godpc.industrialcolonies.space;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import net.minecraft.commands.*;
import net.minecraft.commands.arguments.UuidArgument;
import net.minecraft.network.chat.Component;

/** Explicit operator audit only: never grants a permit or starts a route. */
public final class FreightJourneyCommands {
 private FreightJourneyCommands(){}
 private interface Audit {String run()throws Exception;}
 private static int execute(CommandSourceStack source,Audit audit){
  try{String result=audit.run();source.sendSuccess(()->Component.literal(result),false);return 1;}
  catch(Exception failure){String text=String.valueOf(failure.getMessage());source.sendFailure(Component.literal("Journey held/refused: "+text.substring(0,Math.min(text.length(),240))));return 0;}
 }
 public static LiteralArgumentBuilder<CommandSourceStack> branch(){
  var root=Commands.literal("journey").requires(s->s.hasPermission(4));
  root.then(Commands.literal("status").executes(c->execute(c.getSource(),()->{
   var j=FreightJourneyControl.journal(c.getSource().getServer());
   if(!j.fault().isEmpty())throw new IllegalStateException("Journal storage fault; all journey admission is held");
   var entries=j.entries();
   return "Journeys: "+entries.size()+"; unfinished: "+entries.stream().filter(e->!e.phase().terminal()).count()+"; held unfinished: "+entries.stream().filter(e->!e.phase().terminal()&&j.held(e.plan().journey())).count()+". Recovery never resumes a route.";
  })).then(Commands.argument("id",UuidArgument.uuid()).executes(c->execute(c.getSource(),()->{
   var j=FreightJourneyControl.journal(c.getSource().getServer());var e=j.get(UuidArgument.getUuid(c,"id"));
   return e.plan().journey()+" | "+e.phase()+" | held="+j.held(e.plan().journey())+" | pending encounter="+!e.encounterIntent().isEmpty()+" | retained receipt="+!e.encounterReceipt().isEmpty();
  }))));
  root.then(Commands.literal("recover").then(Commands.argument("id",UuidArgument.uuid()).executes(c->execute(c.getSource(),()->{
   var recovered=OrbitalEncounterCoordinator.recover(c.getSource().getServer(),UuidArgument.getUuid(c,"id"));
   return "Native encounter recovery verified: "+recovered.phase()+". Journey remains held; no movement or route was started.";
  }))));
  return root;
 }
}
