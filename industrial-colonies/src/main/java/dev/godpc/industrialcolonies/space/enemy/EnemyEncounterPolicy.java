package dev.godpc.industrialcolonies.space.enemy;

import java.util.Objects;
import java.util.UUID;

/** Staged, unregistered decision policy. Requests are not actuator/fire authority.
 * A future server adapter must sample native state, own leases, and independently
 * validate weapon aim, ammunition consumption and collision safety each tick.
 */
public final class EnemyEncounterPolicy {
    public enum Phase { HELD, APPROACH, ATTACK, RETREAT, COMPLETE }
    public enum Motion { NONE, APPROACH_TARGET, RETREAT_FROM_TARGET }
    public record Limits(double attackRange, double breakOffRange, double retreatRange,
                         double maximumClosingSpeed, long maximumAge, long timeoutTicks) {
        public Limits {
            if (!Double.isFinite(attackRange) || !Double.isFinite(breakOffRange)
                    || !Double.isFinite(retreatRange) || !Double.isFinite(maximumClosingSpeed)
                    || breakOffRange <= 0 || attackRange <= breakOffRange || retreatRange <= attackRange
                    || maximumClosingSpeed <= 0 || maximumAge < 0 || maximumAge > 2
                    || timeoutTicks < 1 || timeoutTicks > 72000)
                throw new IllegalArgumentException("Invalid encounter limits");
        }
    }
    /** Identities and topology revision must come from native authority, not names/coordinates. */
    public record Observation(UUID ship, UUID target, String frame, long tick, long topologyRevision,
                              double range, double closingSpeed, boolean operatorEnabled,
                              boolean npcOwned, boolean targetHostile, boolean targetPresent,
                              boolean propulsionReady, boolean weaponReady, boolean resourcesReady,
                              boolean pathClear, boolean fireSolutionClear) {}
    public record Request(Phase phase, Motion motion, boolean requestFire, String reason) {}
    public record Checkpoint(UUID ship, UUID target, String frame, long topologyRevision) {
        public Checkpoint {
            Objects.requireNonNull(ship); Objects.requireNonNull(target); Objects.requireNonNull(frame);
            if (ship.equals(target) || frame.isBlank() || topologyRevision < 0)
                throw new IllegalArgumentException("Invalid encounter identity");
        }
    }
    private final Limits limits;
    private Checkpoint identity;
    private Phase phase = Phase.HELD;
    private String reason = "NOT_STARTED";
    private long started, lastTick = -1, lastObservation = -1;

    public EnemyEncounterPolicy(Limits limits) { this.limits = Objects.requireNonNull(limits); }
    /** Restoring identity never restores movement, weapon permission or active phase. */
    public static EnemyEncounterPolicy restore(Limits limits, Checkpoint checkpoint) {
        var policy = new EnemyEncounterPolicy(limits);
        policy.identity = Objects.requireNonNull(checkpoint);
        policy.reason = "RESTART_REQUIRES_EXPLICIT_START";
        return policy;
    }
    public Checkpoint checkpoint() {
        if (identity == null) throw new IllegalStateException("No commissioned encounter");
        return identity;
    }
    /** Explicit operator/admission action. Never call automatically after a hold. */
    public Request start(long now, Observation observation) {
        if (phase != Phase.HELD && phase != Phase.COMPLETE) return hold("ALREADY_ACTIVE");
        String invalid = validate(now, observation, false);
        if (invalid != null) return hold(invalid);
        identity = new Checkpoint(observation.ship, observation.target, observation.frame, observation.topologyRevision);
        started = now; lastTick = now; lastObservation = observation.tick;
        phase = Phase.APPROACH; reason = "ADMITTED";
        // Admission itself does not command motion or fire.
        return idle();
    }
    public Request step(long now, Observation observation) {
        if (phase == Phase.HELD || phase == Phase.COMPLETE) return idle();
        String invalid = validate(now, observation, true);
        if (invalid != null) return hold(invalid);
        if (now <= lastTick || now - lastTick > 2 || observation.tick <= lastObservation)
            return hold("OBSERVATION_SEQUENCE_LOST");
        if (now - started >= limits.timeoutTicks) return hold("ENCOUNTER_TIMEOUT");
        lastTick = now; lastObservation = observation.tick;
        if (phase == Phase.APPROACH && observation.range <= limits.attackRange) phase = Phase.ATTACK;
        if (phase == Phase.ATTACK && observation.range <= limits.breakOffRange) phase = Phase.RETREAT;
        if (phase == Phase.RETREAT && observation.range >= limits.retreatRange) {
            phase = Phase.COMPLETE; reason = "ONE_PASS_COMPLETE"; return idle();
        }
        reason = "ACTIVE";
        return new Request(phase, phase == Phase.RETREAT ? Motion.RETREAT_FROM_TARGET : Motion.APPROACH_TARGET,
                phase == Phase.ATTACK && observation.range <= limits.attackRange && observation.fireSolutionClear, reason);
    }
    public Request stop() { return hold("OPERATOR_STOP"); }
    private Request hold(String why) { phase = Phase.HELD; reason = why; return idle(); }
    private Request idle() { return new Request(phase, Motion.NONE, false, reason); }
    private String validate(long now, Observation o, boolean bound) {
        if (o == null || now < 0 || o.tick < 0 || o.tick > now || now - o.tick > limits.maximumAge)
            return "STALE_OR_INVALID_OBSERVATION";
        if (!o.operatorEnabled) return "SERVER_CONTROL_DISABLED";
        if (o.ship == null || o.target == null || o.ship.equals(o.target) || o.frame == null
                || o.frame.isBlank() || o.topologyRevision < 0) return "INVALID_IDENTITY";
        if (bound && (!identity.ship.equals(o.ship) || !identity.target.equals(o.target)
                || !identity.frame.equals(o.frame))) return "IDENTITY_OR_FRAME_CHANGED";
        if (bound && identity.topologyRevision != o.topologyRevision) return "HULL_CHANGED";
        if (!o.npcOwned) return "NPC_OWNERSHIP_LOST";
        if (!o.targetHostile || !o.targetPresent) return "TARGET_UNAVAILABLE";
        if (!Double.isFinite(o.range) || o.range < 0 || !Double.isFinite(o.closingSpeed)
                || Math.abs(o.closingSpeed) > limits.maximumClosingSpeed) return "UNSAFE_KINEMATICS";
        if (!o.propulsionReady || !o.weaponReady || !o.resourcesReady) return "SUBSYSTEM_UNAVAILABLE";
        if (!o.pathClear) return "PATH_BLOCKED";
        return null;
    }
}
