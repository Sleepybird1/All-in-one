package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.ItemCombinerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.SmithingMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.SmithingRecipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import javax.annotation.Nullable;

/**
 * Applies the shared exact-recipe stage gate to vanilla smithing.
 *
 * <p>The ordinary crafting hook cannot see {@link SmithingMenu}. Clearing the
 * server result slot here prevents old-world currency stock from producing a
 * higher-tier tool or armor piece before its University research is complete.
 * The pickup hook is a second fail-closed guard for shift-click and packet
 * ordering edge cases.</p>
 */
@Mixin(SmithingMenu.class)
public abstract class SmithingMenuMixin extends ItemCombinerMenu {
    @Shadow
    @Nullable
    private RecipeHolder<SmithingRecipe> selectedRecipe;

    protected SmithingMenuMixin(
            @Nullable MenuType<?> menuType,
            int containerId,
            Inventory inventory,
            ContainerLevelAccess access
    ) {
        super(menuType, containerId, inventory, access);
    }

    @Inject(method = "createResult", at = @At("RETURN"))
    private void industrialColonies$clearLockedSmithingResult(CallbackInfo callback) {
        if (this.selectedRecipe != null
                && this.player instanceof ServerPlayer serverPlayer
                && !RecipeStageGate.canUse(serverPlayer, this.selectedRecipe)) {
            this.selectedRecipe = null;
            this.resultSlots.setRecipeUsed(null);
            this.resultSlots.setItem(0, ItemStack.EMPTY);
        }
    }

    @Inject(method = "mayPickup", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$denyLockedSmithingPickup(
            Player player,
            boolean hasItem,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (this.selectedRecipe != null
                && player instanceof ServerPlayer serverPlayer
                && !RecipeStageGate.canUse(serverPlayer, this.selectedRecipe)) {
            callback.setReturnValue(false);
        }
    }
}
