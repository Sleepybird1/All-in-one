package dev.godpc.industrialcolonies.fluidcheck;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenFluidRendering;
import dev.godpc.industrialcolonies.mixin.KjsGenEditorScreenAccessor;
import java.nio.file.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.*;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.client.event.ClientTickEvent;
@Mod(value="ic_fluid_client",dist=Dist.CLIENT)
public final class FluidClient {
    private boolean started;private int ticks;
    public FluidClient(){NeoForge.EVENT_BUS.addListener(this::tick);}
    void tick(ClientTickEvent.Post e){
        var mc=Minecraft.getInstance();if(started||mc.screen==null||mc.getOverlay()!=null)return;
        if(!(mc.screen instanceof TitleScreen)&&!mc.screen.getClass().getSimpleName().equals("AccessibilityOnboardingScreen"))return;
        if(++ticks<40)return;started=true;
        System.out.println("FLUID_CLIENT_OPEN from="+mc.screen.getClass().getName());
        mc.options.guiScale().set(2);mc.resizeDisplay();mc.setScreen(new Sheet());
    }
    static final class Sheet extends VanillaEditorScreen {
        int frames;long done;
        static final String[] IDS={"minecraft:water","minecraft:lava","industrial_colonies:phosphoric_acid","nuclearcraft:boric_acid","tfmg:sulfuric_acid","tfmg:hydrogen","modernfoundry:molten_iron"};
        @Override protected void init() {}
        @Override public void tick() {}
        @Override public void removed() {}
        @Override public void render(GuiGraphics g,int mx,int my,float partial){
            try {
                g.fill(0,0,width,height,0xff202630);
                g.drawString(font,"KubeJS Gen ingredient slots — native renderer",12,12,0xffffffff);
                for(int i=0;i<IDS.length;i++){
                    var content=SlotContent.fluid(IDS[i],i==6?1000:250);
                    if(KjsGenFluidRendering.resolve(content)==Fluids.EMPTY)throw new IllegalStateException("Missing fluid "+IDS[i]);
                    int y=40+i*27;g.fill(12,y,32,y+20,0xff626c7a);
                    ((KjsGenEditorScreenAccessor)(Object)this).industrialColonies$drawSlotContent(g,13,y+1,content);
                    g.drawString(font,IDS[i],40,y+6,0xffeff4ff);
                }
                // Existing item rendering and invalid-fluid fallback remain visible.
                ((KjsGenEditorScreenAccessor)(Object)this).industrialColonies$drawSlotContent(g,13,239,SlotContent.item("tfmg:n_semiconductor",2));
                g.drawString(font,"High-Density Semiconductor (pink)",40,245,0xffeff4ff);
                g.flush();
                if(++frames==60){
                    Path path=Path.of(System.getProperty("user.dir")).resolve("fluid-slots.png");
                    try(var image=Screenshot.takeScreenshot(minecraft.getMainRenderTarget())){image.writeToFile(path);}
                    System.out.println("FLUID_CLIENT_PASS fluidSlots=7 actualEditorMixin=PASS screenshot="+path);done=System.currentTimeMillis();
                }
                if(done>0&&System.currentTimeMillis()-done>1000)minecraft.stop();
            }catch(Throwable error){error.printStackTrace();System.out.println("FLUID_CLIENT_FAIL "+error);minecraft.stop();}
        }
    }
}
