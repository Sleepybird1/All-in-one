package dev.godpc.industrialcolonies.geology;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.function.Predicate;

/** Surface projections must remain in their owning vein, except the approved tiny-patch families. */
public final class SurfaceOutcropPolicy {
    private SurfaceOutcropPolicy() {}

    public static boolean allowsDetachedPatch(String spacingFamily) {
        return "iron".equals(spacingFamily) || "copper".equals(spacingFamily) || "coal".equals(spacingFamily);
    }

    /** Call only after the exposure roll succeeds; the supplied geometry must already honor ownership. */
    public static <T> Predicate<T> permittedPositions(String spacingFamily, Collection<T> ownedGeometry) {
        if (allowsDetachedPatch(spacingFamily)) return ignored -> true;
        Set<T> positions = new HashSet<>(ownedGeometry);
        return positions::contains;
    }
}
