package dev.godpc.industrialcolonies.mixin;

import com.google.gson.JsonObject;
import com.zizazr.kjsgen.templates.JsonLayoutLoader;
import dev.godpc.industrialcolonies.KjsGenAutoExporter;
import dev.godpc.industrialcolonies.KjsGenIntegration;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.profiling.ProfilerFiller;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Map;

/** Keeps our process-centric overrides authoritative after a resource reload. */
@Mixin(value = JsonLayoutLoader.class, remap = false)
public abstract class KjsGenJsonLayoutLoaderMixin {
    @Inject(
            method = "apply(Ljava/util/Map;Lnet/minecraft/server/packs/resources/ResourceManager;"
                    + "Lnet/minecraft/util/profiling/ProfilerFiller;)V",
            at = @At("TAIL")
    )
    private void industrialColonies$restoreProcessEditors(
            Map<ResourceLocation, JsonObject> layouts,
            ResourceManager resources,
            ProfilerFiller profiler,
            CallbackInfo ci
    ) {
        KjsGenIntegration.installMachineCentricDefinitions();
        KjsGenAutoExporter.onRecipeLayoutsReady();
    }
}
