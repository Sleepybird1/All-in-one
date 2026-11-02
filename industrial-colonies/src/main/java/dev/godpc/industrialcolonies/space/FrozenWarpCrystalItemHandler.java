package dev.godpc.industrialcolonies.space;

import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandler;

/**
 * Capability view that never exposes Cosmowarp's mutable concrete handler and
 * dynamically freezes all automation mutations for the full charge window.
 */
public final class FrozenWarpCrystalItemHandler implements IItemHandler {
    private final WarpDriveBlockEntity drive;
    private final IItemHandler delegate;

    public FrozenWarpCrystalItemHandler(
            WarpDriveBlockEntity drive,
            IItemHandler delegate
    ) {
        this.drive = drive;
        this.delegate = delegate;
    }

    @Override
    public int getSlots() {
        return delegate.getSlots();
    }

    @Override
    public ItemStack getStackInSlot(int slot) {
        return delegate.getStackInSlot(slot).copy();
    }

    @Override
    public ItemStack insertItem(
            int slot,
            ItemStack stack,
            boolean simulate
    ) {
        return drive.isCharging()
                ? stack
                : delegate.insertItem(slot, stack, simulate);
    }

    @Override
    public ItemStack extractItem(int slot, int amount, boolean simulate) {
        return drive.isCharging()
                ? ItemStack.EMPTY
                : delegate.extractItem(slot, amount, simulate);
    }

    @Override
    public int getSlotLimit(int slot) {
        return delegate.getSlotLimit(slot);
    }

    @Override
    public boolean isItemValid(int slot, ItemStack stack) {
        return delegate.isItemValid(slot, stack);
    }
}
