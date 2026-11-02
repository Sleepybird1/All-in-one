package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;
import dev.godpc.industrialcolonies.processing.PoweredPolarizingRecipe;

/** Native one-item Polarizer; the ATM runtime policy enforces its real processing_time field. */
public final class TfmgPolarizerCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:tfmg_polarizing";
    public record ElectricalSettings(boolean custom, int power, int ticks, boolean legacyAtm) { }
    public static ElectricalSettings electricalSettings(RecipeInstance recipe) {
        boolean atm=recipe.slot("input").kind()==ContentKind.ITEM&&AtmPolarizingPolicy.applies(recipe.slot("input").id(),recipe.slot("output").id());
        String rawTime=recipe.paramRaw("processingTime"),rawPower=recipe.paramRaw("powerRequired");
        int ticks=rawTime.isBlank()?(atm?6000:200):integer(rawTime,"Polarizing time");
        boolean custom=!rawPower.isBlank()||(!atm&&!rawTime.isBlank()&&ticks!=200);
        if(custom) {
            int power=rawPower.isBlank()?2000:integer(rawPower,"Polarizing power");
            return new ElectricalSettings(true,AtmPolarizingPolicy.validatePower(power),AtmPolarizingPolicy.validateExplicitTicks(ticks),false);
        }
        if(atm) {
            if(!rawTime.isBlank()&&ticks<AtmPolarizingPolicy.MIN_TICKS)
                throw new IllegalArgumentException("Set a positive Power Required to choose an explicit ATM time below the legacy6000-tick fallback");
            return new ElectricalSettings(false,AtmPolarizingPolicy.MIN_POWER,AtmPolarizingPolicy.requiredTicks(ticks),true);
        }
        return new ElectricalSettings(false,2000,200,false);
    }
    private static int integer(String raw,String label) {
        try{return Integer.parseInt(raw);}catch(NumberFormatException invalid){throw new IllegalArgumentException(label+" must be a whole positive number",invalid);}
    }
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        if(!recipe.typeId().equals("industrial_colonies:tfmg_polarizing")||!type.id().equals(recipe.typeId()))
            throw new IllegalArgumentException("Wrong Polarizer editor");
        var savedParams=recipe.toJson().getAsJsonObject("params");
        if(savedParams!=null)for(String key:savedParams.keySet())if(!Set.of("processingTime","powerRequired").contains(key))
            throw new IllegalArgumentException("Unsupported Polarizer parameter: "+key);
        for(var entry:recipe.slots().entrySet())if(!entry.getValue().isEmpty()&&!Set.of("input","output").contains(entry.getKey()))
            throw new IllegalArgumentException("Unrepresented Polarizer slot: "+entry.getKey());
        SlotContent in=recipe.slot("input"),out=recipe.slot("output");
        if(in.isEmpty()||out.isEmpty())throw new IllegalArgumentException("Input and output required");
        if(in.kind()!=ContentKind.ITEM&&in.kind()!=ContentKind.ITEM_TAG)throw new IllegalArgumentException("Item or item tag input required");
        if(out.kind()!=ContentKind.ITEM)throw new IllegalArgumentException("Concrete item output required");
        if(in.count()!=1)throw new IllegalArgumentException("Native Polarizer consumes one item per operation");
        if(out.count()!=1)throw new IllegalArgumentException("Native standalone Polarizer holds one output item");
        if(!in.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+")||!out.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Invalid resource identity");
        if(in.chance()!=1)throw new IllegalArgumentException("Input chance unsupported");
        if(out.chance()!=1)throw new IllegalArgumentException("Standalone Polarizer requires a deterministic one-item output");
        ElectricalSettings electrical=electricalSettings(recipe);
        if(!electrical.custom()&&in.kind()==ContentKind.ITEM_TAG&&out.id().equals(AtmPolarizingPolicy.OUTPUT))
            throw new IllegalArgumentException("ATM polarization requires the explicit raw Allthemodium input so duration and power are unambiguous");
        JsonObject data=new JsonObject();data.addProperty("type",electrical.custom()?PoweredPolarizingRecipe.SERIALIZER_ID:"tfmg:polarizing");
        JsonObject ingredient=new JsonObject();
        if(in.components()!=null&&!in.components().isBlank()){
            if(in.kind()!=ContentKind.ITEM)throw new IllegalArgumentException("Component predicates require a concrete item");
            JsonElement components;
            try{components=JsonParser.parseString(in.components());}
            catch(JsonParseException e){throw new IllegalArgumentException("Input components must be JSON",e);}
            if(!components.isJsonObject()||components.getAsJsonObject().size()==0)
                throw new IllegalArgumentException("Input components must be a nonempty JSON object");
            ingredient.addProperty("type","neoforge:components");
            var items=new JsonArray();items.add(in.id());ingredient.add("items",items);
            ingredient.add("components",components);ingredient.addProperty("strict",true);
        }else ingredient.addProperty(in.kind()==ContentKind.ITEM_TAG?"tag":"item",in.id());
        JsonArray ingredients=new JsonArray();ingredients.add(ingredient);data.add("ingredients",ingredients);
        JsonObject result=new JsonObject();result.addProperty("id",out.id());if(out.count()!=1)result.addProperty("count",out.count());
        if(out.chance()!=1)result.addProperty("chance",out.chance());
        if(out.components()!=null&&!out.components().isBlank()){
            JsonElement components;try{components=JsonParser.parseString(out.components());}catch(JsonParseException e){throw new IllegalArgumentException("Output components must be JSON",e);}
            if(!components.isJsonObject())throw new IllegalArgumentException("Output components must be a JSON object");
            result.add("components",components);
        }
        JsonArray results=new JsonArray();results.add(result);data.add("results",results);
        if(electrical.custom()) {data.addProperty("processing_time",electrical.ticks());data.addProperty("power_required",electrical.power());}
        else if(electrical.legacyAtm()&&!recipe.paramRaw("processingTime").isBlank())data.addProperty("processing_time",electrical.ticks());
        if(!recipe.recipeId().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Explicit valid recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of(electricalSettings(recipe).custom()?PoweredPolarizingRecipe.SERIALIZER_ID:"tfmg:polarizing");}
}
