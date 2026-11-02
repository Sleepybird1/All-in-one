package dev.godpc.industrialcolonies;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;

/** Retains layout initialization. Recipe export is exclusively a user action. */
public final class KjsGenAutoExporter {
    private KjsGenAutoExporter() {}

    public static void register(IEventBus modEventBus) {
        modEventBus.addListener(KjsGenAutoExporter::onClientSetup);
    }

    private static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(KjsGenAutoExporter::initializeLayouts);
    }

    public static synchronized void onRecipeLayoutsReady() {
        initializeLayouts();
    }

    private static void initializeLayouts() {
        try {
            KjsGenIntegration.installMachineCentricDefinitions();
        } catch (Exception | LinkageError error) {
            LogUtils.getLogger().error("Industrial Colonies could not initialize KJSGen layouts", error);
        }
    }
}
