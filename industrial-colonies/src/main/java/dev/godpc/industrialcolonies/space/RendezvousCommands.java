package dev.godpc.industrialcolonies.space;

import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.UuidArgument;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/** Operator commissioning commands; no new recipes or survival unlocks. */
public final class RendezvousCommands {
    private RendezvousCommands(){}
    public static void commands(RegisterCommandsEvent event){
        var rendezvous=Commands.literal("rendezvous")
                .then(Commands.literal("start").then(Commands.argument("shipPort",BlockPosArgument.blockPos())
                .then(Commands.argument("targetPort",BlockPosArgument.blockPos())
                .then(Commands.argument("shipLever",BlockPosArgument.blockPos())
                .then(Commands.argument("targetLever",BlockPosArgument.blockPos()).executes(c->{
                    try{
                        var id=RendezvousService.start(c.getSource().getLevel(),BlockPosArgument.getLoadedBlockPos(c,"shipPort"),BlockPosArgument.getLoadedBlockPos(c,"targetPort"),BlockPosArgument.getLoadedBlockPos(c,"shipLever"),BlockPosArgument.getLoadedBlockPos(c,"targetLever"));
                        c.getSource().sendSuccess(()->Component.literal("Rendezvous started for "+id+". Existing configured levers will switch on only after capture admission. Use status or stop with this ship UUID."),false);return 1;
                    }catch(RuntimeException failure){c.getSource().sendFailure(Component.literal(failure.getMessage()==null?failure.getClass().getSimpleName():failure.getMessage()));return 0;}
                }))))));
        rendezvous.then(Commands.literal("status").then(Commands.argument("ship",UuidArgument.uuid()).executes(c->{c.getSource().sendSuccess(()->Component.literal(RendezvousService.status(c.getSource().getServer(),UuidArgument.getUuid(c,"ship"))),false);return 1;})));
        rendezvous.then(Commands.literal("stop").then(Commands.argument("ship",UuidArgument.uuid()).executes(c->{boolean stopped=RendezvousService.stop(c.getSource().getServer(),UuidArgument.getUuid(c,"ship"));c.getSource().sendSuccess(()->Component.literal(stopped?"Navigation stopped; existing physical dock lever positions retained.":"No rendezvous session for that ship."),false);return stopped?1:0;})));
        event.getDispatcher().register(Commands.literal("icships").requires(source->source.hasPermission(4)).then(rendezvous));
    }
}
