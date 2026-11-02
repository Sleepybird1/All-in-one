package dev.godpc.industrialcolonies.geology;

import dev.godpc.industrialcolonies.IndustrialColonies;
import dev.godpc.industrialcolonies.geology.oil.OilWorldgen;
import dev.godpc.industrialcolonies.geology.oil.OilRules;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.EventPriority;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.neoforge.event.level.LevelEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class GeologyBootstrap {
    private static final DeferredRegister<Feature<?>> FEATURES=DeferredRegister.create(Registries.FEATURE,IndustrialColonies.MOD_ID);
    static{FEATURES.register("regional_geology",GeologyFeature::new);}
    private GeologyBootstrap(){}
    public static void register(IEventBus bus){
        MiningOreOwnership.register(bus);
        MiningNodes.register(bus);
        GeologyConfig.get();
        GeologyBlocks.register(bus);SurfaceRocks.register(bus);MineshaftVeins.register(bus);FEATURES.register(bus);OilWorldgen.register(bus);
        bus.addListener(GeologyCompatibilityPacks::registerPacks);
        NeoForge.EVENT_BUS.addListener(GeologyDebug::registerCommands);
        NeoForge.EVENT_BUS.addListener(VeinLocateCommands::register);
        NeoForge.EVENT_BUS.addListener(VeinLocateCommands::tick);
        NeoForge.EVENT_BUS.addListener(AutomaticVeinSurvey::tick);
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e)->AutomaticVeinSurvey.stop(e.getServer()));
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e)->VeinLocateCommands.stop(e.getServer()));
        NeoForge.EVENT_BUS.addListener(VeinCountCommands::register);
        NeoForge.EVENT_BUS.addListener(VeinCountCommands::tick);
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e)->VeinCountCommands.stop(e.getServer()));
        NeoForge.EVENT_BUS.addListener(EventPriority.HIGHEST,(LevelEvent.Load e)->{
            if(e.getLevel() instanceof ServerLevel level){NearbyVeinClues.load(level);WorldStartOreRuntime.load(level);WorldStartCinnabarRuntime.load(level);CinnabarCapPlans.load(level);}
            if(MassiveDeposits.enabled(GeologyConfig.get())&&e.getLevel() instanceof ServerLevel level)GeologyWorld.of(level);
        });
        NeoForge.EVENT_BUS.addListener((LevelEvent.Unload e)->{
            if(e.getLevel() instanceof ServerLevel level){AutomaticVeinSurvey.unload(level);NearbyVeinClues.unload(level);WorldStartCinnabarRuntime.unload(level);CinnabarCapPlans.unload(level);NativeContinentLevels.unload(level);GeologyWorld.forget(level);}
        });
        NeoForge.EVENT_BUS.addListener((ServerStoppedEvent e)->{WorldStartCinnabarRuntime.stop(e.getServer());NativeContinentLevels.stop(e.getServer());GeologyWorld.clear();GeologyDebug.clear();OilRules.invalidate();});
    }
}
