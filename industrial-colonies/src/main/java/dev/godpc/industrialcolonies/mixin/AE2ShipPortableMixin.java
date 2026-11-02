package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import dev.godpc.industrialcolonies.space.*;
import appeng.api.storage.MEStorage;
import appeng.api.implementations.menuobjects.ItemMenuHost;
@Mixin(targets={"appeng.items.contents.PortableCellMenuHost","appeng.helpers.WirelessTerminalMenuHost"},remap=false)
public abstract class AE2ShipPortableMixin {
 @Unique private boolean ic$allowed() {
  var host=(ItemMenuHost<?>)(Object)this;
  return dev.ryanhcode.sable.Sable.HELPER.getContaining(host.getPlayer())==null;
 }
 @Inject(method="getInventory",at=@At("RETURN"),cancellable=true)
 private void ic$inventory(CallbackInfoReturnable<MEStorage> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeStorage(cir.getReturnValue(),this::ic$allowed));
 }
 @Inject(method="insert",at=@At("HEAD"),cancellable=true)
 private void ic$insert(net.minecraft.world.entity.player.Player player,appeng.api.stacks.AEKey key,long amount,
   appeng.api.config.Actionable mode,CallbackInfoReturnable<Long> cir) {
  if(!ic$allowed())cir.setReturnValue(0L);
 }
 @Inject(method="extractAEPower",at=@At("HEAD"),cancellable=true)
 private void ic$power(double n,appeng.api.config.Actionable action,appeng.api.config.PowerMultiplier multiplier,CallbackInfoReturnable<Double> cir) {
  if(!ic$allowed())cir.setReturnValue(0.0);
 }
}
