package dev.godpc.industrialcolonies;

import com.simibubi.create.foundation.recipe.IRecipeTypeInfo;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;

import java.util.Collections;
import java.util.Map;
import java.util.WeakHashMap;

/**
 * Associates a decoded Create recipe with the tier-specific registry entries
 * that decoded it. Weak keys allow recipes from an old /reload to be collected.
 */
public final class TieredRecipeBindings {
    private static final Map<Recipe<?>, Binding> BINDINGS =
            Collections.synchronizedMap(new WeakHashMap<>());

    private TieredRecipeBindings() {
    }

    public static <R extends Recipe<?>> R bind(R recipe, Binding binding) {
        BINDINGS.put(recipe, binding);
        return recipe;
    }

    public static Binding get(Recipe<?> recipe) {
        return BINDINGS.get(recipe);
    }

    public record Binding(
            RecipeType<?> type,
            RecipeSerializer<?> serializer,
            IRecipeTypeInfo typeInfo,
            TieredRecipeCatalog.Tier tier,
            TieredRecipeCatalog.RecipeFamily family,
            TieredRecipeCatalog.Machine machine
    ) {
    }
}
