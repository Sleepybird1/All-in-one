package dev.godpc.industrialcolonies.geology.oil;

import dev.godpc.industrialcolonies.IndustrialColonies;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Called by GeologyBootstrap, not a second mod entrypoint. */
public final class OilWorldgen {
    private static final DeferredRegister<Feature<?>> FEATURES =
            DeferredRegister.create(Registries.FEATURE, IndustrialColonies.MOD_ID);

    static {
        FEATURES.register("regional_oil_reservoir", OilReservoirFeature::new);
    }

    private OilWorldgen() {}

    public static void register(IEventBus bus) {
        FEATURES.register(bus);
    }
}
