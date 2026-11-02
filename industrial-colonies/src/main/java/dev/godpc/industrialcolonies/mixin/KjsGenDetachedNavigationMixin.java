package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.KjsGenDesktopBridge;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** The game's active screen is untouched when opening or navigating the detached editor. */
@Mixin(Minecraft.class)
public abstract class KjsGenDetachedNavigationMixin {
 @Inject(method="setScreen",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$detach(Screen screen,CallbackInfo ci){if(KjsGenDesktopBridge.routeScreen(screen))ci.cancel();}
 @Inject(method="pauseGame",at=@At("HEAD"),cancellable=true)
 private void industrialColonies$keepPlaying(boolean pause,CallbackInfo ci){if(KjsGenDesktopBridge.suppressFocusPause())ci.cancel();}
}
