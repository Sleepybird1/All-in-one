package dev.godpc.industrialcolonies.space;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;

/** Sable bodies may fly above the orbital dimension's block-building ceiling. */
public final class OrbitalChunkAvailability {
    private static final ResourceLocation DEEP_SPACE = ResourceLocation.fromNamespaceAndPath("rocketnautics", "deep_space");
    private OrbitalChunkAvailability() {}

    public static boolean loadedForMaterialization(ServerLevel level, BlockPos position) {
        if (level.dimension().location().equals(DEEP_SPACE) && position.getY() >= level.getMaxBuildHeight()) {
            // Read existing horizontal chunk availability; never load chunks or change the body pose.
            return level.getChunkSource().hasChunk(position.getX() >> 4, position.getZ() >> 4);
        }
        return level.isLoaded(position);
    }
}
