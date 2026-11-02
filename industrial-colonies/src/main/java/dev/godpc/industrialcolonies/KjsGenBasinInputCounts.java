package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.core.SlotRole;
import java.util.ArrayList;

/** Preserve saved basin bills when the upstream template omits ingredient counts. */
public final class KjsGenBasinInputCounts {
    private static final String INPUTS = "__ic_basin_input_";
    private static final int MAX_SOLID_INPUTS = 64;

    private KjsGenBasinInputCounts() {}

    public static String generate(RecipeInstance recipe, RecipeTypeDefinition type, RecipeCodegen delegate) {
        if (!type.id().equals("kjsgen:create_compacting") && !type.id().equals("kjsgen:create_mixing")) {
            return KjsGenLowHeat.generate(recipe, type, delegate);
        }
        var expanded = new ArrayList<SlotContent>();
        int solids = 0;
        boolean counted = false;
        for (var definition : type.slotsByRole(SlotRole.INPUT)) {
            var contents = definition.list() ? recipe.listSlots(definition.key()) : java.util.List.of(recipe.slot(definition.key()));
            for (var content : contents) {
                if (content.isEmpty()) continue;
                if (content.kind() == ContentKind.ITEM || content.kind() == ContentKind.ITEM_TAG) {
                    int count = content.count();
                    if (count < 1 || count > MAX_SOLID_INPUTS - solids) {
                        throw new IllegalArgumentException("Create basin supports at most 64 solid ingredients");
                    }
                    solids += count;
                    counted |= count > 1;
                    for (int n = 0; n < count; n++) expanded.add(content.withCount(1));
                } else {
                    // Fluid quantities are already explicit mB, not repeated item ingredients.
                    expanded.add(content);
                }
            }
        }
        if (!counted) return KjsGenLowHeat.generate(recipe, type, delegate);
        String template = recipe.param(type, "__template");
        if (template.isEmpty()) template = recipe.param(type, "template");
        if (!template.contains("{inputs}") || template.contains("{slot:") || template.contains("{opt_slot:")) {
            throw new IllegalArgumentException("Counted basin inputs require the standard list-input template");
        }

        // This copy is only an emission view. Never alter user cards, their quantities or UIDs.
        var emission = RecipeInstance.fromJson(recipe.toJson());
        for (var definition : type.slotsByRole(SlotRole.INPUT)) {
            if (definition.list()) {
                int length = recipe.listSlots(definition.key()).size();
                for (int i = 0; i < length; i++) emission.setSlot(definition.key() + i, SlotContent.EMPTY);
            } else emission.setSlot(definition.key(), SlotContent.EMPTY);
        }
        for (int i = 0; i < expanded.size(); i++) emission.setSlot(INPUTS + i, expanded.get(i));
        var definitions = new ArrayList<>(type.slots());
        definitions.removeIf(slot -> slot.role() == SlotRole.INPUT);
        definitions.add(new SlotDefinition(INPUTS, SlotRole.INPUT, 0, 0,
                false, true, true, true, false, true, false, true));
        var emissionType = new RecipeTypeDefinition(type.id(), type.modId(), type.iconItem(),
                type.canvasWidth(), type.canvasHeight(), definitions, type.decorations(), type.parameters(),
                type.codegenId(), type.requiresMod(), type.editorKind(), type.jeiCategory());
        return KjsGenLowHeat.generate(emission, emissionType, delegate);
    }
}
