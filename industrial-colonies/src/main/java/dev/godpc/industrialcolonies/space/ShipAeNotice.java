package dev.godpc.industrialcolonies.space;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import appeng.api.parts.IPartHost;
import appeng.me.helpers.IGridConnectedBlockEntity;
/** Explanation only: physical drive maintenance remains available to remove oversized cells. */
@EventBusSubscriber(modid="industrial_colonies")
public final class ShipAeNotice {
 @SubscribeEvent public static void click(PlayerInteractEvent.RightClickBlock event) {
  if(!(event.getEntity() instanceof ServerPlayer player))return;
  var be=event.getLevel().getBlockEntity(event.getPos());
  if(be!=null&&(be instanceof IPartHost || be instanceof IGridConnectedBlockEntity)
    &&!ShipAePolicy.allowed(be))player.displayClientMessage(Component.literal(ShipAePolicy.DISABLED_MESSAGE),true);
 }
 @SubscribeEvent public static void portable(PlayerInteractEvent.RightClickItem event) {
  if(!(event.getEntity() instanceof ServerPlayer player))return;
  var item=event.getItemStack().getItem();
  if((item instanceof appeng.items.tools.powered.AbstractPortableCell || item instanceof appeng.items.tools.powered.WirelessTerminalItem)
    &&dev.ryanhcode.sable.Sable.HELPER.getContaining(player)!=null)
   player.displayClientMessage(Component.literal("Portable AE2 and wireless ground-network access are disabled aboard ships; use the stabilized local wired network."),true);
 }
}
