package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenMechanicalGrid;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

/** Adds the missing row/column resize controls to KJSGen's dynamic Create grid. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenMechanicalGridMixin extends Screen {
    @Unique
    private static final int industrialColonies$CONTROL_WIDTH = 16;

    @Unique
    private static final int industrialColonies$CONTROL_HEIGHT = 18;

    @Unique
    private static final int industrialColonies$PAIR_GAP = 2;

    @Unique
    private static final int industrialColonies$GROUP_GAP = 6;

    @Unique
    private static final int industrialColonies$VERTICAL_GAP = 2;

    @Unique
    private static final int industrialColonies$GRID_CELL_SIZE = 18;

    @Unique
    private static final int industrialColonies$STRIP_WIDTH =
            industrialColonies$CONTROL_WIDTH * 4
                    + industrialColonies$PAIR_GAP * 2
                    + industrialColonies$GROUP_GAP;

    @Shadow
    private int canvasBoxX;

    @Shadow
    private int canvasBoxY;

    @Shadow
    private int canvasBoxW;

    @Shadow
    private int canvasBoxH;

    @Shadow
    private int gridOriginX;

    @Shadow
    private int gridOriginY;

    @Shadow
    private int gridCols;

    @Shadow
    private int gridRows;

    @Shadow
    private List<Component> hoverTooltip;

    @Shadow
    abstract void markDirty();

    protected KjsGenMechanicalGridMixin(Component title) {
        super(title);
    }

    @Inject(method = "drawGridCanvas", at = @At("TAIL"))
    private void industrialColonies$drawResizeControls(
            GuiGraphics graphics,
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            int mouseX,
            int mouseY,
            CallbackInfo ci
    ) {
        if (!KjsGenMechanicalGrid.supports(recipe, type)) {
            return;
        }
        if (!industrialColonies$controlsFit()) {
            return;
        }

        int controlsY = industrialColonies$controlsY();
        if (gridCols > 1) {
            int x = industrialColonies$removeColumnX();
            boolean hovered = industrialColonies$controlHit(mouseX, mouseY, x, controlsY);
            industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, false);
            if (hovered) {
                hoverTooltip = List.of(Component.translatable(
                        "industrial_colonies.kjsgen.mechanical_grid.remove_column",
                        gridCols - 1));
            }
        }

        if (gridCols < KjsGenMechanicalGrid.maximumSize()) {
            int x = industrialColonies$addColumnX();
            boolean hovered = industrialColonies$controlHit(mouseX, mouseY, x, controlsY);
            industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, true);
            if (hovered) {
                hoverTooltip = List.of(Component.translatable(
                        "industrial_colonies.kjsgen.mechanical_grid.add_column",
                        gridCols + 1,
                        KjsGenMechanicalGrid.maximumSize()));
            }
        }

        if (gridRows > 1) {
            int x = industrialColonies$removeRowX();
            boolean hovered = industrialColonies$controlHit(mouseX, mouseY, x, controlsY);
            industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, false);
            if (hovered) {
                hoverTooltip = List.of(Component.translatable(
                        "industrial_colonies.kjsgen.mechanical_grid.remove_row",
                        gridRows - 1));
            }
        }

        if (gridRows < KjsGenMechanicalGrid.maximumSize()) {
            int x = industrialColonies$addRowX();
            boolean hovered = industrialColonies$controlHit(mouseX, mouseY, x, controlsY);
            industrialColonies$drawResizeButton(graphics, x, controlsY, hovered, true);
            if (hovered) {
                hoverTooltip = List.of(Component.translatable(
                        "industrial_colonies.kjsgen.mechanical_grid.add_row",
                        gridRows + 1,
                        KjsGenMechanicalGrid.maximumSize()));
            }
        }
    }

    @Inject(method = "clickGridCanvas", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$resizeGrid(
            double mouseX,
            double mouseY,
            int button,
            RecipeInstance recipe,
            CallbackInfoReturnable<Boolean> cir
    ) {
        if (button != 0) {
            return;
        }
        RecipeTypeDefinition type = RecipeTypeRegistry.get(recipe.typeId()).orElse(null);
        if (!KjsGenMechanicalGrid.supports(recipe, type)) {
            return;
        }
        if (!industrialColonies$controlsFit()) {
            return;
        }

        boolean changed;
        int controlsY = industrialColonies$controlsY();
        if (gridCols > 1
                && industrialColonies$controlHit(
                        mouseX, mouseY,
                        industrialColonies$removeColumnX(), controlsY)) {
            changed = KjsGenMechanicalGrid.removeColumn(recipe, type);
        } else if (gridCols < KjsGenMechanicalGrid.maximumSize()
                && industrialColonies$controlHit(
                        mouseX, mouseY,
                        industrialColonies$addColumnX(), controlsY)) {
            changed = KjsGenMechanicalGrid.addColumn(recipe, type);
        } else if (gridRows > 1
                && industrialColonies$controlHit(
                        mouseX, mouseY,
                        industrialColonies$removeRowX(), controlsY)) {
            changed = KjsGenMechanicalGrid.removeRow(recipe, type);
        } else if (gridRows < KjsGenMechanicalGrid.maximumSize()
                && industrialColonies$controlHit(
                        mouseX, mouseY,
                        industrialColonies$addRowX(), controlsY)) {
            changed = KjsGenMechanicalGrid.addRow(recipe, type);
        } else {
            changed = false;
        }

        if (changed) {
            markDirty();
            // gridW/gridH remain normal KJSGen parameters for compatibility.
            // Rebuilding refreshes their text fields after a canvas-button edit.
            rebuildWidgets();
            cir.setReturnValue(true);
        }
    }

    @Unique
    private int industrialColonies$controlsX() {
        int diagramWidth = gridCols * industrialColonies$GRID_CELL_SIZE + 54;
        int desired = gridOriginX + (diagramWidth - industrialColonies$STRIP_WIDTH) / 2;
        int minimum = canvasBoxX + 1;
        int maximum = canvasBoxX + canvasBoxW - industrialColonies$STRIP_WIDTH - 1;
        return Math.max(minimum, Math.min(desired, maximum));
    }

    @Unique
    private int industrialColonies$removeColumnX() {
        return industrialColonies$controlsX();
    }

    @Unique
    private int industrialColonies$addColumnX() {
        return industrialColonies$removeColumnX()
                + industrialColonies$CONTROL_WIDTH
                + industrialColonies$PAIR_GAP;
    }

    @Unique
    private int industrialColonies$removeRowX() {
        return industrialColonies$addColumnX()
                + industrialColonies$CONTROL_WIDTH
                + industrialColonies$GROUP_GAP;
    }

    @Unique
    private int industrialColonies$addRowX() {
        return industrialColonies$removeRowX()
                + industrialColonies$CONTROL_WIDTH
                + industrialColonies$PAIR_GAP;
    }

    @Unique
    private int industrialColonies$controlsY() {
        int minimum = canvasBoxY + 1;
        int maximum = canvasBoxY + canvasBoxH - industrialColonies$CONTROL_HEIGHT - 1;
        int below = gridOriginY
                + gridRows * industrialColonies$GRID_CELL_SIZE
                + industrialColonies$VERTICAL_GAP;
        if (below <= maximum) {
            return below;
        }

        int above = gridOriginY
                - industrialColonies$CONTROL_HEIGHT
                - industrialColonies$VERTICAL_GAP;
        if (above >= minimum) {
            return above;
        }

        // Callers guard this method with controlsFit(), so this is unreachable
        // unless upstream changes its canvas geometry between the two calls.
        return minimum;
    }

    @Unique
    private boolean industrialColonies$controlsFit() {
        if (canvasBoxW < industrialColonies$STRIP_WIDTH + 2) {
            return false;
        }

        int minimum = canvasBoxY + 1;
        int maximum = canvasBoxY + canvasBoxH - industrialColonies$CONTROL_HEIGHT - 1;
        int below = gridOriginY
                + gridRows * industrialColonies$GRID_CELL_SIZE
                + industrialColonies$VERTICAL_GAP;
        int above = gridOriginY
                - industrialColonies$CONTROL_HEIGHT
                - industrialColonies$VERTICAL_GAP;
        return below <= maximum || above >= minimum;
    }

    @Unique
    private static boolean industrialColonies$controlHit(
            double mouseX,
            double mouseY,
            int x,
            int y
    ) {
        return mouseX >= x && mouseX < x + industrialColonies$CONTROL_WIDTH
                && mouseY >= y && mouseY < y + industrialColonies$CONTROL_HEIGHT;
    }

    @Unique
    private static void industrialColonies$drawResizeButton(
            GuiGraphics graphics,
            int x,
            int y,
            boolean hovered,
            boolean plus
    ) {
        int border = hovered ? 0xFF5C7BFF : 0xFF9A9A98;
        int symbol = hovered ? 0xFFE7E7EC : 0xFF9A9A98;
        graphics.fill(
                x + 1,
                y + 1,
                x + industrialColonies$CONTROL_WIDTH - 1,
                y + industrialColonies$CONTROL_HEIGHT - 1,
                0xFF24242C);
        graphics.renderOutline(
                x,
                y,
                industrialColonies$CONTROL_WIDTH,
                industrialColonies$CONTROL_HEIGHT,
                border);
        graphics.fill(
                x + 4,
                y + 8,
                x + industrialColonies$CONTROL_WIDTH - 4,
                y + 10,
                symbol);
        if (plus) {
            int centerX = x + industrialColonies$CONTROL_WIDTH / 2;
            graphics.fill(centerX - 1, y + 4, centerX + 1, y + 14, symbol);
        }
    }
}
