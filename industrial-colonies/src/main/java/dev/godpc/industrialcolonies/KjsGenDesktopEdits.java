package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.google.gson.JsonParser;
import java.util.*;

/** Edits a copy only; stale desktop snapshots cannot overwrite concurrent game changes. */
public final class KjsGenDesktopEdits {
    public static RecipeInstance apply(RecipeInstance current,String baseline,Map<String,String> fields) {
        if(!current.toJson().equals(JsonParser.parseString(baseline)))
            throw new IllegalArgumentException("This recipe changed in the game. Reload it before saving.");
        var result=RecipeInstance.fromJson(current.toJson().deepCopy());
        for(var e:fields.entrySet()) {
            if(e.getValue().length()>32768)throw new IllegalArgumentException("Field is too long");
            switch(e.getKey()) {
                case "Recipe ID" -> {
                    String id=e.getValue();
                    if(!id.isBlank()&&!id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Recipe ID must be namespace:path using lowercase letters.");
                    result.setRecipeId(id);
                }
                case "Group" -> result.setGroup(e.getValue());
                case "Comment" -> result.setComment(e.getValue());
                default -> {
                    if(!e.getKey().startsWith("Parameter: ")||!current.parameters().containsKey(e.getKey().substring(11)))
                        throw new IllegalArgumentException("Unknown field: "+e.getKey());
                    result.setParam(e.getKey().substring(11),e.getValue());
                }
            }
        }
        return result;
    }
}
