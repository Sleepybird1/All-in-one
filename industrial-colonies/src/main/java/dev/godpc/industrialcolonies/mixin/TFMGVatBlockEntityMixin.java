package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.recipes.VatMachineRecipe;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import dev.godpc.industrialcolonies.TFMGVatBatchPlan;
import dev.godpc.industrialcolonies.TFMGExpandedVatInventory;
import dev.godpc.industrialcolonies.TFMGVatItemAccess;
import com.drmangotea.tfmg.content.machinery.vat.base.VatInventory;
import net.neoforged.neoforge.items.IItemHandlerModifiable;
import com.drmangotea.tfmg.content.machinery.vat.base.VatBlockEntity;
import com.drmangotea.tfmg.registry.TFMGRecipeTypes;
import com.simibubi.create.foundation.recipe.RecipeConditions;
import com.simibubi.create.foundation.recipe.RecipeFinder;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Exact-ID selection and completion checks for the TFMG Chemical Vat. */
@Mixin(targets = "com.drmangotea.tfmg.content.machinery.vat.base.VatBlockEntity", remap = false)
public abstract class TFMGVatBlockEntityMixin {
    @Shadow protected IItemHandlerModifiable itemCapability;
    // Only construction of inputInventory changes. Native outputInventory remains four slots.
    @Redirect(method = "<init>", at = @At(value = "NEW", target =
        "com/drmangotea/tfmg/content/machinery/vat/base/VatInventory", ordinal = 0))
    private VatInventory industrialColonies$directInputs(int nativeSlots, VatBlockEntity vat) {
        if (nativeSlots != 4) throw new IllegalStateException("Unexpected native Chemical Vat input layout");
        return new TFMGExpandedVatInventory(vat);
    }
    @Inject(method = "<init>", at = @At("RETURN"))
    private void industrialColonies$stableItemIndices(CallbackInfo callback) {
        var vat = (VatBlockEntity) (Object) this;
        itemCapability = new TFMGVatItemAccess(vat.inputInventory, vat.outputInventory);
    }
    @Inject(method = "getNewItemCapability", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$stableControllerCapability(CallbackInfoReturnable<IItemHandlerModifiable> callback) {
        var vat = (VatBlockEntity) (Object) this;
        if (vat.isController()) callback.setReturnValue(new TFMGVatItemAccess(vat.inputInventory, vat.outputInventory));
    }
    @Shadow
    public VatMachineRecipe recipe;
    @Shadow int timer;
    @Shadow protected abstract Object getRecipeCacheKey();

    @Inject(method = "getMatchingRecipe", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$selectConservingBatch(CallbackInfoReturnable<VatMachineRecipe> callback) {
        var vat = (VatBlockEntity) (Object) this;
        if (vat.getLevel() == null) { callback.setReturnValue(null); return; }
        for (var holder : RecipeFinder.get(getRecipeCacheKey(), vat.getLevel(),
                RecipeConditions.isOfType(TFMGRecipeTypes.VAT_MACHINE_RECIPE.getType()))) {
            if (holder.value() instanceof VatMachineRecipe selected
                    && TFMGVatBatchPlan.machineAllows(vat, selected)
                    && TFMGVatBatchPlan.hasInputs(vat, selected)
                    && TFMGVatBatchPlan.outputsFit(vat, selected)) {
                callback.setReturnValue(selected);
                return;
            }
        }
        callback.setReturnValue(null);
    }

    @Inject(method = "getMatchingRecipe", at = @At("RETURN"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedVatSelection(
            CallbackInfoReturnable<VatMachineRecipe> callback
    ) {
        VatMachineRecipe selected = callback.getReturnValue();
        BlockEntity machine = (BlockEntity) (Object) this;
        if (selected != null && !MachineRecipeStageGate.canUse(machine, selected)) {
            callback.setReturnValue(null);
        }
    }

    @Inject(method = "handleRecipe", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$pauseLockedVatRecipe(CallbackInfo callback) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.recipe != null && !MachineRecipeStageGate.canUse(machine, this.recipe)) {
            callback.cancel();
        }
        var vat = (VatBlockEntity) (Object) this;
        if (recipe != null && (!TFMGVatBatchPlan.machineAllows(vat, recipe)
                || !TFMGVatBatchPlan.hasInputs(vat, recipe))) callback.cancel();
    }

    // This invocation is reached only after native controller, heat and duration checks.
    @Inject(method = "handleRecipe", at = @At(value = "INVOKE", target =
        "Lcom/simibubi/create/foundation/blockEntity/behaviour/fluid/SmartFluidTankBehaviour;getPrimaryHandler()Lcom/simibubi/create/foundation/fluid/SmartFluidTank;",
        ordinal = 0), cancellable = true, remap = false)
    private void industrialColonies$finishConservingBatch(CallbackInfo callback) {
        var selected = recipe;
        if (selected != null && TFMGVatBatchPlan.complete((VatBlockEntity) (Object) this, selected)) {
            recipe = null;
            timer = 0;
        }
        callback.cancel();
    }
}
