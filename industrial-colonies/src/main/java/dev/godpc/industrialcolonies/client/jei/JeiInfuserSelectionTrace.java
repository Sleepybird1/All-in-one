package dev.godpc.industrialcolonies.client.jei;

import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

/** Bounded metadata-only diagnostics; never contains stacks, recipe payloads or player data. */
public final class JeiInfuserSelectionTrace {
    public static final String TARGET = "mekanism:metallurgic_infusing";
    public static final int COUNT_LIMIT = 257;
    private static final int SELECTION_LIMIT = 16;
    private int selections;

    public synchronized boolean available() {
        return selections < SELECTION_LIMIT;
    }

    public synchronized Selection begin(String requested, Snapshot before) {
        if (!available() || before == null || !(TARGET.equals(requested)
                || TARGET.equals(before.selected()) || before.targetIndex() >= 0)) return null;
        int number = ++selections;
        return new Selection(number, id(requested), line(number, "BEFORE", requested, before));
    }

    public String finish(Selection selection, Snapshot after) {
        if (selection == null || after == null || !selection.finished.compareAndSet(false, true)) return null;
        return line(selection.number, "AFTER", selection.requested, after);
    }

    private static String line(int number, String phase, String requested, Snapshot value) {
        return "IC_JEI_INFUSER_SELECTION selection=" + number + " phase=" + phase
                + " requested=" + id(requested) + " selected=" + id(value.selected())
                + " category_count=" + value.categoryCount() + " target_index=" + value.targetIndex()
                + " categories=" + value.categoryIds().stream().limit(24).map(JeiInfuserSelectionTrace::id).toList()
                + " focus_roles=" + value.focusRoles().stream().limit(8)
                    .map(role -> role != null && role.matches("[A-Z_]{1,24}") ? role : "INVALID").toList()
                + " selected_recipe_count=" + count(value.selectedRecipeCount())
                + " target_focused_visible=" + count(value.targetFocusedVisible())
                + " target_visible=" + count(value.targetVisible())
                + " target_including_hidden=" + count(value.targetIncludingHidden());
    }

    private static String id(String value) {
        return value != null && value.length() <= 160 && value.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")
                ? value : "UNKNOWN";
    }

    private static String count(long value) {
        return value < 0 ? "UNKNOWN" : value >= COUNT_LIMIT ? ">=257" : Long.toString(value);
    }

    public record Snapshot(String selected, int categoryCount, int targetIndex, List<String> categoryIds,
                           List<String> focusRoles, long selectedRecipeCount, long targetFocusedVisible,
                           long targetVisible, long targetIncludingHidden) {
        public Snapshot {
            categoryIds = List.copyOf(categoryIds);
            focusRoles = List.copyOf(focusRoles);
        }
    }

    public static final class Selection {
        private final int number;
        private final String requested;
        private final String before;
        private final AtomicBoolean finished = new AtomicBoolean();

        private Selection(int number, String requested, String before) {
            this.number = number;
            this.requested = requested;
            this.before = before;
        }

        public String before() { return before; }
    }
}
