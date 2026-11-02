package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.NuclearFusionOutputGuard;
import dev.godpc.industrialcolonies.NuclearFusionPendingJob;
import net.minecraft.nbt.CompoundTag;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Reject a new batch before either fuel tank is drained; do not cancel the reactor tick. */
@Pseudo
@Mixin(targets="igentuman.nc.multiblock.fusion.FusionReaction",remap=false)
public class NuclearFusionOutputAdmissionMixin {
    @Unique private final NuclearFusionPendingJob ic$pendingJob=new NuclearFusionPendingJob();

    @Inject(method="consumeInputs",at=@At("HEAD"),cancellable=true,remap=false)
    private void ic$requireAllOutputSpace(@Coerce Object controller,@Coerce Object recipe,CallbackInfoReturnable<Boolean> cir) {
        if(!NuclearFusionOutputGuard.canStart(controller,recipe)||!ic$pendingJob.prepare(controller,recipe))cir.setReturnValue(false);
    }

    @Inject(method="tick",at=@At("HEAD"),remap=false)
    private void ic$restorePending(@Coerce Object controller,@Coerce Object cache,CallbackInfo ci){ic$pendingJob.beforeTick(this,controller);}

    @Inject(method="matchRecipe",at=@At("HEAD"),cancellable=true,remap=false)
    private void ic$neverRematchConsumedFuel(@Coerce Object controller,@Coerce Object level,CallbackInfoReturnable<Object> cir){
        if(NuclearFusionPendingJob.pending(this))cir.setReturnValue(null);
    }

    @Inject(method="save",at=@At("TAIL"),remap=false)
    private void ic$savePending(CompoundTag tag,CallbackInfo ci){ic$pendingJob.save(this,tag);}
    @Inject(method="load",at=@At("TAIL"),remap=false)
    private void ic$loadPending(CompoundTag tag,CallbackInfo ci){ic$pendingJob.load(this,tag);}
    @Inject(method="idle",at=@At("HEAD"),remap=false)
    private void ic$holdIdle(@Coerce Object controller,CallbackInfo ci){ic$pendingJob.beforeIdle(this);}
    @Inject(method="idle",at=@At("TAIL"),remap=false)
    private void ic$restoreIdle(@Coerce Object controller,CallbackInfo ci){ic$pendingJob.afterIdle(this);}

    // Only the third fuelConsumed read controls active processing. Earlier reads
    // must retain the native pending recipe and prevent a second fuel consumption.
    @ModifyExpressionValue(method="tick",at=@At(value="FIELD",target="Ligentuman/nc/multiblock/fusion/FusionReaction;fuelConsumed:Z",ordinal=2,opcode=180),require=1)
    private boolean ic$holdBlockedBatch(boolean consumed,@Coerce Object controller,@Coerce Object cache) {
        return consumed&&NuclearFusionOutputGuard.canContinue(this,controller);
    }
}
