package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.AE2RecipeStageGate;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Guards AE2 storage-cell disassembly, which runs from item use rather than a crafting menu. */
@Mixin(
        targets = {
                "appeng.items.storage.BasicStorageCell",
                "appeng.items.tools.powered.AbstractPortableCell"
        },
        remap = false
)
public abstract class AE2StorageCellItemMixin {
    @Inject(
            method = "disassembleDrive(Lnet/minecraft/world/item/ItemStack;"
                    + "Lnet/minecraft/world/level/Level;"
                    + "Lnet/minecraft/world/entity/player/Player;)Z",
            at = @At("HEAD"),
            cancellable = true,
            remap = false
    )
    private void industrialColonies$denyLockedCellDisassembly(
            ItemStack stack,
            Level level,
            Player player,
            CallbackInfoReturnable<Boolean> callback
    ) {
        if (player instanceof ServerPlayer serverPlayer
                && !AE2RecipeStageGate.canDisassemble(serverPlayer, level, stack.getItem())) {
            callback.setReturnValue(false);
        }
    }
}
