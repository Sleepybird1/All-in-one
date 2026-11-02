package dev.godpc.industrialcolonies.client.jei;

import dev.godpc.industrialcolonies.TieredRecipeBindings;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Carries the recipe currently being drawn by a Create JEI category into the
 * small reusable animation objects. Create's animation API only receives
 * coordinates, so without this context it cannot distinguish a native recipe
 * from one bound to a Copper Press, Copper Deployer, and so on.
 */
public final class JeiMachineVisualContext {
    private static final ThreadLocal<Deque<Recipe<?>>> ACTIVE_RECIPES =
            ThreadLocal.withInitial(ArrayDeque::new);

    private JeiMachineVisualContext() {
    }

    public static void push(Recipe<?> recipe) {
        ACTIVE_RECIPES.get().push(recipe);
    }

    public static void pop() {
        Deque<Recipe<?>> recipes = ACTIVE_RECIPES.get();
        if (!recipes.isEmpty()) {
            recipes.pop();
        }
        if (recipes.isEmpty()) {
            ACTIVE_RECIPES.remove();
        }
    }

    public static TieredRecipeCatalog.Machine machine(Recipe<?> recipe) {
        TieredRecipeBindings.Binding binding = TieredRecipeBindings.get(recipe);
        return binding == null ? null : binding.machine();
    }

    public static TieredRecipeCatalog.Machine activeMachine() {
        Deque<Recipe<?>> recipes = ACTIVE_RECIPES.get();
        return recipes.isEmpty() ? null : machine(recipes.peek());
    }

    /** Replaces only the machine body; shafts, heads, hands and fluids stay animated by Create. */
    public static BlockState selectedMachineState(BlockState original) {
        TieredRecipeCatalog.Machine machine = activeMachine();
        if (machine == null || machine.blockIds().isEmpty()) {
            return original;
        }

        ResourceLocation id = ResourceLocation.tryParse(machine.blockIds().getFirst());
        if (id == null || !BuiltInRegistries.BLOCK.containsKey(id)) {
            return original;
        }
        return BuiltInRegistries.BLOCK.get(id).defaultBlockState();
    }

    public static ItemStack machineStack(Recipe<?> recipe) {
        TieredRecipeCatalog.Machine machine = machine(recipe);
        if (machine == null) {
            return ItemStack.EMPTY;
        }

        ResourceLocation id = ResourceLocation.tryParse(machine.item());
        if (id == null || !BuiltInRegistries.ITEM.containsKey(id)) {
            return ItemStack.EMPTY;
        }
        return new ItemStack(BuiltInRegistries.ITEM.get(id));
    }
}
