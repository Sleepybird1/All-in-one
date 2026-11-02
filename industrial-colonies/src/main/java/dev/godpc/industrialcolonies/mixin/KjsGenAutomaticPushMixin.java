package dev.godpc.industrialcolonies.mixin;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.integration.net.ClientEditSession;
import dev.godpc.industrialcolonies.KjsGenAutomaticRefresh;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

@Mixin(value=ClientEditSession.class,remap=false)
public abstract class KjsGenAutomaticPushMixin {
 @Inject(method={"pushRecipe","removeRecipe"},at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$recipe(RecipeInstance r,CallbackInfo ci){if(KjsGenAutomaticRefresh.holdPush())ci.cancel();}
 @Inject(method="pushRemoval",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$removal(RemovalRule r,CallbackInfo ci){if(KjsGenAutomaticRefresh.holdPush())ci.cancel();}
 @Inject(method="removeRemoval",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$remove(String uid,CallbackInfo ci){if(KjsGenAutomaticRefresh.holdPush())ci.cancel();}
 @Inject(method="pushMeta",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$meta(CallbackInfo ci){if(KjsGenAutomaticRefresh.holdPush())ci.cancel();}
 @Inject(method="requestExport",at=@At("HEAD"),cancellable=true)
 private static void industrialColonies$export(CallbackInfoReturnable<Boolean> ci){if(KjsGenAutomaticRefresh.holdPush()){
   var player=net.minecraft.client.Minecraft.getInstance().player;if(player!=null)player.displayClientMessage(net.minecraft.network.chat.Component.literal("Wait for automatic project refresh/conflict resolution before exporting."),false);ci.setReturnValue(true);
 }}
 @Inject(method="reset",at=@At("HEAD"))
 private static void industrialColonies$reset(CallbackInfo ci){KjsGenAutomaticRefresh.reset();}
}
