package dev.godpc.industrialcolonies;

import java.util.Set;
import java.util.HashSet;
import java.nio.file.Path;
import java.nio.file.Files;
import java.io.IOException;
import com.google.gson.JsonParser;

/** Shared explicit resource owners; no inference from material names or plate tags. */
public final class SheetCanonicalization {
    public static final Set<String> DEPRECATED_IDS = load(Path.of("kubejs/config/industrial-resource-owners.json"));
    private SheetCanonicalization() {}
    public static boolean isDeprecated(String id) { return DEPRECATED_IDS.contains(id); }
    public static Set<String> load(Path path) {
        if (!Files.exists(path)) return Set.of();
        try {
            var result = new HashSet<String>();
            var root = JsonParser.parseString(Files.readString(path)).getAsJsonObject();
            var rules = root.getAsJsonArray("rules");
            for (var rule : rules) for (var id : rule.getAsJsonObject().getAsJsonArray("alternatives")) result.add(id.getAsString());
            if(root.has("disabled"))for(var id:root.getAsJsonArray("disabled"))result.add(id.getAsString());
            return Set.copyOf(result);
        } catch (IOException | RuntimeException failure) {
            // Visibility fails open; never hide arbitrary registered items on invalid input.
            System.err.println("[Industrial Colonies] Resource owner visibility policy unreadable: " + failure.getMessage());
            return Set.of();
        }
    }
}
