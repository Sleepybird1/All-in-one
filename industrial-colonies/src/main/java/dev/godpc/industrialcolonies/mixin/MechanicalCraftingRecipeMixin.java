package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.crafter.MechanicalCraftingRecipe;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(MechanicalCraftingRecipe.class)
public abstract class MechanicalCraftingRecipeMixin {
    @Inject(method = "getType", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$getTierType(CallbackInfoReturnable<RecipeType<?>> callback) {
        TieredRecipeBindings.Binding binding = binding();
        if (binding != null) callback.setReturnValue(binding.type());
    }

    @Inject(method = "getSerializer", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$getTierSerializer(CallbackInfoReturnable<RecipeSerializer<?>> callback) {
        TieredRecipeBindings.Binding binding = binding();
        if (binding != null) callback.setReturnValue(binding.serializer());
    }

    private TieredRecipeBindings.Binding binding() {
        return TieredRecipeBindings.get((Recipe<?>) (Object) this);
    }
}
