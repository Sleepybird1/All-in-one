package dev.godpc.industrialcolonies;

import com.simibubi.create.AllRecipeTypes;
import com.simibubi.create.content.processing.sequenced.SequencedAssemblyRecipe;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SingleRecipeInput;
import net.neoforged.neoforge.items.ItemStackHandler;
import net.neoforged.neoforge.items.wrapper.RecipeWrapper;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/** Exact recipe-id enforcement and tiered-type discovery for Create machines. */
public final class CreateRecipeStageGate {
    private static final Object RECIPE_ID_CACHE_LOCK = new Object();
    private static final Map<Recipe<?>, ResourceLocation> RECIPE_IDS = new IdentityHashMap<>();
    private static final Object FAMILY_TYPES_LOCK = new Object();
    private static final Map<AllRecipeTypes, List<RecipeType<?>>> FAMILY_TYPES =
            new EnumMap<>(AllRecipeTypes.class);

    private CreateRecipeStageGate() {
    }

    static void clearRecipeIdCache() {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            RECIPE_IDS.clear();
        }
    }

    /**
     * Replaces Create's single-type lookup with base plus tiered family types.
     * Base recipes retain their original priority, followed by catalog order.
     */
    public static <I extends RecipeInput, R extends Recipe<I>> Optional<RecipeHolder<R>> find(
            AllRecipeTypes family,
            I input,
            Level level
    ) {
        RecipeInput matchingInput = matchingInput(family, input);
        for (RecipeType<?> type : recipeTypes(family)) {
            for (RecipeHolder<?> holder : matchingRecipes(level.getRecipeManager(), type, matchingInput, level)) {
                if (canUse(level, holder)) {
                    return Optional.of(castHolder(holder));
                }
            }
        }
        return Optional.empty();
    }

    /** Aggregates all matching recipes for direct-list Create call sites such as FillingBySpout. */
    public static List<RecipeHolder<?>> matchingAllowedRecipes(
            AllRecipeTypes family,
            RecipeInput input,
            Level level
    ) {
        return matchingAllowedRecipes(family, input, level, CreateMachineContext.current());
    }

    public static List<RecipeHolder<?>> matchingAllowedRecipes(
            AllRecipeTypes family,
            RecipeInput input,
            Level level,
            BlockEntity machine
    ) {
        List<RecipeHolder<?>> allowed = new ArrayList<>();
        RecipeInput matchingInput = matchingInput(family, input);
        for (RecipeType<?> type : recipeTypes(family)) {
            for (RecipeHolder<?> holder : matchingRecipes(level.getRecipeManager(), type, matchingInput, level)) {
                if (canUse(level, holder, machine)) {
                    allowed.add(holder);
                }
            }
        }
        return allowed;
    }

    /** CuttingRecipe requires RecipeWrapper even for a one-item saw/Ponder lookup.
     * Other recipe families (notably filling) retain their native input type. */
    private static RecipeInput matchingInput(AllRecipeTypes family, RecipeInput input) {
        if (family == AllRecipeTypes.CUTTING && input instanceof SingleRecipeInput single) {
            ItemStackHandler inventory = new ItemStackHandler(1);
            inventory.setStackInSlot(0, single.item().copy());
            return new RecipeWrapper(inventory);
        }
        return input;
    }

    /** Parent recipes are authorized before Create extracts their next nested assembly step. */
    public static List<RecipeHolder<SequencedAssemblyRecipe>> allowedSequencedAssemblies(Level level) {
        List<RecipeHolder<SequencedAssemblyRecipe>> allowed = new ArrayList<>();
        for (RecipeType<?> type : recipeTypes(AllRecipeTypes.SEQUENCED_ASSEMBLY)) {
            for (RecipeHolder<?> holder : allRecipes(level.getRecipeManager(), type)) {
                if (holder.value() instanceof SequencedAssemblyRecipe && canUse(level, holder)) {
                    allowed.add(castHolder(holder));
                }
            }
        }
        return allowed;
    }

    /** Used when Create has a holder but its method signature does not expose Level. */
    public static boolean canUseCurrent(RecipeHolder<?> holder) {
        BlockEntity machine = CreateMachineContext.current();
        if (!machineMatches(holder.value(), machine)) {
            return false;
        }
        if (RecipeStageGate.requiredStage(holder.id()) == null) {
            return true;
        }

        if (machine == null || machine.getLevel() == null) {
            return false;
        }
        return canUse(machine.getLevel(), holder, machine);
    }

    /** Used by the basin trie, which retains Recipe values rather than RecipeHolders. */
    public static boolean canUse(Level level, Recipe<?> recipe) {
        return canUse(level, recipe, CreateMachineContext.current());
    }

    /** Exact-machine overload for call sites that already own the processing block entity. */
    public static boolean canUse(Level level, Recipe<?> recipe, BlockEntity machine) {
        if (!machineMatches(recipe, machine)) {
            return false;
        }
        if (level == null || level.isClientSide()) {
            return true;
        }

        ResourceLocation recipeId = findRecipeId(level.getRecipeManager(), recipe);
        if (recipeId == null || RecipeStageGate.requiredStage(recipeId) == null) {
            return true;
        }
        return canUseMapped(recipeId, machine);
    }

    public static boolean canUse(Level level, RecipeHolder<?> holder) {
        return canUse(level, holder, CreateMachineContext.current());
    }

    public static boolean canUse(Level level, RecipeHolder<?> holder, BlockEntity machine) {
        if (!machineMatches(holder.value(), machine)) {
            return false;
        }
        if (level == null || level.isClientSide()) {
            return true;
        }
        if (RecipeStageGate.requiredStage(holder.id()) == null) {
            return true;
        }
        return canUseMapped(holder.id(), machine);
    }

    /**
     * Tests the hidden runtime binding against the actual block performing the
     * operation. Native Create recipes and legacy families without variants
     * have no machine binding and remain universally compatible.
     */
    public static boolean machineMatches(Recipe<?> recipe, BlockEntity machine) {
        return machineMatches(TieredRecipeBindings.get(recipe), machine);
    }

    /** Public for nested Sequenced Assembly step enforcement. */
    public static boolean machineMatches(TieredRecipeBindings.Binding binding, BlockEntity machine) {
        if (binding == null || binding.machine() == null || binding.machine().blockIds().isEmpty()) {
            return true;
        }
        if (machine == null) {
            return false;
        }

        ResourceLocation actual = BuiltInRegistries.BLOCK.getKey(machine.getBlockState().getBlock());
        String actualId = actual.toString();
        return binding.machine().blockIds().contains(actualId);
    }

    private static boolean canUseMapped(ResourceLocation recipeId, BlockEntity machine) {
        if (machine == null) {
            return false;
        }

        UUID owner = CreateMachineOwner.get(machine);
        return owner != null && RecipeStageGate.canUse(owner, recipeId);
    }

    private static List<RecipeType<?>> recipeTypes(AllRecipeTypes family) {
        synchronized (FAMILY_TYPES_LOCK) {
            return FAMILY_TYPES.computeIfAbsent(family, key -> {
                List<RecipeType<?>> types = new ArrayList<>();
                types.add(key.getType());
                types.addAll(TieredCreateRecipes.typesFor(key));
                return List.copyOf(types);
            });
        }
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static List<RecipeHolder<?>> matchingRecipes(
            RecipeManager manager,
            RecipeType<?> type,
            RecipeInput input,
            Level level
    ) {
        return (List) manager.getRecipesFor((RecipeType) type, input, level);
    }

    @SuppressWarnings({"rawtypes", "unchecked"})
    private static List<RecipeHolder<?>> allRecipes(RecipeManager manager, RecipeType<?> type) {
        return (List) manager.getAllRecipesFor((RecipeType) type);
    }

    @SuppressWarnings("unchecked")
    private static <R extends Recipe<?>> RecipeHolder<R> castHolder(RecipeHolder<?> holder) {
        return (RecipeHolder<R>) holder;
    }

    private static ResourceLocation findRecipeId(RecipeManager manager, Recipe<?> recipe) {
        synchronized (RECIPE_ID_CACHE_LOCK) {
            ResourceLocation cached = RECIPE_IDS.get(recipe);
            if (cached != null) {
                return cached;
            }
            for (RecipeHolder<?> holder : manager.getRecipes()) {
                if (holder.value() == recipe) {
                    RECIPE_IDS.put(recipe, holder.id());
                    return holder.id();
                }
            }
            return null;
        }
    }
}
