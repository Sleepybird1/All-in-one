package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.blocks.entities.machines.DieselGeneratorBlockEntity;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;

/** Match the native five-unit request to the exact stored, admitted canonical identity. */
@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.blocks.entities.machines.DieselGeneratorBlockEntity",remap=false)
public abstract class StellarisDieselBurnMixin {
    @ModifyArg(method="tick",at=@At(value="INVOKE",target="Ldev/architectury/fluid/FluidStack;create(Lnet/minecraft/world/level/material/Fluid;J)Ldev/architectury/fluid/FluidStack;"),index=0,require=1)
    private Fluid industrialColonies$consumeStoredDiesel(Fluid original){
        var stored=((DieselGeneratorBlockEntity)(Object)this).getDieselTank().getFluidInTank(0);
        return StellarisDieselIdentity.alias(stored.getFluid(),original)?stored.getFluid():original;
    }
}
