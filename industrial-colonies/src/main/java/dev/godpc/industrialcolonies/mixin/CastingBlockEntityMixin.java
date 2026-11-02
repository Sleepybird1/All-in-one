package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Enforces exact research stages on Create Metallurgy table and basin casting. */
@Mixin(
        targets = "fr.lucreeper74.createmetallurgy.content.blocks.casting.CastingBlockEntity",
        remap = false
)
public abstract class CastingBlockEntityMixin {
    @Inject(
            method = "matchCastingRecipe(Lnet/minecraft/world/item/crafting/Recipe;"
                    + "Lnet/neoforged/neoforge/fluids/FluidStack;Z)Z",
            at = @At("HEAD"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedCastingRecipe(
            Recipe<?> recipe,
            FluidStack testedFluid,
            boolean ignoreFluidAmount,
            CallbackInfoReturnable<Boolean> callback
    ) {
        BlockEntity blockEntity = (BlockEntity) (Object) this;
        if (recipe != null && !CreateRecipeStageGate.canUse(blockEntity.getLevel(), recipe)) {
            callback.setReturnValue(false);
        }
    }
}
