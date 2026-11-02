package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.transport.MekanismItemAdmission;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import mekanism.common.content.network.transmitter.LogisticalTransporterBase;
import mekanism.common.content.transporter.TransporterPathfinder;
import mekanism.common.content.transporter.TransporterStack;
import mekanism.common.lib.inventory.TransitRequest;
import net.minecraft.core.GlobalPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = TransporterPathfinder.class, remap = false)
public abstract class MekanismItemPathRangeMixin {
    @Inject(method = "getPaths", at = @At("RETURN"), cancellable = true, require = 1)
    private static void ic$eligibleNewDestinations(LogisticalTransporterBase start, TransporterStack stack,
            TransitRequest request, int minimum, Map<GlobalPos, Set<TransporterStack>> additional,
            CallbackInfoReturnable<List<TransporterPathfinder.Destination>> cir) {
        if (!MekanismItemAdmission.isNewIngress(stack)) return;
        var eligible = new ArrayList<TransporterPathfinder.Destination>();
        for (var destination : cir.getReturnValue())
            if (MekanismItemAdmission.inspect(start, destination.getPath()).allowsNewIngress()) eligible.add(destination);
        // Preserve native score order and round-robin selection among eligible destinations.
        cir.setReturnValue(eligible);
    }
}
