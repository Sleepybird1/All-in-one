package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.core.Holder;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionContents;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;

/** Colored water must remain potion fluid so filling can preserve its color. */
@Pseudo
@Mixin(targets = "com.simibubi.create.content.fluids.potion.PotionFluidHandler", remap = false)
public abstract class CreatePotionWaterContentsMixin {
    @WrapOperation(method = {"getFluidFromPotionItem", "getFluidFromPotion"},
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/alchemy/PotionContents;is(Lnet/minecraft/core/Holder;)Z"), require = 2)
    private static boolean industrialColonies$onlyPlainWater(PotionContents contents, Holder<Potion> potion,
                                                            Operation<Boolean> original) {
        return original.call(contents, potion) && contents.customColor().isEmpty();
    }
}
