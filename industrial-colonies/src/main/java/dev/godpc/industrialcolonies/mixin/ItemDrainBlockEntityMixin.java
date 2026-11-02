package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.fluids.drain.ItemDrainBlockEntity;
import com.simibubi.create.content.fluids.transfer.GenericItemEmptying;
import dev.godpc.industrialcolonies.CreateMachineContext;
import net.createmod.catnip.data.Pair;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Gives every Item Drain recipe probe the drain itself as its exact-machine
 * context. Some probes run from capability/belt insertion callbacks, outside
 * the drain's normal SmartBlockEntity tick, so the global tick scope alone is
 * not sufficient for machine-bound EMPTYING recipes.
 */
@Mixin(ItemDrainBlockEntity.class)
public abstract class ItemDrainBlockEntityMixin {
    @Redirect(
            method = {"tryInsertingFromSide", "tick", "continueProcessing"},
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/fluids/transfer/GenericItemEmptying;"
                            + "canItemBeEmptied(Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/world/item/ItemStack;)Z"
            )
    )
    private boolean industrialColonies$probeWithDrainContext(Level level, ItemStack stack) {
        ItemDrainBlockEntity drain = (ItemDrainBlockEntity) (Object) this;
        try (CreateMachineContext.Scope ignored = CreateMachineContext.enter(drain)) {
            return GenericItemEmptying.canItemBeEmptied(level, stack);
        }
    }

    @Redirect(
            method = "continueProcessing",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/fluids/transfer/GenericItemEmptying;"
                            + "emptyItem(Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/world/item/ItemStack;Z)Lnet/createmod/catnip/data/Pair;"
            )
    )
    private Pair<FluidStack, ItemStack> industrialColonies$emptyWithDrainContext(
            Level level,
            ItemStack stack,
            boolean simulate
    ) {
        ItemDrainBlockEntity drain = (ItemDrainBlockEntity) (Object) this;
        try (CreateMachineContext.Scope ignored = CreateMachineContext.enter(drain)) {
            return GenericItemEmptying.emptyItem(level, stack, simulate);
        }
    }
}
