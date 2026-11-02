package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.recipes.CastingRecipe;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Covers TFMG casting's private RecipeFinder cache and cached in-progress recipe. */
@Mixin(
        targets = "com.drmangotea.tfmg.content.machinery.metallurgy.casting_basin.CastingBasinBlockEntity",
        remap = false
)
public abstract class TFMGCastingBasinBlockEntityMixin {
    @Shadow
    public CastingRecipe recipe;

    @Inject(method = "findRecipe", at = @At("RETURN"), remap = false)
    private void industrialColonies$discardLockedCastingRecipe(CallbackInfo callback) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.recipe != null && !MachineRecipeStageGate.canUse(machine, this.recipe)) {
            this.recipe = null;
        }
    }

    @Inject(method = "tick", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$pauseLockedCastingRecipe(CallbackInfo callback) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.recipe != null && !MachineRecipeStageGate.canUse(machine, this.recipe)) {
            callback.cancel();
        }
    }
}
