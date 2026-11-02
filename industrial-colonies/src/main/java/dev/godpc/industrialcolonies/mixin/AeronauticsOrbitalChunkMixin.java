package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.OrbitalChunkAvailability;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.service.VehicleRoutePlaybackService;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Correct only the route-restoration chunk check for high-altitude orbital ships. */
@Pseudo
@Mixin(value = VehicleRoutePlaybackService.class, remap = false)
public abstract class AeronauticsOrbitalChunkMixin {
    @Redirect(method = {"tryMaterializeUnloadedShip", "tryMaterializePendingRuntime"},
        at = @At(value = "INVOKE", target = "Lnet/minecraft/server/level/ServerLevel;isLoaded(Lnet/minecraft/core/BlockPos;)Z"),
        require = 3, expect = 3, allow = 3)
    private boolean industrialColonies$orbitalChunkLoaded(ServerLevel level, BlockPos position) {
        return OrbitalChunkAvailability.loadedForMaterialization(level, position);
    }
}
