package dev.godpc.industrialcolonies.mixin.jei;

import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.client.jei.JeiInfuserSelectionTrace;
import mezz.jei.api.recipe.IRecipeManager;
import mezz.jei.api.recipe.RecipeType;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.gui.recipes.RecipeGuiLogic;
import mezz.jei.gui.recipes.lookups.ILookupState;
import org.slf4j.Logger;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;
import java.util.Optional;

/** Records at most 16 relevant user category selections without changing JEI navigation. */
@Mixin(value = RecipeGuiLogic.class, remap = false)
public abstract class JeiInfuserSelectionTraceMixin {
    @Shadow @Final private IRecipeManager recipeManager;
    @Shadow private ILookupState state;
    @Unique private static final Logger industrialColonies$infuserLogger = LogUtils.getLogger();
    @Unique private static final JeiInfuserSelectionTrace industrialColonies$infuserTrace = new JeiInfuserSelectionTrace();
    @Unique private final Deque<Optional<JeiInfuserSelectionTrace.Selection>> industrialColonies$infuserSelections = new ArrayDeque<>();
    @Unique private RecipeType<?> industrialColonies$infuserType;

    @Inject(method = "setRecipeCategory(Lmezz/jei/api/recipe/category/IRecipeCategory;)V", at = @At("HEAD"))
    private void industrialColonies$traceInfuserBefore(IRecipeCategory<?> requested, CallbackInfo ci) {
        try {
            industrialColonies$infuserSelections.push(Optional.empty());
            if (!industrialColonies$infuserTrace.available()) return;
            String id = requested.getRecipeType().getUid().toString();
            if (JeiInfuserSelectionTrace.TARGET.equals(id)) industrialColonies$infuserType = requested.getRecipeType();
            List<IRecipeCategory<?>> categories = state.getRecipeCategories();
            boolean present = false;
            for (IRecipeCategory<?> category : categories) {
                if (JeiInfuserSelectionTrace.TARGET.equals(category.getRecipeType().getUid().toString())) {
                    industrialColonies$infuserType = category.getRecipeType();
                    present = true;
                    break;
                }
            }
            if (!present && !JeiInfuserSelectionTrace.TARGET.equals(id)) return;
            var selection = industrialColonies$infuserTrace.begin(id, industrialColonies$infuserSnapshot());
            if (selection != null) {
                industrialColonies$infuserSelections.pop();
                industrialColonies$infuserSelections.push(Optional.of(selection));
                industrialColonies$infuserLogger.info(selection.before());
            }
        } catch (Throwable ignored) {
            // Diagnostic failures, including linkage/logger failures, cannot change navigation.
        }
    }

    @Inject(method = "setRecipeCategory(Lmezz/jei/api/recipe/category/IRecipeCategory;)V", at = @At("RETURN"))
    private void industrialColonies$traceInfuserAfter(IRecipeCategory<?> requested, CallbackInfo ci) {
        try {
            if (industrialColonies$infuserSelections.isEmpty()) return;
            var pending = industrialColonies$infuserSelections.pop();
            if (pending.isEmpty()) return;
            String line = industrialColonies$infuserTrace.finish(pending.get(), industrialColonies$infuserSnapshot());
            if (line != null) industrialColonies$infuserLogger.info(line);
        } catch (Throwable ignored) {
            // No repair, hiding, selection or recipe writes are permitted from this probe.
        }
    }

    @Unique
    private JeiInfuserSelectionTrace.Snapshot industrialColonies$infuserSnapshot() {
        var categories = state.getRecipeCategories();
        var ids = categories.stream().map(category -> category.getRecipeType().getUid().toString()).toList();
        var focuses = state.getFocuses().getAllFocuses();
        String selectedId = "UNKNOWN";
        long selectedCount = -1;
        try {
            var selected = state.getFocusedRecipes();
            selectedId = selected.getRecipeCategory().getRecipeType().getUid().toString();
            selectedCount = selected.getRecipes().size();
        } catch (Throwable ignored) {
            // A failing current layout is itself useful context; keep the remaining counts.
        }
        return new JeiInfuserSelectionTrace.Snapshot(selectedId,
                ids.size(), ids.indexOf(JeiInfuserSelectionTrace.TARGET), ids.stream().limit(24).toList(),
                focuses.stream().map(focus -> focus.getRole().name()).toList(), selectedCount,
                industrialColonies$infuserCount(true, false), industrialColonies$infuserCount(false, false),
                industrialColonies$infuserCount(false, true));
    }

    @Unique
    private long industrialColonies$infuserCount(boolean focused, boolean hidden) {
        try {
            if (industrialColonies$infuserType == null) return -1;
            var lookup = recipeManager.createRecipeLookup(industrialColonies$infuserType);
            if (focused) lookup.limitFocus(state.getFocuses().getAllFocuses());
            if (hidden) lookup.includeHidden();
            try (var values = lookup.get()) {
                return values.limit(JeiInfuserSelectionTrace.COUNT_LIMIT).count();
            }
        } catch (Throwable ignored) {
            return -1;
        }
    }
}
