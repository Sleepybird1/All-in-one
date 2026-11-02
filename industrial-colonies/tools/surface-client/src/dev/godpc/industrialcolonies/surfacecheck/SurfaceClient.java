package dev.godpc.industrialcolonies.surfacecheck;

import dev.godpc.industrialcolonies.geology.SurfaceRocks;
import java.nio.file.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.client.event.ClientTickEvent;

@Mod(value="ic_surface_client",dist=Dist.CLIENT)
public final class SurfaceClient {
    private boolean started;private int ticks;
    public SurfaceClient(){NeoForge.EVENT_BUS.addListener(this::tick);}
    void tick(ClientTickEvent.Post event){
        var mc=Minecraft.getInstance();if(started)return;
        if(!(mc.screen instanceof TitleScreen)||mc.getOverlay()!=null)return;
        if(++ticks<40)return;started=true;
        try {
            for(String material:SurfaceRocks.MATERIALS){
                var block=SurfaceRocks.block(material);var state=block.defaultBlockState();
                var model=mc.getBlockRenderer().getBlockModel(state);
                if(model==mc.getModelManager().getMissingModel())throw new IllegalStateException("Missing model "+material);
                var quads=model.getQuads(state,null,net.minecraft.util.RandomSource.create(1));
                if(quads.size()!=12)throw new IllegalStateException("Expected 12 rock quads: "+material+" got "+quads.size());
                for(var quad:quads)if(quad.getSprite().contents().name().toString().contains("missingno"))throw new IllegalStateException("Missing sprite "+material);
                if(mc.getItemRenderer().getModel(new ItemStack(block),null,null,0)==mc.getModelManager().getMissingModel())throw new IllegalStateException("Missing rock item");
            }
            mc.setScreen(new Sheet());
        }catch(Throwable error){error.printStackTrace();System.out.println("SURFACE_CLIENT_FAIL "+error);mc.stop();}
    }
    private static final class Sheet extends Screen {
        int frames;long done;
        Sheet(){super(Component.literal("Surface prospecting rocks"));}
        @Override public void render(GuiGraphics g,int mouseX,int mouseY,float partial){
            g.fill(0,0,width,height,0xff17221c);g.pose().pushPose();g.pose().scale(width/1280f,height/720f,1);
            g.drawString(font,"SURFACE PROSPECTING ROCKS",30,20,0xffe5efdc,false);
            g.drawString(font,"Actual Minecraft models | 21 collectible geological clues",30,39,0xffb1c7ab,false);
            for(int i=0;i<SurfaceRocks.MATERIALS.size();i++){
                String material=SurfaceRocks.MATERIALS.get(i);int x=30+i%7*177,y=80+i/7*195;
                g.fill(x,y,x+164,y+178,0xff334032);g.pose().pushPose();g.pose().translate(x+32,y+12,0);g.pose().scale(6,6,6);
                g.renderItem(new ItemStack(SurfaceRocks.block(material)),0,0);g.pose().popPose();
                g.drawString(font,material.replace('_',' '),x+7,y+146,0xffeceddf,false);
                g.drawString(font,"Collect by hand",x+7,y+162,0xffb1c7ab,false);
            }
            g.pose().popPose();g.flush();
            try {
                if(++frames==100){
                    Path path=Path.of(System.getProperty("user.dir")).resolve("surface-rocks.png");
                    if(Files.exists(path))throw new IllegalStateException("Screenshot exists");
                    try(var image=Screenshot.takeScreenshot(minecraft.getMainRenderTarget())){image.writeToFile(path);}
                    System.out.println("SURFACE_CLIENT_PASS models=21 quads=252 screenshot="+path);done=System.currentTimeMillis();
                }
                if(done>0&&System.currentTimeMillis()-done>2000)minecraft.stop();
            }catch(Throwable error){error.printStackTrace();System.out.println("SURFACE_CLIENT_FAIL "+error);minecraft.stop();}
        }
    }
}
