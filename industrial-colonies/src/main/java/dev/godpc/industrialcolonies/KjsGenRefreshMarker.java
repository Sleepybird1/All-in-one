package dev.godpc.industrialcolonies;

import com.google.gson.JsonParser;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.Map;

/** Marker discovery only: never creates a project or adopts a refresh baseline. */
public final class KjsGenRefreshMarker {
    private static final int MAX_BYTES = 4096;
    private KjsGenRefreshMarker() {}

    public static String readRevision(Path project, Path marker) {
        try {
            if (!Files.isRegularFile(project, LinkOption.NOFOLLOW_LINKS)
                    || !Files.isRegularFile(marker, LinkOption.NOFOLLOW_LINKS)) return null;
            byte[] bytes;
            try (var input = Files.newInputStream(marker)) {
                bytes = input.readNBytes(MAX_BYTES + 1);
            }
            if (bytes.length > MAX_BYTES) return null;
            var value = JsonParser.parseString(new String(bytes, StandardCharsets.UTF_8));
            if (!value.isJsonObject()) return null;
            var revision = value.getAsJsonObject().get("revision");
            if (revision == null || !revision.isJsonPrimitive()
                    || !revision.getAsJsonPrimitive().isString()) return null;
            String text = revision.getAsString();
            if (text.isBlank() || !Files.isRegularFile(project, LinkOption.NOFOLLOW_LINKS)) return null;
            return text;
        } catch (Exception unavailable) {
            return null;
        }
    }

    /** Invoke on the client thread, including when a previously valid source disappears. */
    public static void record(Map<String, String> available, String key, String revision) {
        if (revision == null) available.remove(key);
        else available.put(key, revision);
    }
}
