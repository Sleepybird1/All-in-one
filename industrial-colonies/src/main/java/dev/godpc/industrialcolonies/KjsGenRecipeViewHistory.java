package dev.godpc.industrialcolonies;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;

/**
 * Browser-style history for the KJSGen recipe review screen.
 *
 * <p>This deliberately does not know anything about pending-review order. A
 * previous-recipe action must return to something the user actually viewed,
 * even when that card has already been approved or rejected.</p>
 */
public final class KjsGenRecipeViewHistory {
    private static final int MAX_ENTRIES = 256;

    private final Deque<String> previous = new ArrayDeque<>();
    private String currentUid;

    /** Records a selection made by KJSGen itself, such as clicking its recipe list. */
    public void observe(String selectedUid) {
        String normalized = normalize(selectedUid);
        if (normalized == null) {
            return;
        }
        if (currentUid == null) {
            currentUid = normalized;
            return;
        }
        if (!currentUid.equals(normalized)) {
            remember(currentUid);
            currentUid = normalized;
        }
    }

    /** Records a forward navigation initiated by the review controls. */
    public void navigateTo(String selectedUid) {
        observe(selectedUid);
    }

    /**
     * Returns the most recently viewed recipe which still exists.
     *
     * <p>The current recipe is intentionally not pushed while going back, so
     * repeated presses continue backwards and can never wrap to a list tail.</p>
     */
    public Optional<String> previous(Predicate<String> stillExists) {
        Objects.requireNonNull(stillExists, "stillExists");
        while (!previous.isEmpty()) {
            String candidate = previous.removeLast();
            if (!candidate.equals(currentUid) && stillExists.test(candidate)) {
                currentUid = candidate;
                return Optional.of(candidate);
            }
        }
        return Optional.empty();
    }

    public boolean hasPrevious(Predicate<String> stillExists) {
        Objects.requireNonNull(stillExists, "stillExists");
        return previous.descendingIterator().hasNext()
                && previous.stream().anyMatch(uid ->
                        !uid.equals(currentUid) && stillExists.test(uid));
    }

    String currentUid() {
        return currentUid;
    }

    private void remember(String uid) {
        if (uid == null || uid.equals(previous.peekLast())) {
            return;
        }
        previous.addLast(uid);
        while (previous.size() > MAX_ENTRIES) {
            previous.removeFirst();
        }
    }

    private static String normalize(String uid) {
        if (uid == null) {
            return null;
        }
        String normalized = uid.trim();
        return normalized.isEmpty() ? null : normalized;
    }
}
