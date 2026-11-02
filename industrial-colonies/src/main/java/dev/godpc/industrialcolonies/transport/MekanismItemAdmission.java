package dev.godpc.industrialcolonies.transport;

import it.unimi.dsi.fastutil.longs.LongList;
import java.util.ArrayList;
import java.util.function.Supplier;
import mekanism.common.content.network.transmitter.LogisticalTransporterBase;
import mekanism.common.content.network.transmitter.Transmitter;
import mekanism.common.content.transporter.TransporterStack;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;

/** Admission scope covers only a newly created stack, never a native reroute or return. */
public final class MekanismItemAdmission {
    private static final ThreadLocal<TransporterStack> NEW_STACK = new ThreadLocal<>();
    private MekanismItemAdmission() {}

    public static boolean isNewIngress(TransporterStack stack) { return stack != null && NEW_STACK.get() == stack; }

    public static <T> T calculate(TransporterStack stack, Supplier<T> action) {
        TransporterStack previous = NEW_STACK.get();
        NEW_STACK.set(stack);
        try { return action.get(); }
        finally { if (previous == null) NEW_STACK.remove(); else NEW_STACK.set(previous); }
    }

    /** Native paths are destination-first, then transmitters, ending at the ingress transmitter. */
    public static ShortRangeAdmission.Result inspect(LogisticalTransporterBase start, LongList path) {
        if (start == null || !(start.getLevel() instanceof ServerLevel level)
                || !level.getServer().isSameThread() || path == null || path.size() < 2)
            return ShortRangeAdmission.unresolved("No complete server-thread item path");
        if (path.size() > ShortRangeAdmission.MAX_SNAPSHOT_NODES + 1)
            return new ShortRangeAdmission.Result(ShortRangeAdmission.Status.TOO_LARGE, 0, "Item path exceeds bound");
        var network = start.getTransmitterNetwork();
        if (network == null || network.getWorld() != level
                || network.getTransmitter(start.getWorldPositionLong()) != start
                || path.getLong(path.size() - 1) != start.getWorldPositionLong())
            return ShortRangeAdmission.unresolved("Path does not begin at ingress");
        BlockPos destination = BlockPos.of(path.getLong(0));
        if (!level.hasChunkAt(destination) || level.getBlockEntity(destination) == null
                || network.getTransmitter(destination.asLong()) != null)
            return ShortRangeAdmission.unresolved("Unavailable destination inventory");
        var nodes = new ArrayList<Long>();
        LogisticalTransporterBase previous = null;
        BlockPos previousPos = destination;
        for (int i = 1; i < path.size(); i++) {
            long id = path.getLong(i);
            var current = network.getTransmitter(id);
            BlockPos pos = BlockPos.of(id);
            if (current == null || current.isOrphan() || current.isUpgrading() || !current.isValid()
                    || current.getWorldPositionLong() != id || !current.getBlockPos().equals(pos)
                    || current.getLevel() != level || current.getTransmitterNetwork() != network
                    || current.getTransmitterTile().getTransmitter() != current
                    || !level.hasChunkAt(pos) || !current.getTransmitterTile().isLoaded()
                    || level.getBlockEntity(pos) != current.getTransmitterTile())
                return ShortRangeAdmission.unresolved("Unavailable item path member");
            Direction side = Direction.fromDelta(previousPos.getX()-pos.getX(), previousPos.getY()-pos.getY(), previousPos.getZ()-pos.getZ());
            if (side == null || pos.distManhattan(previousPos) != 1)
                return ShortRangeAdmission.unresolved("Nonadjacent item path");
            if (previous != null && (!Transmitter.connectionMapContainsSide(current.currentTransmitterConnections, side)
                    || !Transmitter.connectionMapContainsSide(previous.currentTransmitterConnections, side.getOpposite())))
                return ShortRangeAdmission.unresolved("Nonreciprocal item path");
            nodes.add(id); previous = current; previousPos = pos;
        }
        return ShortRangeAdmission.itemPath(nodes, true);
    }
}
