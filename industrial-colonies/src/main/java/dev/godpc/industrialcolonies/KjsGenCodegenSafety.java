package dev.godpc.industrialcolonies;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Small, idempotent repairs applied to KJSGen-authored Create calls. */
public final class KjsGenCodegenSafety {
    private static final Pattern BARE_ITEM_TAG =
            Pattern.compile("(?<!Ingredient\\.of\\()'#[^']+'");

    private KjsGenCodegenSafety() {
    }

    /**
     * Create's KubeJS schemas accept both item and fluid ingredients in the
     * same input array. A bare tag string is therefore ambiguous and may be
     * decoded as a 1000 mB fluid tag. Wrapping it as an Ingredient forces the
     * intended item-tag branch without changing what the editor displays.
     */
    public static String forceItemTagIngredients(String generated) {
        Matcher matcher = BARE_ITEM_TAG.matcher(generated);
        StringBuilder repaired = new StringBuilder();
        while (matcher.find()) {
            matcher.appendReplacement(
                    repaired,
                    Matcher.quoteReplacement("Ingredient.of(" + matcher.group() + ")")
            );
        }
        matcher.appendTail(repaired);
        return repaired.toString();
    }
}
