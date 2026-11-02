package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.fluids.drain.ItemDrainBlockEntity;
import com.simibubi.create.content.fluids.drain.ItemDrainItemHandler;
import com.simibubi.create.content.fluids.transfer.GenericItemEmptying;
import dev.godpc.industrialcolonies.CreateMachineContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Covers direct item-capability insertion, which does not tick the drain. */
@Mixin(ItemDrainItemHandler.class)
public abstract class ItemDrainItemHandlerMixin {
    @Shadow
    private ItemDrainBlockEntity blockEntity;

    @Redirect(
            method = "insertItem",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/content/fluids/transfer/GenericItemEmptying;"
                            + "canItemBeEmptied(Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/world/item/ItemStack;)Z"
            )
    )
    private boolean industrialColonies$probeWithDrainContext(Level level, ItemStack stack) {
        try (CreateMachineContext.Scope ignored = CreateMachineContext.enter(blockEntity)) {
            return GenericItemEmptying.canItemBeEmptied(level, stack);
        }
    }
}
