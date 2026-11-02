package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismRangeSnapshot;
import mekanism.api.Action;
import mekanism.api.fluid.IMekanismFluidHandler;
import mekanism.common.content.network.transmitter.MechanicalPipe;
import net.minecraft.core.Direction;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "mekanism.common.content.network.transmitter.MechanicalPipe", remap = false)
public abstract class MekanismPipeRangeMixin implements IMekanismFluidHandler {
    @Unique
    private boolean ic$admitsFluid() {
        var pipe = (MechanicalPipe) (Object) this;
        return pipe.hasTransmitterNetwork()
                && MekanismRangeSnapshot.inspect(pipe.getTransmitterNetwork()).allowsNewIngress();
    }

    @Override
    public FluidStack insertFluid(FluidStack stack, Direction side, Action action) {
        return ic$admitsFluid() ? IMekanismFluidHandler.super.insertFluid(stack, side, action) : stack;
    }

    @Override
    public FluidStack insertFluid(int tank, FluidStack stack, Direction side, Action action) {
        return ic$admitsFluid() ? IMekanismFluidHandler.super.insertFluid(tank, stack, side, action) : stack;
    }

    @Inject(method = "takeFluid", at = @At("HEAD"), cancellable = true)
    private void ic$holdDirectTake(FluidStack stack, Action action, CallbackInfoReturnable<FluidStack> callback) {
        if (!ic$admitsFluid()) callback.setReturnValue(stack);
    }
}
