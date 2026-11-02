package dev.godpc.industrialcolonies;

import appeng.recipes.AERecipeTypes;
import appeng.recipes.game.CraftingUnitTransformRecipe;
import appeng.recipes.game.StorageCellDisassemblyRecipe;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;

/** Player-aware exact-ID checks for AE2's non-crafting-grid transform recipes. */
public final class AE2RecipeStageGate {
    private AE2RecipeStageGate() {
    }

    public static boolean canDisassemble(ServerPlayer player, Level level, Item cell) {
        for (RecipeHolder<StorageCellDisassemblyRecipe> holder
                : level.getRecipeManager().getAllRecipesFor(AERecipeTypes.CELL_DISASSEMBLY)) {
            if (holder.value().getStorageCell() == cell) {
                return RecipeStageGate.canUse(player, holder);
            }
        }
        return true;
    }

    public static boolean canApplyUpgrade(ServerPlayer player, Level level, ItemStack upgrade) {
        for (RecipeHolder<CraftingUnitTransformRecipe> holder
                : level.getRecipeManager().getAllRecipesFor(AERecipeTypes.CRAFTING_UNIT_TRANSFORM)) {
            if (holder.value().getUpgradeItem() == upgrade.getItem()) {
                return RecipeStageGate.canUse(player, holder);
            }
        }
        return true;
    }

    public static boolean canRemoveUpgrade(ServerPlayer player, Level level, Block upgradedBlock) {
        for (RecipeHolder<CraftingUnitTransformRecipe> holder
                : level.getRecipeManager().getAllRecipesFor(AERecipeTypes.CRAFTING_UNIT_TRANSFORM)) {
            if (holder.value().getUpgradedBlock() == upgradedBlock) {
                return RecipeStageGate.canUse(player, holder);
            }
        }
        return true;
    }
}
