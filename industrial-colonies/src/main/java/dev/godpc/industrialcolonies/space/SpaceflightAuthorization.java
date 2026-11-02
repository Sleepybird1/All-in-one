package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.orbit.DeepSpaceInstance;
import dev.devce.rocketnautics.content.orbit.universe.CubePlanet;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.SubLevel;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Runtime authorization checks for block-built orbital craft. */
public final class SpaceflightAuthorization {
    private static final ResourceKey<Level> MARS = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "mars"));
    private static final ResourceKey<Level> VENUS = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "venus"));
    private static final ResourceKey<Level> MERCURY = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "mercury"));
    private static final ResourceKey<Level> GLACIO = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "glacio"));
    private static final TagKey<Item> HEAT_RESISTANT_ARMOR = TagKey.create(
            Registries.ITEM,
            ResourceLocation.fromNamespaceAndPath("ad_astra", "heat_resistant_armor"));
    private static final EnumSet<EquipmentSlot> ARMOR_SLOTS = EnumSet.of(
            EquipmentSlot.HEAD,
            EquipmentSlot.CHEST,
            EquipmentSlot.LEGS,
            EquipmentSlot.FEET);

    private SpaceflightAuthorization() {
    }

    public static boolean hasOrbitalFlightComputer(ServerSubLevel ship) {
        if (automationDisabled(ship)) return false;
        if (!FreightJourneyControl.journal(ship.getLevel().getServer()).nativeHandoffAllowed(
                ship.getUniqueId(), ship.getLevel().dimension().location().toString())) return false;
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof OrbitalFlightComputerBlockEntity computer && !computer.isRemoved()) {
                return true;
            }
        }
        return false;
    }

    public static boolean hasMarsNavigationComputer(ServerSubLevel ship) {
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof MarsNavigationComputerBlockEntity computer
                    && !computer.isRemoved()) {
                return true;
            }
        }
        return false;
    }

    public static boolean hasVenusNavigationComputer(ServerSubLevel ship) {
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof VenusNavigationComputerBlockEntity computer
                    && !computer.isRemoved()) {
                return true;
            }
        }
        return false;
    }

    public static boolean hasMercuryNavigationComputer(ServerSubLevel ship) {
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof MercuryNavigationComputerBlockEntity computer
                    && !computer.isRemoved()) {
                return true;
            }
        }
        return false;
    }

    public static boolean hasInterstellarNavigationComputer(ServerSubLevel ship) {
        for (BlockEntitySubLevelActor actor : ship.getPlot().getBlockEntityActors()) {
            if (actor instanceof InterstellarNavigationComputerBlockEntity computer
                    && !computer.isRemoved()) {
                return true;
            }
        }
        return false;
    }

    /**
     * Applies physical navigation boundaries only to canonical Mars, Venus,
     * and Mercury surfaces.
     *
     * <p>Deep-space retirement moves an entire instance atomically. Every
     * online player must therefore be associated with a loaded ship, and
     * every ship bearing a player must contain the physical route computer.
     * Later computers satisfy earlier routes, while Venus additionally
     * requires correctly slotted heat-resistant armor.
     * Offline players or unloaded ships fail closed so neither state can be
     * used to bypass inspection.</p>
     */
    public static boolean mayDescendToManagedPlanet(
            MinecraftServer server,
            CubePlanet destination,
            DeepSpaceInstance deepSpace
    ) {
        if (AutonomousShipControl.get(server).allDisabled()) return false;
        List<ServerSubLevel> loadedShips = new ArrayList<>();
        deepSpace.collectLoadedSublevels(server, subLevel -> collectShip(subLevel, loadedShips));
        for (ServerSubLevel ship : loadedShips) if (automationDisabled(ship)) return false;
        if (destination == null || destination.linkedDimension() == null) {
            return true;
        }
        ResourceKey<Level> destinationKey = destination.linkedDimension().key();
        // Glacio is reachable only through the signed Cosmowarp transaction.
        // Rocketnautics' generic deep-space descent would bypass the physical
        // charge, exact route crystal, commissioned ship, and live services.
        if (GLACIO.equals(destinationKey)) {
            return false;
        }
        boolean boundForMars = MARS.equals(destinationKey);
        boolean boundForVenus = VENUS.equals(destinationKey);
        boolean boundForMercury = MERCURY.equals(destinationKey);
        if (!boundForMars && !boundForVenus && !boundForMercury) {
            return true;
        }
        if (!deepSpace.getOfflinePlayers().isEmpty()
                || !deepSpace.getUnloadedSublevels().isEmpty()) {
            return false;
        }

        List<ServerPlayer> players = new ArrayList<>();
        deepSpace.collectOnlinePlayers(server, players::add);
        List<ServerSubLevel> ships = new ArrayList<>();
        deepSpace.collectLoadedSublevels(server, subLevel -> collectShip(subLevel, ships));
        if (ships.isEmpty()) {
            return false;
        }

        if (players.isEmpty()) {
            // An offline OWNER is allowed; an offline PASSENGER remains denied above.
            // Every transferred body must carry its own owned transponder and route hardware.
            for (ServerSubLevel ship : ships) {
                boolean owned = transponders(ship).stream().anyMatch(t -> t.ownerId().isPresent());
                boolean hardware = boundForMercury ? hasMercuryNavigationComputer(ship) || hasInterstellarNavigationComputer(ship)
                        : boundForVenus ? hasVenusNavigationComputer(ship) || hasMercuryNavigationComputer(ship) || hasInterstellarNavigationComputer(ship)
                        : hasMarsNavigationComputer(ship) || hasVenusNavigationComputer(ship) || hasMercuryNavigationComputer(ship) || hasInterstellarNavigationComputer(ship);
                if (!owned || !hardware) return false;
            }
            return true;
        }

        for (ServerPlayer player : players) {
            if (boundForVenus && !hasFullHeatResistantSuit(player)) {
                return false;
            }
            SubLevel associated = Sable.HELPER.getTrackingOrVehicleSubLevel(player);
            if (!(associated instanceof ServerSubLevel ship)
                    || ship.isRemoved()
                    || !ships.contains(ship)) {
                return false;
            }
            boolean hasRequiredComputer;
            if (boundForMercury) {
                hasRequiredComputer = hasMercuryNavigationComputer(ship)
                        || hasInterstellarNavigationComputer(ship);
            } else if (boundForVenus) {
                hasRequiredComputer = hasVenusNavigationComputer(ship)
                        || hasMercuryNavigationComputer(ship)
                        || hasInterstellarNavigationComputer(ship);
            } else {
                hasRequiredComputer = hasMarsNavigationComputer(ship)
                        || hasVenusNavigationComputer(ship)
                        || hasMercuryNavigationComputer(ship)
                        || hasInterstellarNavigationComputer(ship);
            }
            if (!hasRequiredComputer) {
                return false;
            }
        }
        return true;
    }

    private static boolean hasFullHeatResistantSuit(ServerPlayer player) {
        for (EquipmentSlot slot : ARMOR_SLOTS) {
            ItemStack stack = player.getItemBySlot(slot);
            if (!stack.is(HEAT_RESISTANT_ARMOR) || !stack.canEquip(slot, player)) {
                return false;
            }
        }
        return true;
    }

    private static List<net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity> transponders(ServerSubLevel ship) {
        var result = new ArrayList<net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity>();
        // AL transponders are ordinary block entities, not Sable actor interfaces.
        for (var holder : ship.getPlot().getLoadedChunks()) for (var blockEntity : holder.getChunk().getBlockEntities().values()) {
            if (blockEntity instanceof net.sprocketgames.create_aeronautics_automated_logistics.block.entity.ShipTransponderBlockEntity transponder
                    && !transponder.isRemoved() && Sable.HELPER.getContaining(transponder) == ship) result.add(transponder);
        }
        return result;
    }

    public static boolean automationDisabled(ServerSubLevel ship) {
        var control = AutonomousShipControl.get(ship.getLevel().getServer());
        return control.allDisabled() || FreightJourneyControl.holdsBody(ship.getLevel().getServer(), ship.getUniqueId())
                || transponders(ship).stream().anyMatch(t -> control.disabled(t.transponderId()));
    }

    private static void collectShip(SubLevel subLevel, List<ServerSubLevel> ships) {
        if (subLevel instanceof ServerSubLevel ship && !ship.isRemoved()) {
            ships.add(ship);
        }
    }
}
