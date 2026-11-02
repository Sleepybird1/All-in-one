package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.InterstellarWarpPolicy;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import dev.waco0311.cosmowarp.menu.WarpDriveMenu;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Invalidates an open Warp Drive menu when authority is lost or charging begins. */
@Mixin(value = WarpDriveMenu.class, remap = false)
public abstract class CosmowarpWarpDriveMenuMixin {
    @Shadow
    @Final
    public WarpDriveBlockEntity blockEntity;

    @Inject(
            method = "stillValid(Lnet/minecraft/world/entity/player/Player;)Z",
            at = @At("RETURN"),
            cancellable = true,
            require = 1)
    private void industrialColonies$requireLiveOperator(
            Player player,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (player instanceof ServerPlayer serverPlayer) {
            callback.setReturnValue(callback.getReturnValue()
                    && InterstellarWarpPolicy.mayUseWarpDriveMenu(
                            blockEntity, serverPlayer));
        }
    }
}
