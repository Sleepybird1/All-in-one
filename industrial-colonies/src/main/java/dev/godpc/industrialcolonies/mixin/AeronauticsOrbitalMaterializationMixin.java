package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.OrbitalChunkAvailability;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.service.ShipMaterializationService;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Pseudo
@Mixin(value = ShipMaterializationService.class, remap = false)
public abstract class AeronauticsOrbitalMaterializationMixin {
    @Redirect(method = "materializeStoredBodyAt(Lnet/sprocketgames/create_aeronautics_automated_logistics/service/ShipMaterializationService$MaterializationRequest;Ljava/util/function/BooleanSupplier;)Lnet/sprocketgames/create_aeronautics_automated_logistics/service/ShipMaterializationService$MaterializationResult;",
        at = @At(value = "INVOKE", target = "Lnet/minecraft/server/level/ServerLevel;isLoaded(Lnet/minecraft/core/BlockPos;)Z"),
        require = 1, expect = 1, allow = 1)
    private boolean industrialColonies$orbitalTargetChunkLoaded(ServerLevel level, BlockPos position) {
        return OrbitalChunkAvailability.loadedForMaterialization(level, position);
    }
}
