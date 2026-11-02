package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.*;
import dev.godpc.industrialcolonies.processing.PotionRefineryCompatibility;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.crafting.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

@Pseudo
@Mixin(targets="blusunrize.immersiveengineering.api.crafting.RefineryRecipe",remap=false)
public abstract class IePotionRefineryLookupMixin {
    @WrapOperation(method="findRecipe",at=@At(value="INVOKE",target="Lnet/neoforged/neoforge/fluids/crafting/SizedFluidIngredient;test(Lnet/neoforged/neoforge/fluids/FluidStack;)Z"),require=1)
    private static boolean industrialColonies$full(SizedFluidIngredient input,FluidStack fluid,Operation<Boolean> original) {
        return original.call(input,PotionRefineryCompatibility.lookup(input.ingredient(),fluid));
    }
    @WrapOperation(method="findIncompleteRefineryRecipe",at=@At(value="INVOKE",target="Lnet/neoforged/neoforge/fluids/crafting/FluidIngredient;test(Lnet/neoforged/neoforge/fluids/FluidStack;)Z"),require=1)
    private static boolean industrialColonies$partial(FluidIngredient input,FluidStack fluid,Operation<Boolean> original) {
        return original.call(input,PotionRefineryCompatibility.lookup(input,fluid));
    }
}
