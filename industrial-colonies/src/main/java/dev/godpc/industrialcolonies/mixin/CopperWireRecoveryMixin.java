package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.CopperWireRecovery;
import net.minecraft.core.NonNullList;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets="blusunrize.immersiveengineering.api.crafting.ArcRecyclingRecipe",remap=false)
public class CopperWireRecoveryMixin {
    @Inject(method={"generateActualOutput","getBaseOutputs","getItemOutputs"},at=@At("RETURN"),cancellable=true,remap=false)
    private void ic$capCopperRecovery(CallbackInfoReturnable<NonNullList<ItemStack>> cir) {
        cir.setReturnValue(CopperWireRecovery.limit(this,cir.getReturnValue()));
    }
}
