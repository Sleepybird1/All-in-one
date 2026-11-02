package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.core.SlotRole;
import java.util.Optional;

/** Select the first authored output by its real slot role, without changing recipe data. */
public final class KjsGenRecipeIconSelection {
    private KjsGenRecipeIconSelection() {}

    public static Optional<SlotContent> output(RecipeInstance recipe, RecipeTypeDefinition type) {
        if (recipe == null || type == null) return Optional.empty();
        for (var definition : type.slots()) {
            if (definition.role() != SlotRole.OUTPUT) continue;
            if (definition.list()) {
                for (var content : recipe.listSlots(definition.key()))
                    if (!content.isEmpty()) return Optional.of(content);
            } else {
                var content = recipe.slot(definition.key());
                if (!content.isEmpty()) return Optional.of(content);
            }
        }
        // The caller retains the native legacy-prefix/first-item fallback when no
        // declared output exists (including an unavailable recipe definition).
        return Optional.empty();
    }
}
