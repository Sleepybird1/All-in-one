package dev.godpc.industrialcolonies;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;

public final class KjsGenWindowSizeScreen extends Screen {
    private final Screen parent;
    private double windowWidth=KjsGenWindowSize.width(),windowHeight=KjsGenWindowSize.height();
    private String error="";
    public KjsGenWindowSizeScreen(Screen parent){super(Component.literal("Editor window size"));this.parent=parent;}
    @Override protected void init() {
        int w=Math.min(300,width-24),x=(width-w)/2,y=Math.max(34,height/2-64);
        addRenderableWidget(new SizeSlider(x,y,w,true));
        addRenderableWidget(new SizeSlider(x,y+28,w,false));
        addRenderableWidget(Button.builder(Component.literal("Fit screen"),b->{windowWidth=1;windowHeight=1;rebuildWidgets();}).bounds(x,y+58,w,20).build());
        addRenderableWidget(Button.builder(Component.literal("Apply"),b->{
            try{KjsGenWindowSize.save(windowWidth,windowHeight);onClose();}
            catch(Exception e){error="Could not save window size.";}
        }).bounds(x,y+86,(w-6)/2,20).build());
        addRenderableWidget(Button.builder(Component.literal("Cancel"),b->onClose()).bounds(x+(w+6)/2,y+86,(w-6)/2,20).build());
    }
    private final class SizeSlider extends AbstractSliderButton {
        private final boolean horizontal;
        SizeSlider(int x,int y,int w,boolean horizontal){super(x,y,w,20,Component.empty(),((horizontal?windowWidth:windowHeight)-.5)*2);this.horizontal=horizontal;updateMessage();}
        @Override protected void updateMessage(){setMessage(Component.literal((horizontal?"Width: ":"Height: ")+Math.round((.5+value*.5)*100)+"%"));}
        @Override protected void applyValue(){if(horizontal)windowWidth=.5+value*.5;else windowHeight=.5+value*.5;}
    }
    @Override public void render(GuiGraphics g,int x,int y,float partial){
        renderBackground(g,x,y,partial);super.render(g,x,y,partial);
        g.drawCenteredString(font,title,width/2,14,0xFFFFFFFF);
        g.drawCenteredString(font,Component.literal("Changes this editor only. GUI scale stays unchanged."),width/2,27,0xFFBBBBBB);
        if(!error.isEmpty())g.drawCenteredString(font,Component.literal(error),width/2,height-20,0xFFFF8888);
    }
    @Override public void onClose(){minecraft.setScreen(parent);}
}
