package dev.godpc.industrialcolonies.geology;

/** Minecraft compass convention: north is negative Z, east is positive X. */
public final class ProspectingBearing {
    private static final String[] DIRECTIONS = {"north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"};
    private ProspectingBearing() {}
    public static String direction(long dx, long dz) {
        return DIRECTIONS[Math.floorMod(Math.round(Math.atan2(dx, -dz) / (Math.PI / 4)), 8)];
    }
    public static String strength(long distanceSquared) {
        if (distanceSquared <= 64L * 64L) return "very_strong";
        if (distanceSquared <= 200L * 200L) return "strong";
        if (distanceSquared <= 500L * 500L) return "moderate";
        return "weak";
    }
    /** Stable uncertainty per sample area: repeated clicks never reroll a better bearing. */
    public static String roughDirection(long worldSeed, String family, int sampleX, int sampleZ, long dx, long dz) {
        long salt = worldSeed ^ family.hashCode()
                ^ ((long) Math.floorDiv(sampleX, 16) * 341873128712L)
                ^ ((long) Math.floorDiv(sampleZ, 16) * 132897987541L);
        salt = (salt ^ (salt >>> 30)) * 0xbf58476d1ce4e5b9L;
        salt = (salt ^ (salt >>> 27)) * 0x94d049bb133111ebL;
        salt ^= salt >>> 31;
        double distance = Math.hypot(dx, dz);
        double spread = distance > 500 ? 45 : distance > 200 ? 30 : 15;
        double bias = ((salt >>> 11) * 0x1.0p-53 * 2 - 1) * Math.toRadians(spread);
        long sector = Math.round((Math.atan2(dx, -dz) + bias) / (Math.PI / 2));
        return DIRECTIONS[Math.floorMod(sector, 4) * 2];
    }
}
