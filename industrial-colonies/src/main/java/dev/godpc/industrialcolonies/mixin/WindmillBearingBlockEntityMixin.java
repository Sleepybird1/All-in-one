package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity;
import dev.godpc.industrialcolonies.space.AmbientKineticPolicy;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Disables ambient windmill generation only in explicitly denied dimensions. */
@Mixin(WindmillBearingBlockEntity.class)
public abstract class WindmillBearingBlockEntityMixin {
    @Inject(
            method = "getGeneratedSpeed()F",
            at = @At("HEAD"),
            cancellable = true,
            require = 1
    )
    private void industrialColonies$suppressAmbientWind(
            CallbackInfoReturnable<Float> callback
    ) {
        WindmillBearingBlockEntity bearing = (WindmillBearingBlockEntity) (Object) this;
        if (AmbientKineticPolicy.deniesWind(bearing.getLevel())) {
            callback.setReturnValue(0.0F);
        }
    }
}
