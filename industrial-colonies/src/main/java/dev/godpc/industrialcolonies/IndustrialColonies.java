package dev.godpc.industrialcolonies;

import com.mojang.logging.LogUtils;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import dev.godpc.industrialcolonies.food.FoodDiversityProgression;
import dev.godpc.industrialcolonies.space.OffworldEnderChestGate;
import dev.godpc.industrialcolonies.client.RefinedRadianceVisibility;
import org.slf4j.Logger;

/** Integration entrypoint for the All in One modpack's physical factory progression. */
@Mod(IndustrialColonies.MOD_ID)
public final class IndustrialColonies {
    public static final String MOD_ID = "industrial_colonies";
    private static final Logger LOGGER = LogUtils.getLogger();

    public IndustrialColonies(IEventBus modEventBus) {
        dev.godpc.industrialcolonies.geology.GeologyBootstrap.register(modEventBus);
        dev.godpc.industrialcolonies.processing.ProcessingContent.register(modEventBus);
        dev.godpc.industrialcolonies.processing.ProcessingRecipeRuntime.register(modEventBus);
        dev.godpc.industrialcolonies.processing.OptionalMetalBucketCapabilities.register(modEventBus);
        IndustrialAttachments.register(modEventBus);
        IndustrialFluids.register(modEventBus);
        IndustrialBlocks.register(modEventBus);
        IndustrialItems.register(modEventBus);
        IndustrialBlockEntities.register(modEventBus);
        TieredCreateRecipes.register(modEventBus);
        CreateMachineOwner.register(modEventBus);
        KjsGenIntegration.register();
        KjsGenSequencedAssemblyIntegration.register();
        FoodDiversityProgression.register();
        OffworldEnderChestGate.register();
        dev.godpc.industrialcolonies.space.AutonomousShipCommands.register();
        dev.godpc.industrialcolonies.space.ChemicalDockService.register(modEventBus);
        dev.godpc.industrialcolonies.space.AeDockService.register();
        if (net.neoforged.fml.ModList.get().isLoaded("rocketnautics"))
            dev.godpc.industrialcolonies.space.RendezvousService.register();
        if (FMLEnvironment.dist == Dist.CLIENT) {
            KjsGenAutoExporter.register(modEventBus);
            RefinedRadianceVisibility.register(modEventBus);
        }
        // Progression is deliberately enforced by physical recipe dependencies.
        // The former MineColonies-to-FTB stage bridge is retained in source only
        // so old saves can be migrated, but it is not active at runtime.
        LOGGER.info("Industrial Colonies loaded in physical recipe progression mode with {} tiered Create recipe environments",
                TieredCreateRecipes.environmentCount());
    }
}
