package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.PlanetaryGravityCompatibility;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Retains every listener's veto and scales only a compensation that Ad Astra will actually apply. */
@Pseudo
@Mixin(targets = "earth.terrarium.adastra.api.events.AdAstraEvents$GravityTickEvent", remap = false)
public interface AdAstraAltitudeGravityMixin {
    @Inject(method = "fire", at = @At("RETURN"), require = 1)
    private static void industrialColonies$scaleCompensation(Level level, LivingEntity entity, Vec3 movement,
            BlockPos pos, CallbackInfoReturnable<Boolean> result) {
        PlanetaryGravityCompatibility.beforeCompensation(level, entity, result.getReturnValueZ());
    }
}
