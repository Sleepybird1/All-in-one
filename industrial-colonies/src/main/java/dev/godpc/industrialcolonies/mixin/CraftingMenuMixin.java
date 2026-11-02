package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Enforces mapped player-crafting stages before the result slot is populated.
 * CraftingMenu's shared helper is used by both the table and InventoryMenu's
 * 2x2 player grid, and its normal false branch clears and synchronizes slot 0.
 */
@Mixin(CraftingMenu.class)
public abstract class CraftingMenuMixin {
    @Redirect(
            method = "slotChangedCraftingGrid(Lnet/minecraft/world/inventory/AbstractContainerMenu;"
                    + "Lnet/minecraft/world/level/Level;"
                    + "Lnet/minecraft/world/entity/player/Player;"
                    + "Lnet/minecraft/world/inventory/CraftingContainer;"
                    + "Lnet/minecraft/world/inventory/ResultContainer;"
                    + "Lnet/minecraft/world/item/crafting/RecipeHolder;)V",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/inventory/ResultContainer;setRecipeUsed("
                            + "Lnet/minecraft/world/level/Level;"
                            + "Lnet/minecraft/server/level/ServerPlayer;"
                            + "Lnet/minecraft/world/item/crafting/RecipeHolder;)Z"
            )
    )
    private static boolean industrialColonies$enforcePlayerRecipeStage(
            ResultContainer result,
            Level level,
            ServerPlayer player,
            RecipeHolder<?> recipe
    ) {
        return RecipeStageGate.canUse(player, recipe)
                && result.setRecipeUsed(level, player, recipe);
    }
}
