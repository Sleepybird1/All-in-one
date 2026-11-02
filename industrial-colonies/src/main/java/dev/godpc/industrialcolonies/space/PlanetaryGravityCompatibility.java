package dev.godpc.industrialcolonies.space;

import java.lang.reflect.Method;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.neoforged.fml.ModList;

/** Aligns Ad Astra's gravity compensation with Cosmonautics' existing altitude taper. */
public final class PlanetaryGravityCompatibility {
    private PlanetaryGravityCompatibility() {}

    public static void beforeCompensation(Level level, LivingEntity entity, boolean allowed) {
        if (!allowed || !ModList.get().isLoaded("rocketnautics") || entity.isInWater()
                || entity.isInLava() || entity.isFallFlying() || entity.hasEffect(MobEffects.SLOW_FALLING)) return;
        try {
            double removed = ((Number) NativeApi.FACTOR.invoke(null, level, entity.getY())).doubleValue();
            if (removed == 0) return;
            float gravity;
            if (level.isClientSide && entity instanceof Player) {
                // Match Ad Astra's client-player branch, including its transient missing-data fallback.
                Object local = ClientApi.LOCAL_DATA.invoke(null);
                gravity = local == null ? 9.807f : ((Number) ClientApi.GRAVITY.invoke(local)).floatValue();
            } else {
                gravity = ((Number) NativeApi.GRAVITY.invoke(NativeApi.API, entity)).floatValue();
            }
            // Preserve native float rounding. The following native code adds this compensation;
            // subtract only the share removed by the native altitude taper.
            double compensation = (double) 0.08f - (double) (0.08f * gravity);
            entity.setDeltaMovement(entity.getDeltaMovement().add(0, -compensation * removed, 0));
        } catch (ReflectiveOperationException error) {
            throw new IllegalStateException("Installed planetary gravity API changed", error);
        }
    }

    private static final class NativeApi {
        static final Method FACTOR;
        static final Method GRAVITY;
        static final Object API;
        static {
            try {
                FACTOR = Class.forName("dev.devce.rocketnautics.content.physics.GlobalSpacePhysicsHandler")
                        .getMethod("calculateGravityFactor", Level.class, double.class);
                Class<?> type = Class.forName("earth.terrarium.adastra.api.systems.GravityApi");
                API = type.getField("API").get(null);
                GRAVITY = type.getMethod("getGravity", Entity.class);
            } catch (ReflectiveOperationException error) { throw new ExceptionInInitializerError(error); }
        }
    }

    /** Loaded only on the client; dedicated servers never resolve ClientData. */
    private static final class ClientApi {
        static final Method LOCAL_DATA;
        static final Method GRAVITY;
        static {
            try {
                LOCAL_DATA = Class.forName("earth.terrarium.adastra.client.utils.ClientData").getMethod("getLocalData");
                GRAVITY = Class.forName("earth.terrarium.adastra.api.systems.PlanetData").getMethod("gravity");
            } catch (ReflectiveOperationException error) { throw new ExceptionInInitializerError(error); }
        }
    }
}
