package dev.godpc.industrialcolonies.geology.oil;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/** Immutable, centrally configured rules for oil; no mineral-deposit settings are reused. */
public record OilRules(
        boolean enabled, long salt, int regionSize, int regionMargin,
        double fieldChance, double weightNormalizer, double defaultWeight,
        int radiusMin, int radiusMax, int wellsMin, int wellsMax, int reservoirY,
        int maximumSurfaceY, int maximumRelief, int terrainSampleRadius,
        Set<String> prohibitedFamilies, Map<String, Double> biomeWeights, boolean debug) {
    private static volatile OilRules loaded;

    public static OilRules get() {
        OilRules result = loaded;
        if (result != null) return result;
        synchronized (OilRules.class) {
            if (loaded == null) loaded = read(GeologyConfig.externalOrBundled("oil.json"));
            return loaded;
        }
    }

    public static void invalidate() {
        loaded = null;
    }

    static OilRules read(JsonObject root) {
        JsonObject regional = root.getAsJsonObject("regional_fields");
        JsonObject terrain = root.getAsJsonObject("hard_terrain_exclusions");
        Map<String, Double> weights = new LinkedHashMap<>();
        root.getAsJsonObject("biome_weights").entrySet().forEach(entry -> {
            double weight = entry.getValue().getAsDouble();
            if (!Double.isFinite(weight) || weight < 0 || weight > 10) {
                throw new IllegalArgumentException("Invalid oil biome weight: " + entry.getKey());
            }
            weights.put(entry.getKey(), weight);
        });
        Set<String> exclusions = new LinkedHashSet<>();
        for (JsonElement element : root.getAsJsonArray("hard_biome_exclusions")) {
            exclusions.add(element.getAsString());
        }
        int size = integer(regional, "region_size_blocks", 256, 8192);
        int margin = integer(regional, "center_margin_blocks", 32, size / 2 - 1);
        int radiusMin = integer(regional, "radius_min_blocks", 8, 128);
        int radiusMax = integer(regional, "radius_max_blocks", radiusMin, 128);
        if (margin <= radiusMax + 16) {
            throw new IllegalArgumentException("Oil region margin must exceed maximum radius + 16");
        }
        int wellsMin = integer(regional, "native_wells_min", 1, 32);
        int wellsMax = integer(regional, "native_wells_max", wellsMin, 32);
        return new OilRules(root.get("enabled").getAsBoolean(), regional.get("seed_salt").getAsLong(),
                size, margin, decimal(regional, "field_chance_at_max_weight", 0, 1),
                decimal(root, "weight_normalizer", 0.01, 10), decimal(root, "unclassified_weight", 0, 10),
                radiusMin, radiusMax, wellsMin, wellsMax, integer(root, "reservoir_y", -2032, 2031),
                integer(terrain, "maximum_surface_y", -64, 320),
                integer(terrain, "maximum_local_relief", 0, 256),
                integer(terrain, "sample_radius_blocks", 1, 128),
                Set.copyOf(exclusions), Map.copyOf(weights), root.get("debug_logging").getAsBoolean());
    }

    /** A prohibited family wins over every positive family, including coastal mountain overlaps. */
    public double weight(Set<String> families) {
        if (families.stream().anyMatch(prohibitedFamilies::contains)) return 0;
        double weight = -1;
        for (String family : families) {
            Double configured = biomeWeights.get(family);
            if (configured != null) {
                if (configured == 0) return 0;
                weight = Math.max(weight, configured);
            }
        }
        return weight < 0 ? defaultWeight : weight;
    }

    private static int integer(JsonObject object, String key, int minimum, int maximum) {
        int value = object.get(key).getAsInt();
        if (value < minimum || value > maximum) throw new IllegalArgumentException("Oil " + key + " out of range");
        return value;
    }

    private static double decimal(JsonObject object, String key, double minimum, double maximum) {
        double value = object.get(key).getAsDouble();
        if (!Double.isFinite(value) || value < minimum || value > maximum) {
            throw new IllegalArgumentException("Oil " + key + " out of range");
        }
        return value;
    }
}
