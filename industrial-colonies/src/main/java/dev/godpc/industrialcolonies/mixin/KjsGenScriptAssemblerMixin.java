package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.core.RecipeValidator;
import com.zizazr.kjsgen.core.RemovalRule;
import com.zizazr.kjsgen.integration.kubejs.ScriptAssembler;
import dev.godpc.industrialcolonies.KjsGenDisabledRecipeFilter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;
import java.util.Set;

/**
 * Restores the removal-rule export path omitted by KJSGen 2.0.5.
 *
 * <p>KJSGen's exporter calls the two-argument {@code assemble} overload. In
 * 2.0.5 that overload passes an empty removal list to the fully featured
 * three-argument assembler, so removal cards are saved in the project but
 * silently absent from the generated KubeJS file.</p>
 */
@Mixin(value = ScriptAssembler.class, remap = false)
public abstract class KjsGenScriptAssemblerMixin {
    private static final Set<String> INDUSTRIAL_COLONIES$REVIEW_ARCHIVE_PROJECTS = Set.of(
            "approved recipes",
            "rejected recipes",
            "Deferred",
            "maybe recipes",
            "disabled recipes"
    );

    @Inject(
            method = "assemble(Lcom/zizazr/kjsgen/core/RecipeProject;Ljava/util/List;)Ljava/lang/String;",
            at = @At("HEAD"),
            cancellable = true
    )
    private static void industrialColonies$includeProjectRemovals(
            RecipeProject project,
            List<RecipeInstance> recipes,
            CallbackInfoReturnable<String> cir
    ) {
        // The review UI keeps exact card snapshots in normal KJSGen projects
        // so they remain visually browsable. They are archives, not second
        // recipe owners: exporting one must never emit duplicate producers.
        String projectName = project.name() == null ? "" : project.name().trim();
        if (INDUSTRIAL_COLONIES$REVIEW_ARCHIVE_PROJECTS.stream()
                .anyMatch(name -> name.equalsIgnoreCase(projectName))) {
            cir.setReturnValue(ScriptAssembler.assemble(project, List.of(), List.of()));
            return;
        }
        Set<String> disabledRecipeIds = "default".equalsIgnoreCase(projectName)
                ? KjsGenDisabledRecipeFilter.loadDisabledRecipeIds()
                : Set.of();
        List<RecipeInstance> exportableRecipes = recipes.stream()
                .filter(KjsGenScriptAssemblerMixin::isExportable)
                .filter(recipe -> !disabledRecipeIds.contains(recipe.recipeId()))
                .toList();
        List<RemovalRule> removals = isDefaultTargetBatch(project, recipes)
                ? project.removals()
                : List.of();
        cir.setReturnValue(ScriptAssembler.assemble(project, exportableRecipes, removals));
    }

    /** Keep unfinished cards in the project, but never emit invalid KubeJS. */
    private static boolean isExportable(RecipeInstance recipe) {
        return RecipeTypeRegistry.get(recipe.typeId())
                .map(type -> !RecipeValidator.hasErrors(RecipeValidator.validate(recipe, type)))
                .orElse(false);
    }

    /** Removal cards have no target-file field, so they belong to the project default file. */
    private static boolean isDefaultTargetBatch(
            RecipeProject project,
            List<RecipeInstance> recipes
    ) {
        if (recipes.isEmpty()) {
            return true;
        }
        String defaultTarget = project.defaultTargetFile();
        return recipes.stream().anyMatch(
                recipe -> defaultTarget.equals(project.targetFileOf(recipe))
        );
    }
}
