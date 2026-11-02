package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import dev.godpc.industrialcolonies.space.*;
import appeng.api.storage.MEStorage;
import net.minecraft.world.level.block.entity.BlockEntity;
@Mixin(targets="appeng.blockentity.storage.DriveBlockEntity",remap=false)
public abstract class AE2ShipDriveMixin {
 @Inject(method="getCellInventory",at=@At("RETURN"),cancellable=true)
 private void ic$cell(int slot,CallbackInfoReturnable<MEStorage> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeStorage(cir.getReturnValue(),()->ShipAePolicy.allowed((BlockEntity)(Object)this),source->ShipAePolicy.allowedSource((BlockEntity)(Object)this,source)));
 }
}
