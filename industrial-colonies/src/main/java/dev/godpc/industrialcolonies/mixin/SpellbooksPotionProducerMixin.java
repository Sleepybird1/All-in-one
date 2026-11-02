package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

@Pseudo
@Mixin(targets="io.redspace.ironsspellbooks.fluids.PotionFluid",remap=false)
public abstract class SpellbooksPotionProducerMixin {
    @ModifyReturnValue(method={"of(ILnet/minecraft/world/item/alchemy/PotionContents;Lio/redspace/ironsspellbooks/fluids/PotionFluid$BottleType;)Lnet/neoforged/neoforge/fluids/FluidStack;",
            "from(Lnet/minecraft/world/item/ItemStack;)Lnet/neoforged/neoforge/fluids/FluidStack;"},at=@At("RETURN"),require=2)
    private static FluidStack industrialColonies$canonicalPotion(FluidStack original) {
        return PotionIdentityRuntime.produced(original);
    }
}
