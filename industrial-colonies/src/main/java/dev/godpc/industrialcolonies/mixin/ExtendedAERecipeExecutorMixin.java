package dev.godpc.industrialcolonies.mixin;

import appeng.api.networking.ticking.TickRateModulation;
import com.glodblock.github.extendedae.api.IRecipeMachine;
import com.glodblock.github.extendedae.util.RecipeExecutor;
import com.glodblock.github.glodium.recipe.RecipeSearchContext;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Stops ExtendedAE's shared machine executor before a locked cached recipe can advance. */
@Mixin(value = RecipeExecutor.class, remap = false)
public abstract class ExtendedAERecipeExecutorMixin {
    @Shadow
    @Final
    private IRecipeMachine<?, ?> machine;

    @Inject(method = "execute", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedExtendedAERecipe(
            int speed,
            boolean consumePower,
            CallbackInfoReturnable<TickRateModulation> callback
    ) {
        RecipeSearchContext<?, ?> context = this.machine.getContext();
        RecipeHolder<?> recipe = context.currentRecipe;
        if (recipe != null
                && (!(this.machine instanceof BlockEntity blockEntity)
                || !MachineRecipeStageGate.canUse(blockEntity, recipe))) {
            this.machine.setWorking(false);
            callback.setReturnValue(TickRateModulation.SLOWER);
        }
    }
}
