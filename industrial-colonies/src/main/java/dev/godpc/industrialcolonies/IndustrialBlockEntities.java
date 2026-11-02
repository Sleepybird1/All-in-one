package dev.godpc.industrialcolonies;

import dev.godpc.industrialcolonies.space.OrbitalFlightComputerBlockEntity;
import dev.godpc.industrialcolonies.space.InterstellarNavigationComputerBlockEntity;
import dev.godpc.industrialcolonies.space.MarsNavigationComputerBlockEntity;
import dev.godpc.industrialcolonies.space.MercuryNavigationComputerBlockEntity;
import dev.godpc.industrialcolonies.space.VenusNavigationComputerBlockEntity;
import dev.godpc.industrialcolonies.space.station.AtmosphericScoopBlockEntity;
import dev.godpc.industrialcolonies.space.station.StationServicesControllerBlockEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Block entities that participate in integrations with moving structures. */
public final class IndustrialBlockEntities {
    private static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, IndustrialColonies.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<dev.godpc.industrialcolonies.space.MatterStabilizerBlockEntity>>
            MATTER_STABILIZER = BLOCK_ENTITIES.register("matter_stabilizer", () -> BlockEntityType.Builder.of(
                    dev.godpc.industrialcolonies.space.MatterStabilizerBlockEntity::new, IndustrialBlocks.MATTER_STABILIZER.get()).build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<OrbitalFlightComputerBlockEntity>>
            ORBITAL_FLIGHT_COMPUTER = BLOCK_ENTITIES.register(
                    "orbital_flight_computer",
                    () -> BlockEntityType.Builder.of(
                                    OrbitalFlightComputerBlockEntity::new,
                                    IndustrialBlocks.ORBITAL_FLIGHT_COMPUTER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<MarsNavigationComputerBlockEntity>>
            MARS_NAVIGATION_COMPUTER = BLOCK_ENTITIES.register(
                    "mars_navigation_computer",
                    () -> BlockEntityType.Builder.of(
                                    MarsNavigationComputerBlockEntity::new,
                                    IndustrialBlocks.MARS_NAVIGATION_COMPUTER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<VenusNavigationComputerBlockEntity>>
            VENUS_NAVIGATION_COMPUTER = BLOCK_ENTITIES.register(
                    "venus_navigation_computer",
                    () -> BlockEntityType.Builder.of(
                                    VenusNavigationComputerBlockEntity::new,
                                    IndustrialBlocks.VENUS_NAVIGATION_COMPUTER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<MercuryNavigationComputerBlockEntity>>
            MERCURY_NAVIGATION_COMPUTER = BLOCK_ENTITIES.register(
                    "mercury_navigation_computer",
                    () -> BlockEntityType.Builder.of(
                                    MercuryNavigationComputerBlockEntity::new,
                                    IndustrialBlocks.MERCURY_NAVIGATION_COMPUTER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<InterstellarNavigationComputerBlockEntity>>
            INTERSTELLAR_NAVIGATION_COMPUTER = BLOCK_ENTITIES.register(
                    "interstellar_navigation_computer",
                    () -> BlockEntityType.Builder.of(
                                    InterstellarNavigationComputerBlockEntity::new,
                                    IndustrialBlocks.INTERSTELLAR_NAVIGATION_COMPUTER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<StationServicesControllerBlockEntity>>
            STATION_SERVICES_CONTROLLER = BLOCK_ENTITIES.register(
                    "station_services_controller",
                    () -> BlockEntityType.Builder.of(
                                    StationServicesControllerBlockEntity::new,
                                    IndustrialBlocks.STATION_SERVICES_CONTROLLER.get())
                            .build(null));

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<AtmosphericScoopBlockEntity>>
            ATMOSPHERIC_SCOOP = BLOCK_ENTITIES.register(
                    "atmospheric_scoop",
                    () -> BlockEntityType.Builder.of(
                                    AtmosphericScoopBlockEntity::new,
                                    IndustrialBlocks.ATMOSPHERIC_SCOOP.get())
                            .build(null));

    private IndustrialBlockEntities() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCK_ENTITIES.register(modEventBus);
        modEventBus.addListener(IndustrialBlockEntities::registerCapabilities);
    }

    private static void registerCapabilities(RegisterCapabilitiesEvent event) {
        event.registerBlockEntity(
                Capabilities.EnergyStorage.BLOCK,
                STATION_SERVICES_CONTROLLER.get(),
                (controller, side) -> controller.energyStorage());
        event.registerBlockEntity(
                Capabilities.FluidHandler.BLOCK,
                STATION_SERVICES_CONTROLLER.get(),
                (controller, side) -> controller.fluidHandler());
        event.registerBlockEntity(
                Capabilities.EnergyStorage.BLOCK,
                ATMOSPHERIC_SCOOP.get(),
                (scoop, side) -> scoop.energyStorage());
        event.registerBlockEntity(
                Capabilities.FluidHandler.BLOCK,
                ATMOSPHERIC_SCOOP.get(),
                (scoop, side) -> scoop.fluidHandler());
    }
}
