package dev.godpc.industrialcolonies;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.function.ToIntBiFunction;

/** Pure output reservation. Keys must include components, not just registry IDs. */
public final class VatOutputPacking {
    private VatOutputPacking() {}

    public record Bin<K>(K key, int amount, int capacity) {
        public Bin {
            if (amount < 0 || capacity < 0 || amount > capacity || (key == null && amount != 0))
                throw new IllegalArgumentException("Invalid output bin");
        }
    }

    public record Product<K>(K key, int amount) {
        public Product {
            Objects.requireNonNull(key);
            if (amount < 0) throw new IllegalArgumentException("Negative product amount");
        }
    }

    /**
     * Returns a complete immutable replacement snapshot or no plan; never mutates input.
     * The limit function supplies native item-stack/slot limits (or fluid tank capacity).
     * Reserve all possible chance outputs before rolling so blocked ticks never reroll.
     */
    public static <K> Optional<List<Bin<K>>> plan(List<Bin<K>> existing,
            List<Product<K>> products, ToIntBiFunction<Integer, K> nativeLimit) {
        var planned = new ArrayList<>(existing);
        for (var product : products) {
            int remaining = product.amount();
            // Existing compatible stacks/tanks first, then empty space.
            for (int pass = 0; pass < 2 && remaining > 0; pass++) {
                for (int slot = 0; slot < planned.size() && remaining > 0; slot++) {
                    var bin = planned.get(slot);
                    boolean empty = bin.amount() == 0;
                    if (pass == 0 ? empty || !Objects.equals(bin.key(), product.key()) : !empty)
                        continue;
                    int limit = Math.min(bin.capacity(), Math.max(0, nativeLimit.applyAsInt(slot, product.key())));
                    int moved = Math.min(remaining, Math.max(0, limit - bin.amount()));
                    if (moved != 0) {
                        planned.set(slot, new Bin<>(product.key(), bin.amount() + moved, bin.capacity()));
                        remaining -= moved;
                    }
                }
            }
            if (remaining != 0) return Optional.empty();
        }
        return Optional.of(List.copyOf(planned));
    }
}
