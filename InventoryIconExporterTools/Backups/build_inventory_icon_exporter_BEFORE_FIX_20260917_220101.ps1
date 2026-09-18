# ============================================================
# INVENTORY ICON EXPORTER AUTOMATIC LOGGING
# ============================================================

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$LogDirectory = Join-Path $ToolRoot "Logs"

New-Item `
    -ItemType Directory `
    -Path $LogDirectory `
    -Force |
    Out-Null

$LogTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$LogFile = Join-Path `
    $LogDirectory `
    "InventoryIconExporter_$LogTimestamp.log"

try {
    Start-Transcript `
        -Path $LogFile `
        -Force |
        Out-Null
}
catch {
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor DarkCyan
Write-Host " BUILD LOG" -ForegroundColor DarkCyan
Write-Host "======================================================" -ForegroundColor DarkCyan
Write-Host $LogFile
Write-Host ""

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " Minecraft 1.21.1 REAL Inventory Icon Exporter Builder" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ------------------------------------------------------------
# FIND CURSEFORGE INSTANCE ROOT
# ------------------------------------------------------------

$searchDir = (Get-Location).Path
$InstanceDir = $null

for ($i = 0; $i -lt 8; $i++) {

    $candidate = Join-Path $searchDir "minecraftinstance.json"

    if (Test-Path $candidate) {
        $InstanceDir = $searchDir
        break
    }

    $parent = Split-Path $searchDir -Parent

    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $searchDir) {
        break
    }

    $searchDir = $parent
}

if (-not $InstanceDir) {
    Write-Host "Could not find minecraftinstance.json." -ForegroundColor Red
    Write-Host ""
    Write-Host "Open PowerShell inside your CurseForge 'All in one' instance and run this again."
    exit 1
}

Write-Host "Instance found:" -ForegroundColor Green
Write-Host $InstanceDir
Write-Host ""

# ------------------------------------------------------------
# DETECT NEOFORGE VERSION
# ------------------------------------------------------------

$instanceJsonPath = Join-Path $InstanceDir "minecraftinstance.json"
$instanceRaw = Get-Content $instanceJsonPath -Raw

$versionMatches = [regex]::Matches(
    $instanceRaw,
    '21\.1\.\d+'
)

if ($versionMatches.Count -gt 0) {
    $NeoVersion = $versionMatches[0].Value
}
else {
    $NeoVersion = "21.1.250"

    Write-Host "Could not automatically determine the NeoForge 21.1.x version." -ForegroundColor Yellow
    Write-Host "Falling back to NeoForge $NeoVersion." -ForegroundColor Yellow
}

Write-Host "NeoForge build target: $NeoVersion" -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# CHECK JAVA
# ------------------------------------------------------------

$javaOK = $false

if (Get-Command java -ErrorAction SilentlyContinue) {

    $javaOutput = (& java -version 2>&1 | Out-String)

    if ($javaOutput -match 'version "(\d+)') {

        $major = [int]$Matches[1]

        if ($major -ge 21) {
            $javaOK = $true
        }
    }
}

if (-not $javaOK) {

    Write-Host "Java 21 was not found in PATH." -ForegroundColor Yellow
    Write-Host ""

    if (Get-Command winget -ErrorAction SilentlyContinue) {

        Write-Host "Installing Temurin Java 21 with winget..."
        Write-Host ""

        winget install `
            --id EclipseAdoptium.Temurin.21.JDK `
            --accept-package-agreements `
            --accept-source-agreements

        Write-Host ""
        Write-Host "Java installation finished."
        Write-Host ""
        Write-Host "CLOSE THIS POWERSHELL WINDOW, open a new one, and paste this script again." -ForegroundColor Yellow
        exit
    }
    else {

        Write-Host "Install Java 21, then rerun this script." -ForegroundColor Red
        Write-Host "Minecraft 1.21.1 mod development requires Java 21."
        exit 1
    }
}

Write-Host "Java 21+ ready." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# PREP TEMP BUILD DIRECTORY
# ------------------------------------------------------------

$ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Join-Path $ToolRoot "BuildWorkspace\InventoryIconExporter_1211"
$DownloadZip = Join-Path $ToolRoot "BuildWorkspace\neoforge_mdk_1211.zip"

if (Test-Path $BuildRoot) {
    Remove-Item $BuildRoot -Recurse -Force
}

if (Test-Path $DownloadZip) {
    Remove-Item $DownloadZip -Force
}

New-Item -ItemType Directory -Path $BuildRoot | Out-Null

Write-Host "Downloading official NeoForge 1.21.1 MDK..."
Write-Host ""

$MdkUrl = "https://github.com/NeoForgeMDKs/MDK-1.21.1-ModDevGradle/archive/refs/heads/main.zip"

Invoke-WebRequest `
    -Uri $MdkUrl `
    -OutFile $DownloadZip `
    -UseBasicParsing

Write-Host "Extracting MDK..."

Expand-Archive `
    -Path $DownloadZip `
    -DestinationPath $BuildRoot `
    -Force

$ProjectDir = Get-ChildItem $BuildRoot -Directory |
    Select-Object -First 1

if (-not $ProjectDir) {
    throw "NeoForge MDK did not extract correctly."
}

$ProjectDir = $ProjectDir.FullName

Write-Host "Build project:"
Write-Host $ProjectDir
Write-Host ""

# ------------------------------------------------------------
# CONFIGURE GRADLE PROPERTIES
# ------------------------------------------------------------

$gradleProperties = Join-Path $ProjectDir "gradle.properties"

$gp = Get-Content $gradleProperties -Raw

$gp = $gp -replace '(?m)^neo_version=.*$', "neo_version=$NeoVersion"
$gp = $gp -replace '(?m)^mod_id=.*$', "mod_id=inventoryiconexporter"
$gp = $gp -replace '(?m)^mod_name=.*$', "mod_name=Inventory Icon Exporter"
$gp = $gp -replace '(?m)^mod_license=.*$', "mod_license=All Rights Reserved"
$gp = $gp -replace '(?m)^mod_version=.*$', "mod_version=1.0.0"
$gp = $gp -replace '(?m)^mod_group_id=.*$', "mod_group_id=com.reese.inventoryiconexporter"

Set-Content `
    -Path $gradleProperties `
    -Value $gp `
    -Encoding UTF8

# ------------------------------------------------------------
# REMOVE EXAMPLE JAVA CODE
# ------------------------------------------------------------

$JavaRoot = Join-Path $ProjectDir "src\main\java"

if (Test-Path $JavaRoot) {
    Remove-Item $JavaRoot -Recurse -Force
}

$PackageDir = Join-Path $JavaRoot "com\reese\inventoryiconexporter"

New-Item `
    -ItemType Directory `
    -Path $PackageDir `
    -Force |
    Out-Null

# ------------------------------------------------------------
# WRITE THE ACTUAL CLIENT MOD
# ------------------------------------------------------------

$JavaSource = @'
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
'@

$JavaFile = Join-Path $PackageDir "InventoryIconExporter.java"
    [System.IO.File]::WriteAllText(
        $JavaFile,
        $JavaSource,
        (New-Object System.Text.UTF8Encoding($false))
    )

Write-Host "Client exporter source created." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# BUILD MOD
# ------------------------------------------------------------

Push-Location $ProjectDir

try {

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " Building Inventory Icon Exporter..." -ForegroundColor Cyan
    Write-Host " First build may take several minutes." -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host ""

    & ".\gradlew.bat" clean build --no-daemon

    if ($LASTEXITCODE -ne 0) {
        throw "Gradle build failed."
    }

}
finally {
    Pop-Location
}

# ------------------------------------------------------------
# FIND BUILT JAR
# ------------------------------------------------------------

$LibDir = Join-Path $ProjectDir "build\libs"

$BuiltJar = Get-ChildItem `
    -Path $LibDir `
    -Filter "*.jar" |
    Where-Object {
        $_.Name -notmatch "sources|javadoc"
    } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $BuiltJar) {
    throw "Could not find built exporter JAR."
}

Write-Host ""
Write-Host "Built:" -ForegroundColor Green
Write-Host $BuiltJar.FullName
Write-Host ""

# ------------------------------------------------------------
# INSTALL INTO CURSEFORGE INSTANCE
# ------------------------------------------------------------

$ModsDir = Join-Path $InstanceDir "mods"

if (-not (Test-Path $ModsDir)) {
    New-Item -ItemType Directory -Path $ModsDir | Out-Null
}

Get-ChildItem `
    -Path $ModsDir `
    -Filter "inventoryiconexporter*.jar" `
    -ErrorAction SilentlyContinue |
    Remove-Item -Force

$InstalledJar = Join-Path `
    $ModsDir `
    "inventoryiconexporter-1.0.0.jar"

Copy-Item `
    $BuiltJar.FullName `
    $InstalledJar `
    -Force

Write-Host "======================================================" -ForegroundColor Green
Write-Host " EXPORTER INSTALLED" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installed mod:"
Write-Host $InstalledJar
Write-Host ""
Write-Host "NOW DO THIS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Launch your 'All in one' Minecraft instance."
Write-Host "2. Enter a SINGLE PLAYER WORLD."
Write-Host "3. Open chat."
Write-Host "4. Run:"
Write-Host ""
Write-Host "   /exportinventoryicons" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Do not close the exporter screen while it runs."
Write-Host ""
Write-Host "The icons will be saved here:" -ForegroundColor Yellow
Write-Host ""
Write-Host (Join-Path $InstanceDir "inventory_icons")
Write-Host ""
Write-Host "When finished you will see:"
Write-Host "   _EXPORT_COMPLETE.txt"
Write-Host ""
Write-Host "ZIP the entire inventory_icons folder and upload it to me."
Write-Host ""