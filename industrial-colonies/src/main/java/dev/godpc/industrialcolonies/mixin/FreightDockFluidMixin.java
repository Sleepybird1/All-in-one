package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.FreightDockFluidPolicy;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

@Pseudo
@Mixin(targets="dev.simulated_team.simulated.content.blocks.docking_connector.DockingConnectorTank",remap=false)
public abstract class FreightDockFluidMixin {
 @Unique private BlockEntity ic$freightOwner;
 @Inject(method="<init>",at=@At("RETURN"))
 private void ic$captureOwner(@Coerce Object owner,CallbackInfo ci){ic$freightOwner=(BlockEntity)owner;}
 @Inject(method={"insert","extract"},at=@At("HEAD"),cancellable=true)
 private void ic$requireUnloading(@Coerce Object fluid,long amount,boolean simulate,Runnable snapshot,CallbackInfoReturnable<Long> cir){
  if(!FreightDockFluidPolicy.allowed(ic$freightOwner))cir.setReturnValue(0L);
 }
 // Native readSnapshot must remain unconditional: rollback is not new transfer.
}
