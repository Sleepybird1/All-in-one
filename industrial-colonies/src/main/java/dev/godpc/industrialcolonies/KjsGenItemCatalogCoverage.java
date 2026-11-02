package dev.godpc.industrialcolonies;

import java.util.*;
import java.util.function.Function;
import java.util.function.Supplier;

/** Authoring coverage: JEI identities win; omitted registered items may use their real default stack. */
public final class KjsGenItemCatalogCoverage<T> {
    private final Set<String> jeiIds = new HashSet<>();
    private final Map<String, T> choices = new LinkedHashMap<>();
    private final Function<T, String> key;
    private int refused;

    public KjsGenItemCatalogCoverage(Function<T, String> key) { this.key = key; }

    public void addJei(String id, Supplier<T> encode) {
        if (!valid(id)) return;
        // Claim the ID before encoding: an invalid variant must never turn into a bare fallback.
        jeiIds.add(id);
        add(encode);
    }

    public void addRegistered(String id, Supplier<T> encode) {
        if (valid(id) && !jeiIds.contains(id)) add(encode);
    }

    private void add(Supplier<T> encode) {
        try {
            T value = Objects.requireNonNull(encode.get());
            choices.putIfAbsent(Objects.requireNonNull(key.apply(value)), value);
        } catch (RuntimeException invalid) { refused++; }
    }

    private static boolean valid(String id) {
        return id != null && !id.equals("minecraft:air") && id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+");
    }
    public Map<String, T> choices() { return Collections.unmodifiableMap(choices); }
    public int refused() { return refused; }
}
