package dev.godpc.industrialcolonies.mixin;

import java.util.function.BooleanSupplier;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import net.sprocketgames.create_aeronautics_automated_logistics.service.ShipMaterializationService;
import net.sprocketgames.create_aeronautics_automated_logistics.service.ShipMaterializationService.MaterializationRequest;
import net.sprocketgames.create_aeronautics_automated_logistics.service.ShipMaterializationService.MaterializationResult;
import net.sprocketgames.create_aeronautics_automated_logistics.service.ShipMaterializationService.MaterializationResultType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Preserve Sable ownership while a newly unloaded body has no serialization pointer. */
@Pseudo
@Mixin(value=ShipMaterializationService.class, remap=false)
public abstract class AeronauticsHoldingPointerMixin {
    @Unique private static boolean industrialColonies$reportedPendingPointer;

    @Inject(method="materializeStoredBodyAt(Lnet/sprocketgames/create_aeronautics_automated_logistics/service/ShipMaterializationService$MaterializationRequest;Ljava/util/function/BooleanSupplier;)Lnet/sprocketgames/create_aeronautics_automated_logistics/service/ShipMaterializationService$MaterializationResult;",
        at=@At(value="INVOKE",target="Lnet/sprocketgames/create_aeronautics_automated_logistics/materialization/StoredBodyPointer;fromSable(Ldev/ryanhcode/sable/sublevel/storage/holding/GlobalSavedSubLevelPointer;)Lnet/sprocketgames/create_aeronautics_automated_logistics/materialization/StoredBodyPointer;"), cancellable=true, require=1)
    private void industrialColonies$waitForPointer(MaterializationRequest request, BooleanSupplier attemptGate, CallbackInfoReturnable<MaterializationResult> cir) {
        var level=request.server().getLevel(request.dimension());
        if(level==null || request.sableShipId().isEmpty()) return;
        var container=ServerSubLevelContainer.getContainer(level);
        if(container==null) return;
        var holding=container.getHoldingChunkMap().getHoldingSubLevel(request.sableShipId().orElseThrow());
        if(holding==null || holding.pointer()!=null) return;
        // Do not manufacture a pointer, consume the in-memory body, or spawn a replacement.
        if(!industrialColonies$reportedPendingPointer) {
            org.slf4j.LoggerFactory.getLogger("IndustrialColoniesHoldingPointer").warn("Deferring materialization: Sable owns an unsaved holding body; waiting for its native serialization pointer.");
            industrialColonies$reportedPendingPointer=true;
        }
        cir.setReturnValue(new MaterializationResult(MaterializationResultType.SABLE_HOLDING_BODY_WAITING,false,
            "sable_holding_pointer_pending","Sable retains the ship in memory while its serialization pointer is pending."));
    }
}
