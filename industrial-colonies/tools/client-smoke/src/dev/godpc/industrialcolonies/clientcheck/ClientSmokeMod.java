package dev.godpc.industrialcolonies.clientcheck;

import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import dev.godpc.industrialcolonies.geology.GeologyBlocks;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.common.NeoForge;

/** Real client/GPU test, independent of any world, launcher account, or production registration. */
@Mod(value = "ic_client_smoke", dist = Dist.CLIENT)
public final class ClientSmokeMod {
    private boolean started;
    private int titleTicks;
    private final Map<String, Object> report = new LinkedHashMap<>();

    public ClientSmokeMod() {
        NeoForge.EVENT_BUS.addListener(this::tick);
    }

    private void tick(ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        // Never dismiss/intercept onboarding, authentication, errors, or permission screens.
        if (started || !(mc.screen instanceof TitleScreen) || mc.getOverlay() != null) return;
        if (++titleTicks < 40) return;
        started = true;
        try {
            report.put("startedUtc", Instant.now().toString());
            report.put("scope", "Actual full-client stitched sprites, baked models, and GPU inventory renders; no world or survival test");
            report.put("graphicsBackend", RenderSystem.getBackendDescription());
            report.put("graphicsApi", RenderSystem.getApiDescription());
            report.put("loadedModCount", ModList.get().size());
            var ids = new ArrayList<>(GeologyBlocks.APPROVED_IDS);
            ids.add("gold_flakes");
            var checks = new ArrayList<Map<String, Object>>();
            for (String id : ids) {
                BlockState state = GeologyBlocks.block(id).defaultBlockState();
                BakedModel block = mc.getBlockRenderer().getBlockModel(state);
                BakedModel item = mc.getItemRenderer().getModel(new ItemStack(state.getBlock()), null, null, 0);
                require(block != mc.getModelManager().getMissingModel(), id + " missing block model");
                require(item != mc.getModelManager().getMissingModel(), id + " missing item model");
                var quads = new ArrayList<BakedQuad>();
                quads.addAll(block.getQuads(state, null, RandomSource.create(0)));
                for (Direction face : Direction.values()) quads.addAll(block.getQuads(state, face, RandomSource.create(0)));
                require(!quads.isEmpty(), id + " has no baked quads");
                var sprites = new LinkedHashMap<String, Object>();
                for (var quad : quads) {
                    var sprite = quad.getSprite();
                    String name = sprite.contents().name().toString();
                    require(!name.contains("missingno"), id + " missing quad sprite");
                    int expected = id.equals("bertrandite") ? 1254 : 16;
                    require(sprite.contents().width() == expected && sprite.contents().height() == expected,
                            id + " unexpected stitched sprite dimensions " + sprite.contents().width());
                    sprites.put(name, List.of(sprite.contents().width(), sprite.contents().height()));
                }
                require(!item.getParticleIcon().contents().name().toString().contains("missingno"), id + " missing item sprite");
                checks.add(Map.of("id", id, "blockQuads", quads.size(), "itemGui3d", item.isGui3d(), "sprites", sprites));
            }
            report.put("models", checks);
            report.put("approvedCubes", 40);
            report.put("placerBlock", 1);
            report.put("bertranditeException", "Approved 1254x1254 texture preserved; all other checked block sprites 16x16");
            mc.setScreen(new RenderSheet(ids));
        } catch (Throwable error) {
            fail(error);
        }
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }

    private Path reportPath() {
        return Path.of(System.getProperty("ic.client.report")).toAbsolutePath().normalize();
    }

    private void save() throws Exception {
        Path path = reportPath();
        require(path.startsWith(Minecraft.getInstance().gameDirectory.toPath().toAbsolutePath().normalize()), "Report outside disposable stage");
        Files.createDirectories(path.getParent());
        Files.writeString(path, new GsonBuilder().setPrettyPrinting().create().toJson(report) + System.lineSeparator());
    }

    private void fail(Throwable error) {
        report.put("status", "FAIL");
        report.put("error", error.toString());
        error.printStackTrace();
        try { save(); } catch (Exception writeError) { writeError.printStackTrace(); }
        System.err.println("IC_CLIENT_RENDER_FAIL " + error);
        Minecraft.getInstance().stop();
    }

    private final class RenderSheet extends Screen {
        private final List<String> ids;
        private int frames;
        private long completedAt;

        RenderSheet(List<String> ids) {
            super(Component.literal("Industrial Colonies — actual client renders"));
            this.ids = List.copyOf(ids);
        }

        @Override
        public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
            try {
                graphics.fill(0, 0, width, height, 0xff10171d);
                graphics.pose().pushPose();
                graphics.pose().scale(width / 1280f, height / 720f, 1f);
                graphics.drawString(font, "INDUSTRIAL COLONIES | ACTUAL MINECRAFT CLIENT RENDER", 24, 14, 0xffe7ecf0, false);
                graphics.drawString(font, "40 approved rock / ore cubes + placer | original textures | full 239-JAR client test copy", 24, 28, 0xff9facb6, false);
                for (int i = 0; i < ids.size(); i++) {
                    int x = 24 + (i % 8) * 156;
                    int y = 50 + (i / 8) * 107;
                    graphics.fill(x, y, x + 148, y + 101, 0xff1c252e);
                    graphics.pose().pushPose();
                    graphics.pose().translate(x + 42, y + 3, 0);
                    graphics.pose().scale(4f, 4f, 4f);
                    graphics.renderItem(new ItemStack(GeologyBlocks.block(ids.get(i))), 0, 0);
                    graphics.pose().popPose();
                    graphics.drawString(font, ids.get(i).replace('_', ' '), x + 4, y + 78, 0xffe1e8ed, false);
                    graphics.drawString(font, ids.get(i).equals("bertrandite") ? "1254 px source retained" : "16 px source", x + 4, y + 89, 0xff96a8b4, false);
                }
                graphics.drawString(font, "Native item renderer / baked models / stitched atlas. Not a generated mockup; not survival-balance certification.", 24, 706, 0xff9facb6, false);
                graphics.pose().popPose();
                graphics.flush();
                if (++frames == 120) {
                    Path screenshots = Path.of(System.getProperty("ic.client.screenshots")).toAbsolutePath().normalize();
                    require(screenshots.startsWith(minecraft.gameDirectory.toPath().toAbsolutePath().normalize()), "Screenshot outside stage");
                    Files.createDirectories(screenshots);
                    Path shot = screenshots.resolve("industrial-colonies-actual-client-render.png");
                    try (NativeImage image = Screenshot.takeScreenshot(minecraft.getMainRenderTarget())) {
                        image.writeToFile(shot);
                        report.put("screenshotWidth", image.getWidth());
                        report.put("screenshotHeight", image.getHeight());
                    }
                    report.put("screenshot", shot.toString());
                    report.put("renderedFrames", frames);
                    report.put("status", "PASS");
                    report.put("completedUtc", Instant.now().toString());
                    save();
                    System.out.println("IC_CLIENT_RENDER_PASS cubes=40 placer=1 screenshot=" + shot);
                    completedAt = System.currentTimeMillis();
                }
                if (completedAt != 0 && System.currentTimeMillis() - completedAt > 20000
                        && Boolean.getBoolean("ic.client.exitAfterSuccess")) minecraft.stop();
            } catch (Throwable error) {
                fail(error);
            }
        }
    }
}
