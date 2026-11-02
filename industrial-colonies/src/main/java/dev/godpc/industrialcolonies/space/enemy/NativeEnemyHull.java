package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import dev.godpc.industrialcolonies.space.RcsActuatorLease;
import java.util.*;

/** Read-only commissioned-hull adapter; no spawning, movement or firing. */
public final class NativeEnemyHull {
    private final ServerSubLevel body;
    private final EnemyHullGuard<BlockPos> guard;
    private final EnemyHullRevisionAccess topology;
    private final long revision;
    private boolean topologyChanged;
    private NativeEnemyHull(ServerSubLevel body, Collection<BlockPos> positions) {
        this.body = Objects.requireNonNull(body);
        if (!(body.getHeatMapManager() instanceof EnemyHullRevisionAccess access))
            throw new IllegalStateException("Native hull revision observer required");
        topology = access; revision = topology.industrialColonies$hullRevision();
        if (revision == Long.MAX_VALUE) throw new IllegalStateException("Hull revision exhausted");
        var cells = sample(positions);
        for (var p : positions) if (body.getLevel().getBlockState(p).isAir())
            throw new IllegalArgumentException("Empty commissioned hull cell");
        guard = new EnemyHullGuard<>(body.getUniqueId(), cells, body.getLevel().getGameTime());
    }
    public static NativeEnemyHull commission(ServerSubLevel body, Collection<BlockPos> positions) {
        if (positions == null || positions.isEmpty() || positions.size() > 4096
                || new HashSet<>(positions).size() != positions.size())
            throw new IllegalArgumentException("Invalid hull manifest");
        return new NativeEnemyHull(body, positions);
    }
    private Map<BlockPos, EnemyHullGuard.Cell> sample(Collection<BlockPos> positions) {
        var level = body.getLevel();
        if (!level.getServer().isSameThread()) throw new IllegalStateException("Server-thread hull sample required");
        var result = new HashMap<BlockPos, EnemyHullGuard.Cell>();
        for (var p : positions) {
            boolean loaded = !body.isRemoved() && level.hasChunkAt(p);
            var containing = loaded ? Sable.HELPER.getContaining(level, p) : null;
            result.put(p.immutable(), new EnemyHullGuard.Cell(containing == null ? null : containing.getUniqueId(),
                    loaded ? level.getBlockState(p).toString() : "UNAVAILABLE",
                    loaded ? level.getBlockEntity(p) : null, loaded));
        }
        return result;
    }
    public boolean validate() {
        if (!body.getLevel().getServer().isSameThread()) throw new IllegalStateException("Server-thread hull sample required");
        topologyChanged |= topology.industrialColonies$hullRevision() != revision;
        if (topologyChanged) return false;
        return guard.validate(sample(guard.positions()), body.getLevel().getGameTime());
    }
    public String reason() { return topologyChanged ? "TOPOLOGY_CHANGED" : guard.reason(); }
    public boolean belongsTo(ServerSubLevel candidate) { return candidate == body; }
    public boolean observes(BlockPos position) { return guard.positions().contains(position); }
    /** The hull check precedes every write, including zero-power commands.
     * A failed check releases the entire lease; reassembly cannot revive it. */
    public boolean apply(RcsActuatorLease lease, List<Double> throttles) {
        Objects.requireNonNull(lease);
        if (!lease.belongsTo(body)) { lease.close(); return false; }
        if (!validate()) { lease.close(); return false; }
        return lease.apply(throttles);
    }
}
