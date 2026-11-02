package dev.godpc.industrialcolonies;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/** Display-only explanations: never included in recipe approval hashes. */
public final class KjsGenRecipeHelp {
    private static final JsonObject NOTES = load();

    private static JsonObject load() {
        try (var stream = KjsGenRecipeHelp.class.getResourceAsStream(
                "/data/industrial_colonies/recipe_review_help.json")) {
            if (stream == null) return new JsonObject();
            try (var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
                return JsonParser.parseReader(reader).getAsJsonObject();
            }
        } catch (Exception exception) {
            return new JsonObject();
        }
    }

    public static String describe(String id, JsonObject card, String userNote) {
        StringBuilder text = new StringBuilder();
        if (userNote != null && !userNote.isBlank()) text.append("Your review: ").append(userNote).append("\n\n");
        if (NOTES.has(id)) text.append("Recipe help: ").append(NOTES.get(id).getAsString()).append("\n\n");
        {
            if (card.has("comment") && card.get("comment").isJsonPrimitive()) {
                String comment = card.get("comment").getAsString();
                if (!comment.isBlank()) text.append("Design note (from this card): ").append(comment);
            }
        }
        return text.toString().trim();
    }

    private KjsGenRecipeHelp() {}
}
