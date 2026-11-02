package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.InterstellarWarpPolicy;
import dev.waco0311.cosmowarp.block.WarpDriveBlock;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Refuses to open a Warp Drive menu for exterior or unauthorized players. */
@Mixin(value = WarpDriveBlock.class, remap = false)
public abstract class CosmowarpWarpDriveBlockMixin {
    @Inject(
            method = "useWithoutItem(Lnet/minecraft/world/level/block/state/BlockState;"
                    + "Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;"
                    + "Lnet/minecraft/world/entity/player/Player;Lnet/minecraft/world/phys/"
                    + "BlockHitResult;)Lnet/minecraft/world/InteractionResult;",
            at = @At("HEAD"),
            cancellable = true,
            require = 1)
    private void industrialColonies$authorizeMenuOpen(
            BlockState state,
            Level level,
            BlockPos pos,
            Player player,
            BlockHitResult hit,
            CallbackInfoReturnable<InteractionResult> callback
    ) {
        if (level.isClientSide) {
            return;
        }
        if (!(player instanceof ServerPlayer serverPlayer)
                || !(level.getBlockEntity(pos) instanceof WarpDriveBlockEntity drive)
                || !InterstellarWarpPolicy.mayUseWarpDriveMenu(drive, serverPlayer)) {
            callback.setReturnValue(InteractionResult.FAIL);
        }
    }
}
