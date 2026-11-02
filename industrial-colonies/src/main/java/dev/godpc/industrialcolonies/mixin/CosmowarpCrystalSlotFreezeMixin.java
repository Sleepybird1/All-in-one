package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.WarpDriveCrystalSlotAccess;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Freezes every item-handler mutation path for the route crystal while charging. */
@Mixin(value = ItemStackHandler.class, remap = false)
public abstract class CosmowarpCrystalSlotFreezeMixin {
    @Inject(
            method = "insertItem(ILnet/minecraft/world/item/ItemStack;Z)"
                    + "Lnet/minecraft/world/item/ItemStack;",
            at = @At("HEAD"),
            cancellable = true,
            require = 1)
    private void industrialColonies$freezeInsert(
            int slot,
            ItemStack stack,
            boolean simulate,
            CallbackInfoReturnable<ItemStack> callback
    ) {
        if (industrialColonies$isChargingCrystalSlot()) {
            callback.setReturnValue(stack);
        }
    }

    @Inject(
            method = "extractItem(IIZ)Lnet/minecraft/world/item/ItemStack;",
            at = @At("HEAD"),
            cancellable = true,
            require = 1)
    private void industrialColonies$freezeExtract(
            int slot,
            int amount,
            boolean simulate,
            CallbackInfoReturnable<ItemStack> callback
    ) {
        if (industrialColonies$isChargingCrystalSlot()) {
            callback.setReturnValue(ItemStack.EMPTY);
        }
    }

    @Inject(
            method = "setStackInSlot(ILnet/minecraft/world/item/ItemStack;)V",
            at = @At("HEAD"),
            cancellable = true,
            require = 1)
    private void industrialColonies$freezeDirectSet(
            int slot,
            ItemStack stack,
            CallbackInfo callback
    ) {
        if (industrialColonies$isChargingCrystalSlot()) {
            callback.cancel();
        }
    }

    private boolean industrialColonies$isChargingCrystalSlot() {
        return (Object) this instanceof WarpDriveCrystalSlotAccess access
                && access.industrialColonies$owner().isCharging();
    }
}
