package dev.godpc.industrialcolonies;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

/** Immutable ordered read snapshots; callers invalidate while holding their mutation lock. */
public final class VersionedReadOnlySnapshot<K, V> {
    private record Entry<K, V>(long version, Map<K, V> value) {}
    private final AtomicLong version = new AtomicLong();
    private volatile Entry<K, V> cached;

    public void invalidate() { version.incrementAndGet(); }

    public Map<K, V> get(Supplier<Map<K, V>> copyUnderSourceLock) {
        long before = version.get();
        var entry = cached;
        if (entry != null && entry.version() == before) return entry.value();
        // The source API already returns a detached copy. Preserve order and null semantics.
        var snapshot = Collections.unmodifiableMap(new LinkedHashMap<>(copyUnderSourceLock.get()));
        if (version.get() == before) cached = new Entry<>(before, snapshot);
        // A concurrent mutation may make this one detached read old, as with the original API;
        // it must never publish that read as the cache for the new epoch.
        return snapshot;
    }
}
