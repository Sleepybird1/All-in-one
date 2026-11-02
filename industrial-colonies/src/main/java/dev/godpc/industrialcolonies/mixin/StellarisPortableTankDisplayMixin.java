package dev.godpc.industrialcolonies.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** A legacy overfull tank displays full rather than requesting a nonexistent block state. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.blocks.entities.machines.FluidTankBlockEntity", remap = false)
public abstract class StellarisPortableTankDisplayMixin {
    @Redirect(method = "tick", at = @At(value = "INVOKE", target = "Ljava/lang/Math;toIntExact(J)I"), require = 1)
    private int industrialColonies$boundedFillStage(long stage) {
        return (int) Math.clamp(stage, 0L, 9L);
    }
}
