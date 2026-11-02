package dev.godpc.industrialcolonies.processing;

import com.simibubi.create.AllRecipeTypes;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.OnDatapackSyncEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

/** Index only exact-machine fan inputs; leave normal fan recipes' native caching untouched. */
public final class FanRecipeCache {
    private static final Map<RecipeManager, List<Ingredient>> INPUTS = new WeakHashMap<>();
    private static boolean registered;
    private FanRecipeCache() {}
    public static void register() {
        if (registered) return;
        registered = true;
        NeoForge.EVENT_BUS.addListener(FanRecipeCache::synced);
        NeoForge.EVENT_BUS.addListener(FanRecipeCache::stopped);
    }
    public static boolean tierSensitive(ItemStack stack, Level level) {
        if (level.isClientSide() || stack.isEmpty()) return false;
        synchronized (INPUTS) {
            for (Ingredient ingredient : INPUTS.computeIfAbsent(level.getRecipeManager(), FanRecipeCache::collect))
                if (ingredient.test(stack)) return true;
        }
        return false;
    }
    private static List<Ingredient> collect(RecipeManager manager) {
        List<Ingredient> inputs = new ArrayList<>();
        for (RecipeHolder<?> holder : manager.getRecipes()) {
            TieredRecipeBindings.Binding binding = TieredRecipeBindings.get(holder.value());
            if (binding == null || binding.machine() == null || binding.machine().blockIds().isEmpty()) continue;
            AllRecipeTypes family = binding.family().baseType();
            if (family == AllRecipeTypes.SPLASHING || family == AllRecipeTypes.HAUNTING)
                inputs.addAll(holder.value().getIngredients());
        }
        return List.copyOf(inputs);
    }
    private static void synced(OnDatapackSyncEvent event) { synchronized (INPUTS) { INPUTS.clear(); } }
    private static void stopped(ServerStoppedEvent event) { synchronized (INPUTS) { INPUTS.clear(); } }
}
