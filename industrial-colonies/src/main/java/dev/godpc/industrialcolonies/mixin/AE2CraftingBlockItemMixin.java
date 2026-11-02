package dev.godpc.industrialcolonies.mixin;

import appeng.util.InteractionUtil;
import dev.godpc.industrialcolonies.AE2RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Guards AE2's shift-use crafting-unit downgrade while the block is held as an item. */
@Mixin(targets = "appeng.block.crafting.CraftingBlockItem", remap = false)
public abstract class AE2CraftingBlockItemMixin {
    @Inject(method = "use", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedHeldCraftingUnitDowngrade(
            Level level,
            Player player,
            InteractionHand hand,
            CallbackInfoReturnable<InteractionResultHolder<ItemStack>> callback
    ) {
        if (player instanceof ServerPlayer serverPlayer
                && InteractionUtil.isInAlternateUseMode(player)
                && !AE2RecipeStageGate.canRemoveUpgrade(
                        serverPlayer, level, ((BlockItem) (Object) this).getBlock())) {
            callback.setReturnValue(InteractionResultHolder.fail(player.getItemInHand(hand)));
        }
    }
}
