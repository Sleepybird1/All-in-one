package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import com.simibubi.create.AllDataComponents;
import com.simibubi.create.AllFluids;
import com.simibubi.create.content.fluids.potion.PotionFluid.BottleType;
import io.redspace.ironsspellbooks.registries.ComponentRegistry;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.fluids.FluidStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Preserve Create bottle metadata on an already-admitted Spellbooks conversion. */
@Pseudo
@Mixin(targets = "io.redspace.ironsspellbooks.fluids.PotionFluid", remap = false)
public abstract class SpellbooksCreateBottleMixin {
    @ModifyReturnValue(method = "from(Lnet/neoforged/neoforge/fluids/FluidStack;)Lnet/minecraft/world/item/ItemStack;",
            at = @At("RETURN"), require = 1)
    private static ItemStack industrialColonies$createBottle(ItemStack original, FluidStack source) {
        if (original.isEmpty() || !AllFluids.POTION.get().isSame(source.getFluid())
                || source.has(ComponentRegistry.POTION_BOTTLE_TYPE)) return original;
        BottleType type = source.get(AllDataComponents.POTION_FLUID_BOTTLE_TYPE);
        if (type == BottleType.SPLASH) return original.transmuteCopy(Items.SPLASH_POTION);
        if (type == BottleType.LINGERING) return original.transmuteCopy(Items.LINGERING_POTION);
        return original;
    }
}
