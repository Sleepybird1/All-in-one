package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismRangeSnapshot;
import java.util.function.Predicate;
import mekanism.common.content.network.transmitter.MechanicalPipe;
import mekanism.common.content.network.transmitter.PressurizedTube;
import mekanism.common.content.network.transmitter.UniversalCable;
import mekanism.common.tile.transmitter.TileEntityTransmitter;
import net.minecraft.core.Direction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** One return hook for all pooled transports; separate cancellable hooks would bypass each other. */
@Pseudo
@Mixin(targets = "mekanism.common.tile.transmitter.TileEntityTransmitter", remap = false)
public abstract class MekanismBufferedCapabilityRangeMixin {
    @Inject(method = "getInsertPredicate", at = @At("RETURN"), cancellable = true)
    private void ic$gateBufferedIngress(CallbackInfoReturnable<Predicate<Direction>> callback) {
        Predicate<Direction> original = callback.getReturnValue();
        var tile = (TileEntityTransmitter) (Object) this;
        callback.setReturnValue(side -> {
            if (!original.test(side)) return false;
            var transmitter = tile.getTransmitter();
            return !(transmitter instanceof UniversalCable || transmitter instanceof MechanicalPipe || transmitter instanceof PressurizedTube)
                    || (transmitter.hasTransmitterNetwork()
                    && MekanismRangeSnapshot.inspect(transmitter.getTransmitterNetwork()).allowsNewIngress());
        });
    }
}
