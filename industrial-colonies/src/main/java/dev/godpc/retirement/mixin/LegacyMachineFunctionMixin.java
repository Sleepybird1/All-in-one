package dev.godpc.retirement.mixin;
import dev.godpc.retirement.RetiredMekanismMachines;
import mekanism.common.tile.base.TileEntityMekanism;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Freeze recipe work through the machine's normal operating predicate; keep ticking and inventory access. */
@Mixin(value=TileEntityMekanism.class,remap=false)
public abstract class LegacyMachineFunctionMixin {
 @Inject(method="canFunction",at=@At("HEAD"),cancellable=true,require=1,remap=false)
 private void ic$retired(CallbackInfoReturnable<Boolean> result){
  if(RetiredMekanismMachines.contains(((TileEntityMekanism)(Object)this).getBlockState()))result.setReturnValue(false);
 }
}
