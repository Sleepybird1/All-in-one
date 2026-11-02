package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.MekanismRecipeStageGate;
import mekanism.api.recipes.cache.CachedRecipe;
import mekanism.common.recipe.lookup.IRecipeLookupHandler;
import mekanism.common.recipe.lookup.monitor.RecipeCacheLookupMonitor;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = RecipeCacheLookupMonitor.class, remap = false)
public abstract class RecipeCacheLookupMonitorMixin {
    @Shadow
    @Final
    private IRecipeLookupHandler<?> handler;

    @Shadow
    protected CachedRecipe<?> cachedRecipe;

    @Inject(
            method = "updateAndProcess()Z",
            at = @At(
                    value = "INVOKE",
                    target = "Lmekanism/api/recipes/cache/CachedRecipe;process()V",
                    remap = false
            ),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$enforceOwnerTeamStage(CallbackInfoReturnable<Boolean> callback) {
        if (!MekanismRecipeStageGate.canProcess(handler, cachedRecipe.getRecipe())) {
            callback.setReturnValue(false);
        }
    }
}
