package dev.godpc.industrialcolonies.processing;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Only the new categorical serializer is registered; no duplicate Create recipe type. */
public final class ProcessingRecipeRuntime {
    private static final DeferredRegister<RecipeSerializer<?>> SERIALIZERS =
            DeferredRegister.create(Registries.RECIPE_SERIALIZER, "industrial_colonies");
    public static final DeferredHolder<RecipeSerializer<?>, RecipeSerializer<ExclusiveMillingRecipe>> EXCLUSIVE_MILLING =
            SERIALIZERS.register("exclusive_milling", ExclusiveMillingRecipe.Serializer::new);
    public static final DeferredHolder<RecipeSerializer<?>, RecipeSerializer<PoweredPolarizingRecipe>> POWERED_POLARIZING =
            SERIALIZERS.register("powered_polarizing", PoweredPolarizingRecipe.Serializer::new);
    private static boolean registered;
    private ProcessingRecipeRuntime() {}
    public static void register(IEventBus modBus) {
        if (registered) return;
        registered = true;
        SERIALIZERS.register(modBus);
        AssemblyFanRecipes.register(modBus);
        ManualCinnabar.register();
        FanRecipeCache.register();
    }
}
