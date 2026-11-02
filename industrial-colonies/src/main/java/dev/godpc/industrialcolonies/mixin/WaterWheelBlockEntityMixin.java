package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity;
import dev.godpc.industrialcolonies.space.AmbientKineticPolicy;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Disables ambient water-wheel generation only in explicitly denied dimensions. */
@Mixin(WaterWheelBlockEntity.class)
public abstract class WaterWheelBlockEntityMixin {
    @Inject(
            method = "getGeneratedSpeed()F",
            at = @At("HEAD"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$suppressAmbientHydro(
            CallbackInfoReturnable<Float> callback
    ) {
        WaterWheelBlockEntity wheel = (WaterWheelBlockEntity) (Object) this;
        if (AmbientKineticPolicy.deniesHydro(wheel.getLevel())) {
            callback.setReturnValue(0.0F);
        }
    }
}
