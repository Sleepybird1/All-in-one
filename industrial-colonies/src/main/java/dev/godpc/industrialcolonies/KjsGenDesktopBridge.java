package dev.godpc.industrialcolonies;

import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;

import net.minecraft.client.gui.screens.Screen;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.client.event.RenderFrameEvent;
import java.io.*;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import net.minecraft.client.gui.GuiGraphics;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import org.lwjgl.opengl.GL30;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Streams only the native editor, with one outstanding frame and game-thread input. */
public final class KjsGenDesktopBridge {
    private static KjsGenDesktopBridge current;
    private static boolean registered;
    private Process child;
    private DataOutputStream output;
    private final ExecutorService encoder=Executors.newSingleThreadExecutor(r->{var t=new Thread(r,"KJSGen projection frames");t.setDaemon(true);return t;});
    private final AtomicBoolean inFlight=new AtomicBoolean();
    private volatile boolean closed;
    private Screen screen;
    private TextureTarget target;
    private final KjsGenAsyncReadback readback=new KjsGenAsyncReadback();
    private int pendingEpoch,pendingWidth,pendingHeight,pendingGuiWidth,pendingGuiHeight;
    private boolean pendingReadback;
    private int pixelWidth=1600,pixelHeight=900;
    public static boolean detachedContext(){return KjsGenDetachedContext.active()&&current!=null;}
    public static boolean suppressFocusPause(){return current!=null&&!current.closed&&!Minecraft.getInstance().isWindowActive();}
    private void context(Runnable action){
        var mc=Minecraft.getInstance();KjsGenDetachedContext.run(()->mc.screen,value->mc.screen=value,screen,action);
    }
    public static boolean routeScreen(Screen requested){
        var mc=Minecraft.getInstance();
        if(detachedContext()&&current!=null){current.changeScreen(requested);return true;}
        if(mc.level!=null&&requested!=null&&(requested instanceof VanillaEditorScreen||(current!=null&&(requested.getClass().getName().startsWith("com.zizazr.kjsgen.ui.")||requested.getClass().getName().startsWith("dev.godpc.industrialcolonies.KjsGen"))))){
            try{open();current.changeScreen(requested);return true;}
            catch(Exception e){LogUtils.getLogger().error("Could not open detached editor; using in-game editor",e);if(current!=null)current.close();}
        }
        return false;
    }
    private void changeScreen(Screen next){
        if(screen==next)return;
        if(screen!=null)context(()->{release();screen.removed();});
        screen=next;epoch++;
        if(next==null){close();return;}
        context(()->next.init(Minecraft.getInstance(),pixelWidth/2,pixelHeight/2));
        if(detachedContext())Minecraft.getInstance().screen=next;
    }
    public static void refreshSession(){if(!detachedContext()&&current!=null&&current.screen instanceof VanillaEditorScreen editor)current.context(editor::refreshFromSession);}
    public static void refreshedProject(Screen parent,com.zizazr.kjsgen.core.RecipeProject project){
        Runnable apply=()->{((dev.godpc.industrialcolonies.mixin.KjsGenEditorScreenAccessor)parent).industrialColonies$setProject(project);Minecraft.getInstance().setScreen(parent);};
        if(current!=null&&!current.closed)current.context(apply);else apply.run();
    }
    private static void tick(ClientTickEvent.Post event){
        if(current==null)return;
        var active=current;
        if(Minecraft.getInstance().level==null){active.close();return;}
        if(active.screen!=null)active.context(()->active.screen.tick());
    }
    private int epoch,modifiers,held=-1;
    private double mouseX,mouseY;
    private boolean focused;
    private long lastFrame;
    public static boolean editor(Screen s){if(s==null)return false;String n=s.getClass().getName();return n.startsWith("com.zizazr.kjsgen.ui.")||n.startsWith("dev.godpc.industrialcolonies.KjsGen")||n.equals("net.minecraft.client.gui.screens.ConfirmScreen");}
    public static void open()throws IOException {
        if(current!=null&&!current.closed)return;
        var next=new KjsGenDesktopBridge();
        try{next.start();current=next;}catch(IOException e){next.close();throw e;}
        if(!registered){NeoForge.EVENT_BUS.addListener(KjsGenDesktopBridge::afterFrame);NeoForge.EVENT_BUS.addListener(KjsGenDesktopBridge::tick);registered=true;}
    }
    public static boolean externalInput(){return current!=null&&!current.closed&&detachedContext();}
    public static boolean editorUnfocused(){return current!=null&&!current.closed&&!current.focused;}
    public static int pixelWidth(){return current.pixelWidth;}
    public static int pixelHeight(){return current.pixelHeight;}
    public static int mouseX(){return (int)current.mouseX;}
    public static int mouseY(){return (int)current.mouseY;}
    public static int modifiers(){return current.modifiers;}
    private void start()throws IOException {
        Path root=Files.createTempDirectory("industrial-colonies-projection-");
        for(String name:List.of("KjsGenDesktopProtocol","KjsGenFramePixels","KjsGenProjectionInput","KjsGenProjectionInput$Viewport","KjsGenDesktopWindow","KjsGenDesktopWindow$Surface","KjsGenDesktopWindow$MouseInput","KjsGenDesktopWindow$KeyboardInput","KjsGenDesktopWindow$Lifecycle","KjsGenDesktopWindow$ResizeHandler")) {
            String resource="dev/godpc/industrialcolonies/"+name+".class";Path dest=root.resolve(resource);Files.createDirectories(dest.getParent());
            try(var in=KjsGenDesktopBridge.class.getResourceAsStream("/"+resource)){if(in==null)throw new IOException("Projection class missing: "+name);Files.copy(in,dest);}
        }
        Path java=Path.of(System.getProperty("java.home"),"bin",System.getProperty("os.name").startsWith("Windows")?"javaw.exe":"java");
        child=new ProcessBuilder(java.toString(),"-Xmx256m","-Djava.awt.headless=false","-cp",root.toString(),"dev.godpc.industrialcolonies.KjsGenDesktopWindow").redirectError(root.resolve("projection-errors.log").toFile()).start();
        output=new DataOutputStream(new BufferedOutputStream(child.getOutputStream()));
        var reader=new Thread(()->{
            try(var input=new BufferedReader(new InputStreamReader(child.getInputStream(),StandardCharsets.UTF_8))){String line;while((line=input.readLine())!=null){var m=KjsGenDesktopProtocol.decode(line);Minecraft.getInstance().execute(()->handle(m));}}
            catch(Exception e){if(!closed)LogUtils.getLogger().warn("Projection input stopped",e);}
            finally{Minecraft.getInstance().execute(this::close);}
        },"KJSGen projection input");reader.setDaemon(true);reader.start();
    }
    private static void afterFrame(RenderFrameEvent.Post event){if(current!=null)current.capture();}
    private void capture(){
        if(closed||screen==null)return;var mc=Minecraft.getInstance();
        if(mc.level==null){close();return;}
        if(pendingReadback){
            try{byte[] bytes=readback.poll();if(bytes!=null){
                pendingReadback=false;
                final int generation=pendingEpoch,pw=pendingWidth,ph=pendingHeight,gw=pendingGuiWidth,gh=pendingGuiHeight;
                encoder.execute(()->{try{if(closed)return;output.writeInt(0x49435231);output.writeInt(generation);output.writeInt(gw);output.writeInt(gh);output.writeInt(bytes.length+8);output.writeInt(pw);output.writeInt(ph);output.write(bytes);output.flush();}catch(Exception e){Minecraft.getInstance().execute(this::close);}});
            }}catch(Exception e){LogUtils.getLogger().error("Asynchronous editor readback failed",e);close();}
            return;
        }
        long interval=focused?33_333_333L:500_000_000L;
        if(System.nanoTime()-lastFrame<interval||!inFlight.compareAndSet(false,true))return;
        lastFrame=System.nanoTime();final int generation=epoch,w=screen.width,h=screen.height;
        int framebuffer=GL11.glGetInteger(GL30.GL_FRAMEBUFFER_BINDING);int[] viewport=new int[4];GL11.glGetIntegerv(GL11.GL_VIEWPORT,viewport);
        boolean depth=GL11.glIsEnabled(GL11.GL_DEPTH_TEST),blend=GL11.glIsEnabled(GL11.GL_BLEND),scissor=GL11.glIsEnabled(GL11.GL_SCISSOR_TEST),depthMask=GL11.glGetBoolean(GL11.GL_DEPTH_WRITEMASK);
        int[] scissorBox=new int[4];GL11.glGetIntegerv(GL11.GL_SCISSOR_BOX,scissorBox);
        var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();
        var modelView=RenderSystem.getModelViewStack();modelView.pushMatrix();
        try {
            if(target==null)target=new TextureTarget(pixelWidth,pixelHeight,true,Minecraft.ON_OSX);
            RenderSystem.disableScissor();
            target.setClearColor(.06f,.065f,.08f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);
            RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0,w,h,0,1000,21000),VertexSorting.ORTHOGRAPHIC_Z);
            modelView.identity().translate(0,0,-11000);RenderSystem.applyModelViewMatrix();
            var graphics=new GuiGraphics(mc,mc.renderBuffers().bufferSource());
            context(()->screen.renderWithTooltip(graphics,(int)mouseX,(int)mouseY,0));graphics.flush();
            readback.submit(pixelWidth,pixelHeight);pendingReadback=true;
            pendingEpoch=generation;pendingWidth=pixelWidth;pendingHeight=pixelHeight;pendingGuiWidth=w;pendingGuiHeight=h;
        }catch(Exception e){LogUtils.getLogger().error("Detached KJSGen render failed",e);close();}
        finally{modelView.popMatrix();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);GL30.glBindFramebuffer(GL30.GL_FRAMEBUFFER,framebuffer);RenderSystem.viewport(viewport[0],viewport[1],viewport[2],viewport[3]);if(depth)RenderSystem.enableDepthTest();else RenderSystem.disableDepthTest();if(blend)RenderSystem.enableBlend();else RenderSystem.disableBlend();RenderSystem.depthMask(depthMask);if(scissor)RenderSystem.enableScissor(scissorBox[0],scissorBox[1],scissorBox[2],scissorBox[3]);else RenderSystem.disableScissor();}
    }
    private void release(){if(screen!=null&&held>=0){screen.mouseReleased(mouseX,mouseY,held);screen.setDragging(false);}held=-1;modifiers=0;}
    private void handle(String[] m){
        if(closed)return;
        try {
            if(m[0].equals("CLOSE")){context(()->{if(screen!=null)screen.onClose();});close();return;}
            if(m[0].equals("RESIZE")){
                int width=Math.max(640,Math.min(1920,Integer.parseInt(m[1]))),height=Math.max(400,Math.min(1200,Integer.parseInt(m[2])));
                width-=width%2;height-=height%2;
                if(width!=pixelWidth||height!=pixelHeight){pixelWidth=width;pixelHeight=height;epoch++;if(target!=null){target.destroyBuffers();target=null;}if(screen!=null)context(()->screen.resize(Minecraft.getInstance(),pixelWidth/2,pixelHeight/2));}return;
            }
            int generation=Integer.parseInt(m[1]);
            // Even a frame for the previous dialog must release backpressure.
            if(m[0].equals("ACK")){inFlight.set(false);return;}
            if(m[0].equals("FOCUS")){focused=m[2].equals("1");if(!focused)context(this::release);return;}
            if(screen==null||generation!=epoch)return;
            focused=true;
            context(()->{switch(m[0]) {
                case "MOVE","DOWN","UP","DRAG","SCROLL" -> {
                    mouseX=Double.parseDouble(m[2]);mouseY=Double.parseDouble(m[3]);
                    if(!Double.isFinite(mouseX)||!Double.isFinite(mouseY)||mouseX<0||mouseY<0||mouseX>=screen.width||mouseY>=screen.height)return;
                    modifiers=Integer.parseInt(m[m.length-1]);screen.mouseMoved(mouseX,mouseY);
                    switch(m[0]) {
                        case "DOWN" -> {held=Integer.parseInt(m[4]);if(screen.mouseClicked(mouseX,mouseY,held)&&held==0)screen.setDragging(true);}
                        case "UP" -> {screen.mouseReleased(mouseX,mouseY,Integer.parseInt(m[4]));screen.setDragging(false);held=-1;}
                        case "DRAG" -> screen.mouseDragged(mouseX,mouseY,Integer.parseInt(m[4]),Double.parseDouble(m[5]),Double.parseDouble(m[6]));
                        case "SCROLL" -> screen.mouseScrolled(mouseX,mouseY,0,Double.parseDouble(m[4]));
                    }
                }
                case "KEY" -> {int key=Integer.parseInt(m[2]);modifiers=Integer.parseInt(m[4]);if(m[3].equals("1"))screen.keyPressed(key,0,modifiers);else screen.keyReleased(key,0,modifiers);}
                case "CHAR" -> {modifiers=Integer.parseInt(m[3]);screen.charTyped((char)Integer.parseInt(m[2]),modifiers);}
            }});
        }catch(Exception e){LogUtils.getLogger().warn("KJSGen projected input failed",e);release();}
    }
    private void close(){
        if(closed)return;closed=true;
        try{context(()->{release();if(screen!=null)screen.removed();});
            if(Minecraft.getInstance().getConnection()!=null)com.zizazr.kjsgen.integration.net.ClientEditSession.closeProject();
        }catch(Exception e){LogUtils.getLogger().warn("Could not flush detached editor while closing",e);}
        screen=null;focused=false;
        readback.close();
        if(target!=null){target.destroyBuffers();target=null;}
        if(child!=null)child.destroy();encoder.shutdownNow();
        try{if(output!=null)output.close();}catch(IOException ignored){}
        if(current==this)current=null;
    }
}
