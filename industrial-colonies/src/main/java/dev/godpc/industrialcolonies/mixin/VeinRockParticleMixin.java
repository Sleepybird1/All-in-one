package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.client.VeinRockView;
import net.minecraft.client.particle.ParticleEngine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Client-only visual suppression while the explicit rock inspection mode is enabled. */
@Mixin(ParticleEngine.class)
public abstract class VeinRockParticleMixin {
 @Inject(method="render",at=@At("HEAD"),cancellable=true)
 private void rockOnly(CallbackInfo ci){if(VeinRockView.enabled())ci.cancel();}
}
