package dev.godpc.industrialcolonies.space;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.logging.LogUtils;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Predicate;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;

/**
 * Isolates the incompatible planet JSON formats used by Ad Astra and
 * Stellaris.
 *
 * <p>Ad Astra and Stellaris both use
 * {@code data/(namespace)/planets}, but their planet
 * JSON formats are unrelated. Minecraft's JSON reload listener searches that
 * path in every namespace, so each mod otherwise attempts to decode the other
 * mod's files. These filtering helpers preserve each mod's own namespace and
 * admit correctly shaped third-party definitions, including future custom
 * planets.</p>
 */
public final class SpaceCompatibility {
    private static final Logger LOGGER = LogUtils.getLogger();

    public static final String AD_ASTRA = "ad_astra";
    public static final String STELLARIS = "stellaris";

    private SpaceCompatibility() {
    }

    public static Map<ResourceLocation, JsonElement> forAdAstraPlanetLoader(
            Map<ResourceLocation, JsonElement> resources
    ) {
        return filterPlanetDefinitions(
                resources,
                AD_ASTRA,
                STELLARIS,
                SpaceCompatibility::looksLikeAdAstraPlanet,
                "Ad Astra");
    }

    public static Map<ResourceLocation, JsonElement> forStellarisPlanetLoader(
            Map<ResourceLocation, JsonElement> resources
    ) {
        return filterPlanetDefinitions(
                resources,
                STELLARIS,
                AD_ASTRA,
                SpaceCompatibility::looksLikeStellarisPlanet,
                "Stellaris");
    }

    private static Map<ResourceLocation, JsonElement> filterPlanetDefinitions(
            Map<ResourceLocation, JsonElement> resources,
            String nativeNamespace,
            String incompatibleNamespace,
            Predicate<JsonElement> compatibleSchema,
            String loaderName
    ) {
        Map<ResourceLocation, JsonElement> filtered = new LinkedHashMap<>();
        int ignored = 0;
        for (Map.Entry<ResourceLocation, JsonElement> entry : resources.entrySet()) {
            ResourceLocation id = entry.getKey();
            boolean keep;
            if (nativeNamespace.equals(id.getNamespace())) {
                // Keep malformed native files visible to their owner's codec;
                // silently swallowing an authoring mistake makes packs harder
                // to diagnose.
                keep = true;
            } else if (incompatibleNamespace.equals(id.getNamespace())) {
                keep = false;
            } else {
                // Third-party and pack-owned custom planets remain supported,
                // but only by the loader whose schema they actually use.
                keep = compatibleSchema.test(entry.getValue());
            }
            if (keep) {
                filtered.put(id, entry.getValue());
            } else {
                ignored++;
            }
        }
        if (ignored > 0) {
            LOGGER.info(
                    "{} planet loader ignored {} definition(s) belonging to an incompatible planet schema",
                    loaderName,
                    ignored);
        }
        return filtered;
    }

    private static boolean looksLikeAdAstraPlanet(JsonElement element) {
        JsonObject object = asObject(element);
        return object != null
                && object.has("dimension")
                && object.has("solar_system")
                && object.has("tier");
    }

    private static boolean looksLikeStellarisPlanet(JsonElement element) {
        JsonObject object = asObject(element);
        return object != null
                && object.has("level")
                && object.has("system")
                && object.has("name")
                && object.has("translatable")
                && object.has("distanceFromEarth")
                && object.has("textures");
    }

    private static JsonObject asObject(JsonElement element) {
        return element != null && element.isJsonObject() ? element.getAsJsonObject() : null;
    }

}
