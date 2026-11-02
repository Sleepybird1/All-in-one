package dev.godpc.industrialcolonies;

import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandlerModifiable;

/** Preserve old capability indices 0..3 inputs, 4..7 outputs; append new inputs at 8..27. */
public final class TFMGVatItemAccess implements IItemHandlerModifiable {
    private final IItemHandlerModifiable input, output;
    public TFMGVatItemAccess(IItemHandlerModifiable input, IItemHandlerModifiable output) {
        if (input.getSlots() != 24 || output.getSlots() != 4)
            throw new IllegalArgumentException("Unexpected Chemical Vat inventory dimensions");
        this.input = input; this.output = output;
    }
    public static boolean isOutput(int slot) {
        if (slot < 0 || slot >= 28) throw new IndexOutOfBoundsException(slot);
        return slot >= 4 && slot < 8;
    }
    public static int localSlot(int slot) {
        return isOutput(slot) ? slot - 4 : slot < 4 ? slot : slot - 4;
    }
    private IItemHandlerModifiable handler(int slot) { return isOutput(slot) ? output : input; }
    @Override public int getSlots() { return 28; }
    @Override public ItemStack getStackInSlot(int slot) { return handler(slot).getStackInSlot(localSlot(slot)); }
    @Override public void setStackInSlot(int slot, ItemStack stack) { handler(slot).setStackInSlot(localSlot(slot), stack); }
    @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
        return handler(slot).insertItem(localSlot(slot), stack, simulate);
    }
    @Override public ItemStack extractItem(int slot, int amount, boolean simulate) {
        return handler(slot).extractItem(localSlot(slot), amount, simulate);
    }
    @Override public int getSlotLimit(int slot) { return handler(slot).getSlotLimit(localSlot(slot)); }
    @Override public boolean isItemValid(int slot, ItemStack stack) { return handler(slot).isItemValid(localSlot(slot), stack); }
}
