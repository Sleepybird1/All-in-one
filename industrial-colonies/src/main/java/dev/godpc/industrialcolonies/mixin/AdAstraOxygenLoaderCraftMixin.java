package dev.godpc.industrialcolonies.mixin;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Keep the native oxygen recipe's input/output in their designated tanks. */
@Pseudo
@Mixin(targets = "earth.terrarium.adastra.common.blockentities.machines.OxygenLoaderBlockEntity", remap = false)
public abstract class AdAstraOxygenLoaderCraftMixin {
    @Unique private static volatile MethodHandle industrialColonies$extract;
    @Unique private static MethodHandle industrialColonies$insert;

    @Unique
    private static synchronized void industrialColonies$prepareCraft() throws ReflectiveOperationException {
        if (industrialColonies$extract != null) return;
        var storage = Class.forName("earth.terrarium.common_storage_lib.storage.base.CommonStorage");
        var resource = Class.forName("earth.terrarium.common_storage_lib.resources.Resource");
        var type = MethodType.methodType(long.class, int.class, resource, long.class, boolean.class);
        var adapted = MethodType.methodType(long.class, Object.class, int.class, Object.class, long.class, boolean.class);
        var lookup = MethodHandles.publicLookup();
        industrialColonies$insert = lookup.findVirtual(storage, "insert", type).asType(adapted);
        industrialColonies$extract = lookup.findVirtual(storage, "extract", type).asType(adapted);
    }

    @Redirect(method = "craft", at = @At(value = "INVOKE", target =
            "Learth/terrarium/common_storage_lib/fluid/impl/SimpleFluidStorage;extract(" +
            "Learth/terrarium/common_storage_lib/resources/fluid/FluidResource;JZ)J"), require = 1)
    private long industrialColonies$extractInput(@Coerce Object storage, @Coerce Object resource,
                                                long amount, boolean simulate) {
        try {
            if (industrialColonies$extract == null) industrialColonies$prepareCraft();
            return (long) industrialColonies$extract.invokeExact(storage, 0, resource, amount, simulate);
        } catch (Throwable failure) {
            throw new IllegalStateException("Ad Astra oxygen input-tank compatibility failed", failure);
        }
    }

    @Redirect(method = "craft", at = @At(value = "INVOKE", target =
            "Learth/terrarium/common_storage_lib/fluid/impl/SimpleFluidStorage;insert(" +
            "Learth/terrarium/common_storage_lib/resources/fluid/FluidResource;JZ)J"), require = 1)
    private long industrialColonies$insertOutput(@Coerce Object storage, @Coerce Object resource,
                                                long amount, boolean simulate) {
        try {
            if (industrialColonies$extract == null) industrialColonies$prepareCraft();
            return (long) industrialColonies$insert.invokeExact(storage, 1, resource, amount, simulate);
        } catch (Throwable failure) {
            throw new IllegalStateException("Ad Astra oxygen output-tank compatibility failed", failure);
        }
    }
}
