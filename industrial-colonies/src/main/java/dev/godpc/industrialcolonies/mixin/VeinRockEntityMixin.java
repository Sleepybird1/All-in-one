package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.client.VeinRockView;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Client-only visual suppression while the explicit rock inspection mode is enabled. */
@Mixin(EntityRenderDispatcher.class)
public abstract class VeinRockEntityMixin {
 @Inject(method="render",at=@At("HEAD"),cancellable=true)
 private void rockOnly(CallbackInfo ci){if(VeinRockView.enabled())ci.cancel();}
}
