package dev.godpc.industrialcolonies;

import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.IItemHandler;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Native stack adapter for the pure Vat output reservation algorithm. */
public final class VatOutputReservation {
    private VatOutputReservation() {}

    private static final class ItemKey {
        final ItemStack stack;
        ItemKey(ItemStack stack) { this.stack = stack.copyWithCount(1); }
        @Override public boolean equals(Object other) {
            return other instanceof ItemKey key && ItemStack.isSameItemSameComponents(stack, key.stack);
        }
        // Small bounded lists only; identity is checked by equals, never base item alone.
        @Override public int hashCode() { return 0; }
    }
    private static final class FluidKey {
        final FluidStack stack;
        FluidKey(FluidStack stack) { this.stack = stack.copyWithAmount(1); }
        @Override public boolean equals(Object other) {
            return other instanceof FluidKey key && FluidStack.isSameFluidSameComponents(stack, key.stack);
        }
        @Override public int hashCode() { return 0; }
    }

    public static Optional<List<ItemStack>> items(IItemHandler handler, List<ItemStack> products) {
        var bins = new ArrayList<VatOutputPacking.Bin<ItemKey>>();
        for (int i = 0; i < handler.getSlots(); i++) {
            var stack = handler.getStackInSlot(i);
            int capacity = handler.getSlotLimit(i);
            // Existing corrupt/oversized stacks must block, not crash or be silently trimmed.
            if (stack.getCount() > capacity || stack.getCount() > stack.getMaxStackSize()) return Optional.empty();
            bins.add(new VatOutputPacking.Bin<>(stack.isEmpty() ? null : new ItemKey(stack), stack.getCount(), capacity));
        }
        var additions = new ArrayList<VatOutputPacking.Product<ItemKey>>();
        for (var stack : products) if (!stack.isEmpty())
            additions.add(new VatOutputPacking.Product<>(new ItemKey(stack), stack.getCount()));
        return VatOutputPacking.plan(bins, additions, (slot, key) -> key.stack.getMaxStackSize())
            .map(plan -> plan.stream().map(bin -> bin.amount() == 0 ? ItemStack.EMPTY : bin.key().stack.copyWithCount(bin.amount())).toList());
    }

    public static Optional<List<FluidStack>> fluids(List<? extends FluidTank> tanks, List<FluidStack> products) {
        var bins = new ArrayList<VatOutputPacking.Bin<FluidKey>>();
        for (var tank : tanks) {
            var stack = tank.getFluid();
            if (stack.getAmount() > tank.getCapacity()) return Optional.empty();
            bins.add(new VatOutputPacking.Bin<>(stack.isEmpty() ? null : new FluidKey(stack), stack.getAmount(), tank.getCapacity()));
        }
        var additions = new ArrayList<VatOutputPacking.Product<FluidKey>>();
        for (var stack : products) if (!stack.isEmpty())
            additions.add(new VatOutputPacking.Product<>(new FluidKey(stack), stack.getAmount()));
        return VatOutputPacking.plan(bins, additions,
            (slot, key) -> tanks.get(slot).isFluidValid(key.stack) ? tanks.get(slot).getCapacity() : 0)
            .map(plan -> plan.stream().map(bin -> bin.amount() == 0 ? FluidStack.EMPTY : bin.key().stack.copyWithAmount(bin.amount())).toList());
    }
}
