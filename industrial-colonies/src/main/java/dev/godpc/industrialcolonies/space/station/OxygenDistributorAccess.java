package dev.godpc.industrialcolonies.space.station;

import java.util.Set;
import net.minecraft.core.BlockPos;

/** Runtime bridge implemented only by the exact installed Ad Astra distributor. */
public interface OxygenDistributorAccess {
    /** Ad Astra supplies this public method through MachineBlockEntity. */
    boolean isLit();

    /** Ad Astra supplies this public method through ContainerMachineBlockEntity. */
    boolean canFunction();

    Set<BlockPos> industrialColonies$getDistributedBlocks();

    boolean industrialColonies$isLive();

    long industrialColonies$lastVerifiedTick();
}
