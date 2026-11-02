package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.inventory.RecipeBookMenu;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Prevents recipe-book placement from moving ingredients for a locked recipe. */
@Mixin(RecipeBookMenu.class)
public abstract class RecipeBookMenuMixin {
    @Inject(
            method = "handlePlacement(ZLnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lnet/minecraft/server/level/ServerPlayer;)V",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$denyLockedRecipePlacement(
            boolean useMaxItems,
            RecipeHolder<?> recipe,
            ServerPlayer player,
            CallbackInfo callback
    ) {
        Object menu = this;
        if ((menu instanceof CraftingMenu || menu instanceof InventoryMenu)
                && !RecipeStageGate.canUse(player, recipe)) {
            callback.cancel();
        }
    }
}
