package dev.godpc.industrialcolonies.food;

import java.util.OptionalInt;

/** Pure milestone math for the bounded cuisine-health reward. */
public final class FoodDiversityMilestones {
    /** One additional heart is awarded at each threshold. */
    public static final int[] UNIQUE_FOOD_MILESTONES = {10, 25, 45, 70, 100};
    public static final int HEALTH_POINTS_PER_MILESTONE = 2;
    public static final int MAX_BONUS_HEALTH =
            UNIQUE_FOOD_MILESTONES.length * HEALTH_POINTS_PER_MILESTONE;

    private FoodDiversityMilestones() {
    }

    public static int completedMilestones(int uniqueFoodCount) {
        int completed = 0;
        for (int threshold : UNIQUE_FOOD_MILESTONES) {
            if (uniqueFoodCount < threshold) {
                break;
            }
            completed++;
        }
        return completed;
    }

    public static int bonusHealth(int uniqueFoodCount) {
        return completedMilestones(uniqueFoodCount) * HEALTH_POINTS_PER_MILESTONE;
    }

    public static OptionalInt nextMilestone(int uniqueFoodCount) {
        for (int threshold : UNIQUE_FOOD_MILESTONES) {
            if (uniqueFoodCount < threshold) {
                return OptionalInt.of(threshold);
            }
        }
        return OptionalInt.empty();
    }
}
