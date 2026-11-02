package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Rejects a cached AE2 Inscriber task unless its exact ID is unlocked by the owner team. */
@Mixin(targets = "appeng.blockentity.misc.InscriberBlockEntity", remap = false)
public abstract class AE2InscriberBlockEntityMixin {
    @Inject(method = "getTask", at = @At("RETURN"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedInscriberTask(
            CallbackInfoReturnable<Recipe<?>> callback
    ) {
        Recipe<?> task = callback.getReturnValue();
        BlockEntity machine = (BlockEntity) (Object) this;
        if (task != null && !MachineRecipeStageGate.canUse(machine, task)) {
            callback.setReturnValue(null);
        }
    }
}
