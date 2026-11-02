package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.InterstellarWarpPolicy;
import dev.godpc.industrialcolonies.space.InterstellarWarpInitiatorScope;
import dev.godpc.industrialcolonies.space.InterstellarWarpTransaction;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import dev.waco0311.cosmowarp.network.ModNetworking;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import org.joml.Vector3d;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Locks Cosmowarp's mutable charge cycle to one persisted, signed authorization. */
@Mixin(value = WarpDriveBlockEntity.class, remap = false)
public abstract class CosmowarpWarpDriveMixin {
    @Shadow
    private int chargeTicksRemaining;

    @Shadow
    private UUID chargingTargetId;

    @Shadow
    private List<UUID> chargingEffectPlayers;

    @Unique
    private InterstellarWarpPolicy.PendingAuthorization industrialColonies$pendingAuthorization;

    @Unique
    private InterstellarWarpPolicy.Authorization industrialColonies$activeAuthorization;

    @Unique
    private boolean industrialColonies$warpCopySucceeded;

    @Inject(
            method = "beginWarp()Ldev/waco0311/cosmowarp/block/entity/"
                    + "WarpDriveBlockEntity$WarpResult;",
            at = @At("HEAD"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$authorizeBegin(
            CallbackInfoReturnable<WarpDriveBlockEntity.WarpResult> callback
    ) {
        WarpDriveBlockEntity drive = (WarpDriveBlockEntity) (Object) this;
        industrialColonies$pendingAuthorization = null;
        if (drive.getLevel() == null || drive.getLevel().isClientSide || drive.isCharging()) {
            return;
        }
        industrialColonies$activeAuthorization = null;
        Optional<InterstellarWarpPolicy.PendingAuthorization> pending =
                InterstellarWarpPolicy.authorizeStart(
                        drive, InterstellarWarpInitiatorScope.current());
        if (pending.isEmpty()) {
            callback.setReturnValue(WarpDriveBlockEntity.WarpResult.INVALID_DESTINATION);
            return;
        }
        industrialColonies$pendingAuthorization = pending.get();
    }

    @Inject(
            method = "beginWarp()Ldev/waco0311/cosmowarp/block/entity/"
                    + "WarpDriveBlockEntity$WarpResult;",
            at = @At("RETURN"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$consumeAfterBegin(
            CallbackInfoReturnable<WarpDriveBlockEntity.WarpResult> callback
    ) {
        InterstellarWarpPolicy.PendingAuthorization pending =
                industrialColonies$pendingAuthorization;
        industrialColonies$pendingAuthorization = null;
        if (callback.getReturnValue() != WarpDriveBlockEntity.WarpResult.SUCCESS) {
            return;
        }
        Optional<InterstellarWarpPolicy.Authorization> active = pending == null
                ? Optional.empty()
                : InterstellarWarpPolicy.consumeAfterSuccessfulBegin(pending);
        if (active.isEmpty()) {
            industrialColonies$abortCharge();
            callback.setReturnValue(WarpDriveBlockEntity.WarpResult.INVALID_DESTINATION);
            return;
        }
        industrialColonies$activeAuthorization = active.get();
        ((WarpDriveBlockEntity) (Object) this).setChanged();
    }

    @Inject(
            method = "tick()V",
            at = @At("HEAD"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$abortUntrackedReload(CallbackInfo callback) {
        WarpDriveBlockEntity drive = (WarpDriveBlockEntity) (Object) this;
        if (chargeTicksRemaining > 0
                && drive.getLevel() instanceof ServerLevel
                && industrialColonies$activeAuthorization == null) {
            industrialColonies$abortCharge();
            callback.cancel();
        }
    }

    @Inject(
            method = "executeWarp()V",
            at = @At("HEAD"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$revalidateAtExecute(CallbackInfo callback) {
        WarpDriveBlockEntity drive = (WarpDriveBlockEntity) (Object) this;
        if (!InterstellarWarpPolicy.authorizeExecute(
                drive,
                industrialColonies$activeAuthorization,
                chargingTargetId)) {
            industrialColonies$abortCharge();
            callback.cancel();
            return;
        }
        industrialColonies$warpCopySucceeded = false;
    }

    @Redirect(
            method = "executeWarp()V",
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/egg/SubLevelWarper;WarpSubLevel("
                            + "Ldev/ryanhcode/sable/sublevel/ServerSubLevel;"
                            + "Lnet/minecraft/world/level/Level;Lorg/joml/Vector3d;)I"
            ),
            require = 1
    )
    private int industrialColonies$guardWarpCopy(
            ServerSubLevel source,
            Level destination,
            Vector3d target
    ) {
        int moved = InterstellarWarpTransaction.warp(
                source,
                destination,
                target,
                industrialColonies$activeAuthorization);
        industrialColonies$warpCopySucceeded = moved == 1;
        return moved;
    }

    @Inject(
            method = "executeWarp()V",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/server/level/ServerLevel;playSound("
                            + "Lnet/minecraft/world/entity/player/Player;"
                            + "Lnet/minecraft/core/BlockPos;Lnet/minecraft/sounds/SoundEvent;"
                            + "Lnet/minecraft/sounds/SoundSource;FF)V",
                    ordinal = 1
            ),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$suppressFailedCopySuccess(CallbackInfo callback) {
        if (!industrialColonies$warpCopySucceeded) {
            industrialColonies$abortCharge();
            callback.cancel();
        }
    }

    @Inject(
            method = "executeWarp()V",
            at = @At("RETURN"),
            require = 1
    )
    private void industrialColonies$clearCompletedAuthorization(CallbackInfo callback) {
        industrialColonies$pendingAuthorization = null;
        industrialColonies$activeAuthorization = null;
        industrialColonies$warpCopySucceeded = false;
        ((WarpDriveBlockEntity) (Object) this).setChanged();
    }

    @Inject(
            method = "saveAdditional(Lnet/minecraft/nbt/CompoundTag;"
                    + "Lnet/minecraft/core/HolderLookup$Provider;)V",
            at = @At("TAIL"),
            require = 1
    )
    private void industrialColonies$saveAuthorization(
            CompoundTag tag,
            HolderLookup.Provider registries,
            CallbackInfo callback
    ) {
        if (chargeTicksRemaining > 0 && industrialColonies$activeAuthorization != null) {
            tag.put(
                    InterstellarWarpPolicy.AUTHORIZATION_NBT,
                    industrialColonies$activeAuthorization.toTag());
        } else {
            tag.remove(InterstellarWarpPolicy.AUTHORIZATION_NBT);
        }
    }

    @Inject(
            method = "loadAdditional(Lnet/minecraft/nbt/CompoundTag;"
                    + "Lnet/minecraft/core/HolderLookup$Provider;)V",
            at = @At("TAIL"),
            require = 1
    )
    private void industrialColonies$loadAuthorization(
            CompoundTag tag,
            HolderLookup.Provider registries,
            CallbackInfo callback
    ) {
        industrialColonies$pendingAuthorization = null;
        industrialColonies$activeAuthorization = chargeTicksRemaining > 0
                && tag.contains(InterstellarWarpPolicy.AUTHORIZATION_NBT, Tag.TAG_COMPOUND)
                ? InterstellarWarpPolicy.Authorization.fromTag(
                        tag.getCompound(InterstellarWarpPolicy.AUTHORIZATION_NBT)).orElse(null)
                : null;
    }

    @Unique
    private void industrialColonies$abortCharge() {
        WarpDriveBlockEntity drive = (WarpDriveBlockEntity) (Object) this;
        if (drive.getLevel() instanceof ServerLevel level && chargingEffectPlayers != null) {
            List<ServerPlayer> players = chargingEffectPlayers.stream()
                    .map(level.getServer().getPlayerList()::getPlayer)
                    .filter(java.util.Objects::nonNull)
                    .toList();
            ModNetworking.broadcastWarpEffectToPlayers(
                    players, drive.getBlockPos(), false);
        }
        chargeTicksRemaining = 0;
        chargingTargetId = null;
        chargingEffectPlayers = List.of();
        industrialColonies$pendingAuthorization = null;
        industrialColonies$activeAuthorization = null;
        industrialColonies$warpCopySucceeded = false;
        drive.setChanged();
        if (drive.getLevel() instanceof ServerLevel level) {
            level.sendBlockUpdated(
                    drive.getBlockPos(), drive.getBlockState(), drive.getBlockState(), 2);
        }
    }
}
