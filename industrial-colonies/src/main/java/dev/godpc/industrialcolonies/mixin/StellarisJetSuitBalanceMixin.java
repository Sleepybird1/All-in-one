package dev.godpc.industrialcolonies.mixin;

import dev.architectury.fluid.FluidStack;
import com.st0x0ef.stellaris.common.utils.Utils;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Charge each native propulsion branch without changing oxygen, tank contents or motion. */
@Pseudo
@Mixin(targets = "com.st0x0ef.stellaris.common.items.armors.JetSuit$Suit", remap = false)
public abstract class StellarisJetSuitBalanceMixin {
    @Redirect(method = "inventoryTick",
            at = @At(value = "INVOKE", target = "Ldev/architectury/fluid/FluidStack;isEmpty()Z"), require = 2)
    private boolean industrialColonies$requireUsableBoost(FluidStack fuel, ItemStack stack, Level level,
                                                         Entity entity, int slot, boolean selected) {
        // Native boost returns without motion unless these conditions hold, but its
        // caller otherwise still charges fuel and can starve the vertical branch.
        return fuel.isEmpty() || fuel.getAmount() < 5 || !(entity instanceof Player player)
                || !player.isFallFlying()
                || !(Utils.isLivingInJetSuit(player) || Utils.isLivingInSpaceSuit(player));
    }

    @Redirect(method = {"normalFlyModeMovement", "hoverModeMovement", "elytraModeMovement"},
            at = @At(value = "INVOKE", target = "Ldev/architectury/fluid/FluidStack;isEmpty()Z"), require = 3)
    private boolean industrialColonies$requireCompleteFuel(FluidStack fuel) {
        return fuel.isEmpty() || fuel.getAmount() < 5;
    }

    @ModifyArg(method = {"inventoryTick", "normalFlyModeMovement", "hoverModeMovement", "elytraModeMovement"},
            at = @At(value = "INVOKE", target = "Ldev/architectury/fluid/FluidStack;create(Lnet/minecraft/world/level/material/Fluid;J)Ldev/architectury/fluid/FluidStack;"), index = 1, require = 4)
    private long industrialColonies$propulsionCost(long original) {
        return 5;
    }

    @ModifyConstant(method = {"inventoryTick", "normalFlyModeMovement", "hoverModeMovement", "elytraModeMovement"},
            constant = @Constant(intValue = 20), require = 4)
    private int industrialColonies$payEveryPropulsionCall(int original) {
        return 0;
    }
}
