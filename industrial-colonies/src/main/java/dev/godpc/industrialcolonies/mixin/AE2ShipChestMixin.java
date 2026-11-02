package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import dev.godpc.industrialcolonies.space.*;
import appeng.api.storage.MEStorage;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.core.Direction;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
@Mixin(targets="appeng.blockentity.storage.MEChestBlockEntity",remap=false)
public abstract class AE2ShipChestMixin {
 @Unique private boolean ic$allowed() { return ShipAePolicy.allowed((BlockEntity)(Object)this); }
 @Inject(method="getInventory",at=@At("RETURN"),cancellable=true)
 private void ic$inventory(CallbackInfoReturnable<MEStorage> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeStorage(cir.getReturnValue(),this::ic$allowed,source->ShipAePolicy.allowedSource((BlockEntity)(Object)this,source)));
 }
 @Inject(method="getCellInventory",at=@At("RETURN"),cancellable=true)
 private void ic$cell(int slot,CallbackInfoReturnable<MEStorage> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeStorage(cir.getReturnValue(),this::ic$allowed,source->ShipAePolicy.allowedSource((BlockEntity)(Object)this,source)));
 }
 @Inject(method="isPowered",at=@At("HEAD"),cancellable=true)
 private void ic$power(CallbackInfoReturnable<Boolean> cir) {
  if(!((BlockEntity)(Object)this).getLevel().isClientSide && !ic$allowed())cir.setReturnValue(false);
 }
 @Inject(method="getFluidHandler",at=@At("RETURN"),cancellable=true)
 private void ic$fluid(Direction side,CallbackInfoReturnable<IFluidHandler> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeFluidStorage(cir.getReturnValue(),
   ()->ShipAePolicy.body((BlockEntity)(Object)this)==null));
 }
}
