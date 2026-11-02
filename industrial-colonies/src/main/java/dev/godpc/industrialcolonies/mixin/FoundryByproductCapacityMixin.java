package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.FoundryOutputCapacity;
import modernmods.modernfoundry.library.recipe.melting.IMeltingRecipe;
import modernmods.modernfoundry.smeltery.block.entity.module.MeltingModuleInventory;
import modernmods.modernfoundry.smeltery.block.entity.module.ByproductMeltingModuleInventory;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Retain the ore and native NO_SPACE retry state until primary and byproducts all fit. */
@Mixin(targets = "modernmods.modernfoundry.smeltery.block.entity.module.MeltingModuleInventory", remap = false)
public abstract class FoundryByproductCapacityMixin {
    @Shadow @Final protected IFluidHandler fluidHandler;

    @Inject(method = "tryFillTank", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$requireWholeOutput(int slot, IMeltingRecipe recipe,
                                                     CallbackInfoReturnable<Boolean> callback) {
        var inventory = (MeltingModuleInventory) (Object) this;
        if (inventory instanceof ByproductMeltingModuleInventory
                && !FoundryOutputCapacity.fits(recipe, inventory.getModule(slot), fluidHandler)) {
            callback.setReturnValue(false);
        }
    }
}
