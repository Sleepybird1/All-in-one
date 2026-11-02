package dev.godpc.industrialcolonies;

import com.minecolonies.api.colony.IColony;
import com.minecolonies.api.colony.IColonyManager;
import dev.ftb.mods.ftbteams.api.FTBTeamsAPI;
import dev.ftb.mods.ftbteams.api.Team;
import dev.ftb.mods.ftbteams.api.TeamStagesHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Mirrors completed Industrial Colonies University research onto the native
 * stage set of the colony owner's FTB team.
 *
 * <p>Each stage is the exact MineColonies research id, for example
 * {@code industrial_colonies:nuclear_engineering/cr01_uranium_processing}.
 * Stages are additive because completed University research is persistent and
 * irreversible during normal play. The bridge never toggles recipes globally;
 * runtime machine hooks can resolve their owning team and test these keys.</p>
 */
public final class ResearchStageSynchronizer {
    private static final int SYNC_INTERVAL_TICKS = 200;
    private static long lastSyncTick = Long.MIN_VALUE;

    private ResearchStageSynchronizer() {
    }

    public static void register() {
        NeoForge.EVENT_BUS.addListener(ResearchStageSynchronizer::onServerTick);
    }

    public static boolean hasStage(ServerPlayer player, ResourceLocation researchId) {
        return TeamStagesHelper.hasTeamStage(player, researchId.toString());
    }

    private static void onServerTick(ServerTickEvent.Post event) {
        long tick = event.getServer().getTickCount();
        if (lastSyncTick != Long.MIN_VALUE
                && tick >= lastSyncTick
                && tick - lastSyncTick < SYNC_INTERVAL_TICKS) {
            return;
        }
        lastSyncTick = tick;

        FTBTeamsAPI.API api = FTBTeamsAPI.api();
        if (!api.isManagerLoaded()) {
            return;
        }

        for (IColony colony : IColonyManager.getInstance().getAllColonies()) {
            UUID owner = colony.getPermissions().getOwner();
            if (owner == null) {
                continue;
            }

            Set<String> completedStages = new LinkedHashSet<>();
            for (ResourceLocation completed : colony.getResearchManager().getResearchTree().getCompletedList()) {
                if (IndustrialColonies.MOD_ID.equals(completed.getNamespace())) {
                    completedStages.add(completed.toString());
                }
            }
            if (completedStages.isEmpty()) {
                continue;
            }

            api.getManager().getTeamForPlayerID(owner).ifPresent(team -> syncStages(team, completedStages));
        }
    }

    private static void syncStages(Team team, Set<String> completedStages) {
        TeamStagesHelper.addTeamStages(team, completedStages);
    }
}
