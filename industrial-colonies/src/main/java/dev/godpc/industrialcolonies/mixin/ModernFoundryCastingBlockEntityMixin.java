package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Exact-ID selection and progress checks for ModernFoundry table and basin casting. */
@Mixin(
        targets = "modernmods.modernfoundry.smeltery.block.entity.CastingBlockEntity",
        remap = false
)
public abstract class ModernFoundryCastingBlockEntityMixin {
    @Shadow
    private RecipeHolder<?> currentRecipe;

    @Inject(
            method = "findCastingRecipe()Lnet/minecraft/world/item/crafting/RecipeHolder;",
            at = @At("RETURN"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedStoredFluidRecipe(
            CallbackInfoReturnable<RecipeHolder<?>> callback
    ) {
        industrialColonies$filterSelection(callback);
    }

    @Inject(
            method = "findCastingRecipe(Lnet/neoforged/neoforge/fluids/FluidStack;)"
                    + "Lnet/minecraft/world/item/crafting/RecipeHolder;",
            at = @At("RETURN"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedIncomingFluidRecipe(
            FluidStack fluid,
            CallbackInfoReturnable<RecipeHolder<?>> callback
    ) {
        industrialColonies$filterSelection(callback);
    }

    @Inject(method = "serverTick", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$pauseLockedCastingProgress(
            Level level,
            BlockPos pos,
            CallbackInfo callback
    ) {
        BlockEntity machine = (BlockEntity) (Object) this;
        if (this.currentRecipe != null
                && !MachineRecipeStageGate.canUse(machine, this.currentRecipe)) {
            callback.cancel();
        }
    }

    private void industrialColonies$filterSelection(
            CallbackInfoReturnable<RecipeHolder<?>> callback
    ) {
        RecipeHolder<?> recipe = callback.getReturnValue();
        BlockEntity machine = (BlockEntity) (Object) this;
        if (recipe != null && !MachineRecipeStageGate.canUse(machine, recipe)) {
            callback.setReturnValue(null);
        }
    }
}
