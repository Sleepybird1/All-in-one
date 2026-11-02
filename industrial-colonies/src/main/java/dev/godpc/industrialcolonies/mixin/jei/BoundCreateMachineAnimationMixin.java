package dev.godpc.industrialcolonies.mixin.jei;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.simibubi.create.compat.jei.category.animations.AnimatedDeployer;
import com.simibubi.create.compat.jei.category.animations.AnimatedItemDrain;
import com.simibubi.create.compat.jei.category.animations.AnimatedMixer;
import com.simibubi.create.compat.jei.category.animations.AnimatedPress;
import com.simibubi.create.compat.jei.category.animations.AnimatedSaw;
import com.simibubi.create.compat.jei.category.animations.AnimatedSpout;
import dev.godpc.industrialcolonies.client.jei.JeiMachineVisualContext;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Replaces the first block body in each Create animation; later basin/depot bodies are untouched. */
@Mixin(value = {
        AnimatedPress.class,
        AnimatedDeployer.class,
        AnimatedMixer.class,
        AnimatedSaw.class,
        AnimatedSpout.class,
        AnimatedItemDrain.class
}, remap = false)
public abstract class BoundCreateMachineAnimationMixin {
    @ModifyExpressionValue(
            method = "draw",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/tterrag/registrate/util/entry/BlockEntry;getDefaultState()"
                            + "Lnet/minecraft/world/level/block/state/BlockState;",
                    ordinal = 0
            )
    )
    private BlockState industrialColonies$renderSelectedMachine(BlockState original) {
        return JeiMachineVisualContext.selectedMachineState(original);
    }
}
