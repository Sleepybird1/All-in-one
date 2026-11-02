package dev.godpc.industrialcolonies.mixin;

import igentuman.nr.radiation.storage.EntityRadiationData;
import igentuman.nr.recipe.MutationRecipe;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Reject impossible doses before native entity serialization, without caching entity state. */
@Pseudo
@Mixin(targets = "igentuman.nr.radiation.simulation.entity.MutationProcessor", remap = false)
public abstract class RadiationMutationDoseGuardMixin {
    @Redirect(method = "tryMutate", at = @At(value = "INVOKE",
            target = "Ligentuman/nr/recipe/MutationRecipe;matchesEntity(Lnet/minecraft/world/entity/LivingEntity;)Z"), require = 1)
    private static boolean industrialColonies$eligibleBeforeMatching(
            MutationRecipe recipe, LivingEntity candidate,
            ServerLevel level, LivingEntity entity, EntityRadiationData radiation) {
        return recipe.inRange(radiation.svTotalCareer(), radiation.svPerHour())
                && recipe.matchesEntity(candidate);
    }
}
