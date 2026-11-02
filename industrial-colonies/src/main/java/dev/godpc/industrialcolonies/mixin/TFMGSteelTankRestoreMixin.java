package dev.godpc.industrialcolonies.mixin;

import com.drmangotea.tfmg.content.decoration.tanks.steel.SteelTankBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Rebuild the native derived tower classification; it is not stored in tank NBT. */
@Mixin(value = SteelTankBlockEntity.class, remap = false)
public abstract class TFMGSteelTankRestoreMixin {
    @Unique private boolean industrialColonies$restoreTower = true;

    @Inject(method = "read", at = @At("TAIL"))
    private void industrialColonies$afterRead(CallbackInfo ci) {
        industrialColonies$restoreTower = true;
    }

    @Inject(method = "lazyTick", at = @At("HEAD"))
    private void industrialColonies$restoreClassification(CallbackInfo ci) {
        if (!industrialColonies$restoreTower) return;
        var tank = (SteelTankBlockEntity) (Object) this;
        var level = tank.getLevel();
        if (level == null || level.isClientSide) return;
        if (!tank.isController()) {
            industrialColonies$restoreTower = false;
            return;
        }
        var pos = tank.getBlockPos();
        // Wait for the saved footprint and adjacent controllers; never load chunks here.
        if (!level.hasChunksAt(pos.offset(-1, 0, -1),
                pos.offset(tank.getWidth(), tank.getHeight(), tank.getWidth()))) return;
        tank.updateBoilerState();
        industrialColonies$restoreTower = false;
    }
}
