package dev.godpc.industrialcolonies.space;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerContainerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;

/** Keeps interplanetary freight physical without changing terrestrial storage. */
public final class OffworldEnderChestGate {
    private OffworldEnderChestGate() {
    }

    public static void register() {
        NeoForge.EVENT_BUS.addListener(OffworldEnderChestGate::onRightClickBlock);
        NeoForge.EVENT_BUS.addListener(OffworldEnderChestGate::onChangedDimension);
        NeoForge.EVENT_BUS.addListener(OffworldEnderChestGate::onContainerOpened);
    }

    private static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        if (!event.getLevel().getBlockState(event.getPos()).is(Blocks.ENDER_CHEST)
                || !AmbientKineticPolicy.isManagedOffworld(event.getLevel())) {
            return;
        }

        event.setCancellationResult(InteractionResult.FAIL);
        event.setCanceled(true);
        if (event.getEntity() instanceof ServerPlayer player) {
            player.displayClientMessage(
                    Component.translatable("message.industrial_colonies.offworld_ender_chest"),
                    true);
        }
    }

    private static void onChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (AmbientKineticPolicy.isManagedOffworld(event.getTo().location())) {
            closeEnderChestMenu(event.getEntity());
        }
    }

    private static void onContainerOpened(PlayerContainerEvent.Open event) {
        if (AmbientKineticPolicy.isManagedOffworld(event.getEntity().level())) {
            closeEnderChestMenu(event.getEntity());
        }
    }

    private static void closeEnderChestMenu(net.minecraft.world.entity.player.Player player) {
        if (player.containerMenu instanceof ChestMenu menu
                && menu.getContainer() == player.getEnderChestInventory()) {
            player.closeContainer();
        }
    }
}
