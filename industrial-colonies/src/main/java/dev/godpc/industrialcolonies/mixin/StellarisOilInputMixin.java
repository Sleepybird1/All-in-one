package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.blocks.entities.machines.FuelRefineryBlockEntity;
import dev.architectury.fluid.FluidStack;
import dev.godpc.industrialcolonies.processing.SpaceOilIdentity;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.blocks.entities.machines.FuelRefineryBlockEntity$1",remap=false)
public abstract class StellarisOilInputMixin {
    @Shadow @Final FuelRefineryBlockEntity this$0;
    @Inject(method="isFluidValid",at=@At("RETURN"),cancellable=true,require=1)
    private void industrialColonies$admitCanonicalOil(int tank,FluidStack stack,CallbackInfoReturnable<Boolean> cir){
        if(!cir.getReturnValueZ()&&SpaceOilIdentity.ready(this$0.getLevel())
                &&SpaceOilIdentity.preferred().isSame(stack.getFluid())) cir.setReturnValue(true);
    }
}
