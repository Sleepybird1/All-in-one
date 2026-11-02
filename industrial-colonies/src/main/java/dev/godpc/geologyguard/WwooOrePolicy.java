package dev.godpc.geologyguard;

import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Preserve mixed WWOO terrain while honoring Overworld ore ownership. */
public final class WwooOrePolicy {
    public enum Scope { BASALT_DISK, VOLCANIC_EXTINCTION, FLOWER_FOREST, TEPUI, IRON_VENT }
    private static final ThreadLocal<Scope> ACTIVE = new ThreadLocal<>();
    private WwooOrePolicy() {}

    public static boolean applies(ResourceLocation feature, ResourceKey<Level> dimension, boolean suppressOres) {
        return scopeFor(feature, dimension, suppressOres) != null;
    }
    public static Scope scopeFor(ResourceLocation feature, ResourceKey<Level> dimension, boolean suppressOres) {
        if (!suppressOres || !Level.OVERWORLD.equals(dimension) || feature == null
                || !feature.getNamespace().equals("wythers")) return null;
        return switch (feature.getPath()) {
            case "terrain/local/cave_disk_basalt" -> Scope.BASALT_DISK;
            case "terrain/extended/volcanic_extinction" -> Scope.VOLCANIC_EXTINCTION;
            case "terrain/local/replace_volcanics_flower_forest" -> Scope.FLOWER_FOREST;
            case "terrain/feature/tepui_geodes" -> Scope.TEPUI;
            case "terrain/feature/thermal_vents_iron" -> Scope.IRON_VENT;
            default -> null;
        };
    }
    public static boolean active() { return ACTIVE.get() != null; }
    public static Scope scope() { return ACTIVE.get(); }
    public static void restore(Scope scope) { if (scope != null) ACTIVE.set(scope); else ACTIVE.remove(); }
    /** Retain the original basalt-only test API. */
    public static void restore(boolean active) { restore(active ? Scope.BASALT_DISK : null); }
    public static BlockState replace(BlockState original) {
        Scope scope = ACTIVE.get();
        if (scope == Scope.BASALT_DISK && (original.is(Blocks.DEEPSLATE_DIAMOND_ORE) || original.is(Blocks.DEEPSLATE_GOLD_ORE)
                || original.is(Blocks.DEEPSLATE_IRON_ORE) || original.is(Blocks.DEEPSLATE_REDSTONE_ORE))) {
            return Blocks.SMOOTH_BASALT.defaultBlockState();
        }
        if (scope == Scope.VOLCANIC_EXTINCTION && original.is(Blocks.DEEPSLATE_GOLD_ORE))
            return Blocks.SMOOTH_BASALT.defaultBlockState();
        if (scope == Scope.FLOWER_FOREST && original.is(Blocks.DEEPSLATE_GOLD_ORE))
            return Blocks.TUFF.defaultBlockState();
        if (scope == Scope.TEPUI && (original.is(Blocks.DEEPSLATE_DIAMOND_ORE) || original.is(Blocks.DEEPSLATE_COAL_ORE)))
            return Blocks.DEEPSLATE.defaultBlockState();
        if (scope == Scope.IRON_VENT && original.is(Blocks.RAW_IRON_BLOCK))
            return Blocks.DRIPSTONE_BLOCK.defaultBlockState();
        return original;
    }
}
