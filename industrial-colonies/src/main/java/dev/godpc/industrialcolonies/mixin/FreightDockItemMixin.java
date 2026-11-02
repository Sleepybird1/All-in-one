package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.FreightDockFluidPolicy;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;

/** Gate native capability operations without hiding or mutating physical storage. */
@Pseudo
@Mixin(targets="dev.simulated_team.simulated.content.blocks.docking_connector.DockingConnectorDuoInventory",remap=false)
public abstract class FreightDockItemMixin {
 @Unique private BlockEntity ic$freightOwner;
 @Unique private BlockEntity ic$freightPeer;
 @Inject(method="<init>",at=@At("RETURN"))
 private void ic$capture(@Coerce Object owner,@Coerce Object peer,CallbackInfo ci){ic$freightOwner=(BlockEntity)owner;ic$freightPeer=(BlockEntity)peer;}
 @Unique private boolean ic$allowed(){return FreightDockFluidPolicy.itemsAllowed(ic$freightOwner)&&FreightDockFluidPolicy.itemsAllowed(ic$freightPeer);}
 @Inject(method="insertSlot",at=@At("HEAD"),cancellable=true)
 private void ic$insert(ItemStack stack,int slot,boolean simulate,CallbackInfoReturnable<ItemStack> cir){if(!ic$allowed())cir.setReturnValue(stack);}
 @Inject(method={"insertGeneral","extractGeneral"},at=@At("HEAD"),cancellable=true)
 private void ic$general(@Coerce Object item,int amount,boolean simulate,CallbackInfoReturnable<Integer> cir){if(!ic$allowed())cir.setReturnValue(0);}
 @Inject(method="extractSlot",at=@At("HEAD"),cancellable=true)
 private void ic$extract(int slot,int amount,boolean simulate,CallbackInfoReturnable<ItemStack> cir){if(!ic$allowed())cir.setReturnValue(ItemStack.EMPTY);}
}
