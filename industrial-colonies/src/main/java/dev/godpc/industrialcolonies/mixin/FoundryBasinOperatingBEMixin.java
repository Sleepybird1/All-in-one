package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Enforces exact stages on Create Metallurgy foundry-lid melting recipes. */
@Mixin(
        targets = "fr.lucreeper74.createmetallurgy.content.blocks.foundry_basin.FoundryBasinOperatingBE",
        remap = false
)
public abstract class FoundryBasinOperatingBEMixin {
    @Inject(
            method = "matchBasinRecipe(Lnet/minecraft/world/item/crafting/Recipe;)Z",
            at = @At("HEAD"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedFoundryRecipe(
            Recipe<?> recipe,
            CallbackInfoReturnable<Boolean> callback
    ) {
        BlockEntity blockEntity = (BlockEntity) (Object) this;
        if (recipe != null && !CreateRecipeStageGate.canUse(blockEntity.getLevel(), recipe)) {
            callback.setReturnValue(false);
        }
    }
}
