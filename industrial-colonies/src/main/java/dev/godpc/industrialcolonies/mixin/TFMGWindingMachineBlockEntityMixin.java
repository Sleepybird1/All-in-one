package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.recipes.WindingRecipe;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Exact-ID checks for TFMG's cached Winding Machine recipe. */
@Mixin(
        targets = "com.drmangotea.tfmg.content.machinery.misc.winding_machine.WindingMachineBlockEntity",
        remap = false
)
public abstract class TFMGWindingMachineBlockEntityMixin {
    @Shadow
    public WindingRecipe recipe;

    @Inject(method = "findRecipe", at = @At("RETURN"), remap = false)
    private void industrialColonies$discardLockedWindingRecipe(CallbackInfo callback) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.recipe != null && !MachineRecipeStageGate.canUse(machine, this.recipe)) {
            this.recipe = null;
        }
    }

    @Inject(method = "performRecipe", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedWindingOutput(CallbackInfo callback) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.recipe != null && !MachineRecipeStageGate.canUse(machine, this.recipe)) {
            callback.cancel();
        }
    }
}
