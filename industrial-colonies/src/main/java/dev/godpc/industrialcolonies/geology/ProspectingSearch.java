package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.*;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

/** Saved-index queries only. No terrain generation, ore placement, coordinate output or player movement. */
public final class ProspectingSearch {
    private record Cache(long refreshed, CompletableFuture<SavedProspectingIndex> future) {}
    private static final Map<ServerLevel, Cache> CACHES = new WeakHashMap<>();
    private static final Map<ServerPlayer, Long> REQUESTS = new WeakHashMap<>();
    private ProspectingSearch() {}

    public static void cancel(ServerPlayer player) {
        REQUESTS.put(player, REQUESTS.getOrDefault(player, 0L) + 1);
    }

    public static void request(ServerPlayer player, String family) {
        cancel(player);
        long request = REQUESTS.get(player);
        ServerLevel level = player.serverLevel();
        var binding = NativeContinentLevels.find(level).orElse(null);
        if (binding == null || !NativeAccurateTerrain.enabled()) {
            player.displayClientMessage(Component.literal("No saved prospecting survey is available here."), true);
            return;
        }
        var descriptor = binding.recordedLookup();
        var cached = CACHES.get(level);
        long tick = level.getGameTime();
        if (cached == null || cached.future().isDone() && tick - cached.refreshed() >= 200) {
            var future = CompletableFuture.supplyAsync(() -> {
                try { return SavedProspectingIndex.read(descriptor); }
                catch (Exception error) { throw new CompletionException(error); }
            }, net.minecraft.Util.ioPool());
            cached = new Cache(tick, future);
            CACHES.put(level, cached);
        }
        // Native identity noise only; do not invoke the processed terrain/biome survey.
        var geography = ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState());
        if (!cached.future().isDone())
            player.displayClientMessage(Component.literal("Reading saved survey…"), true);
        cached.future().whenComplete((index, error) -> level.getServer().execute(() -> {
            if (player.isRemoved() || player.serverLevel() != level
                    || level.getServer().getPlayerList().getPlayer(player.getUUID()) != player
                    || REQUESTS.getOrDefault(player, 0L) != request) return;
            if (error != null) {
                player.displayClientMessage(Component.literal("Saved survey unavailable; no result confirmed."), true);
                return;
            }
            try {
                int x = player.blockPosition().getX(), z = player.blockPosition().getZ();
                var continent = geography.continent(x, z);
                var answer = index.nearest(family, x, z, continent);
                var site = answer.site();
                if (site.isEmpty()) {
                    var fallback = AutomaticVeinSurvey.nearest(level, family, x, z, 131072);
                    if (fallback.isPresent()) {
                        var point = fallback.get();
                        show(player, family, x, z, point.x(), point.z(),
                                geography.continent(point.x(), point.z()).equals(continent), false);
                    } else player.displayClientMessage(Component.literal(answer.explicitlyAbsent()
                            ? "Not recorded on this continent. No other lead known."
                            : "Not yet known from the saved survey."), true);
                    return;
                }
                var point = site.get();
                show(player, family, x, z, point.x(), point.z(), answer.currentContinent(), answer.explicitlyAbsent());
            } catch (RuntimeException unavailable) {
                player.displayClientMessage(Component.literal("Continent information is not available yet."), true);
            }
        }));
    }

    private static void show(ServerPlayer player, String family, int x, int z, int targetX, int targetZ,
            boolean local, boolean explicitAbsence) {
        long dx = (long) targetX - x, dz = (long) targetZ - z;
        String direction = ProspectingBearing.roughDirection(player.serverLevel().getSeed(), family, x, z, dx, dz);
        String prefix = local ? "On this continent: " : explicitAbsence
                ? "Another continent: " : "Nearest known lead is on another continent: ";
        player.displayClientMessage(Component.literal(prefix)
                .append(Component.translatable("direction.industrial_colonies." + direction)), true);
    }
}
