package dev.godpc.industrialcolonies;

import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Vats name attachments by operation; HashMap iteration is not a physical machine position. */
public final class VatAttachmentRequirements {
    private VatAttachmentRequirements() {}

    public static boolean matches(List<String> required, Collection<String> actual) {
        if (required == null || actual == null || required.size() > 3 || actual.size() > 3
                || required.size() != actual.size()) return false;
        if (required.stream().anyMatch(value -> value == null || value.isBlank())
                || actual.stream().anyMatch(value -> value == null || value.isBlank())) return false;
        return frequencies(required).equals(frequencies(actual));
    }

    private static Map<String, Integer> frequencies(Collection<String> values) {
        Map<String, Integer> counts = new HashMap<>();
        for (String value : values) {
            counts.merge(value, 1, Integer::sum);
        }
        return counts;
    }
}
