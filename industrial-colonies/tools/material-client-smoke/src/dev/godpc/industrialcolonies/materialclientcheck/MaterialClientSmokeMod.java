package dev.godpc.industrialcolonies.materialclientcheck;

import com.google.gson.*;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import dev.godpc.industrialcolonies.geology.GeologyBlocks;
import java.lang.reflect.Method;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.fluids.FluidStack;

/** Current full-client GPU fixture only. Never opens a world, connects, or dismisses onboarding. */
@Mod(value="ic_material_client_smoke",dist=Dist.CLIENT)
public final class MaterialClientSmokeMod {
    private boolean started;
    private int titleTicks,assertions;
    private long waitStartedNanos,lastWaitLogMillis;
    private String lastWaitState;
    private final long titleWaitLimit=Math.min(600000L,Math.max(1000L,Long.getLong("ic.materialclient.titleWaitMillis",180000L)));
    private Path stage,reportPath,screenshotDir;
    private JsonObject preparation,content;
    private final JsonObject report=new JsonObject();
    private final JsonArray screenshots=new JsonArray();
    private final List<Entry> rocks=new ArrayList<>(),items=new ArrayList<>();
    private final List<FluidEntry> fluids=new ArrayList<>();
    private record Entry(String id,ItemStack stack,String note) { }
    private record FluidEntry(String id,TextureAtlasSprite still,TextureAtlasSprite flow,int tint) { }
    public MaterialClientSmokeMod() {
        System.out.println("MATERIAL_CLIENT_BOOTSTRAP awaiting native client ticks; titleWaitLimitMillis="+titleWaitLimit+"; no screen dismissal");
        NeoForge.EVENT_BUS.addListener(this::tick);
    }

    private void tick(ClientTickEvent.Post event) {
        Minecraft mc=Minecraft.getInstance();
        if(started)return;
        try {
            if(waitStartedNanos==0){initializePaths(mc);waitStartedNanos=System.nanoTime();}
            check(mc.level==null&&mc.getConnection()==null,"Unexpected world/connection while waiting for test title screen");
            long waited=(System.nanoTime()-waitStartedNanos)/1_000_000;
            if(!(mc.screen instanceof TitleScreen)||mc.getOverlay()!=null) {
                titleTicks=0;
                String screen=mc.screen==null?"none":mc.screen.getClass().getName();
                String overlay=mc.getOverlay()==null?"none":mc.getOverlay().getClass().getName();
                String state=screen+" / "+overlay;
                if(!state.equals(lastWaitState)||waited-lastWaitLogMillis>=15000) {
                    System.out.println("MATERIAL_CLIENT_WAIT elapsedMillis="+waited+" limitMillis="+titleWaitLimit+" screen="+screen+" overlay="+overlay);
                    lastWaitState=state;lastWaitLogMillis=waited;
                }
                JsonObject wait=new JsonObject();wait.addProperty("elapsedMilliseconds",waited);wait.addProperty("limitMilliseconds",titleWaitLimit);
                wait.addProperty("screenClass",screen);wait.addProperty("overlayClass",overlay);wait.addProperty("screenDismissed",false);report.add("initialScreenWait",wait);
                check(waited<titleWaitLimit,"Timed out waiting for unblocked TitleScreen; screen="+screen+" overlay="+overlay+" (no screen was dismissed)");
                return;
            }
            if(++titleTicks<40)return; started=true;
            report.addProperty("titleReadyAfterMilliseconds",waited);
            initialize(mc); checkGeology(mc); checkItems(mc); checkFluids(mc); checkRadiance();
            mc.setScreen(new RenderSheets());
        } catch(Throwable failure) { started=true;fail(failure); }
    }
    private void check(boolean condition,String message) { assertions++;if(!condition)throw new IllegalStateException(message); }
    private Path guarded(String property) throws Exception {
        String value=System.getProperty(property);check(value!=null&&!value.isBlank(),"Missing property "+property);
        Path path=Path.of(value).toAbsolutePath().normalize();
        check(path.startsWith(stage)&&!path.equals(stage),"Output/input path escaped disposable stage: "+path);
        return path;
    }
    private static String hash(Path path) throws Exception { return hash(Files.readAllBytes(path)); }
    private static String hash(byte[] bytes) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)); }
    private void initializePaths(Minecraft mc) throws Exception {
        stage=Path.of(System.getProperty("ic.materialclient.requireStageRoot")).toRealPath();
        check(mc.gameDirectory.toPath().toRealPath().equals(stage),"Minecraft game directory differs from required stage");
        check(Path.of(System.getProperty("user.dir")).toRealPath().equals(stage),"Process directory differs from required stage");
        check(mc.level==null&&mc.getConnection()==null,"Client must not connect or open a world");
        Path proposedReport=guarded("ic.materialclient.report"),proposedScreenshots=guarded("ic.materialclient.screenshots");
        check(!Files.exists(proposedReport)&&!Files.exists(proposedScreenshots),"Refusing to overwrite prior client evidence");
        reportPath=proposedReport;screenshotDir=proposedScreenshots;
        report.addProperty("stage",stage.toString());report.addProperty("waitingStartedUtc",Instant.now().toString());
    }
    private void initialize(Minecraft mc) throws Exception {
        preparation=JsonParser.parseString(Files.readString(guarded("ic.materialclient.manifest"))).getAsJsonObject();
        check(preparation.get("stagedJarCount").getAsInt()==241,"Wrong full-client physical JAR count");
        check(preparation.getAsJsonObject("initialOptions").get("content").getAsString().equals("onboardAccessibility:false\n"),"Unexpected first-launch fixture options");
        check(!mc.options.onboardAccessibility,"Native orientation-only initial options seed was not applied");
        report.add("initialOptionsSeed",preparation.getAsJsonObject("initialOptions").deepCopy());
        verifyJars();
        Path contentPath=stage.resolve("material-client-inputs/content.json"),catalogPath=stage.resolve("material-client-inputs/catalog.json");
        check(hash(contentPath).equalsIgnoreCase(preparation.get("contentSha256").getAsString()),"Source content snapshot changed");
        check(hash(catalogPath).equalsIgnoreCase(preparation.get("catalogSha256").getAsString()),"Recipe catalog snapshot changed");
        try(var in=GeologyBlocks.class.getResourceAsStream("/data/industrial_colonies/processing/content.json")) {
            check(in!=null,"Loaded candidate has no material content manifest");
            check(hash(in.readAllBytes()).equalsIgnoreCase(preparation.get("contentSha256").getAsString()),"Loaded candidate content differs from copied authoritative source manifest");
        }
        content=JsonParser.parseString(Files.readString(contentPath)).getAsJsonObject();
        check(content.getAsJsonObject("items").size()==74&&content.getAsJsonObject("fluids").size()==25,"Expected 74 new items and 25 tank fluids");
        report.addProperty("startedUtc",Instant.now().toString());
        report.addProperty("scope","Real full-client stitched sprites, baked models, GPU item/fluid sheet renders and transformed Radiance redirect; no connection, world, player operation or survival certification");
        report.addProperty("graphicsBackend",RenderSystem.getBackendDescription());report.addProperty("graphicsApi",RenderSystem.getApiDescription());
        report.addProperty("physicalInputJars",241);report.addProperty("loadedModIds",ModList.get().size());
        report.addProperty("candidateSha256",preparation.get("candidateSha256").getAsString());
        report.addProperty("contentSha256",preparation.get("contentSha256").getAsString());report.addProperty("catalogSha256",preparation.get("catalogSha256").getAsString());
        report.addProperty("catalogRecipes",JsonParser.parseString(Files.readString(catalogPath)).getAsJsonObject().getAsJsonObject("recipes").size());
    }
    private void verifyJars() throws Exception {
        try(var files=Files.list(stage.resolve("mods"))) {
            check(files.filter(p->p.getFileName().toString().endsWith(".jar")).count()==241,"Staged physical JAR set changed");
        }
        for(JsonElement entry:preparation.getAsJsonArray("mods")) {
            JsonObject row=entry.getAsJsonObject();Path file=stage.resolve("mods").resolve(row.get("name").getAsString());
            check(file.normalize().getParent().equals(stage.resolve("mods")),"Unsafe JAR manifest name");
            check(Files.isRegularFile(file)&&Files.size(file)==row.get("bytes").getAsLong()&&hash(file).equalsIgnoreCase(row.get("sha256").getAsString()),"Staged JAR mismatch: "+file.getFileName());
        }
    }
    private List<BakedQuad> quads(BakedModel model,BlockState state) {
        List<BakedQuad> result=new ArrayList<>(model.getQuads(state,null,RandomSource.create(0)));
        for(Direction side:Direction.values())result.addAll(model.getQuads(state,side,RandomSource.create(0)));
        return result;
    }
    private void sprite(TextureAtlasSprite sprite,String id) {
        check(sprite!=null&&!sprite.contents().name().toString().contains("missingno"),"Missing stitched sprite for "+id);
        check(sprite.contents().width()>0&&sprite.contents().height()>0,"Empty sprite dimensions for "+id);
    }
    private void checkGeology(Minecraft mc) {
        List<String> ids=new ArrayList<>(GeologyBlocks.APPROVED_IDS);ids.add("gold_flakes");
        check(ids.size()==41&&new HashSet<>(ids).size()==41,"Expected 40 approved geology cubes plus one Gold Flakes block");
        JsonArray rows=new JsonArray();int total=0;
        for(String id:ids) {
            BlockState state=GeologyBlocks.block(id).defaultBlockState();ItemStack stack=new ItemStack(state.getBlock());
            BakedModel block=mc.getBlockRenderer().getBlockModel(state),item=mc.getItemRenderer().getModel(stack,null,null,0);
            check(block!=mc.getModelManager().getMissingModel()&&item!=mc.getModelManager().getMissingModel(),"Missing geology block/item model "+id);
            List<BakedQuad> quads=quads(block,state);int expectedQuads=id.equals("gold_flakes")?18:6;
            check(quads.size()==expectedQuads,"Changed accepted geometry: "+id+" quads="+quads.size());total+=quads.size();
            JsonObject sprites=new JsonObject();
            for(BakedQuad quad:quads) {
                var sprite=quad.getSprite();sprite(sprite,id);int expected=id.equals("bertrandite")?1254:16;
                check(sprite.contents().width()==expected&&sprite.contents().height()==expected,"Changed approved sprite resolution for "+id);
                sprites.add(sprite.contents().name().toString(),new Gson().toJsonTree(List.of(sprite.contents().width(),sprite.contents().height())));
            }
            sprite(item.getParticleIcon(),id);check(item.isGui3d(),"Geology item lost cube GUI rendering: "+id);
            JsonObject row=new JsonObject();row.addProperty("id",id);row.addProperty("blockQuads",quads.size());row.add("sprites",sprites);rows.add(row);
            rocks.add(new Entry(id,stack,id.equals("bertrandite")?"1254 px approved source":"16 px approved source"));
        }
        check(total==258,"Expected unchanged total of 258 geology/placer quads");report.add("geologyModels",rows);report.addProperty("geologyQuads",total);
    }
    private void checkItems(Minecraft mc) {
        JsonArray rows=new JsonArray();
        for(var entry:content.getAsJsonObject("items").entrySet()) {
            String id="industrial_colonies:"+entry.getKey();ResourceLocation key=ResourceLocation.parse(id);
            check(BuiltInRegistries.ITEM.containsKey(key),"Missing new material item "+id);
            ItemStack stack=new ItemStack(BuiltInRegistries.ITEM.get(key));check(!stack.isEmpty(),"Material item resolved to air "+id);
            BakedModel model=mc.getItemRenderer().getModel(stack,null,null,0);check(model!=mc.getModelManager().getMissingModel(),"Missing material item model "+id);
            List<BakedQuad> quads=quads(model,null);check(!quads.isEmpty(),"Material item has no native baked quads "+id);
            String expected=entry.getValue().getAsJsonObject().get("texture").getAsString();Set<String> used=new LinkedHashSet<>();
            for(BakedQuad quad:quads) {sprite(quad.getSprite(),id);used.add(quad.getSprite().contents().name().toString());}
            sprite(model.getParticleIcon(),id);check(used.contains(expected),"Material item did not stitch its configured source sprite: "+id+" expected="+expected+" actual="+used);
            JsonObject row=new JsonObject();row.addProperty("id",id);row.addProperty("quads",quads.size());row.addProperty("expectedTexture",expected);row.add("sprites",new Gson().toJsonTree(used));rows.add(row);
            items.add(new Entry(entry.getKey(),stack,expected));
        }
        check(items.size()==74,"Not all 74 material items were checked");report.add("materialItemModels",rows);
    }
    private void checkFluids(Minecraft mc) {
        JsonArray rows=new JsonArray();
        for(var entry:content.getAsJsonObject("fluids").entrySet()) {
            String id="industrial_colonies:"+entry.getKey();ResourceLocation key=ResourceLocation.parse(id),flowKey=ResourceLocation.parse("industrial_colonies:flowing_"+entry.getKey());
            check(BuiltInRegistries.FLUID.containsKey(key)&&BuiltInRegistries.FLUID.containsKey(flowKey),"Missing source/flowing tank fluid pair "+id);
            Fluid source=BuiltInRegistries.FLUID.get(key),flow=BuiltInRegistries.FLUID.get(flowKey);
            check(source!=Fluids.EMPTY&&flow!=Fluids.EMPTY&&source!=flow,"Invalid source/flowing fluid registration "+id);
            check(source instanceof FlowingFluid&&((FlowingFluid)source).getSource()==source&&((FlowingFluid)source).getFlowing()==flow,"Broken native flowing/source linkage "+id);
            check(source.getBucket()==Items.AIR&&flow.getBucket()==Items.AIR,"Tank-only intermediate unexpectedly has a bucket "+id);
            check(source.getFluidType()==flow.getFluidType(),"Source/flowing pair has different fluid types "+id);
            var extension=IClientFluidTypeExtensions.of(source);var flowExtension=IClientFluidTypeExtensions.of(flow);
            FluidStack stack=new FluidStack(source,1000);ResourceLocation still=extension.getStillTexture(stack),flowing=extension.getFlowingTexture(stack);
            check(still!=null&&flowing!=null,"Uninitialized client fluid extension "+id);
            int tint=extension.getTintColor(stack),expected=(int)entry.getValue().getAsJsonObject().get("color").getAsLong();
            check(tint==expected&&flowExtension.getTintColor(new FluidStack(flow,1000))==expected,"Tank fluid tint differs from source catalog "+id);
            check((tint>>>24)!=0,"Invisible fluid tint "+id);
            TextureAtlasSprite stillSprite=mc.getTextureAtlas(TextureAtlas.LOCATION_BLOCKS).apply(still),flowSprite=mc.getTextureAtlas(TextureAtlas.LOCATION_BLOCKS).apply(flowing);
            sprite(stillSprite,id+" still");sprite(flowSprite,id+" flow");
            check(stillSprite.contents().name().equals(still)&&flowSprite.contents().name().equals(flowing),"Fluid atlas resolved the wrong texture "+id);
            JsonObject row=new JsonObject();row.addProperty("id",id);row.addProperty("flowingId",flowKey.toString());row.addProperty("argb",String.format("%08X",tint));row.addProperty("still",still.toString());row.addProperty("flow",flowing.toString());
            row.add("stillDimensions",new Gson().toJsonTree(List.of(stillSprite.contents().width(),stillSprite.contents().height())));row.add("flowDimensions",new Gson().toJsonTree(List.of(flowSprite.contents().width(),flowSprite.contents().height())));rows.add(row);
            fluids.add(new FluidEntry(entry.getKey(),stillSprite,flowSprite,tint));
        }
        check(fluids.size()==25,"Not all 25 fluid pairs were checked");report.add("tankFluidSprites",rows);report.addProperty("fluidSpriteChecks",50);
    }
    private void checkRadiance() throws Exception {
        ResourceLocation key=ResourceLocation.parse("create:chromatic_compound");check(BuiltInRegistries.ITEM.containsKey(key),"Missing native Chromatic Compound item");
        Object compound=BuiltInRegistries.ITEM.get(key);Class<?> type=compound.getClass();
        check(type.getName().equals("com.simibubi.create.content.legacy.ChromaticCompoundItem"),"Unexpected native Chromatic Compound runtime class");
        List<Method> handlers=Arrays.stream(type.getDeclaredMethods()).filter(m->m.getName().contains("engineeredRadianceOnly")&&m.getParameterCount()==1).toList();
        check(handlers.size()==1,"Production Radiance redirect did not merge exactly once into the actual loaded Create class");
        Method handler=handlers.getFirst();handler.setAccessible(true);
        check(handler.getParameterTypes()[0].getName().equals("net.createmod.catnip.config.ConfigBase$ConfigBool"),"Radiance redirect targets the wrong config getter signature");
        Object server=Class.forName("com.simibubi.create.infrastructure.config.AllConfigs").getMethod("server").invoke(null);
        Object recipes=server.getClass().getField("recipes").get(server),radiance=recipes.getClass().getField("enableRefinedRadianceRecipe").get(recipes);
        check(Boolean.FALSE.equals(handler.invoke(compound,radiance)),"Applied Radiance redirect did not disable the legacy conversion branch");
        JsonObject row=new JsonObject();row.addProperty("nativeClass",type.getName());row.addProperty("mergedHandler",handler.getName());row.addProperty("refinedRadianceBranchReturnsFalse",true);
        row.addProperty("scope","Strict production mixin applied during native class loading; merged Refined Radiance branch invoked. No thrown entity/world or Shadow Steel config mutation.");report.add("radianceRuntimeApplicability",row);
    }
    private void save() throws Exception {
        report.addProperty("assertions",assertions);report.add("screenshots",screenshots);
        Files.writeString(reportPath,new GsonBuilder().setPrettyPrinting().create().toJson(report)+System.lineSeparator());
    }
    private void fail(Throwable failure) {
        report.addProperty("status","FAIL");report.addProperty("error",failure.toString());failure.printStackTrace();
        try {if(reportPath!=null)save();}catch(Exception write){write.printStackTrace();}
        System.err.println("MATERIAL_CLIENT_RENDER_FAIL "+failure);Minecraft.getInstance().stop();
    }
    private final class RenderSheets extends Screen {
        private int page,frames,totalFrames;private long completed;
        RenderSheets(){super(Component.literal("Industrial Colonies — native material client acceptance"));}
        @Override public void render(GuiGraphics g,int mouseX,int mouseY,float partialTick) {
            try {
                check(minecraft.level==null&&minecraft.getConnection()==null,"Unexpected client connection or world during rendering");
                g.fill(0,0,width,height,0xff10171d);g.pose().pushPose();g.pose().scale(width/1280f,height/720f,1);
                String title=page==0?"41 GEOLOGY BLOCKS / 258 QUADS":page==3?"25 TANK FLUIDS / STILL + FLOW":("MATERIAL COMPONENTS "+(page==1?"1–48":"49–74"));
                g.drawString(font,"INDUSTRIAL COLONIES | ACTUAL CLIENT GPU RENDER | "+title,20,12,0xffecf1f5,false);
                g.drawString(font,"Full 241-JAR disposable client | current source catalog | no world / no connection",20,27,0xff9facb6,false);
                if(page==3)drawFluids(g);else drawItems(g,page==0?rocks:items,page==2?48:0);
                g.drawString(font,"Native baked items and stitched, tinted fluid sprites — not generated artwork or a powered-machine simulation.",20,704,0xff9facb6,false);
                g.pose().popPose();g.flush();totalFrames++;
                if(completed==0&&++frames==120) {
                    capture();
                    if(page<3){page++;frames=0;}else {
                        verifyJars();report.addProperty("renderedFrames",totalFrames);report.addProperty("status","PASS");report.addProperty("completedUtc",Instant.now().toString());save();
                        System.out.println("MATERIAL_CLIENT_RENDER_PASS items=74 fluids=25 geology=41 quads=258 screenshots="+screenshots.size());completed=System.currentTimeMillis();
                    }
                }
                if(completed!=0&&System.currentTimeMillis()-completed>5000&&Boolean.getBoolean("ic.materialclient.exitAfterSuccess"))minecraft.stop();
            }catch(Throwable failure){fail(failure);}
        }
        private void drawItems(GuiGraphics g,List<Entry> entries,int start) {
            for(int n=0;n<48&&start+n<entries.size();n++) {
                Entry entry=entries.get(start+n);int x=20+n%8*157,y=48+n/8*107;
                g.fill(x,y,x+149,y+101,0xff1c252e);g.pose().pushPose();g.pose().translate(x+43,y+3,0);g.pose().scale(3.7f,3.7f,3.7f);g.renderItem(entry.stack(),0,0);g.pose().popPose();
                String label=entry.id().replace('_',' ');int split=label.lastIndexOf(' ',Math.min(label.length()-1,23));
                if(font.width(label)>143&&split>0){g.drawString(font,label.substring(0,split),x+3,y+71,0xffe1e8ed,false);g.drawString(font,label.substring(split+1),x+3,y+82,0xffe1e8ed,false);}else g.drawString(font,label,x+3,y+76,0xffe1e8ed,false);
                g.drawString(font,page==0?entry.note():"native item model",x+3,y+93,0xff96a8b4,false);
            }
        }
        private void drawFluids(GuiGraphics g) {
            for(int i=0;i<fluids.size();i++) {
                FluidEntry fluid=fluids.get(i);int x=20+i%5*250,y=50+i/5*129;
                g.fill(x,y,x+241,y+120,0xff1c252e);
                float a=(fluid.tint()>>>24)/255f,r=((fluid.tint()>>>16)&255)/255f,green=((fluid.tint()>>>8)&255)/255f,b=(fluid.tint()&255)/255f;
                g.blit(x+20,y+5,0,64,64,fluid.still(),r,green,b,a);g.blit(x+143,y+5,0,64,64,fluid.flow(),r,green,b,a);
                g.drawString(font,"still",x+37,y+72,0xff9facb6,false);g.drawString(font,"flow",x+160,y+72,0xff9facb6,false);
                String name=fluid.id().replace('_',' ');g.drawString(font,name,x+5,y+90,0xffe1e8ed,false);g.drawString(font,String.format("ARGB %08X",fluid.tint()),x+5,y+104,0xff96a8b4,false);
            }
        }
        private void capture() throws Exception {
            Files.createDirectories(screenshotDir);String name=switch(page){case 0->"01-geology-blocks.png";case 1->"02-material-items-a.png";case 2->"03-material-items-b.png";default->"04-tank-fluids.png";};
            Path path=screenshotDir.resolve(name);check(!Files.exists(path),"Refusing to overwrite framebuffer evidence");
            JsonObject shot=new JsonObject();try(NativeImage image=Screenshot.takeScreenshot(minecraft.getMainRenderTarget())){image.writeToFile(path);shot.addProperty("width",image.getWidth());shot.addProperty("height",image.getHeight());}
            shot.addProperty("path",path.toString());shot.addProperty("sha256",hash(path));shot.addProperty("frames",frames);screenshots.add(shot);
        }
    }
}
