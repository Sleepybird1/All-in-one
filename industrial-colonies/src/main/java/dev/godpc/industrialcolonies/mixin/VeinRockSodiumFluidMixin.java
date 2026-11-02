package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.client.VeinRockView;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Optional installed Sodium NeoForge path bypasses vanilla LiquidBlockRenderer. */
@Pseudo
@Mixin(targets="net.caffeinemc.mods.sodium.neoforge.render.FluidRendererImpl",remap=false)
public abstract class VeinRockSodiumFluidMixin {
 @Inject(method="render",at=@At("HEAD"),cancellable=true,remap=false)
 private void rockOnly(CallbackInfo ci){if(VeinRockView.enabled())ci.cancel();}
}
