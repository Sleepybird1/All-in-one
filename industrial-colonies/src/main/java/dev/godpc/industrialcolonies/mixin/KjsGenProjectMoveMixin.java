package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenWindowSize;
import dev.godpc.industrialcolonies.KjsGenWindowSizeScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.List;
import dev.godpc.industrialcolonies.KjsGenDesktopBridge;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RecipeInstance;

/** Saved editor size and a separate navigation row, without touching GUI scale. */
@Mixin(value=VanillaEditorScreen.class,remap=false)
public abstract class KjsGenProjectMoveMixin extends Screen {
    protected KjsGenProjectMoveMixin(Component title){super(title);}
    @Unique private boolean industrialColonies$desktopAttempted;
    @Shadow private int listY;
    @Shadow private int listViewH;
    @Shadow private int canvasBoxY;
    @Shadow private int canvasBoxH;
    @Shadow private int paramY;
    @Shadow private int paramViewH;
    @Shadow private int previewH;
    @Shadow private int menuX;
    @Shadow private int menuY;
    @Shadow private int menuW;
    @Shadow private int menuH;
    @Shadow @Final private List<AbstractWidget> menuItems;
    @Shadow private RecipeProject project;
    @ModifyConstant(method="computeGeometry",constant=@Constant(intValue=560))
    private int industrialColonies$windowWidth(int original){return KjsGenWindowSize.dimension(width,560,KjsGenWindowSize.width());}
    @ModifyConstant(method="computeGeometry",constant=@Constant(intValue=320))
    private int industrialColonies$windowHeight(int original){return KjsGenWindowSize.dimension(height,240,KjsGenWindowSize.height());}
    @Inject(method="computeGeometry",at=@At("TAIL"))
    private void industrialColonies$navigationRow(CallbackInfo ci){
        listY+=18;listViewH=Math.max(20,listViewH-18);
        canvasBoxY+=18;canvasBoxH=Math.max(30,canvasBoxH-18);
        paramY+=18;paramViewH=Math.max(18,paramViewH-18);
        previewH=Math.max(18,previewH-24);
    }
    @Inject(method="init",at=@At("TAIL"))
    private void industrialColonies$sizeMenu(CallbackInfo ci){
        int right=menuX+menuW;menuW=Math.max(menuW,88);menuX=right-menuW;
        for(var item:menuItems){item.setX(menuX);item.setWidth(menuW);}
        var button=Button.builder(Component.literal("Window size..."),b->minecraft.setScreen(new KjsGenWindowSizeScreen(this)))
                .bounds(menuX,menuY+menuItems.size()*16,menuW,16).build();
        button.visible=false;button.active=false;
        menuItems.add(button);addWidget(button);
        var desktop=Button.builder(Component.literal("Project editor"),b->industrialColonies$openDesktop())
            .bounds(menuX,menuY+menuItems.size()*16,menuW,16).build();
        desktop.visible=false;desktop.active=false;menuItems.add(desktop);addWidget(desktop);
        var refresh=Button.builder(Component.literal("Refresh from disk"),b->minecraft.setScreen(new dev.godpc.industrialcolonies.KjsGenRefreshScreen(this,project)))
            .bounds(menuX,menuY+menuItems.size()*16,menuW,16).build();
        refresh.visible=false;refresh.active=false;menuItems.add(refresh);addWidget(refresh);
        menuH=menuItems.size()*16;
    }

    @Unique private void industrialColonies$openDesktop() {
        try {
            KjsGenDesktopBridge.open();
        }catch(Exception e){if(minecraft.player!=null)minecraft.player.displayClientMessage(Component.literal("Desktop editor could not open: "+e.getMessage()),false);}
    }
}
