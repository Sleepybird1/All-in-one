package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.nio.ByteBuffer;
import java.security.*;
import java.util.*;

/** Chart-sized optional deposits. No occurrence roll, terrain writes or default biome policy. */
public final class ContinentReservePolicy {
    public record Tier(int oreBlocks, int weight) {
        public Tier {
            if (oreBlocks < 1 || oreBlocks > FiniteOreLimits.MAX_BLOCKS || weight < 0 || weight > 100)
                throw new IllegalArgumentException("Finite ore reserve and percentage weight required");
        }
    }
    public record Family(String id, List<Tier> tiers) {
        public Family {
            optionalFamily(id); tiers = List.copyOf(tiers);
            if (tiers.size() != 3 || tiers.stream().mapToInt(Tier::weight).sum() != 100)
                throw new IllegalArgumentException("Three ordered tiers totaling100percent required");
            if (tiers.get(0).oreBlocks() >= tiers.get(1).oreBlocks()
                    || tiers.get(1).oreBlocks() >= tiers.get(2).oreBlocks())
                throw new IllegalArgumentException("Strictly increasing reserve tiers required");
        }
        public Selection select(ContinentResourceDecision.Scope scope, ReTerraForgedGeography.ContinentKey continent) {
            long seed = seed(scope, continent, id);
            int ticket = new SplittableRandom(seed).nextInt(100), cumulative = 0;
            for (int i = 0; i < tiers.size(); i++) {
                cumulative += tiers.get(i).weight();
                if (ticket < cumulative) return new Selection(id, i, tiers.get(i).oreBlocks(), seed);
            }
            throw new AssertionError("Validated tier weights");
        }
    }
    public record Selection(String family, int tier, int oreBlocks, long shapeSalt) {}
    /** Empty mappings have no fallback. Fixed-probability fixtures use their separate old API. */
    public record BiomeChances(Map<String, Double> values) {
        public BiomeChances {
            Objects.requireNonNull(values);
            TreeMap<String, Double> sorted = new TreeMap<>();
            values.forEach((biome, chance) -> {
                if (biome == null || !biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+") || chance == null
                        || !Double.isFinite(chance) || chance < 0 || chance > 1)
                    throw new IllegalArgumentException("Exact biome IDs and bounded chances required");
                sorted.put(biome, chance);
            });
            if (sorted.isEmpty() || sorted.size() > 4096 || sorted.values().stream().noneMatch(p -> p > 0))
                throw new IllegalArgumentException("At least one eligible biome required");
            values = Collections.unmodifiableMap(sorted);
        }
        public double at(String biome) { return values.getOrDefault(biome, 0.0); }
    }
    static void optionalFamily(String id) {
        if (id == null || !id.matches("[a-z0-9_]+") || id.equals("coal") || id.equals("cinnabar"))
            throw new IllegalArgumentException("Optional ore family required");
    }
    private static long seed(ContinentResourceDecision.Scope scope, ReTerraForgedGeography.ContinentKey continent, String family) {
        Objects.requireNonNull(scope); Objects.requireNonNull(continent);
        try {
            var bytes = new ByteArrayOutputStream();
            try (var out = new DataOutputStream(bytes)) {
                out.writeUTF("industrial-colonies/continent-reserve/v1");
                out.writeLong(scope.worldSeed()); out.writeUTF(scope.dimension()); out.writeUTF(scope.presetSha256());
                out.writeInt(continent.centerX()); out.writeInt(continent.centerZ()); out.writeInt(continent.identityBits()); out.writeUTF(family);
            }
            return ByteBuffer.wrap(MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray())).getLong();
        } catch (IOException | NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
    private ContinentReservePolicy() {}
}
