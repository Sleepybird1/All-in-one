package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.SubLevel;

/**
 * Marks the exact instant Sable begins destructively removing the transaction
 * source, before entity deletion, observers, plot teardown, or map removal.
 */
public final class InterstellarWarpRemovalScope {
    private static final ThreadLocal<State> CURRENT = new ThreadLocal<>();

    private InterstellarWarpRemovalScope() {
    }

    public static boolean begin(ServerSubLevel source) {
        if (source == null || CURRENT.get() != null) {
            return false;
        }
        CURRENT.set(new State(source));
        return true;
    }

    public static void markRemovalStarted(SubLevel candidate) {
        State state = CURRENT.get();
        if (state != null && candidate == state.source) {
            state.removalStarted = true;
        }
    }

    public static boolean sourceRemovalStarted(ServerSubLevel source) {
        State state = CURRENT.get();
        return state == null || state.source != source || state.removalStarted;
    }

    public static void clear(ServerSubLevel source) {
        State state = CURRENT.get();
        if (state != null && state.source == source) {
            CURRENT.remove();
        }
    }

    private static final class State {
        private final ServerSubLevel source;
        private boolean removalStarted;

        private State(ServerSubLevel source) {
            this.source = source;
        }
    }
}
