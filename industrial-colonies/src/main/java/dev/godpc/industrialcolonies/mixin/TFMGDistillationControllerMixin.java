package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.content.machinery.oil_processing.distillation_tower.controller.DistillationControllerBlockEntity;
import dev.godpc.industrialcolonies.TFMGDistillationBatchPlan;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = DistillationControllerBlockEntity.class, remap = false)
public abstract class TFMGDistillationControllerMixin {
    // The second getFluidResults call is the first output in the commit loop.
    // Native selection, heat, height/width and full-output guards already ran.
    @Inject(method = "manageRecipe", at = @At(value = "INVOKE", target =
        "Lcom/drmangotea/tfmg/recipes/DistillationRecipe;getFluidResults()Lnet/minecraft/core/NonNullList;",
        ordinal = 1), cancellable = true, remap = false)
    private void industrialColonies$commitConservingBatch(CallbackInfo callback) {
        TFMGDistillationBatchPlan.complete((DistillationControllerBlockEntity) (Object) this);
        callback.cancel();
    }
}
