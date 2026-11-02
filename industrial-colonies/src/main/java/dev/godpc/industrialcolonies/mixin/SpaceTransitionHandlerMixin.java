package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Prevents an arbitrary low-tier Sable craft from bypassing orbital progression. */
@Pseudo
@Mixin(targets = "dev.devce.rocketnautics.content.physics.SpaceTransitionHandler", remap = false)
public abstract class SpaceTransitionHandlerMixin {
    @ModifyExpressionValue(
            method = "lambda$init$2(Ldev/ryanhcode/sable/sublevel/system/SubLevelPhysicsSystem;D)V",
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/devce/rocketnautics/api/orbit/AllowedTransfer;allowToSpace()Z"),
            require = 1)
    private static boolean industrialColonies$requireOrbitalFlightComputer(
            boolean dimensionAllowsSpace,
            @Local(name = "ship") ServerSubLevel ship) {
        return dimensionAllowsSpace && SpaceflightAuthorization.hasOrbitalFlightComputer(ship);
    }
}
