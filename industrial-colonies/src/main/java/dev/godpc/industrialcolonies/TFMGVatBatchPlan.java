package dev.godpc.industrialcolonies;

import com.drmangotea.tfmg.content.machinery.vat.base.VatBlock;
import com.drmangotea.tfmg.content.machinery.vat.base.VatBlockEntity;
import com.drmangotea.tfmg.content.machinery.vat.base.IVatMachine;
import com.drmangotea.tfmg.mixin.accessor.TankSegmentAccessor;
import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import com.simibubi.create.foundation.blockEntity.behaviour.fluid.SmartFluidTankBehaviour;
import com.simibubi.create.foundation.fluid.SmartFluidTank;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.fluids.FluidStack;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

/** Snapshot and commit one complete batch on the server thread. No pending or voided products. */
public final class TFMGVatBatchPlan {
    private TFMGVatBatchPlan() {}
    private record Inputs(List<ItemStack> items, List<FluidStack> fluids) {}

    public static List<SmartFluidTank> tanks(SmartFluidTankBehaviour behaviour) {
        return Arrays.stream(behaviour.getTanks())
            .map(segment -> ((TankSegmentAccessor) segment).tfmg$tank()).toList();
    }

    public static boolean machineAllows(VatBlockEntity vat, VatMachineRecipe recipe) {
        if (vat.getLevel() == null) return false;
        // Native tick refreshes its cached validity only after handleRecipe. Check the
        // actual machines now so power loss, removal or a mode change cannot advance it.
        for (var entry : vat.machineMap.entrySet()) {
            if (!(vat.getLevel().getBlockEntity(entry.getKey()) instanceof IVatMachine machine)
                    || !entry.getValue().equals(machine.getOperationId())
                    || !machine.canOperate(vat)) return false;
        }
        return vat.getTotalTankSize() >= recipe.minSize && vat.areMachinesValid
            && VatAttachmentRequirements.matches(recipe.machines, vat.machineMap.values())
            && vat.getBlockState().getBlock() instanceof VatBlock block
            && recipe.allowedVatTypes.contains(block.vatType)
            && MachineRecipeStageGate.canUse(vat, recipe);
    }

    private static Optional<Inputs> inputs(VatBlockEntity vat, VatMachineRecipe recipe) {
        var items = new ArrayList<ItemStack>();
        for (int slot=0; slot<vat.inputInventory.getSlots(); slot++) {
            if (vat.inputInventory.getStackInSlot(slot).getCount() > vat.inputInventory.getSlotLimit(slot))
                return Optional.empty();
            items.add(vat.inputInventory.getStackInSlot(slot).copy());
        }
        int[] unitAmounts = new int[recipe.getIngredients().size()];
        Arrays.fill(unitAmounts, 1); // Native Ingredient consumes one; codegen repeats exact counts.
        var itemPlan = VatInputAllocation.reserve(items.stream().mapToInt(ItemStack::getCount).toArray(),
            unitAmounts, (requirement, slot) -> !items.get(slot).isEmpty()
                && recipe.getIngredients().get(requirement).test(items.get(slot)));
        if (itemPlan.isEmpty()) return Optional.empty();
        for (int i = 0; i < items.size(); i++) items.get(i).setCount(itemPlan.get()[i]);
        var fluids = new ArrayList<FluidStack>();
        for (var tank : tanks(vat.inputTank)) {
            if (tank.getFluid().getAmount() > tank.getCapacity()) return Optional.empty();
            fluids.add(tank.getFluid().copy());
        }
        // Test identity/components separately from amount, so a repeated fluid demand can
        // span available tanks without counting the same mB twice.
        var fluidPlan = VatInputAllocation.reserve(fluids.stream().mapToInt(FluidStack::getAmount).toArray(),
            recipe.getFluidIngredients().stream().mapToInt(ingredient -> ingredient.amount()).toArray(),
            (requirement, slot) -> !fluids.get(slot).isEmpty()
                && recipe.getFluidIngredients().get(requirement).ingredient().test(fluids.get(slot)));
        if (fluidPlan.isEmpty()) return Optional.empty();
        for (int i = 0; i < fluids.size(); i++) fluids.get(i).setAmount(fluidPlan.get()[i]);
        return Optional.of(new Inputs(items, fluids));
    }

    public static boolean hasInputs(VatBlockEntity vat, VatMachineRecipe recipe) {
        return inputs(vat, recipe).isPresent();
    }

    public static boolean outputsFit(VatBlockEntity vat, VatMachineRecipe recipe) {
        var maximum = recipe.getRollableResults().stream().filter(out -> out.getChance() > 0)
            .map(out -> out.getStack().copy()).toList();
        return VatOutputReservation.items(vat.outputInventory, maximum).isPresent()
            && VatOutputReservation.fluids(tanks(vat.outputTank), recipe.getFluidResults()).isPresent();
    }

    public static boolean complete(VatBlockEntity vat, VatMachineRecipe recipe) {
        if (vat.getLevel() == null || vat.getLevel().isClientSide || !machineAllows(vat, recipe)) return false;
        var input = inputs(vat, recipe);
        if (input.isEmpty() || !outputsFit(vat, recipe)) return false;
        // No random calls occur until every possible output fits. Each output rolls once.
        var rolled = recipe.getRollableResults().stream()
            .map(out -> out.rollOutput(vat.getLevel().random)).toList();
        var itemOutput = VatOutputReservation.items(vat.outputInventory, rolled).orElseThrow();
        var outputTanks = tanks(vat.outputTank);
        var fluidOutput = VatOutputReservation.fluids(outputTanks, recipe.getFluidResults()).orElseThrow();
        // Callbacks may clear vat.recipe. This transaction uses only the captured snapshots.
        for (int i=0; i<input.get().items().size(); i++) vat.inputInventory.setStackInSlot(i, input.get().items().get(i));
        var inputTanks = tanks(vat.inputTank);
        for (int i=0; i<inputTanks.size(); i++) inputTanks.get(i).setFluid(input.get().fluids().get(i));
        for (int i=0; i<itemOutput.size(); i++) vat.outputInventory.setStackInSlot(i, itemOutput.get(i));
        for (int i=0; i<outputTanks.size(); i++) outputTanks.get(i).setFluid(fluidOutput.get(i));
        vat.setChanged();
        vat.sendData();
        return true;
    }
}
