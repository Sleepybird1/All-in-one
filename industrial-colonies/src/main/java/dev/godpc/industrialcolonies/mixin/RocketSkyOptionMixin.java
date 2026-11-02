package dev.godpc.industrialcolonies.mixin;

import dev.devce.rocketnautics.RocketConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Honor the disabled custom-sky option for expensive Overworld background effects. */
@Mixin(targets = "dev.devce.rocketnautics.client.SkyHandler", remap = false)
public abstract class RocketSkyOptionMixin {
    @Inject(method = {"renderCosmicNebula", "renderSpaceStars", "ensureStarPlasmaTexture"},
            at = @At("HEAD"), cancellable = true, require = 1)
    private static void industrialColonies$honorOverworldSkyOption(CallbackInfo ci) {
        var level = Minecraft.getInstance().level;
        if (level != null && level.dimension() == Level.OVERWORLD
                && !RocketConfig.CLIENT.enableCustomSky.get()) {
            ci.cancel();
        }
    }
}
