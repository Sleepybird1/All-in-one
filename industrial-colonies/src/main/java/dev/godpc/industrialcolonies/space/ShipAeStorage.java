package dev.godpc.industrialcolonies.space;

import appeng.api.storage.MEStorage;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.KeyCounter;
import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import net.minecraft.network.chat.Component;
import java.util.function.BooleanSupplier;

/** Rechecks every operation, including SIMULATE and references retained before assembly. */
public final class ShipAeStorage implements MEStorage {
    private final MEStorage delegate;
    private final BooleanSupplier allowed;
    private final java.util.function.Predicate<IActionSource> sourceAllowed;
    public ShipAeStorage(MEStorage delegate, BooleanSupplier allowed) {
        this(delegate, allowed, source -> true);
    }
    public ShipAeStorage(MEStorage delegate, BooleanSupplier allowed, java.util.function.Predicate<IActionSource> sourceAllowed) {
        this.sourceAllowed = java.util.Objects.requireNonNull(sourceAllowed);
        this.delegate = java.util.Objects.requireNonNull(delegate);
        this.allowed = java.util.Objects.requireNonNull(allowed);
    }
    @Override public long insert(AEKey key, long amount, Actionable mode, IActionSource source) {
        return allowed.getAsBoolean() && sourceAllowed.test(source) ? delegate.insert(key, amount, mode, source) : 0;
    }
    @Override public long extract(AEKey key, long amount, Actionable mode, IActionSource source) {
        return allowed.getAsBoolean() && sourceAllowed.test(source) ? delegate.extract(key, amount, mode, source) : 0;
    }
    @Override public void getAvailableStacks(KeyCounter out) {
        if (allowed.getAsBoolean()) delegate.getAvailableStacks(out);
    }
    @Override public boolean isPreferredStorageFor(AEKey key, IActionSource source) {
        return allowed.getAsBoolean() && sourceAllowed.test(source) && delegate.isPreferredStorageFor(key, source);
    }
    @Override public Component getDescription() {
        return allowed.getAsBoolean() ? delegate.getDescription() : Component.literal(ShipAePolicy.DISABLED_MESSAGE);
    }
}
