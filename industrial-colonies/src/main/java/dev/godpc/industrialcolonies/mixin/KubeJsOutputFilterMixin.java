package dev.godpc.industrialcolonies.mixin;

import com.mojang.logging.LogUtils;
import dev.latvian.mods.kubejs.core.RecipeLikeKJS;
import dev.latvian.mods.kubejs.recipe.filter.RecipeMatchContext;
import dev.latvian.mods.kubejs.recipe.match.ReplacementMatchInfo;
import org.slf4j.Logger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Keeps KubeJS output-filter scans alive when an early Modern Foundry result
 * asks Hilt for its SERVER tag-preference config before that config exists.
 *
 * <p>The affected recipe is treated as a non-match for this one early scan.
 * Exact-ID filters remain authoritative for Modern Foundry compatibility
 * recipes, while ordinary output removals (including KJSGen exports) continue
 * traversing the rest of the recipe map instead of aborting their callback.</p>
 */
@Mixin(
        targets = "dev.latvian.mods.kubejs.recipe.filter.OutputFilter",
        remap = false
)
public abstract class KubeJsOutputFilterMixin {
    @Unique
    private static final Logger industrialColonies$LOGGER = LogUtils.getLogger();
    @Unique
    private static final AtomicBoolean industrialColonies$REPORTED_HILT_BOOTSTRAP_SKIP =
            new AtomicBoolean();
    @Unique
    private static final String industrialColonies$CONFIG_NOT_LOADED =
            "Cannot get config value before config is loaded.";
    @Unique
    private static final String industrialColonies$HILT_COMPARATOR =
            "modernmods.hilt.recipe.helper.TagPreference$RegistryComparator";
    @Unique
    private static final String industrialColonies$MODERN_FOUNDRY_CASTING_RECIPE =
            "modernmods.modernfoundry.library.recipe.casting.ItemCastingRecipe";

    @Redirect(
            method = "test(Ldev/latvian/mods/kubejs/recipe/filter/RecipeMatchContext;)Z",
            at = @At(
                    value = "INVOKE",
                    target = "Ldev/latvian/mods/kubejs/core/RecipeLikeKJS;"
                            + "hasOutput(Ldev/latvian/mods/kubejs/recipe/filter/RecipeMatchContext;"
                            + "Ldev/latvian/mods/kubejs/recipe/match/ReplacementMatchInfo;)Z"
            ),
            require = 1,
            remap = false
    )
    private boolean industrialColonies$continuePastUnloadedHiltOutput(
            RecipeLikeKJS recipe,
            RecipeMatchContext context,
            ReplacementMatchInfo match
    ) {
        try {
            return recipe.hasOutput(context, match);
        } catch (IllegalStateException exception) {
            if (!industrialColonies$isExpectedHiltBootstrapFailure(exception)) {
                throw exception;
            }
            if (industrialColonies$REPORTED_HILT_BOOTSTRAP_SKIP.compareAndSet(false, true)) {
                industrialColonies$LOGGER.info(
                        "Industrial Colonies skipped a tag-backed Modern Foundry result while "
                                + "Hilt's server config was unavailable; KubeJS output filtering "
                                + "will continue and exact-ID foundry removals remain active."
                );
            }
            return false;
        }
    }

    private static boolean industrialColonies$isExpectedHiltBootstrapFailure(
            IllegalStateException exception
    ) {
        if (!industrialColonies$CONFIG_NOT_LOADED.equals(exception.getMessage())) {
            return false;
        }

        boolean sawHiltComparator = false;
        boolean sawModernFoundryRecipe = false;
        for (StackTraceElement frame : exception.getStackTrace()) {
            if (industrialColonies$HILT_COMPARATOR.equals(frame.getClassName())) {
                sawHiltComparator = true;
            } else if (industrialColonies$MODERN_FOUNDRY_CASTING_RECIPE.equals(
                    frame.getClassName()
            )) {
                sawModernFoundryRecipe = true;
            }
            if (sawHiltComparator && sawModernFoundryRecipe) {
                return true;
            }
        }
        return false;
    }
}
