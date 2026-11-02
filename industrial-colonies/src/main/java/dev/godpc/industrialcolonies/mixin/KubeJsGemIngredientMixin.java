package dev.godpc.industrialcolonies.mixin;

import net.minecraft.world.item.crafting.Ingredient;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Retain explicit gem predicates while Apotheosis's data registry is still loading. */
@Pseudo
@Mixin(targets = "dev.latvian.mods.kubejs.recipe.component.IngredientComponent", remap = false)
public abstract class KubeJsGemIngredientMixin {
    @Inject(method = "isEmpty(Lnet/minecraft/world/item/crafting/Ingredient;)Z",
            at = @At("HEAD"), cancellable = true)
    private void industrialColonies$preserveGemPredicate(Ingredient ingredient,
            CallbackInfoReturnable<Boolean> cir) {
        var custom = ingredient.getCustomIngredient();
        if (custom != null && custom.getClass().getName()
                .equals("dev.shadowsoffire.apotheosis.util.GemIngredient")) {
            // An unresolved display list is not an explicitly empty ingredient.
            // Keep the original predicate; absent/wrong gems still cannot match.
            cir.setReturnValue(false);
        }
    }
}
