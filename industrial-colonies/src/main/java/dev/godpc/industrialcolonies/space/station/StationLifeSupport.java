package dev.godpc.industrialcolonies.space.station;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.plot.PlotChunkHolder;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.Vec3;

/** Exact, same-sublevel Ad Astra oxygen coverage checks for deep space. */
public final class StationLifeSupport {
    public static final ResourceKey<Level> DEEP_SPACE = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("rocketnautics", "deep_space"));
    private static final long MAX_DISTRIBUTOR_AGE_TICKS = 2L;

    private StationLifeSupport() {
    }

    /**
     * Returns true only for an entity tracked by a live Sable sublevel whose
     * exact plot-space eye block is in an actively serviced distributor set.
     */
    public static boolean hasLiveCoverage(LivingEntity entity) {
        if (!DEEP_SPACE.equals(entity.level().dimension())) {
            return false;
        }
        if (!(Sable.HELPER.getTrackingOrVehicleSubLevel(entity) instanceof ServerSubLevel subLevel)
                || subLevel.isRemoved()
                || subLevel.getLevel() != entity.level()) {
            return false;
        }
        StationMetadata metadata = StationMetadata.read(subLevel).orElse(null);
        if (metadata == null
                || !metadata.commissioned()
                || !metadata.hasFreshServices(subLevel.getLevel().getGameTime())
                || !metadata.hasValidIdentity(subLevel.getLevel().getServer())
                || !StationServicesControllerBlockEntity.isLiveFor(subLevel, metadata)) {
            return false;
        }
        Vec3 plotEye = subLevel.logicalPose().transformPositionInverse(entity.getEyePosition());
        return hasLiveCoverage(subLevel, BlockPos.containing(plotEye));
    }

    /** Checks a plot-space block against exact distributors on this sublevel. */
    public static boolean hasLiveCoverage(ServerSubLevel subLevel, BlockPos plotPosition) {
        if (subLevel.isRemoved()) {
            return false;
        }
        long gameTime = subLevel.getLevel().getGameTime();
        for (PlotChunkHolder holder : subLevel.getPlot().getLoadedChunks()) {
            for (BlockEntity blockEntity : holder.getChunk().getBlockEntities().values()) {
                if (!(blockEntity instanceof OxygenDistributorAccess distributor)
                        || Sable.HELPER.getContaining(blockEntity) != subLevel
                        || !distributor.industrialColonies$isLive()) {
                    continue;
                }
                long age = gameTime - distributor.industrialColonies$lastVerifiedTick();
                if (age < 0L || age > MAX_DISTRIBUTOR_AGE_TICKS) {
                    continue;
                }
                Set<BlockPos> covered = distributor.industrialColonies$getDistributedBlocks();
                if (covered != null && covered.contains(plotPosition)) {
                    return true;
                }
            }
        }
        return false;
    }
}
