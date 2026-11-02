package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientPacketListener;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Client-only, opt-in registration. Observes server recipes without rewriting them. */
@Mixin(ClientPacketListener.class)
public abstract class ClientPotionRecipeMixin {
    @Inject(method="handleUpdateRecipes", at=@At("RETURN"))
    private void industrialColonies$admitSynchronizedPotions(CallbackInfo ci) {
        var connection=(ClientPacketListener)(Object)this;
        var client=Minecraft.getInstance();
        var manager=connection.getRecipeManager();
        PotionIdentityRuntime.bindClient(() -> client.isSameThread()&&client.getConnection()==connection
                ?manager:null);
        try { PotionIdentityRuntime.admitClient(manager,connection.registryAccess()); }
        catch(RuntimeException error) {
            PotionIdentityRuntime.invalidate(manager);
            org.slf4j.LoggerFactory.getLogger(ClientPotionRecipeMixin.class).warn("Client potion display conversion held",error);
        }
    }
}
