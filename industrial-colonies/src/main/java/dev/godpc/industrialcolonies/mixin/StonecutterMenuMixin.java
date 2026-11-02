package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.DataSlot;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.inventory.StonecutterMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.StonecutterRecipe;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

/** Exact-ID stage checks for stonecutter selection, preview, and result pickup. */
@Mixin(StonecutterMenu.class)
public abstract class StonecutterMenuMixin {
    @Shadow
    @Final
    private DataSlot selectedRecipeIndex;

    @Shadow
    private List<RecipeHolder<StonecutterRecipe>> recipes;

    @Shadow
    @Final
    ResultContainer resultContainer;

    @Unique
    private Player industrialColonies$player;

    @Inject(
            method = "<init>(ILnet/minecraft/world/entity/player/Inventory;"
                    + "Lnet/minecraft/world/inventory/ContainerLevelAccess;)V",
            at = @At("RETURN")
    )
    private void industrialColonies$captureStonecutterPlayer(
            int containerId,
            Inventory inventory,
            ContainerLevelAccess access,
            CallbackInfo callback
    ) {
        this.industrialColonies$player = inventory.player;
    }

    @Inject(method = "clickMenuButton", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$denyLockedSelection(
            Player player,
            int recipeIndex,
            CallbackInfoReturnable<Boolean> callback
    ) {
        RecipeHolder<StonecutterRecipe> recipe = industrialColonies$recipeAt(recipeIndex);
        if (recipe != null
                && player instanceof ServerPlayer serverPlayer
                && !RecipeStageGate.canUse(serverPlayer, recipe)) {
            callback.setReturnValue(false);
        }
    }

    @Inject(method = "setupResultSlot", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$clearLockedResult(CallbackInfo callback) {
        RecipeHolder<StonecutterRecipe> recipe = industrialColonies$recipeAt(
                this.selectedRecipeIndex.get());
        if (recipe != null
                && this.industrialColonies$player instanceof ServerPlayer serverPlayer
                && !RecipeStageGate.canUse(serverPlayer, recipe)) {
            this.resultContainer.setRecipeUsed(null);
            this.resultContainer.setItem(0, ItemStack.EMPTY);
            callback.cancel();
        }
    }

    @Unique
    private RecipeHolder<StonecutterRecipe> industrialColonies$recipeAt(int index) {
        return index >= 0 && index < this.recipes.size() ? this.recipes.get(index) : null;
    }
}
