package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RemovalRule;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Ensures a removal-only KJSGen project still exports its default script file. */
@Mixin(value = RecipeProject.class, remap = false)
public abstract class KjsGenRecipeProjectMixin {
    @Shadow
    public abstract String defaultTargetFile();

    @Shadow
    public abstract List<RemovalRule> removals();

    @Inject(method = "recipesByTargetFile", at = @At("RETURN"))
    private void industrialColonies$includeRemovalOnlyDefaultTarget(
            CallbackInfoReturnable<Map<String, List<RecipeInstance>>> cir
    ) {
        if (removals().stream().noneMatch(rule -> !rule.isEmpty())) {
            return;
        }
        cir.getReturnValue().computeIfAbsent(defaultTargetFile(), ignored -> new ArrayList<>());
    }
}
