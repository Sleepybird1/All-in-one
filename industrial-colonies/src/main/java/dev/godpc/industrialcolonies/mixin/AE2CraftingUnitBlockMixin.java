package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.AE2RecipeStageGate;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Exact recipe-ID checks for in-world AE2 crafting-unit upgrade and downgrade transforms. */
@Mixin(targets = "appeng.block.crafting.AbstractCraftingUnitBlock", remap = false)
public abstract class AE2CraftingUnitBlockMixin {
    @Inject(method = "upgrade", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedCraftingUnitUpgrade(
            ItemStack upgrade,
            BlockState state,
            Level level,
            BlockPos pos,
            Player player,
            BlockHitResult hit,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (player instanceof ServerPlayer serverPlayer
                && !AE2RecipeStageGate.canApplyUpgrade(serverPlayer, level, upgrade)) {
            callback.setReturnValue(false);
        }
    }

    @Inject(method = "removeUpgrade", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$denyLockedCraftingUnitDowngrade(
            Level level,
            Player player,
            BlockPos pos,
            BlockState state,
            CallbackInfoReturnable<InteractionResult> callback
    ) {
        if (player instanceof ServerPlayer serverPlayer
                && !AE2RecipeStageGate.canRemoveUpgrade(
                        serverPlayer, level, (Block) (Object) this)) {
            callback.setReturnValue(InteractionResult.FAIL);
        }
    }
}
