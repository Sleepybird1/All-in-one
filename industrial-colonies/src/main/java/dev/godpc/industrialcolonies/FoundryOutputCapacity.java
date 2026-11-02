package dev.godpc.industrialcolonies;

import modernmods.modernfoundry.library.recipe.melting.IMeltingContainer;
import modernmods.modernfoundry.library.recipe.melting.IMeltingRecipe;
import modernmods.modernfoundry.smeltery.block.entity.tank.SmelteryTank;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;

/** Preflight for Modern Foundry's shared-capacity tank; never touches real fluid. */
public final class FoundryOutputCapacity {
    private FoundryOutputCapacity() {}

    public static boolean fits(IMeltingRecipe recipe, IMeltingContainer input, IFluidHandler handler) {
        // Other handlers may have per-fluid constraints; shared-volume arithmetic is not valid there.
        if (!(handler instanceof SmelteryTank<?> tank)) return false;
        Budget budget = new Budget(tank.getRemainingSpace());
        budget.fill(recipe.getOutput(input), IFluidHandler.FluidAction.EXECUTE);
        // Use the recipe's native byproduct scaling, not JEI display quantities or ore-value copies.
        recipe.handleByproducts(input, budget);
        return !budget.overflow;
    }

    private static final class Budget implements IFluidHandler {
        private int remaining;
        private boolean overflow;

        private Budget(int remaining) { this.remaining = Math.max(0, remaining); }
        @Override public int getTanks() { return 1; }
        @Override public FluidStack getFluidInTank(int tank) { return FluidStack.EMPTY; }
        @Override public int getTankCapacity(int tank) { return remaining; }
        @Override public boolean isFluidValid(int tank, FluidStack stack) { return true; }
        @Override public int fill(FluidStack stack, FluidAction action) {
            int accepted = Math.min(remaining, stack.getAmount());
            if (action.execute()) {
                overflow |= accepted != stack.getAmount();
                remaining -= accepted;
            }
            return accepted;
        }
        @Override public FluidStack drain(FluidStack stack, FluidAction action) { return FluidStack.EMPTY; }
        @Override public FluidStack drain(int amount, FluidAction action) { return FluidStack.EMPTY; }
    }
}
