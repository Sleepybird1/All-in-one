package dev.godpc.industrialcolonies;

import dev.godpc.industrialcolonies.space.OrbitalFlightComputerBlock;
import dev.godpc.industrialcolonies.space.InterstellarNavigationComputerBlock;
import dev.godpc.industrialcolonies.space.MarsNavigationComputerBlock;
import dev.godpc.industrialcolonies.space.MercuryNavigationComputerBlock;
import dev.godpc.industrialcolonies.space.VenusNavigationComputerBlock;
import dev.godpc.industrialcolonies.space.station.AtmosphericScoopBlock;
import dev.godpc.industrialcolonies.space.station.StationServicesControllerBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Blocks owned by the physical progression companion. */
public final class IndustrialBlocks {
    private static final DeferredRegister.Blocks BLOCKS =
            DeferredRegister.createBlocks(IndustrialColonies.MOD_ID);

    public static final DeferredBlock<dev.godpc.industrialcolonies.space.MatterStabilizerBlock> MATTER_STABILIZER =
            BLOCKS.registerBlock("matter_stabilizer", dev.godpc.industrialcolonies.space.MatterStabilizerBlock::new,
                    BlockBehaviour.Properties.of().strength(8.0F, 24.0F).sound(SoundType.METAL).requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> ORBITAL_FLIGHT_COMPUTER =
            BLOCKS.registerBlock(
                    "orbital_flight_computer",
                    OrbitalFlightComputerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(8.0F, 24.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> MARS_NAVIGATION_COMPUTER =
            BLOCKS.registerBlock(
                    "mars_navigation_computer",
                    MarsNavigationComputerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(10.0F, 30.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> VENUS_NAVIGATION_COMPUTER =
            BLOCKS.registerBlock(
                    "venus_navigation_computer",
                    VenusNavigationComputerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(12.0F, 36.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> MERCURY_NAVIGATION_COMPUTER =
            BLOCKS.registerBlock(
                    "mercury_navigation_computer",
                    MercuryNavigationComputerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(14.0F, 42.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> INTERSTELLAR_NAVIGATION_COMPUTER =
            BLOCKS.registerBlock(
                    "interstellar_navigation_computer",
                    InterstellarNavigationComputerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(18.0F, 54.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> STATION_SERVICES_CONTROLLER =
            BLOCKS.registerBlock(
                    "station_services_controller",
                    StationServicesControllerBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(16.0F, 48.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<Block> ATMOSPHERIC_SCOOP =
            BLOCKS.registerBlock(
                    "atmospheric_scoop",
                    AtmosphericScoopBlock::new,
                    BlockBehaviour.Properties.of()
                            .strength(18.0F, 54.0F)
                            .sound(SoundType.METAL)
                            .requiresCorrectToolForDrops());

    public static final DeferredBlock<LiquidBlock> GAS_GIANT_CONDENSATE =
            BLOCKS.register(
                    "gas_giant_condensate",
                    () -> new LiquidBlock(
                            IndustrialFluids.GAS_GIANT_CONDENSATE.get(),
                            BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).noLootTable()));

    private IndustrialBlocks() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
    }
}
