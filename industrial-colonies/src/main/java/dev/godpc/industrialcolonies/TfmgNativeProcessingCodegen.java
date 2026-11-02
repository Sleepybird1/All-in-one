package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Exact installed TFMG StandardProcessingRecipe formats for its four standalone machines. */
public final class TfmgNativeProcessingCodegen implements RecipeCodegen {
    public static final String ID="industrial_colonies:tfmg_native_processing";
    public static final Set<String> FAMILIES=Set.of("casting","coking","distillation","winding");
    private static String family(RecipeTypeDefinition type){
        String prefix="industrial_colonies:tfmg_";
        if(!type.id().startsWith(prefix)||!FAMILIES.contains(type.id().substring(prefix.length())))throw new IllegalArgumentException("Unknown TFMG native process");
        return type.id().substring(prefix.length());
    }
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type){
        String family=family(type);if(!recipe.typeId().equals(type.id()))throw new IllegalArgumentException("Recipe and editor type differ");
        Set<String> represented=new HashSet<>();JsonArray ingredients=new JsonArray(),results=new JsonArray();
        int itemIn=0,fluidIn=0,itemOut=0,fluidOut=0;
        for(SlotDefinition definition:type.slots()){
            represented.add(definition.key());SlotContent slot=recipe.slot(definition.key());
            if(slot.isEmpty()){if(definition.required())throw new IllegalArgumentException("Missing "+definition.key());continue;}
            if(!definition.accepts(slot.kind()))throw new IllegalArgumentException("Wrong content for "+definition.key());
            boolean output=definition.role()==SlotRole.OUTPUT;
            if(!output&&definition.role()!=SlotRole.INPUT)throw new IllegalArgumentException("Unsupported catalyst slot");
            boolean item=slot.kind()==ContentKind.ITEM||slot.kind()==ContentKind.ITEM_TAG;
            boolean fluid=slot.kind()==ContentKind.FLUID||slot.kind()==ContentKind.FLUID_TAG;
            boolean tag=slot.kind()==ContentKind.ITEM_TAG||slot.kind()==ContentKind.FLUID_TAG;
            if(!item&&!fluid)throw new IllegalArgumentException("TFMG uses item/fluid ingredients");
            if(output&&tag)throw new IllegalArgumentException("Concrete output required");
            if(!slot.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Invalid resource identity");
            if(!output&&item&&slot.count()!=1)throw new IllegalArgumentException("Native item ingredient consumes one per physical slot");
            int amount=item?slot.count():slot.amount();if(amount<=0)throw new IllegalArgumentException("Positive amount required");
            if(!Float.isFinite(slot.chance())||slot.chance()<=0||slot.chance()>1)throw new IllegalArgumentException("Invalid chance");
            if(slot.chance()!=1)throw new IllegalArgumentException("Standalone process requires deterministic outputs");
            if(output&&item&&!family.equals("coking")&&slot.count()!=1)throw new IllegalArgumentException("Native standalone inventory holds one output item");
            JsonObject encoded=new JsonObject();
            if(output){
                encoded.addProperty("id",slot.id());
                if(!item||amount!=1)encoded.addProperty(item?"count":"amount",amount);
                if(slot.chance()!=1)encoded.addProperty("chance",slot.chance());
                if(slot.components()!=null&&!slot.components().isBlank()){
                    JsonElement components;try{components=JsonParser.parseString(slot.components());}catch(JsonParseException e){throw new IllegalArgumentException("Output components must be JSON",e);}
                    if(!components.isJsonObject())throw new IllegalArgumentException("Output components must be a JSON object");encoded.add("components",components);
                }
                results.add(encoded);if(item)itemOut++;else fluidOut++;
            }else{
                if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Component input predicate unsupported");
                if(fluid){encoded.addProperty("type",tag?"neoforge:tag":"neoforge:single");encoded.addProperty("amount",amount);}
                encoded.addProperty(tag?"tag":item?"item":"fluid",slot.id());ingredients.add(encoded);if(item)itemIn++;else fluidIn++;
            }
        }
        for(var entry:recipe.slots().entrySet())if(!entry.getValue().isEmpty()&&!represented.contains(entry.getKey()))throw new IllegalArgumentException("Unrepresented TFMG slot: "+entry.getKey());
        switch(family){
            case "casting"->{if(itemIn!=0||fluidIn!=1||itemOut!=1||fluidOut!=0)throw new IllegalArgumentException("Casting requires one fluid and one item output");}
            case "coking"->{if(itemIn!=1||fluidIn!=0||itemOut!=1||fluidOut!=2)throw new IllegalArgumentException("Coking requires one item and both native gas/liquid outputs");}
            case "distillation"->{if(itemIn!=0||fluidIn!=1||itemOut!=0||fluidOut<1||fluidOut>6)throw new IllegalArgumentException("Distillation requires one feed and 1-6 fluid fractions");}
            case "winding"->{if(itemIn!=2||fluidIn!=0||itemOut!=1||fluidOut!=0)throw new IllegalArgumentException("Winding requires workpiece, spool and one output");}
        }
        JsonObject data=new JsonObject();data.addProperty("type","tfmg:"+family);data.add("ingredients",ingredients);data.add("results",results);
        if(family.equals("distillation")){
            // Installed tower throughput derives from the heated tank, not recipe timing/heat enum.
            if(!recipe.paramRaw("processingTime").isBlank()||!recipe.paramRaw("heatRequirement").isBlank())
                throw new IllegalArgumentException("Native distillation uses tank heat and tower outputs, not recipe time/heat settings");
        }else{
            int duration;try{duration=Integer.parseInt(recipe.param(type,"processingTime"));}catch(NumberFormatException e){throw new IllegalArgumentException("Duration must be a whole number",e);}
            if(duration<=0)throw new IllegalArgumentException("Positive duration required");data.addProperty("processing_time",duration);
        }
        if(!recipe.recipeId().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Explicit valid recipe ID required");
        return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("tfmg:"+family(type));}
}
