package com.reese.inventoryiconexporter;

import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.RegisterClientCommandsEvent;
import net.neoforged.neoforge.common.NeoForge;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Mod(value = InventoryIconExporter.MOD_ID, dist = Dist.CLIENT)
public final class InventoryIconExporter {

    public static final String MOD_ID = "inventoryiconexporter";

    public InventoryIconExporter(ModContainer container) {
        NeoForge.EVENT_BUS.addListener(
                InventoryIconExporter::registerClientCommands
        );
    }

    private static void registerClientCommands(
            RegisterClientCommandsEvent event
    ) {

        event.getDispatcher().register(
                Commands.literal("exportinventoryicons")
                        .executes(context -> {

                            Minecraft minecraft =
                                    Minecraft.getInstance();

                            minecraft.execute(() -> {

                                if (minecraft.screen instanceof ExportScreen) {
                                    return;
                                }

                                minecraft.setScreen(
                                        new ExportScreen()
                                );
                            });

                            return 1;
                        })
        );
    }


    private record ExportEntry(
            ResourceLocation id,
            ItemStack stack
    ) {
    }


    private static final class ExportScreen extends Screen {

        /*
         * 8 x 8 inventory icons are rendered per page.
         *
         * Each inventory render is 16 GUI pixels.
         * We leave spacing around them so neighboring items
         * cannot contaminate the crop.
         */
        private static final int COLUMNS = 8;
        private static final int ROWS = 8;
        private static final int ITEMS_PER_PAGE =
                COLUMNS * ROWS;

        private static final int SLOT_SPACING = 24;
        private static final int ITEM_SIZE = 16;

        private static final int START_X = 16;
        private static final int START_Y = 16;

        /*
         * Export is 32x32 regardless of GUI scale.
         */
        private static final int OUTPUT_SIZE = 32;

        private final Minecraft mc;

        private final List<ExportEntry> entries =
                new ArrayList<>();

        private Path outputDirectory;
        private Path manifestPath;

        private int page = 0;

        /*
         * phase 0 = black background
         * phase 1 = white background
         *
         * Comparing both images lets us reconstruct alpha
         * instead of saving a square background.
         */
        private int phase = 0;

        private NativeImage blackCapture;

        private boolean finished = false;


        ExportScreen() {

            super(
                    Component.literal(
                            "Inventory Icon Exporter"
                    )
            );

            this.mc = Minecraft.getInstance();

            BuiltInRegistries.ITEM.keySet()
                    .stream()
                    .sorted(
                            Comparator.comparing(
                                    ResourceLocation::toString
                            )
                    )
                    .forEach(id -> {

                        Item item =
                                BuiltInRegistries.ITEM.get(id);

                        if (item == null) {
                            return;
                        }

                        try {

                            ItemStack stack =
                                    item.getDefaultInstance();

                            entries.add(
                                    new ExportEntry(
                                            id,
                                            stack
                                    )
                            );

                        }
                        catch (Throwable throwable) {

                            entries.add(
                                    new ExportEntry(
                                            id,
                                            new ItemStack(item)
                                    )
                            );
                        }
                    });


            outputDirectory =
                    mc.gameDirectory
                            .toPath()
                            .resolve(
                                    "inventory_icons"
                            );

            manifestPath =
                    outputDirectory.resolve(
                            "inventory_icons_manifest.csv"
                    );


            try {

                Files.createDirectories(
                        outputDirectory
                );

                Files.writeString(
                        manifestPath,
                        "item_id,file_name,status\n",
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.TRUNCATE_EXISTING
                );

            }
            catch (IOException exception) {

                throw new RuntimeException(
                        "Could not create inventory icon output folder.",
                        exception
                );
            }
        }


        @Override
        public boolean isPauseScreen() {
            return false;
        }


        @Override
        public boolean shouldCloseOnEsc() {
            return false;
        }


        @Override
        public void render(
                GuiGraphics graphics,
                int mouseX,
                int mouseY,
                float partialTick
        ) {

            if (finished) {
                return;
            }


            /*
             * Solid backgrounds are intentional.
             *
             * We capture once on black and once on white,
             * then mathematically reconstruct the original
             * transparency.
             */
            int background =
                    phase == 0
                            ? 0xFF000000
                            : 0xFFFFFFFF;

            graphics.fill(
                    0,
                    0,
                    this.width,
                    this.height,
                    background
            );


            int firstIndex =
                    page * ITEMS_PER_PAGE;

            int lastIndex =
                    Math.min(
                            firstIndex + ITEMS_PER_PAGE,
                            entries.size()
                    );


            for (
                    int index = firstIndex;
                    index < lastIndex;
                    index++
            ) {

                int local =
                        index - firstIndex;

                int column =
                        local % COLUMNS;

                int row =
                        local / COLUMNS;

                int x =
                        START_X
                                + column
                                * SLOT_SPACING;

                int y =
                        START_Y
                                + row
                                * SLOT_SPACING;


                ItemStack stack =
                        entries.get(index).stack();


                try {

                    /*
                     * This is the important part:
                     *
                     * Minecraft itself renders the actual
                     * inventory ItemStack.
                     *
                     * We are NOT reading its raw texture.
                     */
                    if (mc.player != null) {

                        graphics.renderItem(
                                mc.player,
                                stack,
                                x,
                                y,
                                index
                        );

                    }
                    else {

                        graphics.renderItem(
                                stack,
                                x,
                                y,
                                index
                        );
                    }

                }
                catch (Throwable throwable) {

                    /*
                     * One broken modded renderer must not
                     * kill the entire export.
                     */
                }
            }


            /*
             * Keep progress text away from icon crops.
             */
            int done =
                    Math.min(
                            firstIndex,
                            entries.size()
                    );

            double percent =
                    entries.isEmpty()
                            ? 100.0
                            : (
                            done
                                    * 100.0
                                    / entries.size()
                    );


            String progress =
                    String.format(
                            "Inventory Icon Export: %.2f%%  %d / %d",
                            percent,
                            done,
                            entries.size()
                    );


            int textColor =
                    phase == 0
                            ? 0xFFFFFFFF
                            : 0xFF000000;

            graphics.drawString(
                    mc.font,
                    progress,
                    16,
                    Math.min(
                            this.height - 20,
                            START_Y
                                    + ROWS
                                    * SLOT_SPACING
                                    + 8
                    ),
                    textColor,
                    false
            );


            /*
             * Force queued GUI rendering before reading
             * the framebuffer.
             */
            graphics.flush();


            if (phase == 0) {

                if (blackCapture != null) {
                    blackCapture.close();
                }

                blackCapture =
                        Screenshot.takeScreenshot(
                                mc.getMainRenderTarget()
                        );

                phase = 1;

                return;
            }


            NativeImage whiteCapture = null;

            try {

                whiteCapture =
                        Screenshot.takeScreenshot(
                                mc.getMainRenderTarget()
                        );

                exportCurrentPage(
                        blackCapture,
                        whiteCapture,
                        firstIndex,
                        lastIndex
                );

            }
            catch (Throwable throwable) {

                throwable.printStackTrace();

            }
            finally {

                if (blackCapture != null) {
                    blackCapture.close();
                    blackCapture = null;
                }

                if (whiteCapture != null) {
                    whiteCapture.close();
                }
            }


            page++;

            phase = 0;


            if (
                    page * ITEMS_PER_PAGE
                            >= entries.size()
            ) {

                finishExport();
            }
        }


        private void exportCurrentPage(
                NativeImage black,
                NativeImage white,
                int firstIndex,
                int lastIndex
        ) {

            double guiScale =
                    mc.getWindow()
                            .getGuiScale();


            for (
                    int index = firstIndex;
                    index < lastIndex;
                    index++
            ) {

                int local =
                        index - firstIndex;

                int column =
                        local % COLUMNS;

                int row =
                        local / COLUMNS;


                int logicalX =
                        START_X
                                + column
                                * SLOT_SPACING;

                int logicalY =
                        START_Y
                                + row
                                * SLOT_SPACING;


                int screenX =
                        (int) Math.round(
                                logicalX
                                        * guiScale
                        );

                int screenY =
                        (int) Math.round(
                                logicalY
                                        * guiScale
                        );

                int physicalSize =
                        Math.max(
                                1,
                                (int) Math.round(
                                        ITEM_SIZE
                                                * guiScale
                                )
                        );


                ExportEntry entry =
                        entries.get(index);


                String safeName =
                        sanitize(
                                entry.id()
                        );


                Path outputFile =
                        outputDirectory.resolve(
                                safeName + ".png"
                        );


                String status = "OK";


                try (
                        NativeImage blackIcon =
                                new NativeImage(
                                        OUTPUT_SIZE,
                                        OUTPUT_SIZE,
                                        false
                                );

                        NativeImage whiteIcon =
                                new NativeImage(
                                        OUTPUT_SIZE,
                                        OUTPUT_SIZE,
                                        false
                                );

                        NativeImage result =
                                new NativeImage(
                                        OUTPUT_SIZE,
                                        OUTPUT_SIZE,
                                        false
                                )
                ) {

                    black.resizeSubRectTo(
                            screenX,
                            screenY,
                            physicalSize,
                            physicalSize,
                            blackIcon
                    );

                    white.resizeSubRectTo(
                            screenX,
                            screenY,
                            physicalSize,
                            physicalSize,
                            whiteIcon
                    );


                    int visiblePixels = 0;


                    for (
                            int py = 0;
                            py < OUTPUT_SIZE;
                            py++
                    ) {

                        for (
                                int px = 0;
                                px < OUTPUT_SIZE;
                                px++
                        ) {

                            int blackColor =
                                    blackIcon
                                            .getPixelRGBA(
                                                    px,
                                                    py
                                            );

                            int whiteColor =
                                    whiteIcon
                                            .getPixelRGBA(
                                                    px,
                                                    py
                                            );


                            int br =
                                    blackColor
                                            & 0xFF;

                            int bg =
                                    (
                                            blackColor
                                                    >>> 8
                                    )
                                            & 0xFF;

                            int bb =
                                    (
                                            blackColor
                                                    >>> 16
                                    )
                                            & 0xFF;


                            int wr =
                                    whiteColor
                                            & 0xFF;

                            int wg =
                                    (
                                            whiteColor
                                                    >>> 8
                                    )
                                            & 0xFF;

                            int wb =
                                    (
                                            whiteColor
                                                    >>> 16
                                    )
                                            & 0xFF;


                            /*
                             * Standard alpha-compositing:
                             *
                             * black pass:
                             *   B = A * C
                             *
                             * white pass:
                             *   W = A * C + (1-A)*255
                             *
                             * therefore:
                             *   A = 255 - (W-B)
                             */
                            int dr =
                                    clamp(
                                            wr - br
                                    );

                            int dg =
                                    clamp(
                                            wg - bg
                                    );

                            int db =
                                    clamp(
                                            wb - bb
                                    );


                            int backgroundContribution =
                                    (
                                            dr
                                                    + dg
                                                    + db
                                    )
                                            / 3;


                            int alpha =
                                    clamp(
                                            255
                                                    - backgroundContribution
                                    );


                            if (alpha <= 3) {

                                result.setPixelRGBA(
                                        px,
                                        py,
                                        0
                                );

                                continue;
                            }


                            int red =
                                    clamp(
                                            (
                                                    br
                                                            * 255
                                                            + alpha / 2
                                            )
                                                    / alpha
                                    );

                            int green =
                                    clamp(
                                            (
                                                    bg
                                                            * 255
                                                            + alpha / 2
                                            )
                                                    / alpha
                                    );

                            int blue =
                                    clamp(
                                            (
                                                    bb
                                                            * 255
                                                            + alpha / 2
                                            )
                                                    / alpha
                                    );


                            int rgba =
                                    red
                                            | (
                                            green
                                                    << 8
                                    )
                                            | (
                                            blue
                                                    << 16
                                    )
                                            | (
                                            alpha
                                                    << 24
                                    );


                            result.setPixelRGBA(
                                    px,
                                    py,
                                    rgba
                            );


                            if (alpha > 10) {
                                visiblePixels++;
                            }
                        }
                    }


                    if (visiblePixels == 0) {
                        status = "BLANK";
                    }


                    result.writeToFile(
                            outputFile
                    );

                }
                catch (Throwable throwable) {

                    status = "ERROR";

                    throwable.printStackTrace();
                }


                appendManifest(
                        entry.id(),
                        outputFile
                                .getFileName()
                                .toString(),
                        status
                );
            }
        }


        private void appendManifest(
                ResourceLocation id,
                String fileName,
                String status
        ) {

            String line =
                    id
                            + ","
                            + fileName
                            + ","
                            + status
                            + "\n";

            try {

                Files.writeString(
                        manifestPath,
                        line,
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.APPEND
                );

            }
            catch (IOException exception) {

                exception.printStackTrace();
            }
        }


        private void finishExport() {

            finished = true;


            Path marker =
                    outputDirectory.resolve(
                            "_EXPORT_COMPLETE.txt"
                    );


            try {

                Files.writeString(
                        marker,
                        "Inventory icon export complete.\n"
                                + "Total registered items: "
                                + entries.size()
                                + "\n"
                                + "Output: "
                                + outputDirectory
                                + "\n",
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE,
                        StandardOpenOption.TRUNCATE_EXISTING
                );

            }
            catch (IOException exception) {

                exception.printStackTrace();
            }


            if (mc.player != null) {

                mc.player.displayClientMessage(
                        Component.literal(
                                "Inventory icon export finished: "
                                        + entries.size()
                                        + " items. Folder: "
                                        + outputDirectory
                        ),
                        false
                );
            }


            mc.execute(
                    () -> mc.setScreen(null)
            );
        }


        private static String sanitize(
                ResourceLocation id
        ) {

            return id.getNamespace()
                    + "__"
                    + id.getPath()
                    .replace(
                            "/",
                            "__"
                    )
                    .replace(
                            "\\",
                            "__"
                    )
                    .replace(
                            ":",
                            "__"
                    );
        }


        private static int clamp(
                int value
        ) {

            return Math.max(
                    0,
                    Math.min(
                            255,
                            value
                    )
            );
        }
    }
}