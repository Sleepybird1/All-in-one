package dev.godpc.industrialcolonies.mixin;

import com.google.gson.JsonElement;
import dev.godpc.industrialcolonies.space.SpaceCompatibility;
import java.util.Map;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Prevents Stellaris's global planets listener from decoding Ad Astra JSON. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.data.planets.StellarisData", remap = false)
public abstract class StellarisPlanetDataMixin {
    @ModifyVariable(
            method = "apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;Lnet/minecraft/util/profiling/ProfilerFiller;)V",
            at = @At("HEAD"),
            argsOnly = true,
            ordinal = 0,
            remap = false)
    private Map<ResourceLocation, JsonElement> industrialColonies$filterStellarisPlanets(
            Map<ResourceLocation, JsonElement> resources
    ) {
        return SpaceCompatibility.forStellarisPlanetLoader(resources);
    }
}
