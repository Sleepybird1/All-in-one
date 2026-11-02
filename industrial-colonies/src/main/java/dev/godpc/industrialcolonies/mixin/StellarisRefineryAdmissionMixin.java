package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import dev.godpc.industrialcolonies.processing.StellarisBatchAdmission;
import java.util.Optional;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Require both native product branches before allowing either branch to consume a batch. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.blocks.entities.machines.FuelRefineryBlockEntity", remap = false)
public abstract class StellarisRefineryAdmissionMixin {
    @WrapOperation(method = "tick", at = @At(value = "INVOKE", target = "Ljava/util/Optional;isPresent()Z"), require = 1)
    private boolean industrialColonies$requireBothOutputs(Optional<?> recipe, Operation<Boolean> original) {
        return original.call(recipe) && StellarisBatchAdmission.refineryCanStart(this, recipe);
    }
}
