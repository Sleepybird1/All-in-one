package dev.godpc.industrialcolonies.processing;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;
import org.slf4j.LoggerFactory;

/** Source-guarded changes to qualified effective recipes, never archive restoration. */
public final class EffectiveFluidNormalizer {
    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private static final String RULES = "/industrial_colonies/effective-fluid-rules.json";
    private static final Map<RecipeManager, Map<String, String>> REPORTS = Collections.synchronizedMap(new WeakHashMap<>());

    public record Result(Map<ResourceLocation, RecipeHolder<?>> recipes, Map<String, String> status, int changed) {}

    public static JsonArray rules() {
        try (var stream = EffectiveFluidNormalizer.class.getResourceAsStream(RULES)) {
            if (stream == null) throw new IllegalStateException("Missing qualified fluid rules");
            return JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonArray();
        } catch (Exception e) { throw new IllegalStateException("Invalid fluid rules", e); }
    }

    public static Map<String, String> report(RecipeManager manager) {
        return REPORTS.getOrDefault(manager, Map.of());
    }

    public static Result apply(RecipeManager manager, Map<ResourceLocation, RecipeHolder<?>> originals, HolderLookup.Provider registries) {
        Result result = normalize(originals, registries, rules());
        REPORTS.put(manager, result.status());
        long held = result.status().values().stream().filter(s -> s.startsWith("HELD")).count();
        LoggerFactory.getLogger(EffectiveFluidNormalizer.class).info("Qualified fluid normalization: {} changed, {} held", result.changed(), held);
        return result;
    }

    public static Result normalize(Map<ResourceLocation, RecipeHolder<?>> originals, HolderLookup.Provider registries, JsonArray rules) {
        var output = new LinkedHashMap<>(originals);
        var status = new LinkedHashMap<String, String>();
        var ops = RegistryOps.create(JsonOps.INSTANCE, registries);
        int changed = 0;
        for (var element : rules) {
            var rule = element.getAsJsonObject();
            String id = rule.get("id").getAsString();
            var key = ResourceLocation.parse(id);
            var holder = originals.get(key);
            if (holder == null) { status.put(id, "ABSENT"); continue; }
            try {
                Recipe<?> original = holder.value();
                if (!original.getClass().getName().equals(rule.get("class").getAsString())) throw new IllegalArgumentException("class changed");
                var before = Recipe.CODEC.encodeStart(ops, original).getOrThrow();
                String hash = fingerprint(before);
                if (hash.equals(rule.get("afterSHA256").getAsString())) { status.put(id, "ALREADY_CANONICAL"); continue; }
                if (!hash.equals(rule.get("beforeSHA256").getAsString())) throw new IllegalArgumentException("effective baseline changed");
                var edited = before.deepCopy();
                for (var value : rule.getAsJsonArray("changes")) {
                    var change = value.getAsJsonObject();
                    if (!change.get("registry").getAsString().equals("fluid")) throw new IllegalArgumentException("not a fluid field");
                    String fluid = change.get("after").getAsString();
                    if (!BuiltInRegistries.FLUID.containsKey(ResourceLocation.parse(fluid))) throw new IllegalArgumentException("canonical fluid absent");
                    replace(edited, change.get("pointer").getAsString(), change.get("before").getAsString(), fluid);
                }
                if (!fingerprint(edited).equals(rule.get("afterSHA256").getAsString())) throw new IllegalArgumentException("unqualified edit");
                Recipe<?> replacement = Recipe.CODEC.parse(ops, edited).getOrThrow();
                if (replacement.getClass() != original.getClass()) throw new IllegalArgumentException("codec class changed");
                var encoded = Recipe.CODEC.encodeStart(ops, replacement).getOrThrow();
                if (!edited.equals(encoded)) throw new IllegalArgumentException("codec changed other fields");
                output.put(key, new RecipeHolder<>(key, replacement));
                status.put(id, "CHANGED"); changed++;
            } catch (RuntimeException e) { status.put(id, "HELD: " + e.getMessage()); }
        }
        return new Result(Collections.unmodifiableMap(output), Collections.unmodifiableMap(status), changed);
    }

    private static void replace(JsonElement root, String pointer, String expected, String replacement) {
        if (!pointer.startsWith("/")) throw new IllegalArgumentException("invalid pointer");
        String[] parts = pointer.substring(1).split("/", -1);
        JsonElement parent = root;
        for (int i=0; i<parts.length-1; i++) parent = child(parent, unescape(parts[i]));
        String last = unescape(parts[parts.length-1]);
        if (!child(parent, last).equals(new JsonPrimitive(expected))) throw new IllegalArgumentException("fluid field changed");
        if (parent.isJsonArray()) parent.getAsJsonArray().set(Integer.parseInt(last), new JsonPrimitive(replacement));
        else parent.getAsJsonObject().addProperty(last, replacement);
    }
    private static String unescape(String part) { return part.replace("~1", "/").replace("~0", "~"); }
    private static JsonElement child(JsonElement parent, String key) {
        return parent.isJsonArray() ? parent.getAsJsonArray().get(Integer.parseInt(key)) : Objects.requireNonNull(parent.getAsJsonObject().get(key));
    }
    private static JsonElement sorted(JsonElement value) {
        if (value.isJsonObject()) {
            var result = new JsonObject();
            value.getAsJsonObject().keySet().stream().sorted().forEach(k -> result.add(k, sorted(value.getAsJsonObject().get(k))));
            return result;
        }
        if (value.isJsonArray()) { var result = new JsonArray(); value.getAsJsonArray().forEach(v -> result.add(sorted(v))); return result; }
        return value;
    }
    public static String fingerprint(JsonElement value) {
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(GSON.toJson(sorted(value)).getBytes(StandardCharsets.UTF_8))); }
        catch (java.security.NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }
}
