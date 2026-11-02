package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import dev.godpc.industrialcolonies.space.station.StationLifeSupport;
import net.neoforged.neoforge.event.entity.living.LivingBreatheEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Suppresses only Cosmonautics' DROWNING flag inside exact serviced rooms. */
@Pseudo
@Mixin(targets = "dev.devce.rocketnautics.content.physics.GlobalSpacePhysicsHandler", remap = false)
public abstract class GlobalSpacePhysicsHandlerMixin {
    @ModifyExpressionValue(
            method = "onLivingBreathe(Lnet/neoforged/neoforge/event/entity/living/LivingBreatheEvent;)V",
            at = @At(
                    value = "INVOKE",
                    target = "Ljava/util/EnumSet;contains(Ljava/lang/Object;)Z"),
            require = 1)
    private static boolean industrialColonies$honorExactStationOxygen(
            boolean drowning,
            @Local(argsOnly = true) LivingBreatheEvent event
    ) {
        return drowning && !StationLifeSupport.hasLiveCoverage(event.getEntity());
    }
}
