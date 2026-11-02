package dev.godpc.industrialcolonies.geology.oil;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Standalone Java 21 regression suite; no Minecraft startup or world mutation. */
public final class OilFieldPlannerTest {
    private static int assertions;

    public static void main(String[] args) {
        long salt = 4896878702299041L;
        List<OilFieldPlanner.Field> fields = new ArrayList<>();
        int basin = 0;
        int plains = 0;
        int forest = 0;
        int rejected = 0;
        for (int x = -50; x < 50; x++) {
            for (int z = -50; z < 50; z++) {
                OilFieldPlanner.Field field = plan(987654321L, salt, x, z);
                require(field.equals(plan(987654321L, salt, x, z)), "Repeated field call differs");
                require(!field.equals(plan(987654322L, salt, x, z)), "World seed has no effect");
                require(field.centerX() >= x * 1024 + 192 && field.centerX() < (x + 1) * 1024 - 192, "X regional margin");
                require(field.centerZ() >= z * 1024 + 192 && field.centerZ() < (z + 1) * 1024 - 192, "Z regional margin");
                require(field.radius() >= 32 && field.radius() <= 80, "Radius bounds");
                require(field.wells().size() >= 1 && field.wells().size() <= 7, "Unique-well bounds");
                for (OilFieldPlanner.Well well : field.wells()) {
                    require(Math.abs(well.x() - field.centerX()) <= field.radius() + 1, "Well outside radius X");
                    require(Math.abs(well.z() - field.centerZ()) <= field.radius() + 1, "Well outside radius Z");
                    require(Math.floorDiv(well.x(), 1024) == x && Math.floorDiv(well.z(), 1024) == z, "Well escaped region");
                    for (int delta = -1; delta <= 1; delta++) {
                        require(Math.floorDiv(well.x() + delta, 16) == well.chunkX(), "Native X footprint crossed owner chunk");
                        require(Math.floorDiv(well.z() + delta, 16) == well.chunkZ(), "Native Z footprint crossed owner chunk");
                    }
                }
                fields.add(field);
                if (OilFieldPlanner.accepted(field.roll(), 2.5, 0.65, 2.5)) basin++;
                if (OilFieldPlanner.accepted(field.roll(), 1.25, 0.65, 2.5)) plains++;
                if (OilFieldPlanner.accepted(field.roll(), 0.5, 0.65, 2.5)) forest++;
                if (OilFieldPlanner.accepted(field.roll(), 0, 0.65, 2.5)) rejected++;
            }
        }
        require(basin > 6200 && basin < 6800, "Basin normalized probability");
        require(plains > 2950 && plains < 3550, "Plains normalized probability");
        require(forest > 1050 && forest < 1550, "Forest normalized probability");
        require(rejected == 0, "Hard-zero biome accepted");
        Map<String, Long> forward = collect(fields);
        Collections.reverse(fields);
        require(forward.equals(collect(fields)), "Generation traversal order changed the result");
        require(!OilFieldPlanner.accepted(0, 0, 1, 2.5), "Zero-weight corner case");
        require(!OilFieldPlanner.accepted(0, 2.5, 0, 2.5), "Disabled chance corner case");
        System.out.printf("PASS: %,d assertions, 10,000 deterministic regional fields; accepted basin=%d plains=%d forest=%d excluded=%d; native columns stay in owner chunks.%n",
                assertions, basin, plains, forest, rejected);
    }

    private static OilFieldPlanner.Field plan(long seed, long salt, int x, int z) {
        return OilFieldPlanner.field(seed, salt, x, z, 1024, 192, 32, 80, 3, 7);
    }

    private static Map<String, Long> collect(List<OilFieldPlanner.Field> fields) {
        Map<String, Long> result = new HashMap<>();
        for (OilFieldPlanner.Field field : fields) {
            for (OilFieldPlanner.Well well : field.wells()) {
                result.put(well.x() + ":" + well.z(), well.seed());
            }
        }
        return result;
    }

    private static void require(boolean condition, String message) {
        assertions++;
        if (!condition) throw new AssertionError(message);
    }
}
