package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.industrialcolonies.processing.StellarisBatchAdmission;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Keep native timer/container/tick behavior; hold only the new-burn tank admission. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.blocks.entities.machines.DieselGeneratorBlockEntity", remap = false)
public abstract class StellarisDieselAdmissionMixin {
    @ModifyExpressionValue(method = "tick", at = @At(value = "INVOKE", target = "Lcom/st0x0ef/stellaris/common/utils/capabilities/fluid/SingleFluidStorage;isEmpty()Z"), require = 1)
    private boolean industrialColonies$requireCompleteBurn(boolean empty) {
        return empty || !StellarisBatchAdmission.generatorCanStart(this);
    }
}
