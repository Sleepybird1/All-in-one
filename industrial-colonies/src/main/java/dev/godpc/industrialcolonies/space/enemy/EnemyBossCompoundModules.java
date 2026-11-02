package dev.godpc.industrialcolonies.space.enemy;

import java.util.*;

/** Groups independently tracked constituents into commissioned combat modules.
 * Mount loss, fragment movement, absent ammunition and unloaded entities are
 * never destruction evidence. Callers must account for mounted-entity custody
 * as well as hull cells. This mapper supplies no native observation authority. */
public final class EnemyBossCompoundModules {
    public record Module(EnemyBossDefeat.Role role, Set<String> parts) {
        public Module {
            Objects.requireNonNull(role);
            parts = Set.copyOf(Objects.requireNonNull(parts));
            if (parts.isEmpty() || parts.size() > 128 || parts.stream().anyMatch(p -> !validName(p)))
                throw new IllegalArgumentException("Invalid constituent manifest");
        }
    }
    private final Map<String, Module> modules;
    private final Set<String> parts;

    public EnemyBossCompoundModules(Map<String, Module> manifest) {
        modules = Map.copyOf(Objects.requireNonNull(manifest));
        if (modules.isEmpty() || modules.size() > 128 || modules.keySet().stream().anyMatch(p -> !validName(p)))
            throw new IllegalArgumentException("Invalid module manifest");
        var seen = new HashSet<String>();
        for (var module : modules.values()) for (var part : module.parts())
            if (!seen.add(part)) throw new IllegalArgumentException("Constituent claimed by multiple modules");
        if (seen.size() > 128 || modules.values().stream().noneMatch(m -> m.role() == EnemyBossDefeat.Role.WEAPON)
                || modules.values().stream().noneMatch(m -> m.role() == EnemyBossDefeat.Role.PROPULSION))
            throw new IllegalArgumentException("Invalid bounded combat manifest");
        parts = Set.copyOf(seen);
    }
    public Map<String, EnemyBossDefeat.Role> roles() {
        var result = new HashMap<String, EnemyBossDefeat.Role>();
        modules.forEach((name, module) -> result.put(name, module.role()));
        return Map.copyOf(result);
    }
    public Set<String> parts() { return parts; }

    /** The input revision must version constituent changes, even when the
     * aggregate module condition remains INTACT. Unknown custody fails closed. */
    public EnemyBossDefeat.Observation aggregate(EnemyBossDefeat.Observation constituents) {
        Objects.requireNonNull(constituents);
        boolean complete = constituents.completeCustody() && constituents.modules().keySet().equals(parts)
                && !constituents.modules().containsValue(EnemyBossDefeat.Condition.UNKNOWN);
        var result = new HashMap<String, EnemyBossDefeat.Condition>();
        for (var entry : modules.entrySet()) {
            var condition = EnemyBossDefeat.Condition.UNKNOWN;
            if (complete) {
                condition = entry.getValue().parts().stream().allMatch(p ->
                    constituents.modules().get(p) == EnemyBossDefeat.Condition.DESTROYED)
                    ? EnemyBossDefeat.Condition.DESTROYED : EnemyBossDefeat.Condition.INTACT;
            }
            result.put(entry.getKey(), condition);
        }
        return new EnemyBossDefeat.Observation(constituents.encounter(), constituents.authority(),
                constituents.tick(), constituents.revision(), complete, constituents.automationEnabled(), result);
    }
    private static boolean validName(String name) { return name != null && !name.isBlank() && name.length() <= 128; }
}
