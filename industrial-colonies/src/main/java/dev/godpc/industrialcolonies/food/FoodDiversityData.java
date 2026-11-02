package dev.godpc.industrialcolonies.food;

import com.mojang.serialization.Codec;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;

/** Immutable, serialized record of the food item types a player has eaten. */
public record FoodDiversityData(Set<ResourceLocation> eatenFoods) {
    public static final Codec<FoodDiversityData> CODEC = ResourceLocation.CODEC
            .listOf()
            .xmap(FoodDiversityData::fromList, FoodDiversityData::orderedFoods);

    public FoodDiversityData {
        eatenFoods = Set.copyOf(eatenFoods);
    }

    public FoodDiversityData() {
        this(Set.of());
    }

    public boolean hasEaten(ResourceLocation foodId) {
        return eatenFoods.contains(foodId);
    }

    public int uniqueFoodCount() {
        return eatenFoods.size();
    }

    public FoodDiversityData withFood(ResourceLocation foodId) {
        if (hasEaten(foodId)) {
            return this;
        }

        Set<ResourceLocation> updated = new HashSet<>(eatenFoods);
        updated.add(foodId);
        return new FoodDiversityData(updated);
    }

    private static FoodDiversityData fromList(List<ResourceLocation> foodIds) {
        return new FoodDiversityData(new HashSet<>(foodIds));
    }

    private List<ResourceLocation> orderedFoods() {
        return eatenFoods.stream()
                .sorted(Comparator.comparing(ResourceLocation::toString))
                .toList();
    }
}
