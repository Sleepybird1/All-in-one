package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.core.RecipeValidator;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenPreviewSafety;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

import java.util.List;

/** The export generator stays strict; an unfinished editor draft must remain editable. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenPreviewSafetyMixin {
    @Shadow private List<RecipeValidator.Issue> issues;
    @Shadow private int previewScroll;

    @WrapOperation(method = "recomputeDerived", at = @At(value = "INVOKE", target =
            "Lcom/zizazr/kjsgen/integration/kubejs/ScriptAssembler;previewSingle(Lcom/zizazr/kjsgen/core/RecipeProject;Lcom/zizazr/kjsgen/core/RecipeInstance;)Ljava/lang/String;"), require = 1)
    private String industrialColonies$keepInvalidDraftOpen(
            RecipeProject project, RecipeInstance recipe, Operation<String> original) {
        var preview = KjsGenPreviewSafety.preview(() -> original.call(project, recipe));
        if (preview.failed()) {
            // Native rendering shows only the first three issues. Keep this failure visible.
            issues.add(0, new RecipeValidator.Issue(RecipeValidator.Severity.ERROR, "",
                    "industrial_colonies.kjsgen.validation.preview_unavailable", preview.diagnostic()));
            previewScroll = 0;
        }
        return preview.script();
    }
}
