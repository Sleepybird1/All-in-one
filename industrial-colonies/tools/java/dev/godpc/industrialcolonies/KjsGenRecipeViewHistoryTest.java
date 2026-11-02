package dev.godpc.industrialcolonies;

import java.util.Set;

/** Standalone focused regression test; run with plain javac/java. */
public final class KjsGenRecipeViewHistoryTest {
    private KjsGenRecipeViewHistoryTest() {
    }

    public static void main(String[] args) {
        KjsGenRecipeViewHistory history = new KjsGenRecipeViewHistory();
        Set<String> existing = Set.of("a", "b", "c", "d");

        history.observe("a");
        require(history.previous(existing::contains).isEmpty(),
                "the first viewed recipe must not wrap to a list tail");

        history.observe("b");
        history.observe("c");
        require(history.previous(existing::contains).orElseThrow().equals("b"),
                "Previous Recipe must return to the immediately viewed card");
        require(history.previous(existing::contains).orElseThrow().equals("a"),
                "repeated Previous Recipe must continue backwards");
        require(history.previous(existing::contains).isEmpty(),
                "history must stop instead of wrapping to the final card");

        history.navigateTo("d");
        require(history.previous(existing::contains).orElseThrow().equals("a"),
                "forward review navigation must retain the card it left");

        history.observe("b");
        history.observe("c");
        require(history.previous(uid -> uid.equals("a") || uid.equals("b"))
                        .orElseThrow().equals("b"),
                "deleted/stale history entries must be skipped");
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
