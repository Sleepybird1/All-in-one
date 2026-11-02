package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** ExtendedAE's sized ingredient format; edits are regenerated from visible slots. */
public final class CrystalAssemblerCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:crystal_assembler";
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        if(!recipe.typeId().equals(ID))throw new IllegalArgumentException("Wrong Crystal Assembler editor");
        JsonObject data=new JsonObject();data.addProperty("type","extendedae:crystal_assembler");
        JsonArray inputs=new JsonArray();Set<String> allowed=new HashSet<>(Set.of("fluid","output"));
        for(int i=0;i<8;i++) {
            String key="in"+i;allowed.add(key);SlotContent slot=recipe.slot(key);
            if(slot.isEmpty())continue;
            inputs.add(input(slot,false));
        }
        if(inputs.isEmpty())throw new IllegalArgumentException("At least one item input required");
        for(var entry:recipe.slots().entrySet())if(!entry.getValue().isEmpty()&&!allowed.contains(entry.getKey()))
            throw new IllegalArgumentException("Unrepresented Crystal Assembler slot: "+entry.getKey());
        data.add("input_items",inputs);
        SlotContent fluid=recipe.slot("fluid");
        if(!fluid.isEmpty())data.add("input_fluid",input(fluid,true));
        SlotContent output=recipe.slot("output");plain(output);
        if(output.kind()!=ContentKind.ITEM || output.count()<1)throw new IllegalArgumentException("Concrete positive item output required");
        JsonObject result=new JsonObject();result.addProperty("id",output.id());result.addProperty("count",output.count());data.add("output",result);
        String conditions=recipe.paramRaw("__nativeConditions");
        if(!conditions.isBlank()) {
            JsonElement parsed=JsonParser.parseString(conditions);
            if(!parsed.isJsonArray())throw new IllegalArgumentException("Conditions must be an array");
            for(JsonElement condition:parsed.getAsJsonArray()) {
                if(!condition.isJsonObject() || !condition.getAsJsonObject().has("type")
                        || !condition.getAsJsonObject().get("type").isJsonPrimitive()
                        || !condition.getAsJsonObject().get("type").getAsString().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                    throw new IllegalArgumentException("Every condition needs a namespaced type");
            }
            data.add("neoforge:conditions",parsed);
        }
        if(recipe.recipeId().isBlank())throw new IllegalArgumentException("Recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    private static JsonObject input(SlotContent slot,boolean fluid) {
        plain(slot);int amount=fluid?slot.amount():slot.count();
        if(amount<1)throw new IllegalArgumentException("Input amount must be positive");
        JsonObject ingredient=new JsonObject();
        if(slot.kind()==(fluid?ContentKind.FLUID:ContentKind.ITEM))ingredient.addProperty(fluid?"fluid":"item",slot.id());
        else if(slot.kind()==(fluid?ContentKind.FLUID_TAG:ContentKind.ITEM_TAG))ingredient.addProperty("tag",slot.id());
        else throw new IllegalArgumentException("Wrong ingredient registry for slot");
        JsonObject result=new JsonObject();result.add("ingredient",ingredient);
        if(fluid||amount!=1)result.addProperty("amount",amount);
        return result;
    }
    private static void plain(SlotContent slot) {
        if(!slot.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Namespaced ingredient ID required");
        if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Unsupported component predicate");
        if(slot.chance()!=1.0f)throw new IllegalArgumentException("Crystal Assembler output cannot be probabilistic");
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("extendedae:crystal_assembler");}
}
