package dev.godpc.industrialcolonies.space;

import com.mojang.logging.LogUtils;
import dev.egg.SubLevelWarper;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.storage.SubLevelRemovalReason;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.joml.Vector3d;
import org.slf4j.Logger;

/**
 * Bounded failure guard around Cosmonautics' non-transactional sublevel copy.
 *
 * <p>The installed implementation allocates and loads the destination ship,
 * teleports entities, and only then removes the source. We validate every
 * loaded block entity before entering it. If an exception occurs while the
 * source still exists, only destination sublevels allocated by this call are
 * removed and the exact authorized player snapshot is restored. If upstream
 * already removed the source, no destructive rollback is attempted and the
 * incident is logged as non-recoverable; callers must suppress success state.
 * The consumed charge is never refunded, preventing retry duplication.</p>
 */
public final class InterstellarWarpTransaction {
    private static final Logger LOGGER = LogUtils.getLogger();

    private InterstellarWarpTransaction() {
    }

    public static int warp(
            ServerSubLevel source,
            net.minecraft.world.level.Level destination,
            Vector3d target,
            InterstellarWarpPolicy.Authorization authorization
    ) {
        if (!(destination instanceof ServerLevel destinationLevel)
                || authorization == null
                || !authorization.structurallyValid()
                || source == null
                || source.isRemoved()
                || source.getUniqueId() == null
                || authorization.identities().size() != 1
                || !source.getUniqueId().equals(
                        authorization.identities().getFirst().subLevelId())
                || !authorization.sourceDimension().equals(source.getLevel().dimension())
                || !expectedDestination(authorization).equals(destinationLevel.dimension())
                || !expectedTarget(authorization).equals(target)) {
            return 0;
        }

        ServerSubLevelContainer sourceContainer = ServerSubLevelContainer.getContainer(
                source.getLevel());
        ServerSubLevelContainer destinationContainer = ServerSubLevelContainer.getContainer(
                destinationLevel);
        if (sourceContainer == null || destinationContainer == null) {
            return 0;
        }

        List<PlayerSnapshot> players = snapshotPlayers(source, authorization);
        if (players.size() != authorization.occupants().size()) {
            return 0;
        }
        try {
            // Force every currently loaded BE through the same serialization
            // boundary the template copier will use, before any allocation or
            // entity movement can occur.
            for (var holder : source.getPlot().getLoadedChunks()) {
                for (BlockEntity blockEntity : holder.getChunk().getBlockEntities().values()) {
                    if (blockEntity.isRemoved()) {
                        return 0;
                    }
                    blockEntity.saveWithFullMetadata(source.getLevel().registryAccess());
                }
            }
            // Validate namespaced metadata copy before entering the upstream
            // method. The Stage 13 allocation hook copies this whole root.
            source.getUserDataTag().copy();
        } catch (RuntimeException | LinkageError error) {
            LOGGER.error("Interstellar warp preflight serialization failed; no copy was attempted", error);
            return 0;
        }

        Set<UUID> destinationBefore = new HashSet<>();
        try {
            for (ServerSubLevel existing : destinationContainer.getAllSubLevels()) {
                destinationBefore.add(existing.getUniqueId());
            }
        } catch (RuntimeException | LinkageError error) {
            LOGGER.error(
                    "Interstellar warp destination snapshot failed; no copy was attempted",
                    error);
            return 0;
        }

        if (!InterstellarWarpRemovalScope.begin(source)) {
            LOGGER.error("Nested interstellar warp removal scope was refused");
            return 0;
        }
        try {
            try {
                return SubLevelWarper.WarpSubLevel(source, destinationLevel, target);
            } catch (RuntimeException | LinkageError error) {
                LOGGER.error(
                        "Interstellar warp copy failed; cleanup safety assessment follows",
                        error);
                boolean sourcePristine = false;
                if (!InterstellarWarpRemovalScope.sourceRemovalStarted(source)) {
                    try {
                        sourcePristine = !source.isRemoved()
                                && sourceContainer.getSubLevel(source.getUniqueId()) == source;
                    } catch (RuntimeException | LinkageError probeFailure) {
                        LOGGER.error(
                                "Interstellar warp source identity could not be verified; "
                                        + "cleanup is unsafe",
                                probeFailure);
                    }
                }
                if (sourcePristine) {
                    LOGGER.error(
                            "Interstellar warp source remains intact; best-effort destination "
                                    + "cleanup and crew restoration follow");
                    List<Throwable> cleanupFailures = new ArrayList<>();
                    rollbackNewDestinations(
                            destinationContainer, destinationBefore, cleanupFailures);
                    restorePlayers(players, cleanupFailures);
                    for (Throwable cleanupFailure : cleanupFailures) {
                        LOGGER.error(
                                "Interstellar warp cleanup encountered an additional failure",
                                cleanupFailure);
                    }
                } else {
                    // The HEAD marker fires before Sable deletes entities,
                    // not after its late removed/map flags. Once marked, the
                    // destination is the only potentially complete copy and
                    // must never be deleted automatically.
                    LOGGER.error(
                            "Interstellar warp destination rollback and crew restoration are "
                                    + "unsafe because destructive source removal began or source "
                                    + "identity could not be proven; success authority remains "
                                    + "suppressed");
                }
                return 0;
            }
        } finally {
            InterstellarWarpRemovalScope.clear(source);
        }
    }

    private static List<PlayerSnapshot> snapshotPlayers(
            ServerSubLevel source,
            InterstellarWarpPolicy.Authorization authorization
    ) {
        List<PlayerSnapshot> snapshots = new ArrayList<>();
        for (UUID id : authorization.occupants()) {
            ServerPlayer player = source.getLevel().getServer().getPlayerList().getPlayer(id);
            if (player == null
                    || player.level() != source.getLevel()
                    || player.isPassenger()
                    || player.isVehicle()) {
                return List.of();
            }
            snapshots.add(new PlayerSnapshot(
                    player,
                    source.getLevel(),
                    player.getX(),
                    player.getY(),
                    player.getZ(),
                    player.getYRot(),
                    player.getXRot()));
        }
        return List.copyOf(snapshots);
    }

    private static void rollbackNewDestinations(
            ServerSubLevelContainer destination,
            Set<UUID> existingIds,
            List<Throwable> cleanupFailures
    ) {
        List<ServerSubLevel> candidates;
        try {
            candidates = new ArrayList<>(destination.getAllSubLevels());
        } catch (RuntimeException | LinkageError failure) {
            cleanupFailures.add(failure);
            return;
        }
        for (ServerSubLevel candidate : candidates) {
            try {
                if (!existingIds.contains(candidate.getUniqueId())) {
                    destination.removeSubLevel(candidate, SubLevelRemovalReason.REMOVED);
                }
            } catch (RuntimeException | LinkageError failure) {
                // One broken removal callback must not prevent cleanup of the
                // remaining allocations or restoration of every crew member.
                cleanupFailures.add(failure);
            }
        }
    }

    private static void restorePlayers(
            List<PlayerSnapshot> snapshots,
            List<Throwable> cleanupFailures
    ) {
        for (PlayerSnapshot snapshot : snapshots) {
            try {
                if (snapshot.player().isRemoved()) {
                    LOGGER.error(
                            "Could not restore removed authorized crew member {} after failed "
                                    + "interstellar copy",
                            snapshot.player().getUUID());
                    continue;
                }
                boolean restored = snapshot.player().teleportTo(
                        snapshot.level(),
                        snapshot.x(),
                        snapshot.y(),
                        snapshot.z(),
                        Set.of(),
                        snapshot.yRot(),
                        snapshot.xRot());
                if (!restored) {
                    LOGGER.error(
                            "Could not restore authorized crew member {} after failed "
                                    + "interstellar copy",
                            snapshot.player().getUUID());
                }
            } catch (RuntimeException | LinkageError failure) {
                // Restoration is deliberately per-player so one corrupt
                // entity cannot strand every later crew snapshot.
                cleanupFailures.add(failure);
            }
        }
    }

    private static net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level>
            expectedDestination(InterstellarWarpPolicy.Authorization authorization) {
        return authorization.inboundToGlacio()
                ? SignedInterstellarRoute.GLACIO_DIMENSION
                : SignedInterstellarRoute.SOL_DIMENSION;
    }

    private static Vector3d expectedTarget(InterstellarWarpPolicy.Authorization authorization) {
        net.minecraft.core.BlockPos pos = authorization.inboundToGlacio()
                ? SignedInterstellarRoute.GLACIO_POINT_POS
                : SignedInterstellarRoute.SOL_POINT_POS;
        return new Vector3d(pos.getX() + 0.5D, pos.getY() + 0.5D, pos.getZ() + 0.5D);
    }

    private record PlayerSnapshot(
            ServerPlayer player,
            ServerLevel level,
            double x,
            double y,
            double z,
            float yRot,
            float xRot
    ) {
    }
}
