package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import com.llamalad7.mixinextras.sugar.Local;
import dev.godpc.industrialcolonies.space.FrozenWarpCrystalItemHandler;
import dev.waco0311.cosmowarp.Cosmonauticswarpdrive;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import net.neoforged.neoforge.items.IItemHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** Replaces Cosmowarp's exposed concrete crystal handler with a safe view. */
@Mixin(value = Cosmonauticswarpdrive.class, remap = false)
public abstract class CosmowarpCapabilityMixin {
    @ModifyReturnValue(
            method = "lambda$registerCapabilities$1(Ldev/waco0311/cosmowarp/block/"
                    + "entity/WarpDriveBlockEntity;Lnet/minecraft/core/Direction;)"
                    + "Lnet/neoforged/neoforge/items/IItemHandler;",
            at = @At("RETURN"),
            require = 1)
    private static IItemHandler industrialColonies$wrapCrystalCapability(
            IItemHandler original,
            @Local(argsOnly = true) WarpDriveBlockEntity drive
    ) {
        return new FrozenWarpCrystalItemHandler(drive, original);
    }
}
