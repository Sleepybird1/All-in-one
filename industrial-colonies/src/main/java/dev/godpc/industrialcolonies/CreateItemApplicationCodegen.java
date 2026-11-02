package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Native item-on-block application; not a substitute deploying recipe. */
public final class CreateItemApplicationCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:create_item_application";
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        if(!recipe.typeId().equals(ID))throw new IllegalArgumentException("Wrong item application editor");
        for(var entry:recipe.slots().entrySet())
            if(!entry.getValue().isEmpty()&&!Set.of("base","held","output").contains(entry.getKey()))
                throw new IllegalArgumentException("Unrepresented slot: "+entry.getKey());
        JsonObject data=new JsonObject();data.addProperty("type","create:item_application");
        JsonArray ingredients=new JsonArray();
        for(String key:List.of("base","held")) {
            SlotContent slot=recipe.slot(key);plain(slot);
            if(slot.count()!=1)throw new IllegalArgumentException("Native input ingredient has no count");
            JsonObject ingredient=new JsonObject();
            if(slot.kind()==ContentKind.ITEM)ingredient.addProperty("item",slot.id());
            else if(slot.kind()==ContentKind.ITEM_TAG)ingredient.addProperty("tag",slot.id());
            else throw new IllegalArgumentException("Item or item tag input required");
            ingredients.add(ingredient);
        }
        data.add("ingredients",ingredients);
        SlotContent output=recipe.slot("output");plain(output);
        if(output.kind()!=ContentKind.ITEM)throw new IllegalArgumentException("Concrete item output required");
        JsonObject result=new JsonObject();result.addProperty("id",output.id());
        if(output.count()!=1)result.addProperty("count",output.count());
        JsonArray results=new JsonArray();results.add(result);data.add("results",results);
        String keep=recipe.paramRaw("keepHeldItem");
        if(!Set.of("","false","true").contains(keep))throw new IllegalArgumentException("Invalid keep-held flag");
        if(keep.equals("true"))data.addProperty("keep_held_item",true);
        String conditions=recipe.paramRaw("__nativeConditions");
        if(!conditions.isBlank()) {
            JsonElement parsed=JsonParser.parseString(conditions);
            if(!parsed.isJsonArray())throw new IllegalArgumentException("Conditions must be an array");
            for(JsonElement condition:parsed.getAsJsonArray())
                if(!condition.isJsonObject()||!condition.getAsJsonObject().has("type")
                        ||!condition.getAsJsonObject().get("type").isJsonPrimitive()
                        ||!condition.getAsJsonObject().get("type").getAsString().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                    throw new IllegalArgumentException("Namespaced condition type required");
            data.add("neoforge:conditions",parsed);
        }
        if(recipe.recipeId().isBlank())throw new IllegalArgumentException("Recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    private static void plain(SlotContent slot) {
        if(slot.isEmpty()||!slot.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Valid ingredient ID required");
        if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Unsupported component predicate");
        if(slot.chance()!=1.0f)throw new IllegalArgumentException("Probabilistic application unsupported");
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("create:item_application");}
}
