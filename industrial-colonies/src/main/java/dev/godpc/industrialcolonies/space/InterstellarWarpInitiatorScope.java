package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import java.util.function.Supplier;
import net.minecraft.server.level.ServerPlayer;

/**
 * Binds one server-network sender to the synchronous Cosmowarp START call.
 * Direct or unscoped calls deliberately have no interstellar authority.
 */
public final class InterstellarWarpInitiatorScope {
    private static final ThreadLocal<ServerPlayer> CURRENT = new ThreadLocal<>();

    private InterstellarWarpInitiatorScope() {
    }

    public static ServerPlayer current() {
        return CURRENT.get();
    }

    public static <T> T callAs(ServerPlayer initiator, Supplier<T> operation) {
        Objects.requireNonNull(initiator, "initiator");
        Objects.requireNonNull(operation, "operation");
        if (CURRENT.get() != null) {
            throw new IllegalStateException("nested interstellar warp initiator scope");
        }
        CURRENT.set(initiator);
        try {
            return operation.get();
        } finally {
            CURRENT.remove();
        }
    }
}
