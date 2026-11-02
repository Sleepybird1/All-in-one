package dev.godpc.industrialcolonies.mixin;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import dev.godpc.industrialcolonies.space.*;
import appeng.api.networking.*;
import appeng.api.storage.MEStorage;
import appeng.api.stacks.KeyCounter;
import net.minecraft.nbt.CompoundTag;
import java.util.List;
@Mixin(targets="appeng.me.service.StorageService",remap=false)
public abstract class AE2ShipStorageServiceMixin {
 @Unique private IGrid ic$grid;
 @Shadow @Final private List<?> globalProviders;
 @Inject(method="addNode",at=@At("HEAD"))
 private void ic$bind(IGridNode node,CompoundTag saved,CallbackInfo ci) { ic$grid=node.getGrid(); }
 @Unique private boolean ic$allowed() {
  if(ic$grid==null || ic$grid.isEmpty())return false;
  if(!ShipAePolicy.allowed(ic$grid))return false;
  for(IGridNode node:ic$grid.getNodes())
   if(node instanceof appeng.me.InWorldGridNode world
     && dev.ryanhcode.sable.Sable.HELPER.getContaining(node.getLevel(),world.getLocation())!=null)
    return globalProviders.isEmpty(); // Unmeasured global storage cannot bypass the cap.
  return true;
 }
 @Inject(method="getInventory",at=@At("RETURN"),cancellable=true)
 private void ic$inventory(CallbackInfoReturnable<MEStorage> cir) {
  if(cir.getReturnValue()!=null)cir.setReturnValue(new ShipAeStorage(cir.getReturnValue(),this::ic$allowed,source->ShipAePolicy.allowedSource(ic$grid,source)));
 }
 @Inject(method="getCachedInventory",at=@At("HEAD"),cancellable=true)
 private void ic$cached(CallbackInfoReturnable<KeyCounter> cir) { if(!ic$allowed())cir.setReturnValue(new KeyCounter()); }
}
