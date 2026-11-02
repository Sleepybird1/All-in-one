package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.WarpDriveCrystalSlotAccess;
import dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

/** Exposes only the owning drive of Cosmowarp's private crystal handler. */
@Mixin(
        targets = "dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity$1",
        remap = false)
public abstract class CosmowarpCrystalSlotOwnerMixin implements WarpDriveCrystalSlotAccess {
    @Shadow
    @Final
    private WarpDriveBlockEntity this$0;

    @Override
    public WarpDriveBlockEntity industrialColonies$owner() {
        return this$0;
    }
}
