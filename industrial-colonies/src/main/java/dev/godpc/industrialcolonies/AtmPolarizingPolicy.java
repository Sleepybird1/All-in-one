package dev.godpc.industrialcolonies;

/** Native TFMG power and qualified-tick requirement, scoped to the final ATM conversion. */
public final class AtmPolarizingPolicy {
    public static final int MIN_POWER = 1_000_000;
    public static final int MAX_POWER = 1_000_000_000;
    public static final int MIN_TICKS = 6_000;
    public static final float ACTIVE_RESISTANCE = 0.5f;
    public static final int MAX_TICKS = 1_200_000;
    public static final String INPUT = "allthemodium:raw_allthemodium";
    public static final String OUTPUT = "allthemodium:allthemodium_ingot";
    private AtmPolarizingPolicy() {}
    public static boolean applies(String input, String output) {
        return INPUT.equals(input) && OUTPUT.equals(output);
    }
    public static boolean managed(String input, java.util.Collection<String> outputs) {
        return INPUT.equals(input) && outputs.contains(OUTPUT);
    }
    public static boolean admissible(int inputCount, int ingredients, int outputs, int outputCount, double chance, boolean matches) {
        return inputCount == 1 && ingredients == 1 && outputs == 1 && outputCount == 1 && chance == 1 && matches;
    }
    public static int requiredTicks(int recipeTicks) {
        if (recipeTicks < 0 || recipeTicks > MAX_TICKS)
            throw new IllegalArgumentException("Polarizing duration must be between 0 and " + MAX_TICKS);
        return Math.max(MIN_TICKS, recipeTicks);
    }
    public static int validatePower(int power) {
        if (power < 1 || power > MAX_POWER) throw new IllegalArgumentException("Polarizing power must be1 to " + MAX_POWER);
        return power;
    }
    public static int validateExplicitTicks(int ticks) {
        if (ticks < 1 || ticks > MAX_TICKS) throw new IllegalArgumentException("Polarizing time must be1 to " + MAX_TICKS);
        return ticks;
    }
    public static float resistanceForPower(int requestedPower) { return Math.min(30f, 500_000f / validatePower(requestedPower)); }
    public static boolean supplyReady(int power, boolean overloaded, long generated, long demanded) {
        return supplyReady(power, overloaded, generated, demanded, MIN_POWER);
    }
    public static boolean supplyReady(int power, boolean overloaded, long generated, long demanded, int requestedPower) {
        // Native network sums are ints; never admit a topology whose native arithmetic can overflow.
        return requestedPower >= 1 && requestedPower <= MAX_POWER && power >= requestedPower && !overloaded && generated >= demanded && demanded >= power
            && generated <= Integer.MAX_VALUE && demanded <= Integer.MAX_VALUE;
    }
    public static int nativeAccumulatorWithdrawal(int ownGeneration, int totalGeneration, int demand, double conversion) {
        if (ownGeneration <= 0 || totalGeneration < ownGeneration || demand < 0
            || !Double.isFinite(conversion) || conversion <= 0) throw new IllegalArgumentException("Invalid native source accounting");
        int nativeShare = (int) Math.max(0f, (float) ownGeneration / (float) totalGeneration * (float) demand);
        return Math.max(1, (int) (nativeShare / conversion));
    }
}
