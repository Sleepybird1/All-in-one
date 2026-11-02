package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.integration.net.*;
import dev.godpc.industrialcolonies.mixin.KjsGenEditorScreenAccessor;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import java.util.UUID;

/** Explicit refresh with no input to the old editor while the ordered request is pending. */
public final class KjsGenRefreshScreen extends Screen {
    private static KjsGenRefreshScreen pending;
    private final Screen parent;
    private final RecipeProject project;
    private String message="Merge disk changes with this project. Conflicts stop the refresh; recovery copies are kept. No recipes are exported or installed.";
    private final String token=UUID.randomUUID().toString();
    private boolean waiting;
    private Button refresh,back;
    public KjsGenRefreshScreen(Screen parent,RecipeProject project) {
        super(Component.literal("Refresh project from disk"));this.parent=parent;this.project=project;
    }
    @Override protected void init() {
        refresh=addRenderableWidget(Button.builder(Component.literal("Refresh from disk"),b->request()).bounds(width/2-154,height/2+38,150,20).build());
        back=addRenderableWidget(Button.builder(Component.literal("Back"),b->onClose()).bounds(width/2+4,height/2+38,150,20).build());
        refresh.active=!waiting;back.active=!waiting;
    }
    private void request() {
        if(KjsGenAutomaticRefresh.busy(project.name())){message="Automatic refresh is working or awaiting conflict resolution. Return to the editor first.";return;}
        if(!minecraft.hasSingleplayerServer() || !ClientEditSession.isRemote()) {
            message="Open a project in your single-player world first. Remote multiplayer refresh is not supported.";return;
        }
        waiting=true;pending=this;refresh.active=false;back.active=false;
        JsonObject body=new JsonObject();body.addProperty("project",project.name());body.addProperty("expected",KjsGenProjectRefresh.fingerprint(project));body.addProperty("token",token);
        message="Refreshing project safely...";
        KjsGenNet.toServer("ic_refresh",body.toString());
    }
    public static void result(String json) {
        KjsGenRefreshScreen screen=pending;if(screen==null)return;
        JsonObject result=JsonParser.parseString(json).getAsJsonObject();
        if(!result.has("token") || !screen.token.equals(result.get("token").getAsString()))return;
        pending=null;screen.waiting=false;
        if(result.has("error")) {
            String detail=result.get("error").getAsString();
            screen.message=detail.split(" Both versions preserved")[0];
            if(screen.message.length()>260)screen.message=screen.message.substring(0,257)+"...";
            if(Minecraft.getInstance().player!=null)Minecraft.getInstance().player.displayClientMessage(Component.literal(detail),false);
            screen.refresh.active=true;screen.back.active=true;return;
        }
        RecipeProject updated=RecipeProject.fromJson(result.getAsJsonObject("project"));
        ClientEditSession.setLocalProject(updated);
        KjsGenDesktopBridge.refreshedProject(screen.parent,updated);
        if(Minecraft.getInstance().player!=null) Minecraft.getInstance().player.displayClientMessage(Component.literal("Project refreshed. No recipes exported; game recipes unchanged."),false);
    }
    @Override public boolean shouldCloseOnEsc(){return !waiting;}
    @Override public void onClose(){if(!waiting)minecraft.setScreen(parent);}
    @Override public void render(GuiGraphics g,int x,int y,float partial) {
        renderBackground(g,x,y,partial);super.render(g,x,y,partial);
        g.drawCenteredString(font,title,width/2,height/2-72,0xFFFFFFFF);
        g.drawWordWrap(font,Component.literal(message),width/2-154,height/2-45,308,0xFFE0E0E0);
    }
}
