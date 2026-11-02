package dev.godpc.industrialcolonies.geology.oil;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Pure coordinate planning: no chunk loads, mutable world state, or decoration RNG consumption. */
public final class OilFieldPlanner {
    private OilFieldPlanner() {}

    public record Field(long seed, int centerX, int centerZ, int radius, double roll, List<Well> wells) {}
    public record Well(int x, int z, long seed) {
        public int chunkX() { return Math.floorDiv(x, 16); }
        public int chunkZ() { return Math.floorDiv(z, 16); }
    }

    public static Field field(long worldSeed, long salt, int cellX, int cellZ, int regionSize,
            int margin, int radiusMin, int radiusMax, int wellsMin, int wellsMax) {
        long seed = mix(worldSeed ^ salt ^ mix(cellX * 341873128712L) ^ mix(cellZ * 132897987541L));
        int span = regionSize - 2 * margin;
        int centerX = cellX * regionSize + margin + bounded(mix(seed + 1), span);
        int centerZ = cellZ * regionSize + margin + bounded(mix(seed + 2), span);
        int radius = radiusMin + bounded(mix(seed + 3), radiusMax - radiusMin + 1);
        int count = wellsMin + bounded(mix(seed + 4), wellsMax - wellsMin + 1);
        List<Well> wells = new ArrayList<>();
        Set<Long> seen = new HashSet<>();
        for (int index = 0; index < count; index++) {
            long wellSeed = mix(seed + 100 + index);
            double angle = unit(mix(wellSeed)) * Math.PI * 2;
            double distance = index == 0 ? 0 : Math.sqrt(unit(mix(wellSeed + 1))) * radius;
            int x = insideChunk(centerX + (int) Math.round(Math.cos(angle) * distance));
            int z = insideChunk(centerZ + (int) Math.round(Math.sin(angle) * distance));
            long key = ((long) x << 32) ^ (z & 0xffffffffL);
            if (seen.add(key)) wells.add(new Well(x, z, wellSeed));
        }
        return new Field(seed, centerX, centerZ, radius, unit(mix(seed + 5)), List.copyOf(wells));
    }

    /** Native placeDeposit writes at most one block horizontally: retain a one-block owner margin. */
    private static int insideChunk(int coordinate) {
        return Math.floorDiv(coordinate, 16) * 16 + Math.clamp(Math.floorMod(coordinate, 16), 1, 14);
    }

    public static boolean accepted(double roll, double weight, double chance, double normalizer) {
        return weight > 0 && roll < Math.clamp(chance * weight / normalizer, 0, 1);
    }

    private static int bounded(long value, int bound) { return (int) Math.floorMod(value, bound); }
    private static double unit(long value) { return (value >>> 11) * 0x1.0p-53; }

    private static long mix(long value) {
        value = (value ^ (value >>> 30)) * 0xbf58476d1ce4e5b9L;
        value = (value ^ (value >>> 27)) * 0x94d049bb133111ebL;
        return value ^ (value >>> 31);
    }
}
