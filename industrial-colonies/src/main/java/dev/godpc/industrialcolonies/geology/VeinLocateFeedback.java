package dev.godpc.industrialcolonies.geology;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.network.chat.*;

/** Compact command feedback with vanilla-style clickable coordinate suggestions. */
final class VeinLocateFeedback {
 private VeinLocateFeedback(){}
 static void text(CommandSourceStack source,String text){source.sendSuccess(()->Component.literal(text),false);}
 static void none(CommandSourceStack source,long checked,String scope){source.sendSuccess(()->Component.literal("None found · "+checked+" spots checked.").withStyle(style->style.withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT,Component.literal(scope)))),false);}
 static void found(CommandSourceStack source,String mineral,int x,int y,int z,long checked,String evidence){
  var origin=source.getEntity()==null?source.getPosition():source.getEntity().position();
  long distance=(long)Math.hypot(x-origin.x,z-origin.z);
  var coords=Component.literal("["+x+", "+y+", "+z+"]").withStyle(style->style.withColor(ChatFormatting.GREEN).withUnderlined(true)
    .withClickEvent(new ClickEvent(ClickEvent.Action.SUGGEST_COMMAND,"/tp @s "+x+" "+y+" "+z))
    .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT,Component.literal("Suggest teleport. Horizontal distance from your current position. "+checked+" spots checked. "+evidence))));
  var result=Component.literal(mineral+": ").append(coords).append(" · "+distance+" blocks away.");source.sendSuccess(()->result,false);
 }
}
