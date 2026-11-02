package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.SableCollisionShapes;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Avoid Sable's shared state-only cache and origin-based contextual shape queries. */
@Pseudo
@Mixin(targets = "dev.ryanhcode.sable.physics.chunk.VoxelNeighborhoodState", remap = false)
public abstract class SableVoxelCacheMixin {
    @Inject(method = "isSolid", at = @At("HEAD"), cancellable = true, require = 1)
    private static void industrialColonies$safeSolid(BlockGetter level, BlockPos pos,
            BlockState state, CallbackInfoReturnable<Boolean> cir) {
        // A state alone cannot cache a shape that depends on location/neighbors.
        // Vanilla retains its own safe static-shape caches where appropriate.
        cir.setReturnValue(SableCollisionShapes.isSolid(level, pos, state));
    }

    @Inject(method = "isFullBlock", at = @At("HEAD"), cancellable = true, require = 1)
    private static void industrialColonies$safeFull(BlockGetter level, BlockPos pos,
            BlockState state, CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(SableCollisionShapes.isFullBlock(level, pos, state));
    }
}
