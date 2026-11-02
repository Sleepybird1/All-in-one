package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.utils.capabilities.fluid.SingleFluidStorage;
import dev.architectury.fluid.FluidStack;
import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Native storage caps against the request twice; cap against actual custody first. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.utils.capabilities.fluid.SingleFluidStorage", remap = false)
public abstract class StellarisFluidDrainMixin {
    @WrapMethod(method="drainWithoutLimits(JZ)Ldev/architectury/fluid/FluidStack;")
    private FluidStack industrialColonies$preserveEmptiedFluid(long requested,boolean simulate,Operation<FluidStack> original) {
        var storage=(SingleFluidStorage)(Object)this;
        var before=storage.getFluidInTank(0).copy();
        var result=original.call(requested,simulate);
        // Native code reads getFluid() after shrink. A fully emptied stack reports EMPTY.
        // Repair only that exact full-drain case; preserve partial, simulated and other results.
        if(!simulate&&!before.isEmpty()&&requested>=before.getAmount()
                &&storage.isEmpty()&&result.isEmpty()) return before;
        return result;
    }

    @ModifyVariable(method = {
            "drain(Ldev/architectury/fluid/FluidStack;Z)Ldev/architectury/fluid/FluidStack;",
            "drainWithoutLimits(Ldev/architectury/fluid/FluidStack;Z)Ldev/architectury/fluid/FluidStack;"
    }, at = @At("HEAD"), argsOnly = true, ordinal = 0, require = 2)
    private FluidStack industrialColonies$boundToActualContents(FluidStack requested) {
        long stored = Math.max(0, ((SingleFluidStorage) (Object) this).getFluidValueInTank());
        long amount = Math.max(0, Math.min(requested.getAmount(), stored));
        if (amount == requested.getAmount()) return requested;
        FluidStack bounded = requested.copy();
        bounded.setAmount(amount);
        return bounded;
    }
}
