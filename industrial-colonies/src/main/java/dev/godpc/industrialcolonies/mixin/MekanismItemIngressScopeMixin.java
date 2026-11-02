package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import dev.godpc.industrialcolonies.transport.MekanismItemAdmission;
import mekanism.common.content.network.transmitter.LogisticalTransporterBase;
import mekanism.common.content.transporter.TransporterStack;
import mekanism.common.lib.inventory.TransitRequest;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Lab-only: scope path calculation, before native reservation and source extraction. */
@Mixin(value = LogisticalTransporterBase.class, remap = false)
public abstract class MekanismItemIngressScopeMixin {
    @WrapOperation(method = {"insert(Lnet/minecraft/world/level/block/entity/BlockEntity;Lnet/minecraft/core/BlockPos;Lmekanism/common/lib/inventory/TransitRequest;Lmekanism/api/text/EnumColor;IZLmekanism/common/content/network/transmitter/LogisticalTransporterBase$PathCalculator;)Lmekanism/common/lib/inventory/TransitRequest$TransitResponse;", "insertUnchecked(Lnet/minecraft/world/level/block/entity/BlockEntity;Lmekanism/common/lib/inventory/TransitRequest;Lmekanism/api/text/EnumColor;ZILmekanism/common/content/network/transmitter/LogisticalTransporterBase$PathCalculator;)Lmekanism/common/lib/inventory/TransitRequest$TransitResponse;"}, at = @At(value = "INVOKE",
            target = "Lmekanism/common/content/network/transmitter/LogisticalTransporterBase$PathCalculator;calculate(Lmekanism/common/content/transporter/TransporterStack;Lmekanism/common/lib/inventory/TransitRequest;Lnet/minecraft/world/level/block/entity/BlockEntity;Lmekanism/common/content/network/transmitter/LogisticalTransporterBase;IZ)Lmekanism/common/lib/inventory/TransitRequest$TransitResponse;"), require = 2)
    private TransitRequest.TransitResponse ic$newCalculatedRoute(LogisticalTransporterBase.PathCalculator<BlockEntity> calculator,
            TransporterStack stack, TransitRequest request, BlockEntity source, LogisticalTransporterBase start,
            int minimum, boolean execute, Operation<TransitRequest.TransitResponse> original) {
        return MekanismItemAdmission.calculate(stack, () -> original.call(calculator, stack, request, source, start, minimum, execute));
    }

    @WrapOperation(method = "insertUnchecked(JLmekanism/common/lib/inventory/TransitRequest;Lmekanism/api/text/EnumColor;ZI)Lmekanism/common/lib/inventory/TransitRequest$TransitResponse;", at = @At(value = "INVOKE",
            target = "Lmekanism/common/content/transporter/TransporterStack;recalculatePath(Lmekanism/common/lib/inventory/TransitRequest;Lmekanism/common/content/network/transmitter/LogisticalTransporterBase;IZ)Lmekanism/common/lib/inventory/TransitRequest$TransitResponse;"), require = 1)
    private TransitRequest.TransitResponse ic$newUncheckedRoute(TransporterStack stack, TransitRequest request,
            LogisticalTransporterBase start, int minimum, boolean execute, Operation<TransitRequest.TransitResponse> original) {
        return MekanismItemAdmission.calculate(stack, () -> original.call(stack, request, start, minimum, execute));
    }
}
