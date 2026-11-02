package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.KjsGenDesktopBridge;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Hover and shortcut modifiers follow the projected cursor only while its window has focus. */
@Mixin(Screen.class)
public abstract class KjsGenProjectionScreenMixin {
    @ModifyVariable(method="renderWithTooltip",at=@At("HEAD"),argsOnly=true,ordinal=0)
    private int industrialColonies$projectedX(int x){return KjsGenDesktopBridge.externalInput()?KjsGenDesktopBridge.mouseX():x;}
    @ModifyVariable(method="renderWithTooltip",at=@At("HEAD"),argsOnly=true,ordinal=1)
    private int industrialColonies$projectedY(int y){return KjsGenDesktopBridge.externalInput()?KjsGenDesktopBridge.mouseY():y;}
    @Inject(method="hasControlDown",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$control(CallbackInfoReturnable<Boolean> ci){if(KjsGenDesktopBridge.externalInput())ci.setReturnValue((KjsGenDesktopBridge.modifiers()&2)!=0);}
    @Inject(method="hasShiftDown",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$shift(CallbackInfoReturnable<Boolean> ci){if(KjsGenDesktopBridge.externalInput())ci.setReturnValue((KjsGenDesktopBridge.modifiers()&1)!=0);}
    @Inject(method="hasAltDown",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$alt(CallbackInfoReturnable<Boolean> ci){if(KjsGenDesktopBridge.externalInput())ci.setReturnValue((KjsGenDesktopBridge.modifiers()&4)!=0);}

    @Inject(method="renderBackground",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$independentBackground(GuiGraphics g,int x,int y,float delta,CallbackInfo ci){
        if(KjsGenDesktopBridge.detachedContext()){var screen=(Screen)(Object)this;g.fill(0,0,screen.width,screen.height,0xFF17191F);ci.cancel();}
    }
    @Inject(method="renderBlurredBackground",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$noWorldBlur(float delta,CallbackInfo ci){if(KjsGenDesktopBridge.detachedContext())ci.cancel();}
}
