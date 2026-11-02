package dev.godpc.industrialcolonies.mixin;

import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;

/** Read and drain native Simulated storage, rather than FluidTank's unused backing field. */
@Pseudo
@Mixin(targets = "dev.simulated_team.simulated.multiloader.tanks.neoforge.SingleTankWrapper", remap = false)
public abstract class SimulatedFluidWrapperMixin extends FluidTank {
    protected SimulatedFluidWrapperMixin() { super(0); }

    @Shadow public abstract FluidStack getFluid();
    @Shadow public abstract FluidStack drain(int amount, FluidAction action);

    @Override
    public FluidStack drain(FluidStack requested, FluidAction action) {
        if (requested.isEmpty() || !FluidStack.isSameFluidSameComponents(requested, getFluid())) {
            return FluidStack.EMPTY;
        }
        // Keep extraction, simulation, and dock ownership in the original implementation.
        return drain(requested.getAmount(), action);
    }

    @Override
    public int getFluidAmount() { return getFluid().getAmount(); }

    @Override
    public boolean isEmpty() { return getFluid().isEmpty(); }

    @Override
    public int getSpace() { return Math.max(0, getCapacity() - getFluidAmount()); }
}
