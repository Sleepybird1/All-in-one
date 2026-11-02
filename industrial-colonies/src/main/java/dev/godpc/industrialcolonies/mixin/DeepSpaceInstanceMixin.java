package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import dev.devce.rocketnautics.content.orbit.DeepSpaceInstance;
import dev.devce.rocketnautics.content.orbit.universe.CubePlanet;
import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import net.minecraft.server.MinecraftServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/** Requires physical route hardware and protective equipment for managed descents. */
@Mixin(value = DeepSpaceInstance.class, remap = false)
public abstract class DeepSpaceInstanceMixin {
    @Shadow
    private CubePlanet lastOrbiting;

    @ModifyExpressionValue(
            method = "tick(Lnet/minecraft/server/MinecraftServer;)V",
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/devce/rocketnautics/api/orbit/AllowedTransfer;allowToDimension()Z"),
            require = 1)
    private boolean industrialColonies$requireManagedDescentAuthorization(
            boolean dimensionAllowsTransfer,
            @Local(argsOnly = true) MinecraftServer server) {
        return dimensionAllowsTransfer
                && SpaceflightAuthorization.mayDescendToManagedPlanet(
                        server,
                        lastOrbiting,
                        (DeepSpaceInstance) (Object) this);
    }
}
