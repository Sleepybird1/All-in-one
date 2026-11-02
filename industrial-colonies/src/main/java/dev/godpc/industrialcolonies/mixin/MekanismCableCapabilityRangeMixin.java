package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismRangeSnapshot;
import java.util.function.Predicate;
import mekanism.common.content.network.transmitter.UniversalCable;
import mekanism.common.tile.transmitter.TileEntityTransmitter;
import net.minecraft.core.Direction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Native tile capability uses DynamicStrictEnergyHandler, bypassing cable insert methods. */
@Pseudo
@Mixin(targets = "mekanism.common.tile.transmitter.TileEntityTransmitter", remap = false)
public abstract class MekanismCableCapabilityRangeMixin {
    @Inject(method = "getInsertPredicate", at = @At("RETURN"), cancellable = true)
    private void ic$gateNativeCapability(CallbackInfoReturnable<Predicate<Direction>> callback) {
        Predicate<Direction> original = callback.getReturnValue();
        var tile = (TileEntityTransmitter) (Object) this;
        callback.setReturnValue(side -> original.test(side)
                && (!(tile.getTransmitter() instanceof UniversalCable cable)
                || (cable.hasTransmitterNetwork()
                && MekanismRangeSnapshot.inspect(cable.getTransmitterNetwork()).allowsNewIngress())));
    }
}
