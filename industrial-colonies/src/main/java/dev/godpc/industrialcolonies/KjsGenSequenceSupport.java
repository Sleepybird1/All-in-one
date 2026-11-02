package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;

import java.util.List;
import java.util.Set;
import java.util.ArrayList;

/** Keeps imported stages from becoming Pressing through KJSGen's default export branch. */
public final class KjsGenSequenceSupport {
    // Expand only when both the exporter and the corresponding processing machine support the stage.
    private static final Set<String> ENABLED = Set.of("deploying", "pressing", "cutting", "filling",
            "mixing", "compacting", "smoking", "blasting", "splashing", "haunting");

    private KjsGenSequenceSupport() {}

    public record UnsupportedStage(int index, String operation) {}

    public static List<UnsupportedStage> unsupported(RecipeInstance recipe, RecipeTypeDefinition type) {
        List<UnsupportedStage> result = new ArrayList<>();
        for (int index = 0; index < CreateSpecialModel.seqLen(recipe, type); index++) {
            String operation = CreateSpecialModel.stepTypeId(recipe, type, index);
            if (!ENABLED.contains(operation)) result.add(new UnsupportedStage(index, operation));
        }
        return List.copyOf(result);
    }

    public static void requireSupported(RecipeInstance recipe, RecipeTypeDefinition type) {
        List<UnsupportedStage> unsupported = unsupported(recipe, type);
        if (!unsupported.isEmpty()) {
            var stage = unsupported.getFirst();
            throw new IllegalArgumentException("Sequenced Assembly stage " + (stage.index() + 1)
                    + " (" + stage.operation() + ") is not supported by this build. "
                    + "The recipe was not exported; the saved stage has not been changed to Pressing.");
        }
    }
}
