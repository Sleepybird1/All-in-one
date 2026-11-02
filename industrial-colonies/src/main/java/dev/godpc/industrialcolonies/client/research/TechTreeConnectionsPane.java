package dev.godpc.industrialcolonies.client.research;

import com.ldtteam.blockui.BOGuiGraphics;
import com.ldtteam.blockui.Pane;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.GameRenderer;
import org.joml.Matrix4f;

import java.util.ArrayList;
import java.util.List;

/**
 * Draws the complete dependency graph as one BlockUI pane and one GPU mesh.
 * Both the geometry and its hierarchy are batched, avoiding the hundreds of
 * panes and per-segment buffer uploads that made the earlier visualization
 * expensive.
 */
public final class TechTreeConnectionsPane extends Pane {
    private static final int CONNECTION_COLOR = 0xD0B79A54;
    private static final float LINE_THICKNESS = 3.0F;
    private static final int ARROW_LENGTH = 9;
    private static final int ARROW_HALF_WIDTH = 5;

    private static final int RED = CONNECTION_COLOR >> 16 & 0xFF;
    private static final int GREEN = CONNECTION_COLOR >> 8 & 0xFF;
    private static final int BLUE = CONNECTION_COLOR & 0xFF;
    private static final int ALPHA = CONNECTION_COLOR >>> 24;

    private final List<Quad> geometry;

    public TechTreeConnectionsPane(TechTreeLayout layout) {
        this.geometry = buildGeometry(layout.edges());
        setPosition(0, 0);
        setSize(layout.canvasWidth(), layout.canvasHeight());
        disable();
    }

    @Override
    public void drawSelf(BOGuiGraphics graphics, double mouseX, double mouseY) {
        if (geometry.isEmpty()) {
            return;
        }

        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        RenderSystem.enableBlend();

        Matrix4f matrix = graphics.pose().last().pose();
        BufferBuilder buffer = Tesselator.getInstance().begin(
                VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
        for (Quad quad : geometry) {
            addVertex(buffer, matrix, quad.x1(), quad.y1());
            addVertex(buffer, matrix, quad.x2(), quad.y2());
            addVertex(buffer, matrix, quad.x3(), quad.y3());
            addVertex(buffer, matrix, quad.x4(), quad.y4());
        }
        BufferUploader.drawWithShader(buffer.buildOrThrow());
        RenderSystem.disableBlend();
    }

    private static List<Quad> buildGeometry(List<TechTreeLayout.Edge> edges) {
        List<Quad> quads = new ArrayList<>();
        for (TechTreeLayout.Edge edge : edges) {
            List<TechTreeLayout.Point> points = edge.points();
            for (int index = 1; index < points.size(); index++) {
                TechTreeLayout.Point start = points.get(index - 1);
                TechTreeLayout.Point end = points.get(index);
                addThickLine(quads, start.x(), start.y(), end.x(), end.y());
            }
            addArrowhead(quads, points);
        }
        return List.copyOf(quads);
    }

    private static void addArrowhead(List<Quad> quads, List<TechTreeLayout.Point> route) {
        TechTreeLayout.Point tip = route.get(route.size() - 1);
        TechTreeLayout.Point previous = route.get(route.size() - 2);
        int dx = Integer.compare(tip.x(), previous.x());
        int dy = Integer.compare(tip.y(), previous.y());
        if (dx == 0 && dy == 0) {
            return;
        }

        if (Math.abs(tip.x() - previous.x()) >= Math.abs(tip.y() - previous.y())) {
            addThickLine(quads, tip.x(), tip.y(), tip.x() - dx * ARROW_LENGTH,
                    tip.y() - ARROW_HALF_WIDTH);
            addThickLine(quads, tip.x(), tip.y(), tip.x() - dx * ARROW_LENGTH,
                    tip.y() + ARROW_HALF_WIDTH);
        } else {
            addThickLine(quads, tip.x(), tip.y(), tip.x() - ARROW_HALF_WIDTH,
                    tip.y() - dy * ARROW_LENGTH);
            addThickLine(quads, tip.x(), tip.y(), tip.x() + ARROW_HALF_WIDTH,
                    tip.y() - dy * ARROW_LENGTH);
        }
    }

    private static void addThickLine(List<Quad> quads, float x1, float y1, float x2, float y2) {
        float dx = x2 - x1;
        float dy = y2 - y1;
        float length = (float) Math.sqrt(dx * dx + dy * dy);
        if (length == 0.0F) {
            return;
        }

        float halfThickness = LINE_THICKNESS / 2.0F;
        float normalX = -dy / length * halfThickness;
        float normalY = dx / length * halfThickness;

        // This order matches BlockUI's clockwise screen-space fill winding.
        quads.add(new Quad(
                x1 - normalX, y1 - normalY,
                x1 + normalX, y1 + normalY,
                x2 + normalX, y2 + normalY,
                x2 - normalX, y2 - normalY
        ));
    }

    private static void addVertex(BufferBuilder buffer, Matrix4f matrix, float x, float y) {
        buffer.addVertex(matrix, x, y, 0.0F).setColor(RED, GREEN, BLUE, ALPHA);
    }

    private record Quad(
            float x1, float y1,
            float x2, float y2,
            float x3, float y3,
            float x4, float y4
    ) {
    }
}
