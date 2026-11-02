package dev.godpc.industrialcolonies.processing;

/** One unit of work per world tick; lost contact restarts the stage, duplicated fan calls do not accelerate it. */
public final class AssemblyCookTimer {
    public record State(String key, long lastTick, int remaining) {}
    public static State tick(State before, String key, int duration, long tick) {
        if (duration < 1) throw new IllegalArgumentException("Stage duration must be positive");
        if (before == null || !before.key().equals(key) || tick < before.lastTick() || tick - before.lastTick() > 1)
            return new State(key, tick, duration);
        if (tick == before.lastTick()) return before;
        return new State(key, tick, Math.max(0, before.remaining() - 1));
    }
}
