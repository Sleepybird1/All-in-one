package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import dev.godpc.industrialcolonies.space.*;
import appeng.api.networking.IGrid;
import appeng.api.config.Actionable;
import appeng.api.config.PowerMultiplier;
@Mixin(targets="appeng.me.service.EnergyService",remap=false)
public abstract class AE2ShipEnergyMixin {
 @Shadow @Final private appeng.me.Grid grid;
 @Inject(method="isNetworkPowered",at=@At("HEAD"),cancellable=true)
 private void ic$power(CallbackInfoReturnable<Boolean> cir) { if(!ShipAePolicy.allowed(grid))cir.setReturnValue(false); }
 @Inject(method="extractAEPower",at=@At("HEAD"),cancellable=true)
 private void ic$drain(double amount,Actionable mode,PowerMultiplier multiplier,CallbackInfoReturnable<Double> cir) {
  if(!ShipAePolicy.allowed(grid))cir.setReturnValue(0.0);
 }
}
