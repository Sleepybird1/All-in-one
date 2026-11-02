package dev.godpc.industrialcolonies.geology;

import java.util.concurrent.CompletionStage;

/** Read-only discovery may suspend before consuming a candidate, never during placement. */
public final class NativeTerrainYield {
    private static final ThreadLocal<Boolean> ACTIVE = new ThreadLocal<>();
    private NativeTerrainYield() {}
    @FunctionalInterface public interface Read { boolean run() throws Exception; }
    public static boolean active() { return Boolean.TRUE.equals(ACTIVE.get()); }
    public static boolean during(Read read) throws Exception {
        Boolean previous = ACTIVE.get(); ACTIVE.set(true);
        try { return read.run(); }
        finally { if (previous == null) ACTIVE.remove(); else ACTIVE.set(previous); }
    }
    public static final class Pending extends RuntimeException {
        private final CompletionStage<?> ready;
        public Pending(CompletionStage<?> ready) {
            super("Native terrain prerequisite pending", null, false, false);
            this.ready = java.util.Objects.requireNonNull(ready);
        }
        public CompletionStage<?> ready() { return ready; }
    }
}
