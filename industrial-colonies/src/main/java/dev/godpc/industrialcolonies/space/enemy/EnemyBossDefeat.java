package dev.godpc.industrialcolonies.space.enemy;

import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Staged read-only defeat proposal. Observations require a trusted native
 * adapter covering the original hull AND every detached fragment. Neither
 * capability absence nor an unloaded/missing body proves destruction.
 * This class grants no actuator, reward, capture or persistence authority. */
public final class EnemyBossDefeat {
    public enum Role { WEAPON, PROPULSION }
    public enum Condition { INTACT, DESTROYED, UNKNOWN }
    public enum State { ACTIVE, DISARMED, IMMOBILIZED, DEFEATED, HELD }
    public record Observation(UUID encounter, UUID authority, long tick, long revision,
            boolean completeCustody, boolean automationEnabled,
            Map<String, Condition> modules) {
        public Observation { modules = Map.copyOf(Objects.requireNonNull(modules)); }
    }
    public record Result(State state, String reason, int weaponsRemaining, int propulsionRemaining) {}

    private final UUID encounter, authority;
    private final Map<String, Role> manifest;
    private long tick, revision;
    private Result result;
    private Map<String, Condition> previous;

    public EnemyBossDefeat(UUID encounter, UUID authority, Map<String, Role> manifest,
                           long tick, long revision) {
        this.encounter = Objects.requireNonNull(encounter);
        this.authority = Objects.requireNonNull(authority);
        this.manifest = Map.copyOf(Objects.requireNonNull(manifest));
        if (tick < 0 || revision < 0 || manifest.size() > 128
                || !manifest.containsValue(Role.WEAPON) || !manifest.containsValue(Role.PROPULSION)
                || manifest.keySet().stream().anyMatch(s -> s.isBlank() || s.length() > 128))
            throw new IllegalArgumentException("Invalid boss module manifest");
        this.tick = tick;
        this.revision = revision;
        result = new Result(State.ACTIVE, "COMMISSIONED", count(Role.WEAPON), count(Role.PROPULSION));
    }

    public Result observe(Observation sample) {
        if (result.state() == State.HELD || result.state() == State.DEFEATED) return result;
        if (sample == null) return hold("OBSERVATION_UNAVAILABLE");
        if (!encounter.equals(sample.encounter()) || !authority.equals(sample.authority()))
            return hold("AUTHORITY_CHANGED");
        if (!sample.automationEnabled()) return hold("AUTOMATION_DISABLED");
        if (sample.tick() <= tick || sample.tick() - tick > 2 || sample.revision() < revision)
            return hold("STALE_OBSERVATION");
        if (!sample.completeCustody() || !sample.modules().keySet().equals(manifest.keySet())
                || sample.modules().containsValue(Condition.UNKNOWN)) return hold("INCOMPLETE_CUSTODY");
        if (previous != null && sample.revision() == revision && !previous.equals(sample.modules()))
            return hold("UNVERSIONED_DAMAGE_CHANGE");
        int weapons = 0, propulsion = 0;
        for (var entry : manifest.entrySet()) {
            if (sample.modules().get(entry.getKey()) == Condition.INTACT) {
                if (entry.getValue() == Role.WEAPON) weapons++; else propulsion++;
            }
        }
        tick = sample.tick(); revision = sample.revision();
        previous = sample.modules();
        State state = weapons == 0 ? (propulsion == 0 ? State.DEFEATED : State.DISARMED)
                : (propulsion == 0 ? State.IMMOBILIZED : State.ACTIVE);
        result = new Result(state, switch (state) {
            case DEFEATED -> "ALL_COMMISSIONED_WEAPONS_AND_PROPULSION_DESTROYED";
            case DISARMED -> "WEAPONS_DESTROYED";
            case IMMOBILIZED -> "PROPULSION_DESTROYED";
            default -> "COMBAT_MODULES_REMAIN";
        }, weapons, propulsion);
        return result;
    }
    public Result hold(String reason) {
        // Defeat is an observation, not a repeatable reward event.
        if (result.state() != State.DEFEATED)
            result = new Result(State.HELD, Objects.requireNonNull(reason), result.weaponsRemaining(), result.propulsionRemaining());
        return result;
    }
    public Result result() { return result; }
    private int count(Role role) { return (int) manifest.values().stream().filter(role::equals).count(); }
}
