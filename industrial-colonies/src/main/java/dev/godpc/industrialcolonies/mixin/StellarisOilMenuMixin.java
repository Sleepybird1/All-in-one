package dev.godpc.industrialcolonies.mixin;

import com.st0x0ef.stellaris.common.blocks.entities.machines.FuelRefineryBlockEntity;
import dev.godpc.industrialcolonies.processing.SpaceOilIdentity;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;

@Pseudo
@Mixin(targets="com.st0x0ef.stellaris.common.menus.FuelRefineryMenu",remap=false)
public abstract class StellarisOilMenuMixin {
    @Shadow @Final private FuelRefineryBlockEntity blockEntity;
    @ModifyArg(method="<init>",at=@At(value="INVOKE",target="Lcom/st0x0ef/stellaris/common/menus/slot/SpecificFluidContainerSlot;<init>(Lnet/minecraft/world/Container;Lnet/minecraft/world/level/material/Fluid;IIIZ)V"),index=1,require=1)
    private Fluid industrialColonies$canonicalOilContainer(Fluid original){
        return SpaceOilIdentity.selected(blockEntity.getLevel(),original);
    }
}
