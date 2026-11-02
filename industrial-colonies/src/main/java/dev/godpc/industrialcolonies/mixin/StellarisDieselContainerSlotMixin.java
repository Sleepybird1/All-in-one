package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

/** Preserve the slot's native empty/container handling, adding only the canonical diesel identity. */
@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.menus.slot.SpecificFluidContainerSlot",remap=false)
public abstract class StellarisDieselContainerSlotMixin {
    @Shadow @Final private Fluid fluid;
    @ModifyExpressionValue(method="mayPlace",at=@At(value="INVOKE",target="Ldev/architectury/fluid/FluidStack;getFluid()Lnet/minecraft/world/level/material/Fluid;"),require=1)
    private Fluid industrialColonies$recognizeCanonicalDiesel(Fluid actual){
        return StellarisDieselIdentity.alias(actual,fluid)?fluid:actual;
    }
}
