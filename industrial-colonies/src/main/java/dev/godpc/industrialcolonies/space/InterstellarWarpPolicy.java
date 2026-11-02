package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.station.StationMetadata;
import dev.godpc.industrialcolonies.space.station.StationRole;
import dev.godpc.industrialcolonies.space.station.StationServicesControllerBlockEntity;
import dev.ryanhcode.sable.api.SubLevelHelper;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.companion.SableCompanion;
import dev.ryanhcode.sable.companion.SubLevelAccess;
import dev.ryanhcode.sable.companion.math.BoundingBox3d;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.SubLevel;
import dev.ryanhcode.sable.sublevel.plot.LevelPlot;
import dev.ryanhcode.sable.sublevel.plot.PlotChunkHolder;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.AABB;

/** Fail-closed begin-time and execute-time authority for the final Glacio route. */
public final class InterstellarWarpPolicy {
    public static final int AUTHORIZATION_SCHEMA = 1;
    public static final int MAX_PERSISTED_OCCUPANTS = 256;
    public static final String AUTHORIZATION_NBT = "IndustrialColoniesInterstellarWarp";
    public static final ResourceLocation WARP_CHARGE = ResourceLocation.fromNamespaceAndPath(
            "industrial_colonies", "interstellar_warp_charge");
    private static final TagKey<Item> FREEZE_RESISTANT_ARMOR = TagKey.create(
            Registries.ITEM,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "freeze_resistant_armor"));
    private static final List<EquipmentSlot> ARMOR_SLOTS = List.of(
            EquipmentSlot.HEAD,
            EquipmentSlot.CHEST,
            EquipmentSlot.LEGS,
            EquipmentSlot.FEET);

    private InterstellarWarpPolicy() {
    }

    /**
     * Captures immutable expectations before Cosmowarp extracts power or starts
     * its charge timer. Nothing is consumed by this method.
     */
    public static Optional<PendingAuthorization> authorizeStart(
            WarpDriveBlockEntity drive,
            ServerPlayer initiator
    ) {
        if (initiator == null) {
            return Optional.empty();
        }
        Optional<SignedInterstellarRoute.Route> route = SignedInterstellarRoute.resolve(drive);
        Optional<VesselState> state = inspectVessel(drive, route.orElse(null));
        if (route.isEmpty()
                || state.isEmpty()
                || state.get().occupants().stream().noneMatch(
                        player -> player == initiator
                                && player.getUUID().equals(initiator.getUUID()))) {
            return Optional.empty();
        }
        Optional<ChargeLocation> charge = findCharge(state.get().occupants());
        if (charge.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(new PendingAuthorization(
                route.get(),
                state.get().occupantIds(),
                state.get().identities(),
                charge.get()));
    }

    /**
     * Allows pre-charge route edits only to the exact authorized onboard
     * sender. All mutation packets are denied while a charge is active.
     */
    public static boolean mayMutateRoute(
            WarpDriveBlockEntity drive,
            ServerPlayer initiator
    ) {
        if (!mayUseWarpDriveMenu(drive, initiator)) {
            return false;
        }
        Optional<SignedInterstellarRoute.Route> route = SignedInterstellarRoute.resolve(drive);
        Optional<VesselState> state = inspectVessel(drive, route.orElse(null));
        return route.isPresent()
                && state.isPresent()
                && state.get().occupants().stream().anyMatch(
                        player -> player == initiator
                                && player.getUUID().equals(initiator.getUUID()));
    }

    /**
     * Keeps the menu physically aboard the commissioned ship and closes it as
     * soon as the drive begins charging or the sender loses live authority.
     */
    public static boolean mayUseWarpDriveMenu(
            WarpDriveBlockEntity drive,
            ServerPlayer initiator
    ) {
        if (drive == null || initiator == null || drive.isCharging()) {
            return false;
        }
        return isLiveShipOperator(drive, initiator);
    }

    /**
     * Route-independent menu authority. This deliberately does not require a
     * crystal, destination clearance, Glacio suit, warp charge, empty cargo
     * AABB, or rollback-safe entity shape; those remain START/execute checks.
     */
    private static boolean isLiveShipOperator(
            WarpDriveBlockEntity drive,
            ServerPlayer initiator
    ) {
        if (!(drive.getLevel() instanceof ServerLevel level)
                || drive.isRemoved()
                || level.getBlockEntity(drive.getBlockPos()) != drive) {
            return false;
        }
        ServerSubLevel ship = findShip(drive).orElse(null);
        if (ship == null || ship.isRemoved()) {
            return false;
        }
        StationMetadata metadata = StationMetadata.read(ship).orElse(null);
        if (metadata == null
                || metadata.role() != StationRole.SHIP
                || !metadata.commissioned()
                || metadata.commissionedAt() <= 0L
                || !metadata.hasValidIdentity(level.getServer())
                || !metadata.isAuthorized(initiator)
                || !StationServicesControllerBlockEntity.isLiveFor(ship, metadata)) {
            return false;
        }
        SubLevelAccess access = SableCompanion.INSTANCE.getTrackingOrVehicleSubLevel(initiator);
        if (!(access instanceof ServerSubLevel occupied) || occupied != ship) {
            return false;
        }
        if (level.getEntities(null, stockCandidateBox(ship)).stream()
                .noneMatch(entity -> entity == initiator)) {
            return false;
        }

        boolean hasInterstellarComputer = false;
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof InterstellarNavigationComputerBlockEntity computer
                    && !computer.isRemoved()) {
                hasInterstellarComputer = true;
                break;
            }
        }
        if (!hasInterstellarComputer) {
            return false;
        }
        int warpDrives = 0;
        boolean containsThisDrive = false;
        for (PlotChunkHolder holder : ship.getPlot().getLoadedChunks()) {
            for (BlockEntity blockEntity : holder.getChunk().getBlockEntities().values()) {
                if (blockEntity instanceof WarpDriveBlockEntity found) {
                    warpDrives++;
                    containsThisDrive |= found == drive;
                }
            }
        }
        return warpDrives == 1 && containsThisDrive;
    }

    /** Consumes one charge only after stock beginWarp has returned SUCCESS. */
    public static Optional<Authorization> consumeAfterSuccessfulBegin(PendingAuthorization pending) {
        if (!pending.charge().consumeExactlyOne()) {
            return Optional.empty();
        }
        return Optional.of(new Authorization(
                AUTHORIZATION_SCHEMA,
                SignedInterstellarRoute.SIGNATURE,
                pending.route().source().dimension(),
                pending.route().target().id(),
                pending.route().inboundToGlacio(),
                pending.occupants(),
                pending.identities(),
                true));
    }

    /**
     * Revalidates every mutable input immediately before Cosmowarp copies the
     * connected sublevel chain. The current crystal is compared with the
     * persisted begin-time expectation; it never supplies new authority.
     */
    public static boolean authorizeExecute(
            WarpDriveBlockEntity drive,
            Authorization expected,
            UUID stockChargingTarget
    ) {
        if (expected == null || !expected.structurallyValid()) {
            return false;
        }
        // Cosmowarp persists this independently of the mutable crystal. Both
        // values must still name the begin-time target or a crystal/target
        // swap during the charge window could redirect the stock execution.
        if (!expected.targetPoint().equals(stockChargingTarget)) {
            return false;
        }
        Optional<SignedInterstellarRoute.Route> currentRoute = SignedInterstellarRoute.resolve(drive);
        if (currentRoute.isEmpty()) {
            return false;
        }
        SignedInterstellarRoute.Route route = currentRoute.get();
        if (!expected.sourceDimension().equals(route.source().dimension())
                || !expected.targetPoint().equals(route.target().id())
                || expected.inboundToGlacio() != route.inboundToGlacio()) {
            return false;
        }
        Optional<VesselState> current = inspectVessel(drive, route);
        return current.isPresent()
                && expected.occupants().equals(current.get().occupantIds())
                && expected.identities().equals(current.get().identities());
    }

    private static Optional<VesselState> inspectVessel(
            WarpDriveBlockEntity drive,
            SignedInterstellarRoute.Route route
    ) {
        if (!(drive.getLevel() instanceof ServerLevel level)
                || drive.isRemoved()
                || level.getBlockEntity(drive.getBlockPos()) != drive) {
            return Optional.empty();
        }
        ServerSubLevel origin = findShip(drive).orElse(null);
        if (origin == null || origin.isRemoved()) {
            return Optional.empty();
        }

        List<ServerSubLevel> chain = new ArrayList<>();
        for (SubLevel member : SubLevelHelper.getConnectedChain(origin)) {
            if (!(member instanceof ServerSubLevel ship) || ship.isRemoved()) {
                return Optional.empty();
            }
            chain.add(ship);
        }
        if (chain.isEmpty()) {
            return Optional.empty();
        }
        // Cosmowarp 1.0.1 builds every connected member's entity candidate
        // box around the primary center. Until that offset behavior is fixed
        // upstream, multi-sublevel warps could leave legitimate passengers
        // behind. A single loaded sublevel is the only proven-safe shape.
        if (chain.size() != 1) {
            return Optional.empty();
        }
        // The signed route uses fixed endpoints. Translate the vessel's exact
        // current physical bounds by the same center delta as stock
        // SubLevelWarper and reject every destination-sublevel intersection.
        // inspectVessel is called at both begin and execute, so another ship
        // arriving during the charge window also aborts the warp.
        if (route != null && !destinationIsClear(origin, route, level)) {
            return Optional.empty();
        }

        int warpDrives = 0;
        boolean containsThisDrive = false;
        boolean hasInterstellarComputer = false;
        List<VesselIdentity> identities = new ArrayList<>();
        Map<ServerSubLevel, StationMetadata> metadataByShip = new HashMap<>();
        UUID commonOwner = null;
        UUID commonTeam = null;
        for (ServerSubLevel ship : chain) {
            // Stock disassembles every kinematic contraption only after this
            // authorization point. A contraption could otherwise materialize
            // a hidden second drive or restricted block entity between the
            // exact hardware count and template serialization.
            if (!ship.getPlot().getContraptions().isEmpty()) {
                return Optional.empty();
            }
            StationMetadata metadata = StationMetadata.read(ship).orElse(null);
            if (metadata == null
                    || metadata.role() != StationRole.SHIP
                    || !metadata.commissioned()
                    || metadata.commissionedAt() <= 0L
                    || !metadata.hasValidIdentity(level.getServer())
                    // The persisted heartbeat is only evidence. The canonical
                    // live check also requires the exact loaded controller,
                    // a service tick no more than one tick old, current FE and
                    // coolant, and current same-sublevel oxygen coverage.
                    || !StationServicesControllerBlockEntity.isLiveFor(ship, metadata)) {
                return Optional.empty();
            }
            if (commonOwner == null) {
                commonOwner = metadata.owner();
                commonTeam = metadata.team();
            } else if (!commonOwner.equals(metadata.owner()) || !commonTeam.equals(metadata.team())) {
                return Optional.empty();
            }
            metadataByShip.put(ship, metadata);
            identities.add(VesselIdentity.from(ship, metadata));

            for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
                if (actor instanceof InterstellarNavigationComputerBlockEntity computer
                        && !computer.isRemoved()) {
                    hasInterstellarComputer = true;
                }
            }
            for (PlotChunkHolder holder : ship.getPlot().getLoadedChunks()) {
                for (BlockEntity blockEntity : holder.getChunk().getBlockEntities().values()) {
                    if (blockEntity instanceof WarpDriveBlockEntity found) {
                        warpDrives++;
                        containsThisDrive |= found == drive;
                    }
                }
            }
        }
        if (!hasInterstellarComputer || warpDrives != 1 || !containsThisDrive) {
            return Optional.empty();
        }

        List<ServerPlayer> occupants = new ArrayList<>();
        for (ServerPlayer player : level.players()) {
            SubLevelAccess access = SableCompanion.INSTANCE.getTrackingOrVehicleSubLevel(player);
            if (!(access instanceof ServerSubLevel occupied) || !metadataByShip.containsKey(occupied)) {
                continue;
            }
            StationMetadata metadata = metadataByShip.get(occupied);
            if (!metadata.isAuthorized(player)
                    // Cosmowarp unmounts passengers during transfer. Until a
                    // transactional vehicle graph restore exists, passenger
                    // or carrier state is not an authorized crew shape.
                    || player.isPassenger()
                    || player.isVehicle()
                    || route != null && route.inboundToGlacio()
                            && !hasFullFreezeResistantSuit(player)) {
                return Optional.empty();
            }
            occupants.add(player);
        }
        if (occupants.isEmpty()) {
            return Optional.empty();
        }
        // SubLevelWarper selects entities by physical AABB rather than by
        // Sable association. The two exact player sets must agree, otherwise
        // an uninspected bystander could be moved or an authorized crew member
        // could be left behind.
        AABB candidateBox = stockCandidateBox(origin);
        List<Entity> physicalEntities = level.getEntities(null, candidateBox);
        // Upstream teleports every entity in this box before removing the
        // source ship. Our bounded rollback can restore players but cannot
        // atomically reconstruct arbitrary mount/cargo/entity graphs after a
        // mid-copy failure. Therefore the proven-safe warp shape contains
        // authorized, unmounted crew and no other entity at both begin and
        // execute revalidation.
        if (physicalEntities.stream().anyMatch(entity -> !(entity instanceof ServerPlayer))) {
            return Optional.empty();
        }
        List<ServerPlayer> physicalCandidates = physicalEntities.stream()
                .filter(ServerPlayer.class::isInstance)
                .map(entity -> (ServerPlayer) entity)
                .sorted(Comparator.comparing(player -> player.getUUID().toString()))
                .toList();
        occupants.sort(Comparator.comparing(player -> player.getUUID().toString()));
        if (!occupants.stream().map(ServerPlayer::getUUID).toList().equals(
                physicalCandidates.stream().map(ServerPlayer::getUUID).toList())) {
            return Optional.empty();
        }
        identities.sort(Comparator.comparing(VesselIdentity::canonical));
        return Optional.of(new VesselState(
                List.copyOf(occupants),
                occupants.stream().map(ServerPlayer::getUUID).toList(),
                List.copyOf(identities)));
    }

    /**
     * Byte-for-byte geometry equivalent to Cosmowarp 1.0.1's
     * {@code SubLevelWarper.WarpSubLevels} player/entity sweep. The stock code
     * uses the primary logical-pose position as the center and the Sable
     * bounding-box dimensions as half extents (its ignored inflate call does
     * not change the immutable AABB).
     */
    private static AABB stockCandidateBox(ServerSubLevel origin) {
        var bounds = origin.boundingBox();
        var center = origin.logicalPose().position();
        double halfWidth = bounds.width() / 2.0D;
        double halfHeight = bounds.height() / 2.0D;
        double halfLength = bounds.length() / 2.0D;
        return new AABB(
                center.x() - halfWidth,
                center.y() - halfHeight,
                center.z() - halfLength,
                center.x() + halfWidth,
                center.y() + halfHeight,
                center.z() + halfLength);
    }

    private static boolean destinationIsClear(
            ServerSubLevel origin,
            SignedInterstellarRoute.Route route,
            ServerLevel sourceLevel
    ) {
        ServerLevel destinationLevel = sourceLevel.getServer().getLevel(
                route.target().dimension());
        if (destinationLevel == null) {
            return false;
        }
        ServerSubLevelContainer destinationContainer = ServerSubLevelContainer.getContainer(
                destinationLevel);
        if (destinationContainer == null) {
            return false;
        }

        BlockPos target = route.target().pos();
        var sourceCenter = origin.logicalPose().position();
        BoundingBox3d translatedBounds = origin.boundingBox().move(
                target.getX() + 0.5D - sourceCenter.x(),
                target.getY() + 0.5D - sourceCenter.y(),
                target.getZ() + 0.5D - sourceCenter.z(),
                new BoundingBox3d());
        return !destinationContainer.queryIntersecting(translatedBounds).iterator().hasNext();
    }

    private static Optional<ServerSubLevel> findShip(WarpDriveBlockEntity drive) {
        if (!(drive.getLevel() instanceof ServerLevel level)) {
            return Optional.empty();
        }
        ServerSubLevelContainer container = ServerSubLevelContainer.getContainer(level);
        if (container == null) {
            return Optional.empty();
        }
        LevelPlot plot = container.getPlot(new ChunkPos(drive.getBlockPos()));
        if (plot == null || !(plot.getSubLevel() instanceof ServerSubLevel ship)) {
            return Optional.empty();
        }
        return Optional.of(ship);
    }

    private static boolean hasFullFreezeResistantSuit(ServerPlayer player) {
        for (EquipmentSlot slot : ARMOR_SLOTS) {
            ItemStack stack = player.getItemBySlot(slot);
            if (!stack.is(FREEZE_RESISTANT_ARMOR) || !stack.canEquip(slot, player)) {
                return false;
            }
        }
        return true;
    }

    private static Optional<ChargeLocation> findCharge(List<ServerPlayer> occupants) {
        for (ServerPlayer player : occupants) {
            for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
                ItemStack stack = player.getInventory().getItem(slot);
                if (!stack.isEmpty() && WARP_CHARGE.equals(BuiltInRegistries.ITEM.getKey(stack.getItem()))) {
                    return Optional.of(new ChargeLocation(player, slot));
                }
            }
        }
        return Optional.empty();
    }

    public record PendingAuthorization(
            SignedInterstellarRoute.Route route,
            List<UUID> occupants,
            List<VesselIdentity> identities,
            ChargeLocation charge
    ) {
    }

    public record ChargeLocation(ServerPlayer player, int slot) {
        boolean consumeExactlyOne() {
            if (slot < 0 || slot >= player.getInventory().getContainerSize()) {
                return false;
            }
            ItemStack stack = player.getInventory().getItem(slot);
            if (stack.isEmpty()
                    || !WARP_CHARGE.equals(BuiltInRegistries.ITEM.getKey(stack.getItem()))) {
                return false;
            }
            stack.shrink(1);
            player.getInventory().setChanged();
            return true;
        }
    }

    private record VesselState(
            List<ServerPlayer> occupants,
            List<UUID> occupantIds,
            List<VesselIdentity> identities
    ) {
    }

    public record VesselIdentity(
            UUID subLevelId,
            UUID owner,
            UUID team,
            BlockPos controller,
            long commissionedAt
    ) {
        static VesselIdentity from(ServerSubLevel ship, StationMetadata metadata) {
            return new VesselIdentity(
                    ship.getUniqueId(),
                    metadata.owner(),
                    metadata.team(),
                    metadata.controller(),
                    metadata.commissionedAt());
        }

        String canonical() {
            return subLevelId + "/" + owner + "/" + team + "/"
                    + controller.asLong() + "/" + commissionedAt;
        }

        CompoundTag toTag() {
            CompoundTag tag = new CompoundTag();
            tag.putUUID("sublevel", subLevelId);
            tag.putUUID("owner", owner);
            tag.putUUID("team", team);
            tag.putLong("controller", controller.asLong());
            tag.putLong("commissioned_at", commissionedAt);
            return tag;
        }

        static Optional<VesselIdentity> fromTag(CompoundTag tag) {
            if (!tag.hasUUID("sublevel")
                    || !tag.hasUUID("owner")
                    || !tag.hasUUID("team")
                    || !tag.contains("controller", Tag.TAG_LONG)
                    || !tag.contains("commissioned_at", Tag.TAG_LONG)
                    || tag.getLong("commissioned_at") <= 0L) {
                return Optional.empty();
            }
            return Optional.of(new VesselIdentity(
                    tag.getUUID("sublevel"),
                    tag.getUUID("owner"),
                    tag.getUUID("team"),
                    BlockPos.of(tag.getLong("controller")),
                    tag.getLong("commissioned_at")));
        }
    }

    public record Authorization(
            int schema,
            String routeSignature,
            ResourceKey<Level> sourceDimension,
            UUID targetPoint,
            boolean inboundToGlacio,
            List<UUID> occupants,
            List<VesselIdentity> identities,
            boolean chargeConsumed
    ) {
        boolean structurallyValid() {
            return schema == AUTHORIZATION_SCHEMA
                    && SignedInterstellarRoute.SIGNATURE.equals(routeSignature)
                    && chargeConsumed
                    && sourceDimension != null
                    && targetPoint != null
                    && occupants != null
                    && identities != null
                    && !occupants.isEmpty()
                    && occupants.size() <= MAX_PERSISTED_OCCUPANTS
                    && occupants.stream().noneMatch(java.util.Objects::isNull)
                    && identities.size() == 1
                    && identities.stream().noneMatch(java.util.Objects::isNull)
                    && hasUniqueValues(occupants)
                    && hasUniqueSubLevels(identities)
                    && (SignedInterstellarRoute.SOL_DIMENSION.equals(sourceDimension)
                            && SignedInterstellarRoute.GLACIO_POINT_ID.equals(targetPoint)
                            && inboundToGlacio
                            || SignedInterstellarRoute.GLACIO_DIMENSION.equals(sourceDimension)
                            && SignedInterstellarRoute.SOL_POINT_ID.equals(targetPoint)
                            && !inboundToGlacio);
        }

        private static boolean hasUniqueValues(List<UUID> values) {
            Set<UUID> unique = new HashSet<>(values);
            return unique.size() == values.size();
        }

        private static boolean hasUniqueSubLevels(List<VesselIdentity> values) {
            Set<UUID> unique = new HashSet<>();
            for (VesselIdentity value : values) {
                if (!unique.add(value.subLevelId())) {
                    return false;
                }
            }
            return true;
        }

        public CompoundTag toTag() {
            CompoundTag tag = new CompoundTag();
            tag.putInt("schema", schema);
            tag.putString("route_signature", routeSignature);
            tag.putString("source_dimension", sourceDimension.location().toString());
            tag.putUUID("target_point", targetPoint);
            tag.putBoolean("inbound_to_glacio", inboundToGlacio);
            tag.putBoolean("charge_consumed", chargeConsumed);
            ListTag occupantTags = new ListTag();
            for (UUID occupant : occupants) {
                CompoundTag entry = new CompoundTag();
                entry.putUUID("id", occupant);
                occupantTags.add(entry);
            }
            tag.put("occupants", occupantTags);
            ListTag identityTags = new ListTag();
            for (VesselIdentity identity : identities) {
                identityTags.add(identity.toTag());
            }
            tag.put("vessels", identityTags);
            return tag;
        }

        public static Optional<Authorization> fromTag(CompoundTag tag) {
            if (!tag.contains("schema", Tag.TAG_INT)
                    || tag.getInt("schema") != AUTHORIZATION_SCHEMA
                    || !tag.contains("route_signature", Tag.TAG_STRING)
                    || !SignedInterstellarRoute.SIGNATURE.equals(tag.getString("route_signature"))
                    || !tag.contains("source_dimension", Tag.TAG_STRING)
                    || !tag.hasUUID("target_point")
                    || !tag.contains("inbound_to_glacio", Tag.TAG_BYTE)
                    || !tag.contains("charge_consumed", Tag.TAG_BYTE)
                    || !tag.contains("occupants", Tag.TAG_LIST)
                    || !tag.contains("vessels", Tag.TAG_LIST)
                    || !tag.getBoolean("charge_consumed")) {
                return Optional.empty();
            }
            ResourceLocation sourceId = ResourceLocation.tryParse(tag.getString("source_dimension"));
            if (sourceId == null) {
                return Optional.empty();
            }
            ResourceKey<Level> source = ResourceKey.create(Registries.DIMENSION, sourceId);
            List<UUID> occupants = new ArrayList<>();
            ListTag occupantTags = tag.getList("occupants", Tag.TAG_COMPOUND);
            if (occupantTags.isEmpty()
                    || occupantTags.size() > MAX_PERSISTED_OCCUPANTS) {
                return Optional.empty();
            }
            for (Tag entry : occupantTags) {
                CompoundTag compound = (CompoundTag) entry;
                if (!compound.hasUUID("id")) {
                    return Optional.empty();
                }
                occupants.add(compound.getUUID("id"));
            }
            List<VesselIdentity> identities = new ArrayList<>();
            ListTag identityTags = tag.getList("vessels", Tag.TAG_COMPOUND);
            if (identityTags.size() != 1) {
                return Optional.empty();
            }
            for (Tag entry : identityTags) {
                Optional<VesselIdentity> identity = VesselIdentity.fromTag((CompoundTag) entry);
                if (identity.isEmpty()) {
                    return Optional.empty();
                }
                identities.add(identity.get());
            }
            occupants.sort(Comparator.comparing(UUID::toString));
            identities.sort(Comparator.comparing(VesselIdentity::canonical));
            Authorization authorization = new Authorization(
                    AUTHORIZATION_SCHEMA,
                    tag.getString("route_signature"),
                    source,
                    tag.getUUID("target_point"),
                    tag.getBoolean("inbound_to_glacio"),
                    List.copyOf(occupants),
                    List.copyOf(identities),
                    true);
            return authorization.structurallyValid()
                    ? Optional.of(authorization)
                    : Optional.empty();
        }
    }
}
