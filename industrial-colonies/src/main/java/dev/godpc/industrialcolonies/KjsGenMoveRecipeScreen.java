package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.*;
import com.zizazr.kjsgen.integration.net.ClientEditSession;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.mixin.KjsGenServerProjectStoreAccessor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import java.util.*;
import java.util.concurrent.CompletableFuture;

public final class KjsGenMoveRecipeScreen extends Screen {
    private final Screen parent;
    private final RecipeProject source;
    private final RecipeInstance recipe;
    private int page;
    private String error="";
    public KjsGenMoveRecipeScreen(Screen parent,RecipeProject source,RecipeInstance recipe) {
        super(Component.literal("Move recipe to project"));this.parent=parent;this.source=source;this.recipe=recipe;
    }
    @Override protected void init() {
        var choices=ProjectManager.listProjects().stream()
            .filter(n->!ProjectManager.sanitizeName(n).equalsIgnoreCase(ProjectManager.sanitizeName(source.name())))
            .filter(n->!KjsGenProjectMove.archive(n)).toList();
        int rows=Math.max(1,Math.min(8,(height-100)/24));
        page=Math.min(page,Math.max(0,(choices.size()-1)/rows));
        int x=width/2-140;
        for(int i=page*rows;i<Math.min(choices.size(),(page+1)*rows);i++) {
            String name=choices.get(i);
            addRenderableWidget(Button.builder(Component.literal(name),b->move(name)).bounds(x,38+(i%rows)*24,280,20).build());
        }
        if(choices.isEmpty())error="Create a destination using Projects first.";
        var previous=Button.builder(Component.literal("Previous"),b->{page--;rebuildWidgets();}).bounds(x,height-54,88,20).build();previous.active=page>0;addRenderableWidget(previous);
        var next=Button.builder(Component.literal("Next"),b->{page++;rebuildWidgets();}).bounds(x+96,height-54,88,20).build();next.active=(page+1)*rows<choices.size();addRenderableWidget(next);
        addRenderableWidget(Button.builder(Component.literal("Cancel"),b->onClose()).bounds(x+192,height-54,88,20).build());
    }
    private void move(String destination) {
        if(KjsGenAutomaticRefresh.busy(source.name())){error="Return to the editor to finish automatic refresh first.";return;}
        if(ClientEditSession.isRemote() && !minecraft.hasSingleplayerServer()){error="Project moves are available in local/single-player sessions.";return;}
        try {
            var server=minecraft.getSingleplayerServer();
            RecipeProject updated;
            if(server==null)updated=KjsGenProjectMove.move(ProjectManager.projectsDir(),null,source,recipe,destination);
            else {
                var snapshot=KjsGenProjectMove.copy(source);
                var selected=RecipeInstance.fromJson(recipe.toJson().deepCopy());
                var future=new CompletableFuture<RecipeProject>();
                server.execute(()->{
                    try {future.complete(KjsGenProjectMove.move(ProjectManager.projectsDir(),KjsGenServerProjectStoreAccessor.industrialColonies$loadedProjects(),snapshot,selected,destination));}
                    catch(Throwable e){future.completeExceptionally(e);}
                });
                updated=future.get();
            }
            // This packet follows any pending editor upsert flushed when opening the dialog.
            ClientEditSession.removeRecipe(recipe);
            ClientEditSession.setLocalProject(updated);
            minecraft.setScreen(new VanillaEditorScreen());
            if(minecraft.player!=null)minecraft.player.displayClientMessage(Component.literal("Recipe moved to "+destination+". No scripts exported."),false);
        }catch(Exception e){error=e.getCause()==null?e.getMessage():e.getCause().getMessage();}
    }
    @Override public void render(GuiGraphics g,int x,int y,float partial) {
        renderBackground(g,x,y,partial);super.render(g,x,y,partial);
        g.drawCenteredString(font,title,width/2,12,0xFFFFFFFF);
        if(!error.isEmpty())g.drawWordWrap(font,Component.literal(error),width/2-140,height-30,280,0xFFFF8888);
    }
    @Override public void onClose(){minecraft.setScreen(parent);}
}
