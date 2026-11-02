package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.blocks.entities.machines.PumpjackBlockEntity;
import dev.godpc.industrialcolonies.processing.SpaceOilIdentity;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.blocks.entities.machines.PumpjackBlockEntity",remap=false)
public abstract class StellarisOilPumpMixin {
    @ModifyArg(method="tick",at=@At(value="INVOKE",target="Ldev/architectury/fluid/FluidStack;create(Lnet/minecraft/world/level/material/Fluid;J)Ldev/architectury/fluid/FluidStack;"),index=0,require=1)
    private Fluid industrialColonies$canonicalOilOutput(Fluid original){
        return SpaceOilIdentity.selected(((PumpjackBlockEntity)(Object)this).getLevel(),original);
    }
    @Inject(method="tick",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/chunk/ChunkAccess;stellaris$setChunkOilLevel(I)V"),cancellable=true,require=1)
    private void industrialColonies$holdBeforeDepletingOil(CallbackInfo ci){
        var pump=(PumpjackBlockEntity)(Object)this;
        if(!Boolean.getBoolean("industrial_colonies.canonicalSpaceOil")) return;
        var stored=pump.getResultTank().getFluidInTank(0);
        var selected=SpaceOilIdentity.selected(pump.getLevel(),com.st0x0ef.stellaris.common.registry.FluidRegistry.OIL_STILL.get());
        if(!stored.isEmpty()&&!selected.isSame(stored.getFluid())) ci.cancel();
    }
}
