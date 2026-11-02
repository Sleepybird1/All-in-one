package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="dev.simulated_team.simulated.content.blocks.docking_connector.DockingConnectorBlockEntity",remap=false)
public abstract class SimulatedChemicalDockMixin implements ChemicalDockAccess {
 @Unique private long ic$chemicalEpoch;
 @Unique private ChemicalDockService.Lease ic$chemicalLease;
 public long ic$chemicalEpoch(){return ic$chemicalEpoch;}
 public ChemicalDockService.Lease ic$chemicalLease(){return ic$chemicalLease;}
 public void ic$chemicalLease(ChemicalDockService.Lease lease){ic$chemicalLease=lease;}
 public void ic$revokeChemical(){ic$chemicalEpoch++;if(ic$chemicalLease!=null)ic$chemicalLease.view.revoke();ic$chemicalLease=null;}
 @Inject(method={"unDock","remove"},at=@At("HEAD"),remap=false)
 private void ic$invalidate(CallbackInfo ci){ChemicalDockService.invalidate((BlockEntity)(Object)this);}
 @Inject(method="setDock",at=@At("HEAD"),remap=false)
 private void ic$pair(@Coerce Object peer,boolean locked,org.joml.Quaterniondc rotation,org.joml.Vector3dc position,org.joml.Quaterniondc targetRotation,CallbackInfo ci) {
  ChemicalDockService.beforeSetDock((BlockEntity)(Object)this,peer,locked);
 }
}
