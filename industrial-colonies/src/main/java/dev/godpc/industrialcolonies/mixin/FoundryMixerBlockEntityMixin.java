package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Enforces exact research stages on Create Metallurgy foundry-alloying recipes. */
@Mixin(
        targets = "fr.lucreeper74.createmetallurgy.content.blocks.foundry_mixer.FoundryMixerBlockEntity",
        remap = false
)
public abstract class FoundryMixerBlockEntityMixin {
    @Inject(
            method = "matchBasinRecipe(Lnet/minecraft/world/item/crafting/Recipe;)Z",
            at = @At("HEAD"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedAlloyingRecipe(
            Recipe<?> recipe,
            CallbackInfoReturnable<Boolean> callback
    ) {
        BlockEntity blockEntity = (BlockEntity) (Object) this;
        if (recipe != null && !CreateRecipeStageGate.canUse(blockEntity.getLevel(), recipe)) {
            callback.setReturnValue(false);
        }
    }
}
