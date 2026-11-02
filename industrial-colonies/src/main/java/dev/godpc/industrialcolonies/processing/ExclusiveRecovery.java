package dev.godpc.industrialcolonies.processing;

/** Pure categorical recovery: a failed roll gives nothing; success chooses one and only one category. */
public final class ExclusiveRecovery {
    private ExclusiveRecovery() {}
    public static void validate(double recoveryChance, double[] weights) {
        probability(recoveryChance, "recovery_chance");
        if (weights.length == 0 || weights.length > 9) throw new IllegalArgumentException("1..9 exclusive results required");
        double sum = 0;
        for (double weight : weights) { probability(weight, "exclusive result chance"); sum += weight; }
        if (Math.abs(sum - 1) > 0.000001) throw new IllegalArgumentException("Exclusive result chances must sum to 1");
    }
    public static int select(double recoveryChance, double[] weights, double recoveryRoll, double choiceRoll) {
        validate(recoveryChance, weights);
        roll(recoveryRoll); roll(choiceRoll);
        if (recoveryRoll >= recoveryChance) return -1;
        double total = 0;
        for (double weight : weights) total += weight;
        double target = choiceRoll * total;
        double cumulative = 0;
        int lastPositive = -1;
        for (int i = 0; i < weights.length; i++) {
            if (weights[i] > 0) lastPositive = i;
            cumulative += weights[i];
            if (target < cumulative) return i;
        }
        return lastPositive; // Only possible from floating-point rounding at the upper boundary.
    }
    private static void probability(double value, String name) {
        if (!Double.isFinite(value) || value < 0 || value > 1) throw new IllegalArgumentException(name + " must be in [0,1]");
    }
    private static void roll(double value) {
        if (!Double.isFinite(value) || value < 0 || value >= 1) throw new IllegalArgumentException("Random roll must be in [0,1)");
    }
}
