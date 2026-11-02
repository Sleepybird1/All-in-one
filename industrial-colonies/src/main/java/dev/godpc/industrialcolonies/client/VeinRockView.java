package dev.godpc.industrialcolonies.client;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterClientCommandsEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import com.mojang.brigadier.arguments.StringArgumentType;
import java.util.*;

/** Default-off local inspection. Changes render decisions only; never block state or saved generation. */
@EventBusSubscriber(modid="industrial_colonies",value=Dist.CLIENT)
public final class VeinRockView {
 private record View(boolean enabled,String family,Set<Block> rocks) {}
 private static volatile View view=new View(false,"all",Set.of());
 private static ClientLevel boundLevel;
 private VeinRockView(){}
 public static boolean enabled(){return view.enabled();}
 public static boolean hidden(BlockState state){var v=view;return v.enabled()&&!v.rocks().contains(state.getBlock());}
 public static boolean visibleRock(BlockState state){var v=view;return v.enabled()&&v.rocks().contains(state.getBlock());}
 @SubscribeEvent public static void commands(RegisterClientCommandsEvent event){
  event.getDispatcher().register(Commands.literal("icveinsview").requires(s->s.hasPermission(2))
   .executes(c->{set(view.enabled()?"off":"all");return 1;})
   .then(Commands.argument("family",StringArgumentType.word()).suggests((c,b)->{b.suggest("all");b.suggest("off");for(var row:GeologyConfig.get().deposits().getAsJsonArray("deposits"))b.suggest(row.getAsJsonObject().get("id").getAsString());return b.buildFuture();}).executes(c->{set(StringArgumentType.getString(c,"family"));return 1;})));
 }
 private static void add(Set<Block> rocks,String value){
  var id=ResourceLocation.parse(value);var block=BuiltInRegistries.BLOCK.getOptional(id).orElseThrow(()->new IllegalArgumentException("Unknown vein rock "+value));if(block.defaultBlockState().isAir())throw new IllegalArgumentException("Air cannot be a visible vein rock");rocks.add(block);
 }
 public static void set(String family){
  var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null)return;
  if(!mc.player.hasPermissions(2)){mc.player.displayClientMessage(Component.literal("Rock view requires operator/cheat permission."),false);return;}
  if(family.equals("off")){view=new View(false,"all",Set.of());boundLevel=mc.level;mc.levelRenderer.allChanged();mc.player.displayClientMessage(Component.literal("Rock-only view off; normal terrain rendering restored."),false);return;}
  try{
   var rocks=new HashSet<Block>();boolean found=false;
   for(var element:GeologyConfig.get().deposits().getAsJsonArray("deposits")){
    var row=element.getAsJsonObject();if(!family.equals("all")&&!row.get("id").getAsString().equals(family))continue;found=true;add(rocks,row.get("hostRock").getAsString());
    if(row.has("richOres"))for(var rich:row.getAsJsonArray("richOres"))add(rocks,rich.getAsJsonObject().get("block").getAsString());
   }
   if(!found||rocks.isEmpty())throw new IllegalArgumentException("Unknown or empty vein rock family");
   view=new View(true,family,Set.copyOf(rocks));boundLevel=mc.level;mc.levelRenderer.allChanged();
   mc.player.displayClientMessage(Component.literal("Rock-only view: "+family+"; "+rocks.size()+" configured host/rich rock types. Loaded terrain meshes are rebuilding. Same-material decorative/natural blocks are also visible; this is not finite ownership proof. /icveinsview off restores normal terrain."),false);
  }catch(RuntimeException error){mc.player.displayClientMessage(Component.literal("Rock view unchanged: "+error.getMessage()),false);}
 }
 @SubscribeEvent public static void tick(ClientTickEvent.Post event){
  var mc=Minecraft.getInstance();if(view.enabled()&&(mc.level!=boundLevel||mc.player==null||!mc.player.hasPermissions(2))){view=new View(false,"all",Set.of());boundLevel=mc.level;if(mc.level!=null)mc.levelRenderer.allChanged();}
 }
}
