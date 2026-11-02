package dev.godpc.industrialcolonies.mixin;

import com.google.gson.JsonElement;
import dev.godpc.industrialcolonies.space.SpaceCompatibility;
import java.util.Map;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Prevents Ad Astra's global planets listener from decoding Stellaris JSON. */
@Pseudo
@Mixin(targets = "earth.terrarium.adastra.common.planets.AdAstraData", remap = false)
public abstract class AdAstraPlanetDataMixin {
    @ModifyVariable(
            method = "apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V",
            at = @At("HEAD"),
            argsOnly = true,
            ordinal = 0,
            remap = false)
    private Map<ResourceLocation, JsonElement> industrialColonies$filterAdAstraPlanets(
            Map<ResourceLocation, JsonElement> resources
    ) {
        return SpaceCompatibility.forAdAstraPlanetLoader(resources);
    }
}
