package dev.godpc.industrialcolonies.space.station;

import java.util.Locale;
import java.util.Optional;

/** Explicit role assigned to a Sable moving sublevel. */
public enum StationRole {
    SHIP,
    STATION;

    public static Optional<StationRole> parse(String value) {
        if (value == null || value.isBlank()) {
            return Optional.empty();
        }
        try {
            return Optional.of(valueOf(value.toUpperCase(Locale.ROOT)));
        } catch (IllegalArgumentException ignored) {
            return Optional.empty();
        }
    }
}
