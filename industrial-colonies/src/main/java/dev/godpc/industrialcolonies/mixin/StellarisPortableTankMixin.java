package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.utils.capabilities.fluid.SingleFluidStorage;
import dev.architectury.fluid.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Generic carryable tanks only; oxygen equipment and vehicle fuel use other blocks. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.blocks.machines.FluidTankBlock", remap = false)
public abstract class StellarisPortableTankMixin {
    @ModifyVariable(method = "<init>", at = @At("HEAD"), argsOnly = true, ordinal = 0, require = 1)
    private static long industrialColonies$portableCapacity(long nativeCapacity) {
        return Math.min(nativeCapacity, 8000L);
    }

    // Placement transfers custody from the consumed item; it is not a refill operation.
    @Redirect(method = "setPlacedBy", at = @At(value = "INVOKE",
            target = "Lcom/st0x0ef/stellaris/common/utils/capabilities/fluid/SingleFluidStorage;fill(Ldev/architectury/fluid/FluidStack;Z)J"), require = 1)
    private long industrialColonies$preservePlacedContents(SingleFluidStorage tank, FluidStack contents, boolean simulate) {
        if (!tank.isEmpty()) return tank.fill(contents, simulate);
        if (!simulate) tank.setFluidInTank(contents);
        return contents.getAmount();
    }
}
