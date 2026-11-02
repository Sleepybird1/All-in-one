package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismRangeSnapshot;
import mekanism.api.Action;
import mekanism.api.energy.IMekanismStrictEnergyHandler;
import mekanism.common.content.network.transmitter.UniversalCable;
import net.minecraft.core.Direction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Lab-qualified registration only until the other transport families and topology cases pass. */
@Pseudo
@Mixin(targets = "mekanism.common.content.network.transmitter.UniversalCable", remap = false)
public abstract class MekanismCableRangeMixin implements IMekanismStrictEnergyHandler {
    @Unique
    private boolean ic$admitsEnergy() {
        var cable = (UniversalCable) (Object) this;
        return cable.hasTransmitterNetwork()
                && MekanismRangeSnapshot.inspect(cable.getTransmitterNetwork()).allowsNewIngress();
    }

    @Override
    public long insertEnergy(long amount, Direction side, Action action) {
        return ic$admitsEnergy() ? IMekanismStrictEnergyHandler.super.insertEnergy(amount, side, action) : amount;
    }

    @Override
    public long insertEnergy(int container, long amount, Direction side, Action action) {
        return ic$admitsEnergy() ? IMekanismStrictEnergyHandler.super.insertEnergy(container, amount, side, action) : amount;
    }

    @Inject(method = "pullFromAcceptors", at = @At("HEAD"), cancellable = true)
    private void ic$holdAutomaticPull(CallbackInfo callback) {
        if (!ic$admitsEnergy()) callback.cancel();
    }
}
