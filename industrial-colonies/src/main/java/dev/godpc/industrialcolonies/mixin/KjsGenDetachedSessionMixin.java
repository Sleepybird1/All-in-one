package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.KjsGenDesktopBridge;
import com.zizazr.kjsgen.integration.net.ClientEditSession;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Native server project updates must refresh the detached editor too. */
@Mixin(value=ClientEditSession.class,remap=false)
public abstract class KjsGenDetachedSessionMixin {
 @Inject(method="handleServer",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$refreshResult(String op,String json,CallbackInfo ci){
   if(op.equals("ic_refresh_result")){if(!dev.godpc.industrialcolonies.KjsGenAutomaticRefresh.result(json))dev.godpc.industrialcolonies.KjsGenRefreshScreen.result(json);ci.cancel();}
 }
 @Inject(method="refreshEditor",at=@At("TAIL"))
 private static void industrialColonies$refresh(CallbackInfo ci){KjsGenDesktopBridge.refreshSession();}
}
