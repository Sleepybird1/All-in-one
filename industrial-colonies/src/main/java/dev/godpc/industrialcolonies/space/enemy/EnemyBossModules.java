package dev.godpc.industrialcolonies.space.enemy;

import java.util.*;

/** Staged immutable module custody. Only a trusted observer of a COMPLETE
 * native mutation may submit transitions. A split uses Move, never Destroy.
 * Not a persisted journal, native event hook, reward or actuator authority. */
public final class EnemyBossModules {
    public record Location(UUID body, int x, int y, int z) {
        public Location { Objects.requireNonNull(body); }
    }
    public record Module(EnemyBossDefeat.Role role, Location location, boolean destroyed) {
        public Module {
            Objects.requireNonNull(role);
            if (destroyed == (location != null)) throw new IllegalArgumentException("Invalid custody");
        }
    }
    public record Change(String module, Location expected, Location destination) {
        public Change { Objects.requireNonNull(module); Objects.requireNonNull(expected); }
        // null destination means confirmed destruction, NOT missing observation.
    }
    private final UUID encounter, authority;
    private final long revision;
    private final Map<String, Module> modules;
    private final Object versionIdentity = new Object();
    private final Object predecessor;

    private EnemyBossModules(UUID encounter, UUID authority, long revision, Map<String, Module> modules, Object predecessor) {
        this.encounter = Objects.requireNonNull(encounter);
        this.authority = Objects.requireNonNull(authority);
        this.revision = revision;
        this.modules = Map.copyOf(modules);
        this.predecessor = predecessor;
        var locations = new HashSet<Location>();
        for (var entry : modules.entrySet()) {
            if (entry.getKey().isBlank() || entry.getKey().length() > 128)
                throw new IllegalArgumentException("Invalid module name");
            var module = entry.getValue();
            if (!module.destroyed() && !locations.add(module.location()))
                throw new IllegalArgumentException("Duplicate module location");
        }
    }
    public static EnemyBossModules commission(UUID encounter, UUID authority, Map<String, Module> modules) {
        if (modules == null || modules.isEmpty() || modules.size() > 128
                || modules.values().stream().anyMatch(m -> m == null || m.destroyed()))
            throw new IllegalArgumentException("Fresh intact modules required");
        if (modules.values().stream().noneMatch(m -> m.role() == EnemyBossDefeat.Role.WEAPON)
                || modules.values().stream().noneMatch(m -> m.role() == EnemyBossDefeat.Role.PROPULSION))
            throw new IllegalArgumentException("Both combat module classes required");
        return new EnemyBossModules(encounter, authority, 0, modules, null);
    }
    public EnemyBossModules apply(UUID encounter, UUID authority, long expectedRevision, List<Change> changes) {
        if (!this.encounter.equals(encounter) || !this.authority.equals(authority)
                || revision != expectedRevision || changes == null || changes.isEmpty() || changes.size() > modules.size())
            throw new IllegalArgumentException("Invalid transition authority");
        var next = new HashMap<>(modules);
        var touched = new HashSet<String>();
        for (var change : changes) {
            Objects.requireNonNull(change);
            var old = modules.get(change.module());
            if (old == null || old.destroyed() || !old.location().equals(change.expected())
                    || !touched.add(change.module()) || change.expected().equals(change.destination()))
                throw new IllegalArgumentException("Stale, duplicate or empty module change");
            next.put(change.module(), new Module(old.role(), change.destination(), change.destination() == null));
        }
        // Validate the FINAL set: simultaneous moves may swap locations atomically.
        return new EnemyBossModules(encounter, authority, Math.incrementExact(revision), next, versionIdentity);
    }
    public EnemyBossDefeat.Observation observation(long tick, boolean enabled, Set<Location> verifiedIntact) {
        var expected = new HashSet<Location>();
        modules.values().stream().filter(m -> !m.destroyed()).forEach(m -> expected.add(m.location()));
        boolean complete = verifiedIntact != null && expected.equals(verifiedIntact);
        var conditions = new HashMap<String, EnemyBossDefeat.Condition>();
        modules.forEach((name, module) -> conditions.put(name, module.destroyed()
                ? EnemyBossDefeat.Condition.DESTROYED
                : complete ? EnemyBossDefeat.Condition.INTACT : EnemyBossDefeat.Condition.UNKNOWN));
        return new EnemyBossDefeat.Observation(encounter, authority, tick, revision, complete, enabled, conditions);
    }
    public long revision() { return revision; }
    public boolean belongsTo(UUID encounter, UUID authority) {
        return this.encounter.equals(encounter) && this.authority.equals(authority);
    }
    /** In-memory lineage only; carries no restart or serialized authority. */
    public boolean isDirectSuccessorOf(EnemyBossModules previous) {
        return previous != null && predecessor == previous.versionIdentity;
    }
    public Map<String, Module> modules() { return modules; }
}
