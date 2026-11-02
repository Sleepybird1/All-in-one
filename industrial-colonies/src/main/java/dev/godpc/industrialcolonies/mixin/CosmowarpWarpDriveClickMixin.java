package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.InterstellarWarpPolicy;
import dev.waco0311.cosmowarp.menu.WarpDriveMenu;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ClickType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Server-authoritative freeze for every click mode while the drive charges. */
@Mixin(AbstractContainerMenu.class)
public abstract class CosmowarpWarpDriveClickMixin {
    @Inject(
            method = "clicked(IILnet/minecraft/world/inventory/ClickType;"
                    + "Lnet/minecraft/world/entity/player/Player;)V",
            at = @At("HEAD"),
            cancellable = true,
            require = 1)
    private void industrialColonies$freezeUnauthorizedClicks(
            int slotId,
            int button,
            ClickType clickType,
            Player player,
            CallbackInfo callback
    ) {
        if ((Object) this instanceof WarpDriveMenu menu
                && player instanceof ServerPlayer serverPlayer
                && !InterstellarWarpPolicy.mayUseWarpDriveMenu(
                        menu.blockEntity, serverPlayer)) {
            callback.cancel();
        }
    }
}
