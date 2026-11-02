package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import dev.godpc.industrialcolonies.TFMGExpandedVatInventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Native repeated-ingredient encoding remains count-exact; fluid/output limits stay four. */
@Mixin(value = VatMachineRecipe.class, remap = false)
public abstract class TFMGVatRecipeCapacityMixin {
    @Inject(method = "getMaxInputCount", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$expandedInputs(CallbackInfoReturnable<Integer> callback) {
        callback.setReturnValue(TFMGExpandedVatInventory.MAX_INGREDIENT_UNITS);
    }
}
