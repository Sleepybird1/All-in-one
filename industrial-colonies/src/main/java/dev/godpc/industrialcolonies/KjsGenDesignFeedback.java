package dev.godpc.industrialcolonies;

import java.util.List;
import java.util.Set;
import java.util.function.Function;

/** Specific design feedback, retaining the existing review-ledger reason schema. */
public final class KjsGenDesignFeedback {
    public static final List<String> CHOICES = List.of(
            "materials", "odd_shape", "lopsided", "ring", "jumble");

    private KjsGenDesignFeedback() {}

    public static String reasonCode(Set<String> selected) {
        requireSelection(selected);
        return selected.size() == 1 && selected.contains("ring") ? "ring_of_items" : "manual";
    }

    public static String note(Set<String> selected, String details, Function<String, String> text) {
        requireSelection(selected);
        String result = CHOICES.stream().filter(selected::contains)
                .map(text).reduce((a, b) -> a + " " + b).orElseThrow();
        if (details != null && !details.isBlank()) result += " Notes: " + details.trim();
        return result;
    }

    private static void requireSelection(Set<String> selected) {
        if (selected == null || selected.isEmpty() || !CHOICES.containsAll(selected))
            throw new IllegalArgumentException("Select at least one valid shape/material concern.");
    }
}
