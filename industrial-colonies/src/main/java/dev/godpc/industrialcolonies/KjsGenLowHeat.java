package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.core.ParameterDefinition;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import java.util.ArrayList;

/** Create Low Heated uses a heat codec value, not a KubeJS .lowheated() shortcut. */
public final class KjsGenLowHeat {
    private KjsGenLowHeat() {}

    public static RecipeTypeDefinition extend(RecipeTypeDefinition source, boolean installed) {
        if (!installed) return source;
        var parameters = new ArrayList<ParameterDefinition>();
        for (var parameter : source.parameters()) {
            if (parameter.key().equals("heat") && !parameter.options().contains("lowheated")) {
                var options = new ArrayList<>(parameter.options());
                options.add(options.contains("none") ? options.indexOf("none") + 1 : 0, "lowheated");
                parameters.add(new ParameterDefinition(parameter.key(), parameter.type(), parameter.defaultValue(), options));
            } else parameters.add(parameter);
        }
        return new RecipeTypeDefinition(source.id(), source.modId(), source.iconItem(),
                source.canvasWidth(), source.canvasHeight(), source.slots(), source.decorations(),
                parameters, source.codegenId(), source.requiresMod(), source.editorKind(), source.jeiCategory());
    }

    public static String generate(RecipeInstance recipe, RecipeTypeDefinition type, RecipeCodegen delegate) {
        if (!"lowheated".equals(recipe.param(type, "heat"))) return delegate.generate(recipe, type);
        var copy = recipe.copy();
        // KJSGen copy() is a user-duplication helper and adjusts nonempty recipe IDs.
        copy.setRecipeId(recipe.recipeId());
        copy.setParam("heat", "none");
        // merge writes heat_requirement then re-decodes the installed Create heat-condition codec.
        return delegate.generate(copy, type) + ".merge({heat_requirement: 'lowheated'})";
    }
}
