package dev.godpc.industrialcolonies.mixin;

import dev.devce.rocketnautics.api.orbit.DeepSpaceHelper;
import dev.devce.rocketnautics.content.physics.AsteroidSpawner;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Pins random asteroid eligibility to Rocketnautics' canonical deep-space API. */
@Mixin(value = AsteroidSpawner.class, remap = false)
public abstract class AsteroidSpawnerMixin {
    @ModifyVariable(
            method = "onPlayerTick(Lnet/neoforged/neoforge/event/tick/PlayerTickEvent$Post;)V",
            at = @At("STORE"),
            ordinal = 0,
            require = 1)
    private static boolean industrialColonies$requireCanonicalDeepSpace(
            boolean installedEligibility,
            PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return false;
        }
        return DeepSpaceHelper.isDeepSpace(player.level());
    }
}
