package dev.godpc.industrialcolonies.space.station;

import dev.ftb.mods.ftbteams.api.FTBTeamsAPI;
import dev.ftb.mods.ftbteams.api.Team;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.util.Optional;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

/**
 * Durable, versioned station identity stored inside Sable's user-data root.
 *
 * <p>The controller coordinate is relative to the plot center. It therefore
 * survives a Sable plot reallocation without granting a different block the
 * controller identity. Writes always preserve unrelated root keys.</p>
 */
public record StationMetadata(
        StationRole role,
        boolean commissioned,
        UUID owner,
        UUID team,
        BlockPos controller,
        long commissionedAt,
        long servicesHeartbeat,
        long lifeSupportHeartbeat
) {
    public static final String ROOT_KEY = "industrial_colonies:station";
    public static final int SCHEMA = 1;
    public static final long HEARTBEAT_FRESHNESS_TICKS = 40L;

    private static final String SCHEMA_KEY = "schema";
    private static final String ROLE_KEY = "role";
    private static final String COMMISSIONED_KEY = "commissioned";
    private static final String OWNER_KEY = "owner";
    private static final String TEAM_KEY = "team";
    private static final String CONTROLLER_KEY = "controller";
    private static final String COMMISSIONED_AT_KEY = "commissioned_at";
    private static final String SERVICES_HEARTBEAT_KEY = "services_heartbeat";
    private static final String LIFE_SUPPORT_HEARTBEAT_KEY = "life_support_heartbeat";

    public StationMetadata {
        if (role == null || owner == null || team == null || controller == null) {
            throw new IllegalArgumentException("Station metadata identity fields cannot be null");
        }
    }

    public static Optional<StationMetadata> read(ServerSubLevel subLevel) {
        CompoundTag root = subLevel.getUserDataTag();
        if (root == null || !root.contains(ROOT_KEY, Tag.TAG_COMPOUND)) {
            return Optional.empty();
        }
        CompoundTag station = root.getCompound(ROOT_KEY);
        if (!station.contains(SCHEMA_KEY, Tag.TAG_INT)
                || station.getInt(SCHEMA_KEY) != SCHEMA
                || !station.contains(ROLE_KEY, Tag.TAG_STRING)
                || !station.contains(COMMISSIONED_KEY, Tag.TAG_BYTE)
                || !station.hasUUID(OWNER_KEY)
                || !station.hasUUID(TEAM_KEY)
                || !station.contains(CONTROLLER_KEY, Tag.TAG_LONG)
                || !station.contains(COMMISSIONED_AT_KEY, Tag.TAG_LONG)
                || !station.contains(SERVICES_HEARTBEAT_KEY, Tag.TAG_LONG)
                || !station.contains(LIFE_SUPPORT_HEARTBEAT_KEY, Tag.TAG_LONG)) {
            return Optional.empty();
        }
        Optional<StationRole> role = StationRole.parse(station.getString(ROLE_KEY));
        if (role.isEmpty()) {
            return Optional.empty();
        }
        try {
            StationMetadata metadata = new StationMetadata(
                    role.get(),
                    station.getBoolean(COMMISSIONED_KEY),
                    station.getUUID(OWNER_KEY),
                    station.getUUID(TEAM_KEY),
                    BlockPos.of(station.getLong(CONTROLLER_KEY)),
                    station.getLong(COMMISSIONED_AT_KEY),
                    station.getLong(SERVICES_HEARTBEAT_KEY),
                    station.getLong(LIFE_SUPPORT_HEARTBEAT_KEY));
            if (metadata.owner.equals(new UUID(0L, 0L))
                    || metadata.team.equals(new UUID(0L, 0L))
                    || metadata.commissionedAt < 0L
                    || metadata.servicesHeartbeat < 0L
                    || metadata.lifeSupportHeartbeat < 0L
                    || (metadata.commissioned
                            && (metadata.commissionedAt == 0L
                                    || metadata.servicesHeartbeat == 0L
                                    || metadata.lifeSupportHeartbeat == 0L))
                    || (!metadata.commissioned
                            && (metadata.commissionedAt != 0L
                                    || metadata.servicesHeartbeat != 0L
                                    || metadata.lifeSupportHeartbeat != 0L))) {
                return Optional.empty();
            }
            return Optional.of(metadata);
        } catch (RuntimeException ignored) {
            return Optional.empty();
        }
    }

    /** Whether our namespaced root exists in any form, including malformed data. */
    public static boolean hasRoot(ServerSubLevel subLevel) {
        CompoundTag root = subLevel.getUserDataTag();
        return root != null && root.contains(ROOT_KEY);
    }

    public void write(ServerSubLevel subLevel) {
        CompoundTag existing = subLevel.getUserDataTag();
        CompoundTag root = existing == null ? new CompoundTag() : existing.copy();
        CompoundTag station = new CompoundTag();
        station.putInt(SCHEMA_KEY, SCHEMA);
        station.putString(ROLE_KEY, role.name());
        station.putBoolean(COMMISSIONED_KEY, commissioned);
        station.putUUID(OWNER_KEY, owner);
        station.putUUID(TEAM_KEY, team);
        station.putLong(CONTROLLER_KEY, controller.asLong());
        station.putLong(COMMISSIONED_AT_KEY, commissionedAt);
        station.putLong(SERVICES_HEARTBEAT_KEY, servicesHeartbeat);
        station.putLong(LIFE_SUPPORT_HEARTBEAT_KEY, lifeSupportHeartbeat);
        root.put(ROOT_KEY, station);
        subLevel.setUserDataTag(root);
    }

    public static Optional<StationMetadata> begin(
            ServerSubLevel subLevel,
            ServerPlayer player,
            BlockPos controllerPosition
    ) {
        FTBTeamsAPI.API api = FTBTeamsAPI.api();
        if (!api.isManagerLoaded()) {
            return Optional.empty();
        }
        Optional<Team> team = api.getManager().getTeamForPlayer(player);
        if (team.isEmpty() || !team.get().isValid()) {
            return Optional.empty();
        }
        StationMetadata metadata = new StationMetadata(
                StationRole.STATION,
                false,
                player.getUUID(),
                team.get().getTeamId(),
                relativePosition(subLevel, controllerPosition),
                0L,
                0L,
                0L);
        metadata.write(subLevel);
        return Optional.of(metadata);
    }

    public boolean isAuthorized(ServerPlayer player) {
        FTBTeamsAPI.API api = FTBTeamsAPI.api();
        if (!api.isManagerLoaded()) {
            return false;
        }
        return api.getManager().getTeamForPlayer(player)
                .filter(current -> current.isValid() && team.equals(current.getTeamId()))
                .filter(current -> owner.equals(player.getUUID()) || current.getMembers().contains(player.getUUID()))
                .isPresent();
    }

    public boolean hasValidIdentity(MinecraftServer server) {
        FTBTeamsAPI.API api = FTBTeamsAPI.api();
        if (!api.isManagerLoaded() || api.getManager().getServer() != server) {
            return false;
        }
        return api.getManager().getTeamForPlayerID(owner)
                .filter(current -> current.isValid() && team.equals(current.getTeamId()))
                .isPresent();
    }

    public boolean matchesController(ServerSubLevel subLevel, BlockPos position) {
        return controller.equals(relativePosition(subLevel, position));
    }

    public boolean hasFreshServices(long gameTime) {
        return isFresh(gameTime, servicesHeartbeat) && isFresh(gameTime, lifeSupportHeartbeat);
    }

    public StationMetadata asShip() {
        return new StationMetadata(
                StationRole.SHIP, false, owner, team, controller, 0L, 0L, 0L);
    }

    public StationMetadata decommissioned() {
        return new StationMetadata(
                role, false, owner, team, controller, 0L, 0L, 0L);
    }

    public StationMetadata commissioned(long gameTime) {
        return new StationMetadata(
                role,
                true,
                owner,
                team,
                controller,
                gameTime,
                gameTime,
                gameTime);
    }

    public StationMetadata heartbeat(long gameTime) {
        return new StationMetadata(
                role,
                commissioned,
                owner,
                team,
                controller,
                commissionedAt,
                gameTime,
                gameTime);
    }

    private static boolean isFresh(long gameTime, long heartbeat) {
        long age = gameTime - heartbeat;
        return heartbeat > 0L && age >= 0L && age <= HEARTBEAT_FRESHNESS_TICKS;
    }

    private static BlockPos relativePosition(ServerSubLevel subLevel, BlockPos position) {
        return position.subtract(subLevel.getPlot().getCenterBlock());
    }
}
