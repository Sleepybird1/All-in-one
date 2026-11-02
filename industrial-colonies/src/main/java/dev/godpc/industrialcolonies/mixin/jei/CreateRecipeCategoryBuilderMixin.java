package dev.godpc.industrialcolonies.mixin.jei;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.compat.jei.category.CreateRecipeCategory;
import com.simibubi.create.foundation.recipe.IRecipeTypeInfo;
import dev.godpc.industrialcolonies.TieredCreateRecipes;
import net.minecraft.world.item.crafting.Recipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Extends Create's own category recipe supplier when it adds a native Create
 * type. This is intentionally inside Create's builder instead of a second JEI
 * category/plugin, so machine-bound recipes inherit the exact same category,
 * layout, filtering and registration lifecycle as native recipes.
 */
@Mixin(value = CreateRecipeCategory.Builder.class, remap = false)
public abstract class CreateRecipeCategoryBuilderMixin<T extends Recipe<?>> {
    @Inject(
            method = "addTypedRecipes(Lcom/simibubi/create/foundation/recipe/IRecipeTypeInfo;)"
                    + "Lcom/simibubi/create/compat/jei/category/CreateRecipeCategory$Builder;",
            at = @At("RETURN")
    )
    @SuppressWarnings({"rawtypes", "unchecked"})
    private void industrialColonies$includeMachineBoundTypes(
            IRecipeTypeInfo typeInfo,
            CallbackInfoReturnable<CreateRecipeCategory.Builder<T>> callback
    ) {
        if (!(typeInfo instanceof AllRecipeTypes baseType)) {
            return;
        }

        CreateRecipeCategory.Builder builder = (CreateRecipeCategory.Builder) (Object) this;
        TieredCreateRecipes.typesFor(baseType).forEach(customType ->
                builder.addTypedRecipes(() -> customType));

        // BASIN is Create's shared parent process and has no standalone JEI
        // category. User-authored exact-mixer basin recipes belong on the
        // normal Mixing page alongside ordinary MIXING recipes.
        if (baseType == AllRecipeTypes.MIXING) {
            TieredCreateRecipes.typesFor(AllRecipeTypes.BASIN).forEach(customType ->
                    builder.addTypedRecipes(() -> customType));
        }
    }
}
