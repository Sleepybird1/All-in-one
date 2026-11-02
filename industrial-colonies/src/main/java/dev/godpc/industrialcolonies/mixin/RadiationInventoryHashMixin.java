package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.RadiationInventoryHash;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "igentuman.nr.radiation.simulation.inventory.InventoryRadCache", remap = false)
public abstract class RadiationInventoryHashMixin {
    @Inject(method = "computeHash", at = @At("HEAD"), cancellable = true, require = 1)
    private static void industrialColonies$withoutVanillaSlotMaterialization(
            LivingEntity entity, CallbackInfoReturnable<Integer> callback) {
        callback.setReturnValue(RadiationInventoryHash.compute(entity));
    }
}
