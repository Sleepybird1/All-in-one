package dev.godpc.industrialcolonies.mixin;

import com.iafenvoy.iceandfire.entity.DragonBaseEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A veto only: large dragons still obey native global, tame and block protections. */
@Pseudo
@Mixin(targets="com.iafenvoy.iceandfire.entity.util.dragon.DragonUtils",remap=false)
public abstract class IafDragonSizeGriefingMixin {
    @Inject(method={
        "canGrief(Lcom/iafenvoy/iceandfire/entity/DragonBaseEntity;)Z",
        "canSoftGrief(Lcom/iafenvoy/iceandfire/entity/DragonBaseEntity;)Z"
    },at=@At("HEAD"),cancellable=true,require=2)
    private static void industrialColonies$smallDragonProtection(DragonBaseEntity dragon,CallbackInfoReturnable<Boolean> cir) {
        if(dragon.getDragonStage()<4)cir.setReturnValue(false);
    }
}
