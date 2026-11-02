package dev.godpc.industrialcolonies;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.logging.LogUtils;
import net.neoforged.fml.loading.FMLPaths;
import org.slf4j.Logger;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;

/**
 * Common-side view of KJSGen cards deliberately disabled in the durable
 * review ledger.
 *
 * <p>This helper intentionally has no client-class dependency. Export is fail
 * open: a missing, incompatible, or unreadable ledger suppresses nothing and
 * logs the problem instead of risking removal of unrelated recipes.</p>
 */
public final class KjsGenDisabledRecipeFilter {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final int SCHEMA_VERSION = 2;
    private static final int LEGACY_SCHEMA_VERSION = 1;
    private static final String DEFAULT_PROJECT = "default";
    private static final String REVIEW_FILE = "default.recipe_reviews.json";

    private KjsGenDisabledRecipeFilter() {
    }

    /** Reads the latest exact recipe IDs with ledger status {@code disabled}. */
    public static Set<String> loadDisabledRecipeIds() {
        Path path = reviewPath();
        if (!Files.isRegularFile(path)) {
            return Set.of();
        }
        try {
            return parseDisabledRecipeIds(Files.readString(path, StandardCharsets.UTF_8));
        } catch (Exception exception) {
            LOGGER.error(
                    "Failed to read disabled KJSGen recipe IDs from {}; exporting unchanged",
                    path, exception);
            return Set.of();
        }
    }

    static Set<String> parseDisabledRecipeIds(String contents) {
        JsonObject root = JsonParser.parseString(contents).getAsJsonObject();
        int schemaVersion = root.has("schemaVersion")
                ? root.get("schemaVersion").getAsInt()
                : -1;
        String project = root.has("project") && root.get("project").isJsonPrimitive()
                ? root.get("project").getAsString()
                : "";
        if ((schemaVersion != SCHEMA_VERSION && schemaVersion != LEGACY_SCHEMA_VERSION)
                || !DEFAULT_PROJECT.equals(project)) {
            throw new IllegalArgumentException(
                    "Incompatible KJSGen recipe-review ledger schema or project");
        }

        if (!root.has("reviews") || !root.get("reviews").isJsonObject()) {
            return Set.of();
        }
        Set<String> disabled = new HashSet<>();
        for (var entry : root.getAsJsonObject("reviews").entrySet()) {
            String recipeId = entry.getKey();
            JsonElement value = entry.getValue();
            if (recipeId == null || recipeId.isBlank() || !value.isJsonObject()) {
                continue;
            }
            JsonObject review = value.getAsJsonObject();
            if (review.has("status")
                    && review.get("status").isJsonPrimitive()
                    && "disabled".equals(review.get("status").getAsString())) {
                disabled.add(recipeId);
            }
        }
        return Set.copyOf(disabled);
    }

    private static Path reviewPath() {
        return FMLPaths.GAMEDIR.get()
                .resolve("kjsgen")
                .resolve("industrial_colonies_sync")
                .resolve(REVIEW_FILE);
    }
}
