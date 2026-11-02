package dev.godpc.industrialcolonies;

import java.util.Arrays;
import java.util.Optional;
import java.util.function.BiPredicate;

/** Bounded integral allocation; overlapping tags cannot consume a later exact input. */
public final class VatInputAllocation {
    private VatInputAllocation() {}

    public static Optional<int[]> reserve(int[] available, int[] required,
                                         BiPredicate<Integer, Integer> accepts) {
        if (available.length > 24 || required.length > 128) return Optional.empty();
        if (Arrays.stream(available).anyMatch(value -> value < 0)
                || Arrays.stream(required).anyMatch(value -> value <= 0)) return Optional.empty();
        int source = 0, requirements = 1, slots = requirements + required.length;
        int sink = slots + available.length, vertices = sink + 1;
        long[][] capacity = new long[vertices][vertices];
        long total = 0;
        for (int r = 0; r < required.length; r++) {
            capacity[source][requirements + r] = required[r];
            total += required[r];
            for (int s = 0; s < available.length; s++)
                if (accepts.test(r, s)) capacity[requirements + r][slots + s] = required[r];
        }
        for (int s = 0; s < available.length; s++) capacity[slots + s][sink] = available[s];
        long allocated = 0;
        while (allocated < total) {
            int[] parent = new int[vertices];
            Arrays.fill(parent, -1);
            int[] queue = new int[vertices]; int head = 0, tail = 0;
            parent[source] = source; queue[tail++] = source;
            while (head < tail && parent[sink] < 0) {
                int from = queue[head++];
                for (int to = 0; to < vertices; to++)
                    if (parent[to] < 0 && capacity[from][to] > 0) {
                        parent[to] = from; queue[tail++] = to;
                    }
            }
            if (parent[sink] < 0) return Optional.empty();
            long flow = Long.MAX_VALUE;
            for (int to = sink; to != source; to = parent[to])
                flow = Math.min(flow, capacity[parent[to]][to]);
            for (int to = sink; to != source; to = parent[to]) {
                capacity[parent[to]][to] -= flow;
                capacity[to][parent[to]] += flow;
            }
            allocated += flow;
        }
        int[] remaining = new int[available.length];
        for (int s = 0; s < available.length; s++) remaining[s] = (int) capacity[slots + s][sink];
        return Optional.of(remaining);
    }
}
