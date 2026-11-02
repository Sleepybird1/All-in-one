package dev.godpc.industrialcolonies;

import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Reversible picker/history key. These keys are never authored item resource IDs. */
public final class KjsGenItemReference {
    private static final String PREFIX = "@kjsgen-item:";
    public static final int MAX_REFERENCE_LENGTH = 1_048_576;
    private record Input(String id,String components) { }
    private static final Map<Input,String> KEYS = new LinkedHashMap<>(64,.75f,true) {
        @Override protected boolean removeEldestEntry(Map.Entry<Input,String> entry){return size()>64;}
    };
    private KjsGenItemReference() { }
    public record Item(String id, String components) { }
    public static boolean isReference(String key) { return key != null && key.startsWith(PREFIX); }
    public static synchronized String key(String id, String components) {
        if (id == null || !id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
            throw new IllegalArgumentException("Actual item resource ID required");
        if (components == null || components.isBlank()) return id;
        if (components.length()>MAX_REFERENCE_LENGTH) throw new IllegalArgumentException("Item component reference is too large");
        Input source=new Input(id,components);String cached=KEYS.get(source);if(cached!=null)return cached;
        JsonElement patch = JsonParser.parseString(components);
        if (!patch.isJsonObject()) throw new IllegalArgumentException("Item components must be an object");
        if (patch.getAsJsonObject().isEmpty()) return id;
        JsonObject item = new JsonObject(); item.addProperty("id", id); item.add("components", patch);
        String reference = PREFIX + Base64.getUrlEncoder().withoutPadding().encodeToString(canonical(item).getBytes(StandardCharsets.UTF_8));
        if (reference.length() > MAX_REFERENCE_LENGTH) throw new IllegalArgumentException("Item component reference is too large");
        KEYS.put(source,reference);
        return reference;
    }
    public static Optional<Item> decode(String key) {
        if (!isReference(key) || key.length() > MAX_REFERENCE_LENGTH) return Optional.empty();
        try {
            JsonObject item = JsonParser.parseString(new String(Base64.getUrlDecoder().decode(key.substring(PREFIX.length())), StandardCharsets.UTF_8)).getAsJsonObject();
            if (!item.keySet().equals(Set.of("id", "components")) || !item.get("id").isJsonPrimitive()
                || !item.get("components").isJsonObject()) return Optional.empty();
            String id = item.get("id").getAsString(), components = canonical(item.get("components"));
            if (!key(id, components).equals(key)) return Optional.empty();
            return Optional.of(new Item(id, components));
        } catch (RuntimeException invalid) { return Optional.empty(); }
    }
    public static String baseId(String key) {
        return isReference(key) ? decode(key).map(Item::id).orElse("") : key;
    }
    public static String canonical(JsonElement value) {
        if (value.isJsonObject()) {
            JsonObject sorted = new JsonObject();
            value.getAsJsonObject().keySet().stream().sorted().forEach(key -> sorted.add(key, JsonParser.parseString(canonical(value.getAsJsonObject().get(key)))));
            return sorted.toString();
        }
        if (value.isJsonArray()) {
            JsonArray array = new JsonArray(); value.getAsJsonArray().forEach(child -> array.add(JsonParser.parseString(canonical(child)))); return array.toString();
        }
        return value.toString();
    }
}
