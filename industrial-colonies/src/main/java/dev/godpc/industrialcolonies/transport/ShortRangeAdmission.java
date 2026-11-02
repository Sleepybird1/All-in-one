package dev.godpc.industrialcolonies.transport;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Read-only decisions for new ingress. Never authorizes deleting, splitting or replaying cargo. */
public final class ShortRangeAdmission {
    public static final int MAX_SEGMENTS = 30;
    public static final int MAX_SNAPSHOT_NODES = 2048;

    public enum Status { ALLOW, OVER_RANGE, UNRESOLVED, TOO_LARGE }
    public record Result(Status status, int longestSegments, String reason) {
        public boolean allowsNewIngress() { return status == Status.ALLOW; }
    }
    public record Node(long id, Set<Long> neighbors) {
        public Node { neighbors = Set.copyOf(neighbors); }
    }

    private ShortRangeAdmission() {}

    /**
     * Shared energy/fluid/chemical buffers erase ingress provenance. Every pair of transmitters
     * must fit, not just the nearest sink. Distances count cable blocks, so 30 blocks means 29
     * graph edges. Branches may have more than 30 total blocks; a disconnected snapshot is held.
     * The adapter must establish completeness and sample on the server thread immediately before
     * admission. This value must not be persisted or cached across a topology mutation.
     */
    public static Result sharedBuffer(List<Node> snapshot, boolean complete) {
        if (!complete || snapshot == null || snapshot.isEmpty()) return unresolved("Incomplete topology");
        if (snapshot.size() > MAX_SNAPSHOT_NODES) return new Result(Status.TOO_LARGE, 0, "Snapshot exceeds bounded work");
        Map<Long, Set<Long>> graph = new HashMap<>();
        for (Node node : snapshot) {
            if (node == null || node.neighbors().size() > 6 || node.neighbors().contains(node.id())
                    || graph.put(node.id(), node.neighbors()) != null) return unresolved("Invalid transmitter graph");
        }
        for (var entry : graph.entrySet()) for (long other : entry.getValue()) {
            Set<Long> reverse = graph.get(other);
            if (reverse == null || !reverse.contains(entry.getKey())) return unresolved("Missing or asymmetric connection");
        }
        // Check full connectivity before returning OVER_RANGE; an incomplete graph is not a route.
        long first = snapshot.getFirst().id();
        Set<Long> connected = new HashSet<>();
        ArrayDeque<Long> pending = new ArrayDeque<>();
        pending.add(first); connected.add(first);
        while (!pending.isEmpty()) for (long next : graph.get(pending.remove())) {
            if (connected.add(next)) pending.add(next);
        }
        if (connected.size() != graph.size()) return unresolved("Disconnected network snapshot");
        int longest = 1;
        // Reuse bounded scratch storage within this observation only. No graph
        // or result survives a native topology mutation.
        var indices = new HashMap<Long, Integer>();
        for (long id : graph.keySet()) indices.put(id, indices.size());
        int[][] edges = new int[graph.size()][];
        for (var entry : graph.entrySet())
            edges[indices.get(entry.getKey())] = entry.getValue().stream().mapToInt(indices::get).toArray();
        int[] distances = new int[graph.size()], queue = new int[graph.size()];
        for (int source = 0; source < edges.length; source++) {
            java.util.Arrays.fill(distances, 0);
            int head = 0, tail = 0;
            distances[source] = 1; queue[tail++] = source;
            while (head < tail) {
                int current = queue[head++];
                int nextDistance = distances[current] + 1;
                for (int next : edges[current]) if (distances[next] == 0) {
                    if (nextDistance > MAX_SEGMENTS) return new Result(Status.OVER_RANGE, nextDistance, "Shared-buffer route exceeds 30 transmitters");
                    distances[next] = nextDistance; queue[tail++] = next;
                    longest = Math.max(longest, nextDistance);
                }
            }
        }
        return new Result(Status.ALLOW, longest, "All shared-buffer paths fit");
    }

    /** An item route must be the selected ordered native path, excluding both inventory endpoints. */
    public static Result itemPath(List<Long> transmitters, boolean complete) {
        if (!complete || transmitters == null || transmitters.isEmpty()) return unresolved("No complete selected route");
        if (transmitters.size() > MAX_SNAPSHOT_NODES) return new Result(Status.TOO_LARGE, 0, "Route exceeds bounded work");
        Set<Long> seen = new HashSet<>();
        for (Long id : transmitters) if (id == null || !seen.add(id)) return unresolved("Repeated or missing route node");
        return transmitters.size() <= MAX_SEGMENTS
                ? new Result(Status.ALLOW, transmitters.size(), "Selected item route fits")
                : new Result(Status.OVER_RANGE, transmitters.size(), "Selected item route exceeds 30 transmitters");
    }

    public static Result unresolved(String reason) { return new Result(Status.UNRESOLVED, 0, reason); }
}
