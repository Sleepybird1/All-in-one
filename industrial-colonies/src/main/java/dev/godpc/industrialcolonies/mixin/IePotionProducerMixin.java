package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

@Pseudo
@Mixin(targets="blusunrize.immersiveengineering.common.fluids.PotionFluid",remap=false)
public abstract class IePotionProducerMixin {
    @ModifyReturnValue(method="getFluidStackForType",at=@At("RETURN"),require=1)
    private static FluidStack industrialColonies$canonicalPotion(FluidStack original) {
        return PotionIdentityRuntime.produced(original);
    }
}
