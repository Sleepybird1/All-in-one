package dev.godpc.industrialcolonies.client.research;

import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.IndustrialColonies;
import dev.godpc.industrialcolonies.research.IndustrialResearchIds;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import org.slf4j.Logger;

import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

/**
 * Validated client representation of the Draw.io-authored University layout.
 * The JSON is generated alongside the MineColonies research data and can be
 * replaced by a resource pack without changing Java code.
 */
public record TechTreeLayout(
        int canvasWidth,
        int canvasHeight,
        int nodeWidth,
        int nodeHeight,
        List<Node> nodes,
        List<Edge> edges
) {
    public static final int EXPECTED_NODE_COUNT = 77;
    public static final int EXPECTED_EDGE_COUNT = 99;
    public static final String AUTHORITATIVE_DRAWIO_SHA256 =
            "d941f52c1bdd8e0ab2fd30011a48b339abc526524cb6a3e314493e60a59560b5";

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Gson GSON = new Gson();
    private static final ResourceLocation LAYOUT_RESOURCE = ResourceLocation.fromNamespaceAndPath(
            IndustrialColonies.MOD_ID, "research_layout/tech_tree.json");

    public static Optional<TechTreeLayout> load() {
        Optional<Resource> resource = Minecraft.getInstance().getResourceManager().getResource(LAYOUT_RESOURCE);
        if (resource.isEmpty()) {
            LOGGER.error("Missing custom University Tech Tree layout: {}", LAYOUT_RESOURCE);
            return Optional.empty();
        }

        try (Reader reader = resource.get().openAsReader()) {
            SerializedLayout serialized = GSON.fromJson(reader, SerializedLayout.class);
            return Optional.of(validate(serialized));
        } catch (IOException | JsonParseException | IllegalArgumentException exception) {
            LOGGER.error("Invalid custom University Tech Tree layout {}; using MineColonies' stock renderer",
                    LAYOUT_RESOURCE, exception);
            return Optional.empty();
        }
    }

    private static TechTreeLayout validate(SerializedLayout serialized) {
        require(serialized != null, "root object is null");
        require(serialized.schemaVersion == 1, "unsupported schema_version: " + serialized.schemaVersion);
        require(IndustrialResearchIds.TECH_TREE.toString().equals(serialized.branch),
                "layout branch must be " + IndustrialResearchIds.TECH_TREE);
        require(AUTHORITATIVE_DRAWIO_SHA256.equalsIgnoreCase(serialized.drawioSourceSha256),
                "layout was not generated from the authoritative Draw.io source");
        require(serialized.canvas != null, "canvas is missing");
        require(serialized.canvas.width > 0 && serialized.canvas.height > 0,
                "canvas dimensions must be positive");
        require(serialized.canvas.width <= 100_000 && serialized.canvas.height <= 100_000,
                "canvas dimensions are unreasonably large");
        require(serialized.nodeWidth == 175 && serialized.nodeHeight == 50,
                "layout must target MineColonies' 175x50 research cards");
        require(serialized.nodes != null && serialized.nodes.size() == EXPECTED_NODE_COUNT,
                "expected " + EXPECTED_NODE_COUNT + " nodes");
        require(serialized.edges != null && serialized.edges.size() == EXPECTED_EDGE_COUNT,
                "expected " + EXPECTED_EDGE_COUNT + " edges");

        Set<ResourceLocation> nodeIds = new HashSet<>();
        Map<ResourceLocation, Node> nodesById = new HashMap<>();
        List<Node> nodes = new ArrayList<>(serialized.nodes.size());
        for (SerializedNode serializedNode : serialized.nodes) {
            require(serializedNode != null, "node is null");
            ResourceLocation research = parseId(serializedNode.research, "node research");
            require(nodeIds.add(research), "duplicate node: " + research);
            require(serializedNode.x >= 0 && serializedNode.y >= 0,
                    "negative node coordinate for " + research);
            require(serializedNode.x + serialized.nodeWidth <= serialized.canvas.width
                            && serializedNode.y + serialized.nodeHeight <= serialized.canvas.height,
                    "node lies outside canvas: " + research);
            Node node = new Node(research, serializedNode.x, serializedNode.y);
            nodes.add(node);
            nodesById.put(research, node);
        }

        Set<String> edgeIds = new HashSet<>();
        List<Edge> edges = new ArrayList<>(serialized.edges.size());
        for (SerializedEdge serializedEdge : serialized.edges) {
            require(serializedEdge != null, "edge is null");
            require(serializedEdge.drawioId != null && !serializedEdge.drawioId.isBlank(),
                    "edge drawio_id is missing");
            require(edgeIds.add(serializedEdge.drawioId), "duplicate edge: " + serializedEdge.drawioId);
            ResourceLocation from = parseId(serializedEdge.from, "edge source");
            ResourceLocation to = parseId(serializedEdge.to, "edge target");
            require(nodeIds.contains(from) && nodeIds.contains(to),
                    "edge references an unknown node: " + from + " -> " + to);
            List<Point> points = validatePoints(serializedEdge.points, serialized.canvas, "edge " + serializedEdge.drawioId);
            require(onPerimeter(points.get(0), nodesById.get(from), serialized.nodeWidth, serialized.nodeHeight),
                    "edge does not start on its source card: " + serializedEdge.drawioId);
            require(onPerimeter(points.get(points.size() - 1), nodesById.get(to),
                            serialized.nodeWidth, serialized.nodeHeight),
                    "edge does not end on its target card: " + serializedEdge.drawioId);
            List<Point> routedPoints = validatePoints(
                    serializedEdge.drawioPoints, serialized.canvas, "drawio route " + serializedEdge.drawioId);
            require(routedPoints.size() >= 2, "drawio route needs at least two points: " + serializedEdge.drawioId);
            edges.add(new Edge(from, to, points, routedPoints));
        }

        return new TechTreeLayout(
                serialized.canvas.width,
                serialized.canvas.height,
                serialized.nodeWidth,
                serialized.nodeHeight,
                List.copyOf(nodes),
                List.copyOf(edges)
        );
    }

    private static List<Point> validatePoints(
            List<SerializedPoint> serializedPoints,
            SerializedCanvas canvas,
            String context
    ) {
        require(serializedPoints != null && serializedPoints.size() >= 2,
                context + " needs at least two points");
        List<Point> points = new ArrayList<>(serializedPoints.size());
        for (SerializedPoint point : serializedPoints) {
            require(point != null, context + " contains a null point");
            require(point.x >= 0 && point.x <= canvas.width && point.y >= 0 && point.y <= canvas.height,
                    context + " contains a point outside the canvas");
            points.add(new Point(point.x, point.y));
        }
        return List.copyOf(points);
    }

    private static ResourceLocation parseId(String value, String context) {
        ResourceLocation id = ResourceLocation.tryParse(value);
        require(id != null, context + " is not a valid resource location: " + value);
        return id;
    }

    private static boolean onPerimeter(Point point, Node node, int width, int height) {
        int right = node.x() + width;
        int bottom = node.y() + height;
        boolean withinX = point.x() >= node.x() && point.x() <= right;
        boolean withinY = point.y() >= node.y() && point.y() <= bottom;
        return withinX && withinY
                && (point.x() == node.x() || point.x() == right
                || point.y() == node.y() || point.y() == bottom);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalArgumentException(message);
        }
    }

    public record Node(ResourceLocation research, int x, int y) {
    }

    public record Edge(
            ResourceLocation from,
            ResourceLocation to,
            List<Point> points,
            List<Point> routedPoints
    ) {
    }

    public record Point(int x, int y) {
    }

    private static final class SerializedLayout {
        @com.google.gson.annotations.SerializedName("schema_version")
        private int schemaVersion;
        private String branch;
        @com.google.gson.annotations.SerializedName("drawio_source_sha256")
        private String drawioSourceSha256;
        private SerializedCanvas canvas;
        @com.google.gson.annotations.SerializedName("node_width")
        private int nodeWidth;
        @com.google.gson.annotations.SerializedName("node_height")
        private int nodeHeight;
        private List<SerializedNode> nodes;
        private List<SerializedEdge> edges;
    }

    private static final class SerializedCanvas {
        private int width;
        private int height;
    }

    private static final class SerializedNode {
        private String research;
        private int x;
        private int y;
    }

    private static final class SerializedEdge {
        @com.google.gson.annotations.SerializedName("drawio_id")
        private String drawioId;
        private String from;
        private String to;
        private List<SerializedPoint> points;
        @com.google.gson.annotations.SerializedName("drawio_points")
        private List<SerializedPoint> drawioPoints;
    }

    private static final class SerializedPoint {
        private int x;
        private int y;
    }
}
