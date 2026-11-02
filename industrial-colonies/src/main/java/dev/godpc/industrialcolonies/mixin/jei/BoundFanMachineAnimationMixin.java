package dev.godpc.industrialcolonies.mixin.jei;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.simibubi.create.compat.jei.category.ProcessingViaFanCategory;
import dev.godpc.industrialcolonies.client.jei.JeiMachineVisualContext;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Fan categories render their machine inline instead of using an Animated* helper. */
@Mixin(value = ProcessingViaFanCategory.class, remap = false)
public abstract class BoundFanMachineAnimationMixin {
    @ModifyExpressionValue(
            method = "draw",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/tterrag/registrate/util/entry/BlockEntry;getDefaultState()"
                            + "Lnet/minecraft/world/level/block/state/BlockState;",
                    ordinal = 0
            )
    )
    private BlockState industrialColonies$renderSelectedFan(BlockState original) {
        return JeiMachineVisualContext.selectedMachineState(original);
    }
}
