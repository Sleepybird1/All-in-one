package dev.godpc.industrialcolonies;

import mekanism.api.recipes.MekanismRecipe;
import mekanism.common.recipe.lookup.IRecipeLookupHandler;
import mekanism.common.tile.base.TileEntityMekanism;
import net.minecraft.resources.ResourceLocation;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Server-side, owner-team stage checks for recipes executed by Mekanism's
 * cached machine recipe monitor.
 */
public final class MekanismRecipeStageGate {
    private static final Object RECIPE_ID_CACHE_LOCK = new Object();
    private static final Map<MekanismRecipe<?>, ResourceLocation> RECIPE_IDS = new IdentityHashMap<>();

    private MekanismRecipeStageGate() {
    }

    static void clearRecipeIdCache() {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            RECIPE_IDS.clear();
        }
    }

    /**
     * Unmapped recipes pass through. Mapped recipes fail closed when the
     * handler is not an owned Mekanism tile or its owner's team lacks the
     * exact MineColonies research stage.
     */
    public static boolean canProcess(IRecipeLookupHandler<?> handler, MekanismRecipe<?> recipe) {
        ResourceLocation recipeId = findRecipeId(handler, recipe);
        if (recipeId == null) {
            return true;
        }
        ResourceLocation requiredStage = RecipeStageGate.requiredStage(recipeId);
        if (requiredStage == null) {
            return true;
        }
        if (handler.getLevel() == null || handler.getLevel().isClientSide()) {
            return true;
        }
        if (!(handler instanceof TileEntityMekanism tile)) {
            return false;
        }
        UUID owner = tile.getOwnerUUID();
        if (owner == null) {
            return deny(tile);
        }

        boolean allowed = RecipeStageGate.canUse(owner, recipeId);
        return allowed || deny(tile);
    }

    private static boolean deny(TileEntityMekanism tile) {
        tile.setActive(false);
        return false;
    }

    private static ResourceLocation findRecipeId(IRecipeLookupHandler<?> handler, MekanismRecipe<?> recipe) {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            ResourceLocation cached = RECIPE_IDS.get(recipe);
            if (cached != null) {
                return cached;
            }
            // Dynamic food recipes have no registered type or stage-mappable holder ID.
            var recipeType = handler.getRecipeType();
            if (recipeType == null) {
                return null;
            }
            for (var holder : recipeType.getRecipes(handler.getLevel())) {
                if (holder.value() == recipe) {
                    RECIPE_IDS.put(recipe, holder.id());
                    return holder.id();
                }
            }
            return null;
        }
    }
}
