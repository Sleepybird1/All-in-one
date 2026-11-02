package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.utils.capabilities.fluid.SingleFluidStorage;
import dev.architectury.fluid.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;

/** Preserve existing saved/synchronized tank cargo; normal fill still enforces capacity. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.blocks.entities.machines.FluidTankBlockEntity$1", remap = false)
public abstract class StellarisPortableTankContentsMixin extends SingleFluidStorage {
    protected StellarisPortableTankContentsMixin(long capacity) { super(capacity); }

    @Override
    public void setFluidInTank(FluidStack contents) {
        stack = contents.copy();
        onChange();
    }
}
