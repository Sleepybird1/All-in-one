package dev.godpc.industrialcolonies.transport;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import mekanism.common.content.network.transmitter.Transmitter;
import mekanism.common.lib.transmitter.DynamicNetwork;
import mekanism.common.tile.transmitter.TileEntityTransmitter;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;

/** Read-only optional adapter used by the staged lab's admission hooks. */
public final class MekanismRangeSnapshot {
    private MekanismRangeSnapshot() {}

    public static ShortRangeAdmission.Result inspect(DynamicNetwork<?, ?, ?> network) {
        if (network == null || !(network.getWorld() instanceof ServerLevel level)
                || !level.getServer().isSameThread()) return ShortRangeAdmission.unresolved("Server-thread network required");
        var transmitters = network.getTransmitters();
        if (transmitters.size() > ShortRangeAdmission.MAX_SNAPSHOT_NODES)
            return new ShortRangeAdmission.Result(ShortRangeAdmission.Status.TOO_LARGE, 0, "Native network exceeds bounded work");
        Map<Long, Transmitter<?, ?, ?>> members = new HashMap<>();
        for (Transmitter<?, ?, ?> transmitter : transmitters) {
            if (transmitter == null || transmitter.isOrphan() || transmitter.isUpgrading()
                    || !transmitter.isValid() || transmitter.getLevel() != level
                    || transmitter.getTransmitterNetwork() != network
                    || transmitter.getWorldPositionLong() != transmitter.getBlockPos().asLong()
                    || network.getTransmitter(transmitter.getWorldPositionLong()) != transmitter
                    || transmitter.getTransmitterTile().getTransmitter() != transmitter
                    || !level.hasChunkAt(transmitter.getBlockPos())
                    || !transmitter.getTransmitterTile().isLoaded()
                    || level.getBlockEntity(transmitter.getBlockPos()) != transmitter.getTransmitterTile()
                    || members.put(transmitter.getWorldPositionLong(), transmitter) != null)
                return ShortRangeAdmission.unresolved("Unsettled or stale native membership");
        }
        var nodes = new ArrayList<ShortRangeAdmission.Node>();
        for (var transmitter : members.values()) {
            var edges = new HashSet<Long>();
            for (Direction side : Direction.values()) {
                var adjacent = transmitter.getBlockPos().relative(side);
                // Do not load chunks or infer an absent neighbor from unavailable world data.
                if (!level.hasChunkAt(adjacent)) return ShortRangeAdmission.unresolved("Unloaded boundary");
                boolean connected = Transmitter.connectionMapContainsSide(transmitter.currentTransmitterConnections, side);
                var tile = level.getBlockEntity(adjacent);
                if (connected) {
                    var other = members.get(adjacent.asLong());
                    if (!(tile instanceof TileEntityTransmitter) || other == null
                            || tile != other.getTransmitterTile()
                            || !Transmitter.connectionMapContainsSide(other.currentTransmitterConnections, side.getOpposite()))
                        return ShortRangeAdmission.unresolved("Connection does not match loaded reciprocal member");
                    edges.add(adjacent.asLong());
                } else if (tile instanceof TileEntityTransmitter otherTile) {
                    var other = otherTile.getTransmitter();
                    if (transmitter.supportsTransmissionType(other)
                            && transmitter.canConnect(side) && other.canConnect(side.getOpposite())
                            && transmitter.isValidTransmitter(otherTile, side)
                            && other.isValidTransmitter(transmitter.getTransmitterTile(), side.getOpposite()))
                        return ShortRangeAdmission.unresolved("Potential connection has not settled");
                }
            }
            nodes.add(new ShortRangeAdmission.Node(transmitter.getWorldPositionLong(), edges));
        }
        return ShortRangeAdmission.sharedBuffer(nodes, true);
    }
}
