package dev.godpc.industrialcolonies;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.util.IdentityHashMap;
import java.util.Map;
import java.util.UUID;

/** Exact recipe-id enforcement shared by non-Mekanism processing machines. */
public final class MachineRecipeStageGate {
    private static final Object RECIPE_ID_CACHE_LOCK = new Object();
    private static final Map<Recipe<?>, ResourceLocation> RECIPE_IDS = new IdentityHashMap<>();

    private MachineRecipeStageGate() {
    }

    static void clearRecipeIdCache() {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            RECIPE_IDS.clear();
        }
    }

    public static boolean canUse(BlockEntity machine, RecipeHolder<?> recipe) {
        return canUse(machine, recipe.id());
    }

    public static boolean canUse(BlockEntity machine, Recipe<?> recipe) {
        if (machine == null) {
            return false;
        }
        Level level = machine.getLevel();
        if (level == null || level.isClientSide()) {
            return true;
        }

        ResourceLocation recipeId = findRecipeId(level.getRecipeManager(), recipe);
        return recipeId == null || canUse(machine, recipeId);
    }

    public static boolean canUse(BlockEntity machine, ResourceLocation recipeId) {
        if (RecipeStageGate.requiredStage(recipeId) == null) {
            return true;
        }
        if (machine == null || machine.getLevel() == null) {
            return false;
        }
        if (machine.getLevel().isClientSide()) {
            return true;
        }

        UUID owner = CreateMachineOwner.get(machine);
        return owner != null && RecipeStageGate.canUse(owner, recipeId);
    }

    private static ResourceLocation findRecipeId(RecipeManager manager, Recipe<?> recipe) {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            ResourceLocation cached = RECIPE_IDS.get(recipe);
            if (cached != null) {
                return cached;
            }
            for (RecipeHolder<?> holder : manager.getRecipes()) {
                if (holder.value() == recipe) {
                    RECIPE_IDS.put(recipe, holder.id());
                    return holder.id();
                }
            }
            return null;
        }
    }
}
