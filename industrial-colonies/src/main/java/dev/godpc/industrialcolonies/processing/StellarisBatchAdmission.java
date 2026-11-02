package dev.godpc.industrialcolonies.processing;

import com.st0x0ef.stellaris.common.blocks.entities.machines.DieselGeneratorBlockEntity;
import com.st0x0ef.stellaris.common.blocks.entities.machines.FuelRefineryBlockEntity;
import com.st0x0ef.stellaris.common.data.recipes.FuelRefineryRecipe;
import com.st0x0ef.stellaris.common.registry.FluidRegistry;
import com.st0x0ef.stellaris.common.utils.capabilities.fluid.SingleFluidStorage;
import dev.architectury.fluid.FluidStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import java.util.Optional;

/** Read-only admission for the installed Stellaris batch semantics. No fluid aliases or recipe edits. */
public final class StellarisBatchAdmission {
    private StellarisBatchAdmission() {}

    public static boolean generatorCanStart(Object target) {
        if (!(target instanceof DieselGeneratorBlockEntity generator)) return false;
        int energy = generator.getEnergyGeneratedPT();
        if (energy <= 0 || generator.getEnergy(null).insert(energy, true) != energy) return false;
        FluidStack stored = generator.getDieselTank().getFluidInTank(0);
        // Canonical admission and the paired burn hook use the same exact stored identity.
        // The opt-in bridge changes neither the native five units nor the energy amount.
        var identity=StellarisDieselIdentity.alias(stored.getFluid(),FluidRegistry.DIESEL_STILL.get())
                ?stored.getFluid():FluidRegistry.DIESEL_STILL.get();
        FluidStack requested = FluidStack.create(identity, 5);
        if (stored.getAmount() < 5 || !stored.isFluidEqual(requested)) return false;
        FluidStack available = generator.getDieselTank().drain(requested, true);
        return available.getAmount() == 5 && available.isFluidEqual(requested);
    }

    public static boolean refineryCanStart(Object target, Optional<?> found) {
        if (!(target instanceof FuelRefineryBlockEntity refinery)
                || found.isEmpty() || !(found.get() instanceof RecipeHolder<?> holder)
                || !(holder.value() instanceof FuelRefineryRecipe recipe)) return false;
        // Called after native container handling/recipe matching but before either output write.
        return nativeOutputFits(refinery.getOutputFuelTank(), recipe.fuelStack())
                && nativeOutputFits(refinery.getOutputDieselTank(), recipe.dieselStack());
    }

    private static boolean nativeOutputFits(SingleFluidStorage tank, FluidStack output) {
        long amount = output.getAmount();
        long stored = tank.getFluidValueInTank();
        long capacity = tank.getTankCapacity(0);
        if (amount <= 0 || stored < 0 || stored > capacity) return false;
        // Preserve the installed strict-less-than branch, including its exact-fit hold.
        // Merely allowing equality here cannot make the native branch write that output.
        return amount < capacity - stored && tank.fill(output.copy(), true) == amount;
    }
}
