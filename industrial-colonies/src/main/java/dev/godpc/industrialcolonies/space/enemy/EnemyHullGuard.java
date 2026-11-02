package dev.godpc.industrialcolonies.space.enemy;

import java.util.*;

/** Commissioned, bounded hull manifest. A change latches a hold; restoring a
 * block never renews authority. Native adapters must sample on the server thread
 * and include containing-body identity, block state and control entity identity.
 * Inventory contents are deliberately separate custody, not hull topology. */
public final class EnemyHullGuard<K> {
    public record Cell(UUID body, String state, Object controlIdentity, boolean loaded) {}
    private final UUID body;
    private final Map<K, Cell> manifest;
    private String reason = "ACTIVE";
    private long lastTick;
    public EnemyHullGuard(UUID body, Map<K, Cell> cells, long tick) {
        this.body = Objects.requireNonNull(body);
        if (tick < 0 || cells == null || cells.isEmpty() || cells.size() > 4096)
            throw new IllegalArgumentException("Invalid commissioned hull");
        for (var e : cells.entrySet()) {
            var c = e.getValue();
            if (e.getKey() == null || c == null || !c.loaded() || !body.equals(c.body())
                    || c.state() == null || c.state().isBlank())
                throw new IllegalArgumentException("Unavailable commissioned cell");
        }
        manifest = Map.copyOf(cells); lastTick = tick;
    }
    public boolean validate(Map<K, Cell> current, long tick) {
        if (!reason.equals("ACTIVE")) return false;
        if (tick < lastTick || tick - lastTick > 2) return hold("STALE_SAMPLE");
        if (current == null || !current.keySet().equals(manifest.keySet())) return hold("MANIFEST_CHANGED");
        for (var e : manifest.entrySet()) {
            var c = current.get(e.getKey()); var old = e.getValue();
            if (c == null || !c.loaded()) return hold("HULL_UNAVAILABLE");
            if (!body.equals(c.body())) return hold("BODY_CHANGED");
            if (!old.state().equals(c.state())) return hold("BLOCK_CHANGED");
            if (old.controlIdentity() != c.controlIdentity()) return hold("CONTROL_CHANGED");
        }
        lastTick = tick; return true;
    }
    private boolean hold(String value) { reason = value; return false; }
    public boolean active() { return reason.equals("ACTIVE"); }
    public String reason() { return reason; }
    public Set<K> positions() { return manifest.keySet(); }
}
