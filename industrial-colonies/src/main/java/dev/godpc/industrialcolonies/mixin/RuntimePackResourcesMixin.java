package dev.godpc.industrialcolonies.mixin;

import java.io.InputStream;
import java.nio.file.Path;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.server.packs.resources.IoSupplier;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Runtime data providers write concurrently through DataProvider.saveStable. */
@Pseudo
@Mixin(targets = "plus.dragons.createdragonsplus.data.runtime.RuntimePackResources", remap = false)
public abstract class RuntimePackResourcesMixin {
    @Shadow @Final @Mutable
    private Map<Path, IoSupplier<InputStream>> resources;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void industrialColonies$preserveConcurrentResources(CallbackInfo ci) {
        // Retain constructor-provided metadata/icon resources before providers run.
        resources = new ConcurrentHashMap<>(resources);
    }
}
