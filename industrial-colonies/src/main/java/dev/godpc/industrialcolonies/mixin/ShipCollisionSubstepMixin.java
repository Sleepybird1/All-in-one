package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.collision.CollisionDamageRuntime;
import dev.ryanhcode.sable.api.physics.PhysicsPipeline;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Read-only before-step hook. No active capture until a trusted server session is armed. */
@Pseudo
@Mixin(targets="dev.ryanhcode.sable.physics.impl.rapier.RapierPhysicsPipeline",remap=false)
public abstract class ShipCollisionSubstepMixin {
    @Shadow @Final private ServerLevel level;
    @Shadow @Final private Int2ObjectMap<ServerSubLevel> activeSubLevels;
    @Inject(method="physicsTick",at=@At(value="INVOKE",target="Ldev/ryanhcode/sable/physics/impl/rapier/Rapier3D;step(JD)V",shift=At.Shift.BEFORE),require=1)
    private void industrialColonies$captureBeforeStep(double dt,CallbackInfo ci){
        CollisionDamageRuntime.beforeStep(level,(PhysicsPipeline)(Object)this,activeSubLevels.values());
    }
}
