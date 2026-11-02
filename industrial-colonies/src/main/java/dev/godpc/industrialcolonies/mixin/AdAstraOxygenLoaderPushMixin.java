package dev.godpc.industrialcolonies.mixin;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Repairs the pinned loader's reversed fluid push without changing its recipes or rate. */
@Pseudo
@Mixin(targets = "earth.terrarium.adastra.common.blockentities.machines.OxygenLoaderBlockEntity", remap = false)
public abstract class AdAstraOxygenLoaderPushMixin {
    @Unique private static volatile MethodHandle industrialColonies$getConfiguration;
    @Unique private static MethodHandle industrialColonies$canPush;
    @Unique private static MethodHandle industrialColonies$relative;
    @Unique private static MethodHandle industrialColonies$sync;
    @Unique private static MethodHandle industrialColonies$getSlot;
    @Unique private static MethodHandle industrialColonies$getResource;
    @Unique private static MethodHandle industrialColonies$getAmount;
    @Unique private static MethodHandle industrialColonies$findFluid;
    @Unique private static MethodHandle industrialColonies$move;
    @Unique private static MethodHandle industrialColonies$batch;

    @Unique
    private static synchronized void industrialColonies$preparePush(Object entry) throws ReflectiveOperationException {
        if (industrialColonies$getConfiguration != null) return;
        var lookup = MethodHandles.publicLookup();
        var configuration = Class.forName("earth.terrarium.adastra.common.blockentities.base.sideconfig.Configuration");
        var utility = Class.forName("earth.terrarium.adastra.common.utils.ModUtils");
        var machine = Class.forName("earth.terrarium.adastra.common.blockentities.base.ContainerMachineBlockEntity");
        industrialColonies$canPush = lookup.findVirtual(configuration, "canPush", MethodType.methodType(boolean.class))
                .asType(MethodType.methodType(boolean.class, Object.class));
        industrialColonies$relative = lookup.findStatic(utility, "relative",
                MethodType.methodType(Direction.class, BlockEntity.class, Direction.class));
        industrialColonies$sync = lookup.findVirtual(machine, "sync", MethodType.methodType(void.class))
                .asType(MethodType.methodType(void.class, Object.class));
        var storage = Class.forName("earth.terrarium.common_storage_lib.storage.base.CommonStorage");
        var slot = Class.forName("earth.terrarium.common_storage_lib.storage.base.StorageSlot");
        var io = Class.forName("earth.terrarium.common_storage_lib.storage.base.StorageIO");
        var resource = Class.forName("earth.terrarium.common_storage_lib.resources.Resource");
        var blockLookup = Class.forName("earth.terrarium.common_storage_lib.lookup.BlockLookup");
        var fluidApi = Class.forName("earth.terrarium.common_storage_lib.fluid.FluidApi");
        var transfer = Class.forName("earth.terrarium.common_storage_lib.storage.util.TransferUtil");
        var updates = Class.forName("earth.terrarium.common_storage_lib.storage.base.UpdateManager");
        industrialColonies$getSlot = lookup.findVirtual(storage, "get", MethodType.methodType(slot, int.class))
                .asType(MethodType.methodType(Object.class, Object.class, int.class));
        industrialColonies$getResource = lookup.findVirtual(slot, "getResource", MethodType.methodType(resource))
                .asType(MethodType.methodType(Object.class, Object.class));
        industrialColonies$getAmount = lookup.findVirtual(slot, "getAmount", MethodType.methodType(long.class))
                .asType(MethodType.methodType(long.class, Object.class));
        industrialColonies$findFluid = lookup.findVirtual(blockLookup, "find",
                MethodType.methodType(Object.class, BlockEntity.class, Object.class))
                .bindTo(fluidApi.getField("BLOCK").get(null))
                .asType(MethodType.methodType(Object.class, BlockEntity.class, Direction.class));
        industrialColonies$move = lookup.findStatic(transfer, "move",
                MethodType.methodType(long.class, io, io, Object.class, long.class, boolean.class))
                .asType(MethodType.methodType(long.class, Object.class, Object.class, Object.class, long.class, boolean.class));
        industrialColonies$batch = lookup.findStatic(updates, "batch", MethodType.methodType(void.class, Object[].class))
                .asFixedArity();
        // Publish last: the volatile write also publishes the other handles.
        industrialColonies$getConfiguration = lookup.findVirtual(entry.getClass(), "get",
                MethodType.methodType(configuration, Direction.class))
                .asType(MethodType.methodType(Object.class, Object.class, Direction.class));
    }

    @Redirect(method = "tickSideInteractions", at = @At(value = "INVOKE", target =
            "Learth/terrarium/adastra/common/utils/TransferUtils;pushFluidNearby(" +
            "Learth/terrarium/adastra/common/blockentities/base/ContainerMachineBlockEntity;" +
            "Lnet/minecraft/core/BlockPos;Learth/terrarium/common_storage_lib/storage/base/CommonStorage;JI" +
            "Learth/terrarium/adastra/common/blockentities/base/sideconfig/ConfigurationEntry;" +
            "Ljava/util/function/Predicate;)V"), require = 1)
    private void industrialColonies$pushOutput(
            @Coerce Object owner, BlockPos pos, @Coerce Object nativeStorage,
            long maximum, int sourceTank, @Coerce Object configuration, Predicate<Direction> allowedSide) {
        var machine = (BlockEntity) owner;
        var level = machine.getLevel();
        if (level == null || level.isClientSide || maximum <= 0 || sourceTank < 0) return;
        // NeoForge's platform fluid amount is already in mB. Keep the caller's native budget.
        int limit = (int) Math.min(maximum, Integer.MAX_VALUE);
        try {
            if (industrialColonies$getConfiguration == null) industrialColonies$preparePush(configuration);
            for (var configuredSide : Direction.values()) {
                Object mode = industrialColonies$getConfiguration.invokeExact(configuration, configuredSide);
                if (!(boolean) industrialColonies$canPush.invokeExact(mode)) continue;
                var side = (Direction) industrialColonies$relative.invokeExact(machine, configuredSide);
                if (!allowedSide.test(side)) continue;
                var neighbor = level.getBlockEntity(pos.relative(side));
                if (neighbor == null) continue;
                Object target = industrialColonies$findFluid.invokeExact(neighbor, side.getOpposite());
                if (target == null) continue;
                Object slot = industrialColonies$getSlot.invokeExact(nativeStorage, sourceTank);
                long amount = (long) industrialColonies$getAmount.invokeExact(slot);
                if (amount <= 0) continue;
                Object resource = industrialColonies$getResource.invokeExact(slot);
                // A slot, not the whole storage: matching fluid in the input must remain untouched.
                long moved = (long) industrialColonies$move.invokeExact(slot, target, resource,
                        Math.min((long) limit, amount), false);
                if (moved > 0) {
                    industrialColonies$batch.invokeExact(new Object[]{nativeStorage, target});
                    machine.setChanged();
                    industrialColonies$sync.invokeExact(owner);
                }
            }
        } catch (Throwable failure) {
            throw new IllegalStateException("Ad Astra oxygen-loader output compatibility failed", failure);
        }
    }
}
