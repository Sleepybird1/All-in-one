package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import dev.godpc.industrialcolonies.processing.StellarisDieselIdentity;
import net.minecraft.world.level.material.Fluid;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

/** Only the diesel comparison changes; tank index, oxygen and suit-module gates remain native. */
@Pseudo
@Mixin(targets={"com.st0x0ef.stellaris.common.blocks.entities.machines.DieselGeneratorBlockEntity$1",
        "com.st0x0ef.stellaris.common.items.armors.SpaceSuit$1",
        "com.st0x0ef.stellaris.common.items.armors.AbstractSpaceArmor$Chestplate$1",
        "com.st0x0ef.stellaris.common.items.armors.AbstractSpaceArmor$AbstractSpaceChestplate$1"},remap=false)
public abstract class StellarisDieselFilterMixin {
    @WrapOperation(method="isFluidValid",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/material/Fluid;isSame(Lnet/minecraft/world/level/material/Fluid;)Z"),require=1)
    private boolean industrialColonies$canonicalDiesel(Fluid actual,Fluid expected,Operation<Boolean> original){
        return original.call(actual,expected)||StellarisDieselIdentity.alias(actual,expected);
    }
}
