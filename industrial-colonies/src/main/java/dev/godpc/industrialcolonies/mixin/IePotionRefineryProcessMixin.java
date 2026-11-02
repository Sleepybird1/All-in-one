package dev.godpc.industrialcolonies.mixin;

import blusunrize.immersiveengineering.api.multiblocks.blocks.env.IMultiblockLevel;
import blusunrize.immersiveengineering.common.blocks.multiblocks.process.*;
import com.llamalad7.mixinextras.injector.wrapoperation.*;
import dev.godpc.industrialcolonies.processing.PotionRefineryCompatibility;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.crafting.FluidIngredient;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="blusunrize.immersiveengineering.common.blocks.multiblocks.process.MultiblockProcessInMachine",remap=false)
public abstract class IePotionRefineryProcessMixin {
    @Inject(method="doProcessTick(Lblusunrize/immersiveengineering/common/blocks/multiblocks/process/ProcessContext$ProcessContextInMachine;Lblusunrize/immersiveengineering/api/multiblocks/blocks/env/IMultiblockLevel;)V",at=@At("HEAD"),cancellable=true,require=1)
    private void industrialColonies$hold(ProcessContext.ProcessContextInMachine<?> context,IMultiblockLevel level,CallbackInfo ci) {
        if(!PotionRefineryCompatibility.canProcess((MultiblockProcess<?,?>)(Object)this,context,level.getRawLevel())) ci.cancel();
    }
    @WrapOperation(method="processFinish(Lblusunrize/immersiveengineering/common/blocks/multiblocks/process/ProcessContext$ProcessContextInMachine;Lblusunrize/immersiveengineering/api/multiblocks/blocks/env/IMultiblockLevel;)V",at=@At(value="INVOKE",target="Lnet/neoforged/neoforge/fluids/crafting/FluidIngredient;test(Lnet/neoforged/neoforge/fluids/FluidStack;)Z"),require=1)
    private boolean industrialColonies$consume(FluidIngredient ingredient,FluidStack fluid,Operation<Boolean> original,ProcessContext.ProcessContextInMachine<?> context,IMultiblockLevel level) {
        return original.call(ingredient,PotionRefineryCompatibility.consumption((MultiblockProcess<?,?>)(Object)this,ingredient,fluid,level.getRawLevel()));
    }
}
