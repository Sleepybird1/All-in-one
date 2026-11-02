package dev.godpc.industrialcolonies.geology;

import java.util.Objects;

/** Pure, bounded geological fields. No world access or whole-deposit position collections. */
public final class MassiveDepositGeometry {
    private MassiveDepositGeometry() {}

    /** Inclusive integer bounds. A body must fit representable block coordinates. */
    public record Bounds(int minX, int minY, int minZ, int maxX, int maxY, int maxZ) {
        public Bounds {
            if (minX > maxX || minY > maxY || minZ > maxZ)
                throw new IllegalArgumentException("Inverted geological bounds");
        }

        public boolean contains(int x, int y, int z) {
            return x >= minX && x <= maxX && y >= minY && y <= maxY && z >= minZ && z <= maxZ;
        }

        public boolean contains(Bounds other) {
            return contains(other.minX, other.minY, other.minZ) && contains(other.maxX, other.maxY, other.maxZ);
        }

        /** Long arithmetic prevents remote chunk coordinates from wrapping into this body. */
        public boolean intersectsChunk(int chunkX, int chunkZ) {
            long x = (long) chunkX * 16, z = (long) chunkZ * 16;
            return maxX >= x && minX <= x + 15 && maxZ >= z && minZ <= z + 15;
        }
    }

    /**
     * Exact field extracted from the September 22 ShapeStudy prototype.
     * Radii describe an envelope, not an exact ore-block quota; native-rock pockets remain inside it.
     */
    public record Body(long seed, double cx, double cy, double cz, double rx, double ry, double rz) {
        public Body {
            if (!Double.isFinite(cx) || !Double.isFinite(cy) || !Double.isFinite(cz)
                    || !Double.isFinite(rx) || !Double.isFinite(ry) || !Double.isFinite(rz)
                    || rx <= 0 || ry <= 0 || rz <= 0)
                throw new IllegalArgumentException("Invalid geological body");
            // Reject overflow instead of letting double-to-int conversion silently saturate the bounds.
            lower(cx, rx); lower(cy, ry); lower(cz, rz);
            upper(cx, rx); upper(cy, ry); upper(cz, rz);
        }

        public Bounds bounds() {
            return new Bounds(lower(cx, rx), lower(cy, ry), lower(cz, rz),
                    upper(cx, rx), upper(cy, ry), upper(cz, rz));
        }

        public double density(int x, int y, int z) {
            double nx = (x - cx) / rx, ny = (y - cy) / ry, nz = (z - cz) / rz;
            double wx = nx + .08 * GeologyMath.noise(seed + 101, nx * 2, ny * 2, nz * 2);
            double wz = nz + .08 * GeologyMath.noise(seed + 102, nx * 2, ny * 2, nz * 2);
            double q = wx * wx + ny * ny + wz * wz;
            return 1 + .22 * GeologyMath.noise(seed + 103, nx * 2, ny * 2, nz * 2)
                    + .07 * GeologyMath.noise(seed + 104, (x - cx) / 7, (y - cy) / 7, (z - cz) / 7) - q;
        }

        public boolean contains(int x, int y, int z) {
            if (Math.abs(x - cx) > rx * 1.3 || Math.abs(y - cy) > ry * 1.3 || Math.abs(z - cz) > rz * 1.3)
                return false;
            double nx = Math.max(0, Math.abs((x - cx) / rx) - .08), ny = (y - cy) / ry,
                    nz = Math.max(0, Math.abs((z - cz) / rz) - .08);
            if (nx * nx + ny * ny + nz * nz > 1.290000001) return false;
            return density(x, y, z) >= 0
                    && GeologyMath.noise(seed + 105, (x - cx) / 3.5, (y - cy) / 3.5, (z - cz) / 3.5) < .42;
        }

        /**
         * Constant-time sufficient test for the entire box to lie in the density envelope.
         * False can be inconclusive. True allows native-rock pockets, as the field intends.
         */
        public boolean conservativelyEncloses(Bounds box) {
            double nx = Math.max(Math.abs(box.minX - cx), Math.abs(box.maxX - cx)) / rx + .08;
            double ny = Math.max(Math.abs(box.minY - cy), Math.abs(box.maxY - cy)) / ry;
            double nz = Math.max(Math.abs(box.minZ - cz), Math.abs(box.maxZ - cz)) / rz + .08;
            // Minimum lobe threshold is 1 - .22 - .07; leave a floating-point safety margin.
            return nx * nx + ny * ny + nz * nz <= .709999999;
        }

        /**
         * Checks every integer position of a bounded structure piece if the sufficient test fails.
         * This is an envelope test, not a promise of mineral at intended native-rock pockets.
         * Callers must keep the supplied piece box bounded; do not use this to scan a whole deposit.
         */
        public boolean enclosesEnvelope(Bounds box) {
            if (!bounds().contains(box)) return false;
            if (conservativelyEncloses(box)) return true;
            for (long x = box.minX; x <= box.maxX; x++)
                for (long z = box.minZ; z <= box.maxZ; z++)
                    for (long y = box.minY; y <= box.maxY; y++)
                        if (!(density((int) x, (int) y, (int) z) >= 0)) return false;
            return true;
        }
    }

    @FunctionalInterface
    public interface VoxelSink {
        void accept(int x, int y, int z);
    }

    @FunctionalInterface
    public interface VoxelPredicate {
        boolean test(int x, int y, int z);
    }

    /** Same mineral order and clipping as visitChunk, stopping at the first matching position. */
    public static boolean anyMatchChunk(Body body, int chunkX, int chunkZ, int minY, int maxYExclusive,
            VoxelPredicate predicate) {
        Objects.requireNonNull(body, "body");
        Objects.requireNonNull(predicate, "predicate");
        Bounds b = body.bounds();
        long chunkMinX = (long) chunkX * 16, chunkMinZ = (long) chunkZ * 16;
        long x0 = Math.max(b.minX, chunkMinX), x1 = Math.min(b.maxX, chunkMinX + 15);
        long z0 = Math.max(b.minZ, chunkMinZ), z1 = Math.min(b.maxZ, chunkMinZ + 15);
        long y0 = Math.max(b.minY, (long) minY), y1 = Math.min(b.maxY, (long) maxYExclusive - 1);
        for (long x = x0; x <= x1; x++)
            for (long z = z0; z <= z1; z++)
                for (long y = y0; y <= y1; y++)
                    if (body.contains((int) x, (int) y, (int) z)
                            && predicate.test((int) x, (int) y, (int) z)) return true;
        return false;
    }

    /**
     * Visits mineral positions only in this chunk and [minY, maxYExclusive).
     * Returns the number of candidate coordinates evaluated, matching the prototype's counter.
     * Empty intersections are no-ops. Generation configuration owns the maximum allowed vertical span.
     */
    public static long visitChunk(Body body, int chunkX, int chunkZ, int minY, int maxYExclusive, VoxelSink sink) {
        Objects.requireNonNull(body, "body");
        Objects.requireNonNull(sink, "sink");
        Bounds b = body.bounds();
        long chunkMinX = (long) chunkX * 16, chunkMinZ = (long) chunkZ * 16;
        long x0 = Math.max(b.minX, chunkMinX), x1 = Math.min(b.maxX, chunkMinX + 15);
        long z0 = Math.max(b.minZ, chunkMinZ), z1 = Math.min(b.maxZ, chunkMinZ + 15);
        long y0 = Math.max(b.minY, (long) minY), y1 = Math.min(b.maxY, (long) maxYExclusive - 1);
        long candidates = 0;
        for (long x = x0; x <= x1; x++)
            for (long z = z0; z <= z1; z++)
                for (long y = y0; y <= y1; y++) {
                    candidates++;
                    if (body.contains((int) x, (int) y, (int) z)) sink.accept((int) x, (int) y, (int) z);
                }
        return candidates;
    }

    private static int lower(double center, double radius) {
        return coordinate(Math.floor(center - radius * 1.3));
    }

    private static int upper(double center, double radius) {
        return coordinate(Math.ceil(center + radius * 1.3));
    }

    private static int coordinate(double value) {
        if (!Double.isFinite(value) || value < Integer.MIN_VALUE || value > Integer.MAX_VALUE)
            throw new IllegalArgumentException("Geological bounds exceed integer block coordinates");
        return (int) value;
    }
}
