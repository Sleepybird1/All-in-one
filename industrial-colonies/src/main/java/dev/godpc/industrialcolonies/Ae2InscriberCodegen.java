package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Exact AE2 ingredient positions and native press/inscribe consumption semantics. */
public final class Ae2InscriberCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:ae2_inscriber";
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        if (!recipe.typeId().equals(ID)) throw new IllegalArgumentException("Wrong Inscriber editor");
        String mode=recipe.param(type,"mode");
        if (!Set.of("inscribe","press").contains(mode)) throw new IllegalArgumentException("Unknown Inscriber mode");
        JsonObject data=new JsonObject();data.addProperty("type","ae2:inscriber");data.addProperty("mode",mode);
        JsonObject ingredients=new JsonObject();
        for(String key:List.of("top","middle","bottom")) {
            SlotContent slot=recipe.slot(key);
            if(slot.isEmpty()) {
                if(key.equals("middle"))throw new IllegalArgumentException("Middle input required");
                continue;
            }
            plain(slot);
            if(slot.count()!=1)throw new IllegalArgumentException("Inscriber ingredient is one item");
            JsonObject value=new JsonObject();
            if(slot.kind()==ContentKind.ITEM)value.addProperty("item",slot.id());
            else if(slot.kind()==ContentKind.ITEM_TAG)value.addProperty("tag",slot.id());
            else throw new IllegalArgumentException("Inscriber requires an item or item tag");
            ingredients.add(key,value);
        }
        for(var e:recipe.slots().entrySet())if(!e.getValue().isEmpty()&&!Set.of("top","middle","bottom","output").contains(e.getKey()))
            throw new IllegalArgumentException("Unrepresented Inscriber slot: "+e.getKey());
        SlotContent output=recipe.slot("output");plain(output);
        if(output.kind()!=ContentKind.ITEM||output.count()<1)throw new IllegalArgumentException("Concrete positive item output required");
        JsonObject result=new JsonObject();result.addProperty("id",output.id());result.addProperty("count",output.count());
        data.add("ingredients",ingredients);data.add("result",result);
        if(!recipe.paramRaw("__nativeConditions").isBlank())throw new IllegalArgumentException("Conditional Inscriber imports not yet supported");
        if(recipe.recipeId().isBlank())throw new IllegalArgumentException("Recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    private static void plain(SlotContent slot) {
        if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Unrepresented component predicate");
        if(slot.chance()!=1.0f)throw new IllegalArgumentException("Inscriber output cannot be probabilistic");
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("ae2:inscriber");}
}
