package dev.godpc.industrialcolonies.mixin;

import com.simibubi.create.foundation.blockEntity.SmartBlockEntity;
import com.simibubi.create.foundation.blockEntity.SmartBlockEntityTicker;
import dev.godpc.industrialcolonies.CreateMachineContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Wraps the complete virtual SmartBlockEntity tick in an exception-safe owner context. */
@Mixin(SmartBlockEntityTicker.class)
public abstract class SmartBlockEntityTickerMixin {
    @Redirect(
            method = "tick(Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;"
                    + "Lnet/minecraft/world/level/block/state/BlockState;"
                    + "Lnet/minecraft/world/level/block/entity/BlockEntity;)V",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/simibubi/create/foundation/blockEntity/SmartBlockEntity;tick()V"
            )
    )
    private void industrialColonies$wrapCompleteTick(SmartBlockEntity blockEntity) {
        try (CreateMachineContext.Scope ignored = CreateMachineContext.enter(blockEntity)) {
            blockEntity.tick();
        }
    }
}
