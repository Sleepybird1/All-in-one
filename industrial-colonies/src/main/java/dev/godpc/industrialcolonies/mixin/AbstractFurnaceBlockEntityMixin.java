package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Prevents furnace, smoker, and blast-furnace progress for locked exact recipe IDs. */
@Mixin(AbstractFurnaceBlockEntity.class)
public abstract class AbstractFurnaceBlockEntityMixin {
    @Inject(
            method = "canBurn(Lnet/minecraft/core/RegistryAccess;"
                    + "Lnet/minecraft/world/item/crafting/RecipeHolder;"
                    + "Lnet/minecraft/core/NonNullList;I"
                    + "Lnet/minecraft/world/level/block/entity/AbstractFurnaceBlockEntity;)Z",
            at = @At("HEAD"),
            cancellable = true
    )
    private static void industrialColonies$denyLockedCookingRecipe(
            RegistryAccess registryAccess,
            RecipeHolder<?> recipe,
            NonNullList<ItemStack> inventory,
            int maxStackSize,
            AbstractFurnaceBlockEntity furnace,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (recipe != null && !MachineRecipeStageGate.canUse(furnace, recipe)) {
            callback.setReturnValue(false);
        }
    }
}
