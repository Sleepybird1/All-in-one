package dev.godpc.industrialcolonies.client.jei;

import dev.godpc.industrialcolonies.TieredRecipeBindings;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import mezz.jei.api.ingredients.ITypedIngredient;
import mezz.jei.api.recipe.IFocus;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.RecipeIngredientRole;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;

import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

/** Shared identification and filtering for exact-machine JEI Uses lookups. */
public final class ExactMachineRecipeLookup {
    private static final Set<String> EXACT_MACHINE_ITEMS = TieredRecipeCatalog.load()
            .recipeFamilies().stream()
            .flatMap(family -> family.machines().stream())
            .filter(machine -> !machine.isBase())
            .map(machine -> machine.item())
            .collect(Collectors.toUnmodifiableSet());

    private ExactMachineRecipeLookup() {
    }

    /**
     * Resolves a Uses lookup for one non-base machine. JEI normally supplies
     * both INPUT and CATALYST focuses for the U key, although some public-API
     * callers supply INPUT alone. Both forms must resolve to the same exact
     * per-recipe index. Output lookups, mixed ingredients, and ordinary Create
     * base machines are deliberately excluded.
     */
    public static Optional<MachineUses> machineUses(IFocusGroup focuses) {
        if (focuses == null) {
            return Optional.empty();
        }
        var all = focuses.getAllFocuses();
        if (all.isEmpty()) {
            return Optional.empty();
        }

        ResourceLocation machineId = null;
        boolean hasInput = false;
        boolean hasCatalyst = false;
        for (IFocus<?> focus : all) {
            RecipeIngredientRole role = focus.getRole();
            if (role != RecipeIngredientRole.INPUT
                    && role != RecipeIngredientRole.CATALYST) {
                return Optional.empty();
            }

            Optional<ResourceLocation> candidate = itemId(focus.getTypedValue())
                    .filter(id -> EXACT_MACHINE_ITEMS.contains(id.toString()));
            if (candidate.isEmpty()) {
                return Optional.empty();
            }
            if (machineId != null && !machineId.equals(candidate.get())) {
                return Optional.empty();
            }
            machineId = candidate.get();
            hasInput |= role == RecipeIngredientRole.INPUT;
            hasCatalyst |= role == RecipeIngredientRole.CATALYST;
        }

        return hasInput && machineId != null
                ? Optional.of(new MachineUses(machineId, hasCatalyst))
                : Optional.empty();
    }

    public static boolean isExactMachineItem(ITypedIngredient<?> ingredient) {
        return itemId(ingredient).map(EXACT_MACHINE_ITEMS::contains).orElse(false);
    }

    public static boolean isBoundTo(Object candidate, ResourceLocation machineId) {
        Recipe<?> recipe = unwrap(candidate);
        TieredRecipeBindings.Binding binding = recipe == null
                ? null
                : TieredRecipeBindings.get(recipe);
        return binding != null
                && binding.machine() != null
                && machineId.toString().equals(binding.machine().item());
    }

    private static Optional<ResourceLocation> itemId(ITypedIngredient<?> ingredient) {
        if (ingredient == null) {
            return Optional.empty();
        }
        ItemStack stack = ingredient.getItemStack().orElse(ItemStack.EMPTY);
        if (stack.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(BuiltInRegistries.ITEM.getKey(stack.getItem()));
    }

    private static Recipe<?> unwrap(Object candidate) {
        if (candidate instanceof RecipeHolder<?> holder) {
            return holder.value();
        }
        return candidate instanceof Recipe<?> recipe ? recipe : null;
    }

    public record MachineUses(ResourceLocation machineId, boolean includesCatalyst) {
    }
}
