package dev.godpc.industrialcolonies.mixin;
import com.google.gson.*;
import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.integration.net.*;
import dev.godpc.industrialcolonies.KjsGenProjectRefresh;
import dev.godpc.industrialcolonies.KjsGenProjectMove;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.*;

@Mixin(value=ServerProjectStore.class,remap=false)
public abstract class KjsGenServerRefreshMixin {
    @Shadow @Final private static Map<String,RecipeProject> loaded;
    @Shadow @Final private static Map<String,Set<UUID>> viewers;
    @Shadow @Final private static Map<UUID,String> viewing;
    @Unique private static long industrialColonies$lastNotice;
    @Inject(method="handle",at=@At("TAIL"))
    private static void industrialColonies$notice(ServerPlayer player,String op,String json,CallbackInfo ci) {
        if(!Set.of("upsertRecipe","removeRecipe","upsertRemoval","removeRemoval","meta").contains(op))return;
        try {
            String name=JsonParser.parseString(json).getAsJsonObject().get("project").getAsString();
            if(!KjsGenProjectMove.archive(name) && KjsGenProjectRefresh.changed(ProjectManager.fileFor(name)) && System.currentTimeMillis()-industrialColonies$lastNotice>5000) {
                industrialColonies$lastNotice=System.currentTimeMillis();
                player.sendSystemMessage(net.minecraft.network.chat.Component.literal("KubeJS Gen: disk project changed. Your editor work is preserved; use menu > Refresh from disk before continuing."));
            }
        }catch(Exception ignored) {}
    }
    @Inject(method="handle",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$refresh(ServerPlayer player,String op,String json,CallbackInfo ci) {
        if(!op.equals("ic_refresh")) return;
        ci.cancel(); JsonObject result=new JsonObject();
        try {
            JsonObject request=JsonParser.parseString(json).getAsJsonObject();
            result.addProperty("token",request.get("token").getAsString());
            var server=player.getServer();
            if(server==null || !server.isSingleplayerOwner(player.getGameProfile())) throw new Exception("Refresh is restricted to the local single-player owner.");
            String name=request.get("project").getAsString(), key=ProjectManager.sanitizeName(name);
            if(KjsGenProjectMove.archive(name))throw new Exception("Refresh a regular project; review archives are managed by approval controls.");
            if(!key.equals(viewing.get(player.getUUID())) || viewers.getOrDefault(key,Set.of()).size()!=1)
                throw new Exception("Close other project viewers before refreshing.");
            RecipeProject project=loaded.get(key);
            if(project==null || !KjsGenProjectRefresh.fingerprint(project).equals(request.get("expected").getAsString()))
                throw new Exception("Editor and server are not synchronized. Nothing reloaded; save/synchronize and retry.");
            RecipeProject updated=KjsGenProjectRefresh.refresh(ProjectManager.fileFor(name),project);
            loaded.put(key,updated); result.add("project",updated.toJson());
        }catch(Exception e){result.addProperty("error",e.getMessage()==null?e.toString():e.getMessage());}
        KjsGenNet.toPlayer(player,"ic_refresh_result",result.toString());
    }
    // Exporting a stale cached project would bypass the explicit disk review.
    @Inject(method="export",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$exportGuard(ServerPlayer player,String name,CallbackInfo ci) {
        if(KjsGenProjectMove.archive(name))return;
        try {if(!KjsGenProjectRefresh.changed(ProjectManager.fileFor(name))) return;}
        catch(Exception ignored) {}
        ci.cancel();JsonObject error=new JsonObject();error.addProperty("error","Project changed on disk. Refresh from disk before exporting.");
        KjsGenNet.toPlayer(player,"exportResult",error.toString());
    }
}
