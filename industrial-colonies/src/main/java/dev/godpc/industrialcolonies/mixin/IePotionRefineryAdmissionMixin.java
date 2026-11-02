package dev.godpc.industrialcolonies.mixin;

import blusunrize.immersiveengineering.common.blocks.multiblocks.process.*;
import dev.godpc.industrialcolonies.processing.PotionRefineryCompatibility;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets="blusunrize.immersiveengineering.common.blocks.multiblocks.process.MultiblockProcess",remap=false)
public abstract class IePotionRefineryAdmissionMixin {
    @Inject(method="canProcess",at=@At("HEAD"),cancellable=true,require=1)
    private void industrialColonies$hold(ProcessContext<?> context,Level level,CallbackInfoReturnable<Boolean> cir) {
        if(!PotionRefineryCompatibility.canProcess((MultiblockProcess<?,?>)(Object)this,context,level)) cir.setReturnValue(false);
    }
}
