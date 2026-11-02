package dev.godpc.industrialcolonies.geology;

/** Deterministic scattered sites become sparser toward the edge of a source's clue area. */
public final class TraceScatterPolicy {
    private TraceScatterPolicy() {}
    public static boolean accepts(long seed, long distanceSquared, int radius) {
        if (radius <= 0 || radius > 4000 || distanceSquared < 0) throw new IllegalArgumentException("Invalid trace distance");
        if (distanceSquared > (long) radius * radius) return false;
        double fraction = Math.sqrt(distanceSquared) / radius;
        double chance = 0.15 + 0.85 * (1 - fraction) * (1 - fraction);
        long roll = (seed ^ (seed >>> 30)) * 0xbf58476d1ce4e5b9L;
        roll = (roll ^ (roll >>> 27)) * 0x94d049bb133111ebL;
        roll ^= roll >>> 31;
        return (roll >>> 11) * 0x1.0p-53 < chance;
    }
}
