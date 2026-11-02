package dev.godpc.industrialcolonies.client.jei;

import com.mojang.logging.LogUtils;
import com.simibubi.create.AllRecipeTypes;
import dev.godpc.industrialcolonies.IndustrialColonies;
import dev.godpc.industrialcolonies.client.RefinedRadianceVisibility;
import dev.godpc.industrialcolonies.TieredRecipeBindings;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.ingredients.IIngredientSupplier;
import mezz.jei.api.recipe.IFocus;
import mezz.jei.api.recipe.IRecipeManager;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.api.runtime.IJeiRuntime;
import mezz.jei.api.registration.IExtraIngredientRegistration;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import org.slf4j.Logger;

import java.util.Collection;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

/**
 * One-shot, read-only acceptance probe for JEI's Uses lookup on an exact
 * machine. It intentionally uses only JEI's public runtime API.
 *
 * <p>The pre-runtime observation distinguishes a missing recipe binding while
 * JEI built its maps from a later focus-map problem: a bound Copper Press
 * recipe should be observed by the category before {@code onRuntimeAvailable},
 * appear in the freshly rebuilt INPUT and CATALYST suppliers, and be returned
 * from both focused lookups. The expected count is deliberately derived from
 * the current binding index: Copper-line growth must not require changing a
 * hard-coded acceptance fixture.</p>
 */
@JeiPlugin
public final class JeiExactMachineUsesProbe implements IModPlugin {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final ResourceLocation PLUGIN_ID = ResourceLocation.fromNamespaceAndPath(
            IndustrialColonies.MOD_ID, "exact_machine_uses_probe");
    private static final ResourceLocation COPPER_PRESS_ID = ResourceLocation.fromNamespaceAndPath(
            "createcasing", "copper_press");
    private static final ResourceLocation MECHANICAL_PRESS_ID = ResourceLocation.fromNamespaceAndPath(
            "create", "mechanical_press");
    private static final Set<Recipe<?>> PRE_RUNTIME_COPPER_RECIPES =
            Collections.newSetFromMap(new IdentityHashMap<>());

    private static boolean runtimeAvailable;
    private static boolean ranForCurrentRuntime;
    private static boolean usesFocusRewriteObserved;

    @Override
    public ResourceLocation getPluginUid() {
        return PLUGIN_ID;
    }

    @Override
    public void registerExtraIngredients(IExtraIngredientRegistration registration) {
        registration.addExtraItemStacks(RefinedRadianceVisibility.itemStacks());
    }

    /** Called by the Create category mixin while JEI is building recipe layouts. */
    public static synchronized void observeLayout(
            Recipe<?> recipe,
            TieredRecipeCatalog.Machine machine
    ) {
        if (!runtimeAvailable && machine != null && COPPER_PRESS_ID.toString().equals(machine.item())) {
            PRE_RUNTIME_COPPER_RECIPES.add(recipe);
        }
    }

    /**
     * Called by the JEI Uses-focus compatibility mixin after it successfully
     * reduces the Copper Press query to INPUT only. The marker is intentionally
     * one-shot so a player can prove the real U-key path ran without log spam.
     */
    public static synchronized void observeUsesFocusRewrite(ItemStack stack) {
        if (usesFocusRewriteObserved || stack == null || stack.isEmpty()) {
            return;
        }
        if (!stack.is(BuiltInRegistries.ITEM.get(COPPER_PRESS_ID))) {
            return;
        }

        usesFocusRewriteObserved = true;
        LOGGER.info(
                "IC_JEI_EXACT_U_FILTER machine={} status=APPLIED "
                        + "roles_before=INPUT,CATALYST roles_after=INPUT",
                COPPER_PRESS_ID
        );
    }

    /**
     * Called when JEI keeps its combined INPUT + CATALYST focus group and the
     * recipe-manager guard applies the equivalent exact bound-input filter.
     */
    public static synchronized void observeCombinedUsesFilter(ResourceLocation machineId) {
        if (usesFocusRewriteObserved || !COPPER_PRESS_ID.equals(machineId)) {
            return;
        }

        usesFocusRewriteObserved = true;
        LOGGER.info(
                "IC_JEI_EXACT_U_FILTER machine={} status=APPLIED "
                        + "roles_before=INPUT,CATALYST roles_after=INPUT",
                COPPER_PRESS_ID
        );
    }

    @Override
    public void onRuntimeAvailable(IJeiRuntime runtime) {
        final int preRuntimeObserved;
        synchronized (JeiExactMachineUsesProbe.class) {
            runtimeAvailable = true;
            if (ranForCurrentRuntime) {
                return;
            }
            ranForCurrentRuntime = true;
            preRuntimeObserved = PRE_RUNTIME_COPPER_RECIPES.size();
        }

        try {
            Result result = inspect(runtime, preRuntimeObserved);
            LOGGER.info(
                    "IC_JEI_USES_PROBE machine={} status={} pre_runtime_bound={} bound={} "
                            + "supplier_input={} supplier_catalyst={} focus_input_bound={} "
                            + "focus_catalyst_bound={} categories_input={} categories_catalyst={} "
                            + "focus_input_total={} focus_input_unbound={} focus_input_other_machine={} "
                            + "bound_outputs={} mechanical_native_expected={} mechanical_native_focused={} "
                            + "mechanical_native_missing={} mechanical_bound_visible={} mechanical_status={}",
                    COPPER_PRESS_ID,
                    result.status(),
                    result.preRuntimeBound(),
                    result.bound(),
                    result.supplierInput(),
                    result.supplierCatalyst(),
                    result.focusInputBound(),
                    result.focusCatalystBound(),
                    result.categoriesInput(),
                    result.categoriesCatalyst(),
                    result.focusInputTotal(),
                    result.focusInputUnbound(),
                    result.focusInputOtherMachine(),
                    result.boundOutputs(),
                    result.mechanicalNativeExpected(),
                    result.mechanicalNativeFocused(),
                    result.mechanicalNativeMissing(),
                    result.mechanicalBoundVisible(),
                    result.mechanicalStatus()
            );
        } catch (RuntimeException | LinkageError exception) {
            // A diagnostic must never interfere with JEI startup.
            LOGGER.warn(
                    "IC_JEI_USES_PROBE machine={} status=ERROR error={}",
                    COPPER_PRESS_ID,
                    exception.toString()
            );
        }
    }

    @Override
    public synchronized void onRuntimeUnavailable() {
        runtimeAvailable = false;
        ranForCurrentRuntime = false;
        usesFocusRewriteObserved = false;
        PRE_RUNTIME_COPPER_RECIPES.clear();
    }

    private static Result inspect(IJeiRuntime runtime, int preRuntimeBound) {
        ItemStack target = new ItemStack(BuiltInRegistries.ITEM.get(COPPER_PRESS_ID));
        if (target.isEmpty()) {
            return Result.empty(preRuntimeBound, "MACHINE_ITEM_MISSING");
        }

        IRecipeManager recipeManager = runtime.getRecipeManager();
        MutableResult result = new MutableResult(preRuntimeBound);
        List<RecipeType<?>> allTypes = runtime.getJeiHelpers().getAllRecipeTypes().toList();

        allTypes.forEach(type -> inspectType(recipeManager, type, target, result));

        IFocus<ItemStack> inputFocus = runtime.getJeiHelpers().getFocusFactory().createFocus(
                RecipeIngredientRole.INPUT, VanillaTypes.ITEM_STACK, target);
        IFocus<ItemStack> catalystFocus = runtime.getJeiHelpers().getFocusFactory().createFocus(
                RecipeIngredientRole.CATALYST, VanillaTypes.ITEM_STACK, target);

        allTypes.forEach(type -> inspectCopperInputFocus(recipeManager, type, inputFocus, result));
        allTypes.forEach(type -> inspectCopperCatalystFocus(recipeManager, type, catalystFocus, result));

        result.categoriesInput = recipeManager.createRecipeCategoryLookup()
                .limitFocus(List.of(inputFocus))
                .get()
                .count();
        result.categoriesCatalyst = recipeManager.createRecipeCategoryLookup()
                .limitFocus(List.of(catalystFocus))
                .get()
                .count();

        ItemStack mechanicalPress = new ItemStack(BuiltInRegistries.ITEM.get(MECHANICAL_PRESS_ID));
        if (!mechanicalPress.isEmpty()) {
            IFocus<ItemStack> mechanicalCatalystFocus = runtime.getJeiHelpers().getFocusFactory().createFocus(
                    RecipeIngredientRole.CATALYST, VanillaTypes.ITEM_STACK, mechanicalPress);
            allTypes.forEach(type -> inspectMechanicalPressFocus(
                    recipeManager, type, mechanicalCatalystFocus, result));
        }

        return result.freeze();
    }

    private static <T> void inspectType(
            IRecipeManager recipeManager,
            RecipeType<T> type,
            ItemStack target,
            MutableResult result
    ) {
        IRecipeCategory<T> category = recipeManager.getRecipeCategory(type);
        List<T> recipes = recipeManager.createRecipeLookup(type).get().toList();
        for (T candidate : recipes) {
            Recipe<?> recipe = unwrap(candidate);
            if (isNativePressRecipe(recipe)) {
                result.mechanicalNativeRecipes.add(recipe);
            }
            if (!isBoundTo(recipe, COPPER_PRESS_ID)) {
                continue;
            }

            result.bound++;
            IIngredientSupplier supplier = recipeManager.getRecipeIngredients(category, candidate);
            if (containsItem(supplier.getIngredients(RecipeIngredientRole.INPUT), target)) {
                result.supplierInput++;
            }
            if (containsItem(supplier.getIngredients(RecipeIngredientRole.CATALYST), target)) {
                result.supplierCatalyst++;
            }
            supplier.getIngredients(RecipeIngredientRole.OUTPUT).stream()
                    .map(ingredient -> ingredient.getItemStack().orElse(ItemStack.EMPTY))
                    .filter(stack -> !stack.isEmpty())
                    .map(stack -> BuiltInRegistries.ITEM.getKey(stack.getItem()).toString())
                    .forEach(result.boundOutputs::add);
        }
    }

    private static <T> void inspectCopperInputFocus(
            IRecipeManager recipeManager,
            RecipeType<T> type,
            IFocus<?> focus,
            MutableResult result
    ) {
        recipeManager.createRecipeLookup(type)
                .limitFocus(List.of(focus))
                .get()
                .forEach(candidate -> {
                    result.focusInputTotal++;
                    Recipe<?> recipe = unwrap(candidate);
                    TieredRecipeBindings.Binding binding = binding(recipe);
                    if (binding == null || binding.machine() == null) {
                        result.focusInputUnbound++;
                    } else if (COPPER_PRESS_ID.toString().equals(binding.machine().item())) {
                        result.focusInputBound++;
                    } else {
                        result.focusInputOtherMachine++;
                    }
                });
    }

    private static <T> void inspectCopperCatalystFocus(
            IRecipeManager recipeManager,
            RecipeType<T> type,
            IFocus<?> focus,
            MutableResult result
    ) {
        result.focusCatalystBound += recipeManager.createRecipeLookup(type)
                .limitFocus(List.of(focus))
                .get()
                .map(JeiExactMachineUsesProbe::unwrap)
                .filter(recipe -> isBoundTo(recipe, COPPER_PRESS_ID))
                .count();
    }

    private static <T> void inspectMechanicalPressFocus(
            IRecipeManager recipeManager,
            RecipeType<T> type,
            IFocus<?> focus,
            MutableResult result
    ) {
        recipeManager.createRecipeLookup(type)
                .limitFocus(List.of(focus))
                .get()
                .map(JeiExactMachineUsesProbe::unwrap)
                .filter(recipe -> recipe != null)
                .forEach(recipe -> {
                    if (isNativePressRecipe(recipe)) {
                        result.mechanicalFocusedRecipes.add(recipe);
                    } else if (TieredRecipeBindings.get(recipe) != null) {
                        result.mechanicalBoundVisible++;
                    }
                });
    }

    private static Recipe<?> unwrap(Object candidate) {
        if (candidate instanceof RecipeHolder<?> holder) {
            return holder.value();
        }
        return candidate instanceof Recipe<?> recipe ? recipe : null;
    }

    private static boolean isBoundTo(Recipe<?> recipe, ResourceLocation machineId) {
        TieredRecipeBindings.Binding binding = binding(recipe);
        return binding != null
                && binding.machine() != null
                && machineId.toString().equals(binding.machine().item());
    }

    private static TieredRecipeBindings.Binding binding(Recipe<?> recipe) {
        return recipe == null ? null : TieredRecipeBindings.get(recipe);
    }

    private static boolean isNativePressRecipe(Recipe<?> recipe) {
        if (recipe == null || TieredRecipeBindings.get(recipe) != null) {
            return false;
        }
        return recipe.getType() == AllRecipeTypes.PRESSING.getType()
                || recipe.getType() == AllRecipeTypes.COMPACTING.getType();
    }

    private static boolean containsItem(
            Collection<mezz.jei.api.ingredients.ITypedIngredient<?>> ingredients,
            ItemStack target
    ) {
        return ingredients.stream()
                .map(ingredient -> ingredient.getItemStack().orElse(ItemStack.EMPTY))
                .anyMatch(stack -> !stack.isEmpty() && stack.is(target.getItem()));
    }

    private static final class MutableResult {
        private final int preRuntimeBound;
        private final Set<Recipe<?>> mechanicalNativeRecipes =
                Collections.newSetFromMap(new IdentityHashMap<>());
        private final Set<Recipe<?>> mechanicalFocusedRecipes =
                Collections.newSetFromMap(new IdentityHashMap<>());
        private final Set<String> boundOutputs = new TreeSet<>();
        private int bound;
        private int supplierInput;
        private int supplierCatalyst;
        private long focusInputTotal;
        private long focusInputBound;
        private long focusInputUnbound;
        private long focusInputOtherMachine;
        private long focusCatalystBound;
        private long categoriesInput;
        private long categoriesCatalyst;
        private long mechanicalBoundVisible;

        private MutableResult(int preRuntimeBound) {
            this.preRuntimeBound = preRuntimeBound;
        }

        private Result freeze() {
            int mechanicalNativeExpected = mechanicalNativeRecipes.size();
            int mechanicalNativeFocused = mechanicalFocusedRecipes.size();
            long mechanicalNativeMissing = mechanicalNativeRecipes.stream()
                    .filter(recipe -> !mechanicalFocusedRecipes.contains(recipe))
                    .count();
            String mechanicalStatus;
            if (mechanicalNativeExpected == 0) {
                mechanicalStatus = "NO_NATIVE_BASELINE";
            } else if (mechanicalNativeMissing > 0) {
                mechanicalStatus = "NATIVE_RECIPES_MISSING";
            } else {
                mechanicalStatus = "PASS";
            }

            String status;
            if (bound == 0) {
                status = "NO_BOUND_RECIPES";
            } else if (preRuntimeBound != bound) {
                status = "BINDING_INDEX_COUNT_MISMATCH";
            } else if (boundOutputs.isEmpty()) {
                status = "BOUND_OUTPUT_MISSING";
            } else if (supplierInput != bound || supplierCatalyst != bound) {
                status = "SUPPLIER_INCOMPLETE";
            } else if (focusInputBound != bound
                    || focusCatalystBound != bound
                    || categoriesInput == 0) {
                status = "INPUT_INDEX_MISS";
            } else if (focusInputTotal != bound
                    || focusInputUnbound != 0
                    || focusInputOtherMachine != 0) {
                status = "INPUT_INDEX_LEAK";
            } else if (!"PASS".equals(mechanicalStatus)) {
                status = "MECHANICAL_NATIVE_REGRESSION";
            } else {
                status = "PASS";
            }
            return new Result(
                    preRuntimeBound,
                    bound,
                    supplierInput,
                    supplierCatalyst,
                    focusInputTotal,
                    focusInputBound,
                    focusInputUnbound,
                    focusInputOtherMachine,
                    focusCatalystBound,
                    categoriesInput,
                    categoriesCatalyst,
                    String.join(",", boundOutputs),
                    mechanicalNativeExpected,
                    mechanicalNativeFocused,
                    mechanicalNativeMissing,
                    mechanicalBoundVisible,
                    mechanicalStatus,
                    status
            );
        }
    }

    private record Result(
            int preRuntimeBound,
            int bound,
            int supplierInput,
            int supplierCatalyst,
            long focusInputTotal,
            long focusInputBound,
            long focusInputUnbound,
            long focusInputOtherMachine,
            long focusCatalystBound,
            long categoriesInput,
            long categoriesCatalyst,
            String boundOutputs,
            int mechanicalNativeExpected,
            int mechanicalNativeFocused,
            long mechanicalNativeMissing,
            long mechanicalBoundVisible,
            String mechanicalStatus,
            String status
    ) {
        private static Result empty(int preRuntimeBound, String status) {
            return new Result(
                    preRuntimeBound,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    "",
                    0,
                    0,
                    0,
                    0,
                    "NOT_RUN",
                    status
            );
        }
    }
}
