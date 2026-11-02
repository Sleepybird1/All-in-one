package dev.godpc.industrialcolonies.processing;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.neoforged.fml.loading.FMLPaths;

import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;

/** Restart-scoped, fail-loud settings for the deliberately non-batch manual route. */
public record ManualCinnabarConfig(boolean enabled, int heatingTicks, int hammerCooldownTicks,
                                   int hammerDamage, double reach, boolean manualNoBatch) {
    private static volatile ManualCinnabarConfig current;
    public ManualCinnabarConfig {
        if (heatingTicks < 20 || heatingTicks > 72000) throw new IllegalArgumentException("heatingTicks: 20..72000");
        if (hammerCooldownTicks < 1 || hammerCooldownTicks > 1200) throw new IllegalArgumentException("hammerCooldownTicks: 1..1200");
        if (hammerDamage < 1 || hammerDamage > 100) throw new IllegalArgumentException("hammerDamage: 1..100");
        if (!Double.isFinite(reach) || reach < 1 || reach > 5) throw new IllegalArgumentException("reach: 1..5 blocks");
        if (!manualNoBatch) throw new IllegalArgumentException("manualNoBatch must remain true; automated recovery belongs to industrial recipes");
    }
    public static ManualCinnabarConfig get() {
        if (current == null) synchronized (ManualCinnabarConfig.class) {
            if (current == null) current = load();
        }
        return current;
    }
    public static ManualCinnabarConfig fromJson(JsonObject json) {
        return new ManualCinnabarConfig(bool(json, "enabled"),
                integer(json, "heatingTicks"), integer(json, "hammerCooldownTicks"),
                integer(json, "hammerDamage"), number(json, "reach"),
                bool(json, "manualNoBatch"));
    }
    private static boolean bool(JsonObject json, String key) {
        if (!json.has(key) || !json.get(key).isJsonPrimitive() || !json.getAsJsonPrimitive(key).isBoolean())
            throw new IllegalArgumentException("Expected boolean: " + key);
        return json.get(key).getAsBoolean();
    }
    private static int integer(JsonObject json, String key) {
        double value = number(json, key);
        if (!Double.isFinite(value) || value != Math.rint(value) || value > Integer.MAX_VALUE || value < Integer.MIN_VALUE)
            throw new IllegalArgumentException("Expected integer: " + key);
        return (int) value;
    }
    private static double number(JsonObject json, String key) {
        if (!json.has(key) || !json.get(key).isJsonPrimitive() || !json.getAsJsonPrimitive(key).isNumber())
            throw new IllegalArgumentException("Expected number: " + key);
        return json.get(key).getAsDouble();
    }
    private static ManualCinnabarConfig load() {
        Path file = FMLPaths.CONFIGDIR.get().resolve("industrial_colonies/processing/manual_cinnabar.json");
        try {
            if (!Files.exists(file)) {
                Files.createDirectories(file.getParent());
                try (InputStream in = ManualCinnabarConfig.class.getResourceAsStream(
                        "/data/industrial_colonies/processing/manual_cinnabar.json")) {
                    if (in == null) throw new IOException("Missing bundled manual Cinnabar settings");
                    try { Files.copy(in, file); } catch (FileAlreadyExistsException ignored) { }
                }
            }
            try (Reader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
                return fromJson(JsonParser.parseReader(reader).getAsJsonObject());
            }
        } catch (IOException | RuntimeException exception) {
            throw new IllegalStateException("Invalid manual Cinnabar config: " + file, exception);
        }
    }
}
