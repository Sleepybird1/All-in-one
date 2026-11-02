package dev.godpc.industrialcolonies.mixin;

import earth.terrarium.adastra.common.utils.KeybindManager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/** Short powered excursions without reducing existing stored energy or oxygen. */
@Pseudo
@Mixin(targets = "earth.terrarium.adastra.common.items.armor.JetSuitItem", remap = false)
public abstract class AdAstraJetSuitBalanceMixin {
    // Native canFly compares stored energy > 0. Match admission to the complete
    // debit below, before either thrust method runs. Native creative bypass stays.
    // Native particles and powered-elytra admission use this same canFly method.
    @ModifyConstant(method = "canFly", constant = @Constant(longValue = 0L), require = 1)
    private long industrialColonies$completePropulsionCost(long original, Player player, ItemStack stack) {
        return KeybindManager.sprintDown(player) ? 999L : 499L;
    }

    @ModifyConstant(method = "inventoryTick", constant = @Constant(intValue = 50), require = 1)
    private int industrialColonies$upwardCost(int original) {
        return 500;
    }

    @ModifyConstant(method = "inventoryTick", constant = @Constant(intValue = 100), require = 1)
    private int industrialColonies$sprintCost(int original) {
        return 1000;
    }
}
