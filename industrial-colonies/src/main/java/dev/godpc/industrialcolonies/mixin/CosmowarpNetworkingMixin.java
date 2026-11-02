package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Local;
import dev.godpc.industrialcolonies.space.InterstellarWarpInitiatorScope;
import dev.godpc.industrialcolonies.space.InterstellarWarpPolicy;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import dev.waco0311.cosmowarp.network.ModNetworking;
import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Binds every Warp Drive menu mutation to its actual authorized server sender. */
@Mixin(value = ModNetworking.class, remap = false)
public abstract class CosmowarpNetworkingMixin {
    private static final String SIMPLE_HANDLER =
            "lambda$handleSimpleAction$0(Lnet/neoforged/neoforge/network/handling/"
                    + "IPayloadContext;Ldev/waco0311/cosmowarp/network/"
                    + "WarpDriveSimpleActionPayload;)V";
    private static final String SELECT_HANDLER =
            "lambda$handleSelect$1(Lnet/neoforged/neoforge/network/handling/"
                    + "IPayloadContext;Ldev/waco0311/cosmowarp/network/"
                    + "WarpDriveSelectPayload;)V";
    private static final String RENAME_HANDLER =
            "lambda$handleRename$2(Lnet/neoforged/neoforge/network/handling/"
                    + "IPayloadContext;Ldev/waco0311/cosmowarp/network/"
                    + "WarpDriveRenamePayload;)V";

    @WrapOperation(
            method = SIMPLE_HANDLER,
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/waco0311/cosmowarp/block/entity/"
                            + "WarpDriveBlockEntity;beginWarp()Ldev/waco0311/cosmowarp/"
                            + "block/entity/WarpDriveBlockEntity$WarpResult;"),
            require = 1)
    private static WarpDriveBlockEntity.WarpResult industrialColonies$bindStartSender(
            WarpDriveBlockEntity drive,
            Operation<WarpDriveBlockEntity.WarpResult> original,
            @Local(argsOnly = true) IPayloadContext context
    ) {
        if (!(context.player() instanceof ServerPlayer initiator)) {
            return WarpDriveBlockEntity.WarpResult.INVALID_DESTINATION;
        }
        return InterstellarWarpInitiatorScope.callAs(
                initiator, () -> original.call(drive));
    }

    @WrapOperation(
            method = SIMPLE_HANDLER,
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/waco0311/cosmowarp/block/entity/"
                            + "WarpDriveBlockEntity;registerHere()Z"),
            require = 1)
    private static boolean industrialColonies$gateRegister(
            WarpDriveBlockEntity drive,
            Operation<Boolean> original,
            @Local(argsOnly = true) IPayloadContext context
    ) {
        return context.player() instanceof ServerPlayer initiator
                && InterstellarWarpPolicy.mayMutateRoute(drive, initiator)
                && original.call(drive);
    }

    @WrapOperation(
            method = SELECT_HANDLER,
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/waco0311/cosmowarp/block/entity/"
                            + "WarpDriveBlockEntity;setSelectedId(Ljava/util/UUID;)V"),
            require = 1)
    private static void industrialColonies$gateSelection(
            WarpDriveBlockEntity drive,
            UUID selected,
            Operation<Void> original,
            @Local(argsOnly = true) IPayloadContext context
    ) {
        if (context.player() instanceof ServerPlayer initiator
                && InterstellarWarpPolicy.mayMutateRoute(drive, initiator)) {
            original.call(drive, selected);
        }
    }

    @WrapOperation(
            method = RENAME_HANDLER,
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/waco0311/cosmowarp/block/entity/"
                            + "WarpDriveBlockEntity;renamePoint(Ljava/util/UUID;"
                            + "Ljava/lang/String;)V"),
            require = 1)
    private static void industrialColonies$gateRename(
            WarpDriveBlockEntity drive,
            UUID point,
            String name,
            Operation<Void> original,
            @Local(argsOnly = true) IPayloadContext context
    ) {
        if (context.player() instanceof ServerPlayer initiator
                && InterstellarWarpPolicy.mayMutateRoute(drive, initiator)) {
            original.call(drive, point, name);
        }
    }
}
