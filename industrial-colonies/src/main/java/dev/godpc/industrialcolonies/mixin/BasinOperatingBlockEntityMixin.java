package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.processing.basin.BasinOperatingBlockEntity;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.world.item.crafting.Recipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Performs per-owner authorization after Create's globally cached basin-family lookup. */
@Mixin(BasinOperatingBlockEntity.class)
public abstract class BasinOperatingBlockEntityMixin {
    @Inject(
            method = "matchBasinRecipe(Lnet/minecraft/world/item/crafting/Recipe;)Z",
            at = @At("HEAD"),
            cancellable = true
    )
    private void industrialColonies$denyLockedBasinRecipe(
            Recipe<?> recipe,
            CallbackInfoReturnable<Boolean> callback
    ) {
        BasinOperatingBlockEntity blockEntity = (BasinOperatingBlockEntity) (Object) this;
        if (recipe != null && !CreateRecipeStageGate.canUse(blockEntity.getLevel(), recipe, blockEntity)) {
            callback.setReturnValue(false);
        }
    }
}
