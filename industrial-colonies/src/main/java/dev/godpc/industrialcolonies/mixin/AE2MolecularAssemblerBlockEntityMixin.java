package dev.godpc.industrialcolonies.mixin;

import appeng.api.crafting.IPatternDetails;
import appeng.api.networking.IGridNode;
import appeng.api.networking.ticking.TickRateModulation;
import appeng.api.stacks.KeyCounter;
import appeng.blockentity.crafting.IMolecularAssemblerSupportedPattern;
import appeng.blockentity.crafting.MolecularAssemblerBlockEntity;
import appeng.crafting.pattern.AECraftingPattern;
import dev.godpc.industrialcolonies.MachineRecipeStageGate;
import net.minecraft.core.Direction;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Prevents an AE2 Molecular Assembler from bypassing an exact crafting-recipe stage.
 * The push check rejects new locked jobs and the tick check also protects persisted jobs.
 */
@Mixin(value = MolecularAssemblerBlockEntity.class, remap = false)
public abstract class AE2MolecularAssemblerBlockEntityMixin {
    @Shadow
    private IMolecularAssemblerSupportedPattern myPlan;

    @Inject(method = "pushPattern", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedPatternPush(
            IPatternDetails pattern,
            KeyCounter[] inputHolder,
            Direction direction,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (!industrialColonies$canUse(pattern)) {
            callback.setReturnValue(false);
        }
    }

    @Inject(method = "tickingRequest", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$pauseLockedPersistedPattern(
            IGridNode node,
            int ticksSinceLastCall,
            CallbackInfoReturnable<TickRateModulation> callback
    ) {
        if (!industrialColonies$canUse(this.myPlan)) {
            // Keep polling so completing the research resumes an already queued job.
            callback.setReturnValue(TickRateModulation.SLOWER);
        }
    }

    private boolean industrialColonies$canUse(IPatternDetails pattern) {
        if (!(pattern instanceof AECraftingPattern craftingPattern)) {
            // Processing patterns are not backed by a vanilla crafting RecipeHolder.
            return true;
        }

        RecipeHolder<?> recipe = ((AECraftingPatternAccessor) (Object) craftingPattern)
                .industrialColonies$getRecipeHolder();
        return MachineRecipeStageGate.canUse((BlockEntity) (Object) this, recipe);
    }
}
