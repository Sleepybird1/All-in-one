package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="dev.simulated_team.simulated.content.blocks.docking_connector.DockingConnectorBlockEntity",remap=false)
public abstract class SimulatedAeDockMixin implements AeDockAccess {
 @Unique private AeDockService.Link ic$aeLink;
 public AeDockService.Link ic$aeLink(){return ic$aeLink;}
 public void ic$aeLink(AeDockService.Link link){ic$aeLink=link;}
 @Inject(method="tick",at=@At("TAIL"),remap=false)
 private void ic$refreshAe(CallbackInfo ci){AeDockService.refresh((BlockEntity)(Object)this);}
 @Inject(method={"unDock","remove"},at=@At("HEAD"),remap=false)
 private void ic$removeAe(CallbackInfo ci){AeDockService.invalidate((BlockEntity)(Object)this);}
 @Inject(method="setDock",at=@At("HEAD"),remap=false)
 private void ic$pairAe(@Coerce Object peer,boolean locked,org.joml.Quaterniondc rotation,org.joml.Vector3dc position,org.joml.Quaterniondc targetRotation,CallbackInfo ci){AeDockService.beforeSetDock((BlockEntity)(Object)this,peer,locked);}
}
