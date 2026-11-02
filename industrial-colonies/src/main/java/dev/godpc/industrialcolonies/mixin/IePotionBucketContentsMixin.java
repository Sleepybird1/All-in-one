package dev.godpc.industrialcolonies.mixin;

import blusunrize.immersiveengineering.common.fluids.PotionFluid.PotionBottleType;
import blusunrize.immersiveengineering.common.register.IEDataComponents;
import blusunrize.immersiveengineering.common.register.IEFluids;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import com.simibubi.create.AllFluids;
import com.simibubi.create.AllDataComponents;
import dev.godpc.industrialcolonies.processing.PotionIdentityRuntime;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/** Keep the complete potion component when the native bucket projects only its base. */
@Pseudo
@Mixin(targets = "blusunrize.immersiveengineering.common.items.PotionBucketItem$FluidHandler", remap = false)
public abstract class IePotionBucketContentsMixin {
    @Shadow @Final private ItemStack stack;

    @ModifyReturnValue(method = "getFluid", at = @At("RETURN"), require = 1)
    private FluidStack industrialColonies$preserveCustomPotion(FluidStack original) {
        // Empty handlers and ordinary registered potions/water retain native behavior.
        if (original.isEmpty()) return original;
        var contents = stack.get(DataComponents.POTION_CONTENTS);
        if (contents == null || (contents.customColor().isEmpty() && contents.customEffects().isEmpty())) return PotionIdentityRuntime.produced(original);
        boolean canonical = AllFluids.POTION.get().isSame(original.getFluid());
        if (original.getFluid() != Fluids.WATER && original.getFluid() != IEFluids.POTION.get() && !canonical) return original;
        FluidStack result = original.getFluid() == IEFluids.POTION.get() || canonical
                ? original.copy() : new FluidStack(IEFluids.POTION.get(), original.getAmount());
        result.set(DataComponents.POTION_CONTENTS, contents);
        if(canonical) result.set(AllDataComponents.POTION_FLUID_BOTTLE_TYPE,com.simibubi.create.content.fluids.potion.PotionFluid.BottleType.REGULAR);
        else result.set(IEDataComponents.POTION_BOTTLE_TYPE, PotionBottleType.REGULAR);
        return PotionIdentityRuntime.produced(result);
    }
}
