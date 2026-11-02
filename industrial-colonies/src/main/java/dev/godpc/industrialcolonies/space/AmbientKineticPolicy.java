package dev.godpc.industrialcolonies.space;

import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;

/**
 * Dimension policy for kinetic generators that would otherwise create power
 * from ambient wind or flowing fluid aboard an orbital craft.
 *
 * <p>Sable stores a craft's block entities in its parent {@link Level}, so the
 * block entity level's dimension is the physical environment that owns the
 * craft. The two deny sets stay deliberately separate: a later expansion may
 * restore one ambient resource without implicitly restoring the other.</p>
 */
public final class AmbientKineticPolicy {
    private static final Set<ResourceLocation> MANAGED_OFFWORLD_DIMENSIONS = Set.of(
            dimension("rocketnautics", "deep_space"),
            dimension("ad_astra", "earth_orbit"),
            dimension("ad_astra", "moon"),
            dimension("ad_astra", "moon_orbit"),
            dimension("ad_astra", "mars"),
            dimension("ad_astra", "mars_orbit"),
            dimension("ad_astra", "mercury"),
            dimension("ad_astra", "mercury_orbit"),
            dimension("ad_astra", "venus"),
            dimension("ad_astra", "venus_orbit"),
            dimension("ad_astra", "glacio"),
            dimension("ad_astra", "glacio_orbit"),
            dimension("rocketnautics", "moon"),
            dimension("rocketnautics_addon", "mars")
    );

    private static final Set<ResourceLocation> WIND_DENY_DIMENSIONS = Set.of(
            dimension("rocketnautics", "deep_space"),
            dimension("ad_astra", "earth_orbit"),
            dimension("ad_astra", "moon"),
            dimension("ad_astra", "moon_orbit"),
            dimension("ad_astra", "mars"),
            dimension("ad_astra", "mars_orbit"),
            dimension("ad_astra", "mercury"),
            dimension("ad_astra", "mercury_orbit"),
            dimension("ad_astra", "venus"),
            dimension("ad_astra", "venus_orbit"),
            dimension("ad_astra", "glacio"),
            dimension("ad_astra", "glacio_orbit"),
            dimension("rocketnautics", "moon"),
            dimension("rocketnautics_addon", "mars")
    );

    private static final Set<ResourceLocation> HYDRO_DENY_DIMENSIONS = Set.of(
            dimension("rocketnautics", "deep_space"),
            dimension("ad_astra", "earth_orbit"),
            dimension("ad_astra", "moon"),
            dimension("ad_astra", "moon_orbit"),
            dimension("ad_astra", "mars"),
            dimension("ad_astra", "mars_orbit"),
            dimension("ad_astra", "mercury"),
            dimension("ad_astra", "mercury_orbit"),
            dimension("ad_astra", "venus"),
            dimension("ad_astra", "venus_orbit"),
            dimension("ad_astra", "glacio"),
            dimension("ad_astra", "glacio_orbit"),
            dimension("rocketnautics", "moon"),
            dimension("rocketnautics_addon", "mars")
    );

    private AmbientKineticPolicy() {
    }

    public static boolean deniesWind(Level parentLevel) {
        return denies(parentLevel, WIND_DENY_DIMENSIONS);
    }

    public static boolean deniesHydro(Level parentLevel) {
        return denies(parentLevel, HYDRO_DENY_DIMENSIONS);
    }

    /**
     * Shared physical-space boundary for systems that must not become
     * dimensionless infrastructure, such as the vanilla Ender Chest.
     *
     * <p>This is intentionally not every non-Overworld dimension. Nether and
     * End gameplay remain vanilla-compatible while the authored Ad Astra and
     * Rocketnautics environments obey physical freight rules.</p>
     */
    public static boolean isManagedOffworld(Level level) {
        return denies(level, MANAGED_OFFWORLD_DIMENSIONS);
    }

    public static boolean isManagedOffworld(ResourceLocation dimension) {
        return dimension != null && MANAGED_OFFWORLD_DIMENSIONS.contains(dimension);
    }

    private static boolean denies(Level parentLevel, Set<ResourceLocation> dimensions) {
        return parentLevel != null && dimensions.contains(parentLevel.dimension().location());
    }

    private static ResourceLocation dimension(String namespace, String path) {
        return ResourceLocation.fromNamespaceAndPath(namespace, path);
    }
}
