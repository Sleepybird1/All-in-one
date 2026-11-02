package dev.godpc.industrialcolonies.mixin;
import com.mojang.blaze3d.platform.Window;
import dev.godpc.industrialcolonies.KjsGenDesktopBridge;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
/** Window dimensions are scoped to detached UI execution; the game keeps its own dimensions. */
@Mixin(Window.class)
public abstract class KjsGenDetachedWindowMixin {
 @Inject(method="getWidth",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$width(CallbackInfoReturnable<Integer> ci){if(KjsGenDesktopBridge.detachedContext())ci.setReturnValue(KjsGenDesktopBridge.pixelWidth());}
 @Inject(method="getHeight",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$height(CallbackInfoReturnable<Integer> ci){if(KjsGenDesktopBridge.detachedContext())ci.setReturnValue(KjsGenDesktopBridge.pixelHeight());}
 @Inject(method="getGuiScaledWidth",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$guiWidth(CallbackInfoReturnable<Integer> ci){if(KjsGenDesktopBridge.detachedContext())ci.setReturnValue(KjsGenDesktopBridge.pixelWidth()/2);}
 @Inject(method="getGuiScaledHeight",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$guiHeight(CallbackInfoReturnable<Integer> ci){if(KjsGenDesktopBridge.detachedContext())ci.setReturnValue(KjsGenDesktopBridge.pixelHeight()/2);}
 @Inject(method="getGuiScale",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$scale(CallbackInfoReturnable<Double> ci){if(KjsGenDesktopBridge.detachedContext())ci.setReturnValue(2.0);}
}
