package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import dev.godpc.industrialcolonies.space.collision.ShipCollisionProbe;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.At;

/** Native queue remains untouched. Damage capture is inert until explicitly armed. */
@Pseudo
@Mixin(targets="dev.ryanhcode.sable.physics.impl.rapier.RapierPhysicsPipeline",remap=false)
public abstract class ShipCollisionObservationMixin {
    @Shadow @Final private ServerLevel level;
    @ModifyExpressionValue(method="processCollisionEffects",at=@At(value="INVOKE",
            target="Ldev/ryanhcode/sable/physics/impl/rapier/Rapier3D;clearCollisions(J)[D"),require=1)
    private double[] industrialColonies$observeNativeQueue(double[] original){
        dev.godpc.industrialcolonies.space.collision.CollisionDamageRuntime.observe(level,level.getGameTime(),original);
        return ShipCollisionProbe.observe(level,level.getGameTime(),original);
    }
}
