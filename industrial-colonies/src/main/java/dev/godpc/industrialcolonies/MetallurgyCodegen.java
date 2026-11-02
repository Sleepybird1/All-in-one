package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import net.minecraft.resources.ResourceLocation;
import java.util.*;

/** Native Create Metallurgy serializers, deliberately distinct from Create mixing. */
public final class MetallurgyCodegen implements RecipeCodegen {
    private static final Set<String> FAMILIES=Set.of("alloying","bulk_melting","entity_melting","grinding","casting_in_table","casting_in_basin");
    public static String family(RecipeTypeDefinition type) {
        String family=type.id().replace("industrial_colonies:metallurgy_","");
        if(!FAMILIES.contains(family))throw new IllegalArgumentException("Unknown Metallurgy editor: "+type.id());
        return family;
    }
    @Override public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type) {return Optional.of("createmetallurgy:"+family(type));}
    @Override public String generate(RecipeInstance recipe,RecipeTypeDefinition type) {
        if(recipe.recipeId()==null || ResourceLocation.tryParse(recipe.recipeId())==null)throw new IllegalArgumentException("An explicit recipe ID is required");
        return "event.custom("+json(recipe,type)+").id("+JsUtil.quote(recipe.recipeId())+")";
    }
    public static JsonObject json(RecipeInstance recipe,RecipeTypeDefinition type) {
        String family=family(type);boolean casting=family.startsWith("casting_");
        boolean entity=family.equals("entity_melting"),bulk=family.equals("bulk_melting"),alloy=family.equals("alloying"),grinding=family.equals("grinding");
        var inputs=populated(recipe.listSlots("ingredients"));var outputs=populated(recipe.listSlots("results"));
        if((inputs.isEmpty()&&!entity) || (entity&&!inputs.isEmpty()) || outputs.isEmpty())throw new IllegalArgumentException("Missing ingredients/results or unexpected entity-melting ingredients");
        int itemInputs=0,fluidInputs=0,itemOutputs=0,fluidOutputs=0;
        var ingredients=new JsonArray();var results=new JsonArray();
        for(var content:inputs) {
            validate(content);if(content.chance()!=1f)throw new IllegalArgumentException("Ingredients cannot have probability");
            if(content.kind()==ContentKind.ITEM || content.kind()==ContentKind.ITEM_TAG) {
                int count=positive(content.count(),"item count");if(count>64)throw new IllegalArgumentException("Ingredient count exceeds native capacity");
                itemInputs+=count;var value=new JsonObject();value.addProperty(content.kind()==ContentKind.ITEM?"item":"tag",content.id());
                for(int i=0;i<count;i++)ingredients.add(value.deepCopy());
            } else if(content.kind()==ContentKind.FLUID || content.kind()==ContentKind.FLUID_TAG) {
                fluidInputs++;var value=new JsonObject();boolean tag=content.kind()==ContentKind.FLUID_TAG;
                value.addProperty("type",tag?"neoforge:tag":"neoforge:single");value.addProperty(tag?"tag":"fluid",content.id());value.addProperty("amount",positive(content.amount(),"mB"));ingredients.add(value);
            } else throw new IllegalArgumentException("Unsupported Metallurgy ingredient");
        }
        for(var content:outputs) {
            validate(content);var value=new JsonObject();value.addProperty("id",content.id());
            if(content.kind()==ContentKind.ITEM) {itemOutputs++;value.addProperty("count",positive(content.count(),"output count"));if(content.chance()!=1f)value.addProperty("chance",content.chance());}
            else if(content.kind()==ContentKind.FLUID) {fluidOutputs++;if(content.chance()!=1f)throw new IllegalArgumentException("Fluid results cannot have probability");value.addProperty("amount",positive(content.amount(),"mB"));}
            else throw new IllegalArgumentException("Results must be concrete items or fluids");
            results.add(value);
        }
        int maxItemIn=alloy?3:entity?0:1,maxFluidIn=alloy?4:casting?1:0;
        int maxItemOut=alloy||grinding?4:1,maxFluidOut=alloy?2:bulk||entity?20:0;
        if(itemInputs>maxItemIn||fluidInputs>maxFluidIn||itemOutputs>maxItemOut||fluidOutputs>maxFluidOut)throw new IllegalArgumentException("Native "+family+" capacity exceeded (items/fluids input "+maxItemIn+"/"+maxFluidIn+", output "+maxItemOut+"/"+maxFluidOut+")");
        var json=new JsonObject();json.addProperty("type","createmetallurgy:"+family);json.add("ingredients",ingredients);
        if(casting) {
            if(fluidInputs!=1||outputs.size()!=1||outputs.getFirst().chance()!=1f)throw new IllegalArgumentException("Casting needs one fluid and one certain item result");
            var result=new JsonObject();result.add("item",results.get(0));json.add("result",result);
            String consumed=recipe.param(type,"moldConsumed");if(!Set.of("true","false").contains(consumed))throw new IllegalArgumentException("Invalid mold consumed flag");
            boolean consume=Boolean.parseBoolean(consumed);if(consume&&itemInputs==0)throw new IllegalArgumentException("A consumed mold must be selected");json.addProperty("mold_consumed",consume);
        } else json.add("results",results);
        if(!entity)json.addProperty("processing_time",positive(integer(recipe,type,"processingTime"),"processing ticks"));
        if(alloy) {String heat=recipe.param(type,"heat");if(!Set.of("none","heated","superheated").contains(heat))throw new IllegalArgumentException("Unsupported alloying heat");json.addProperty("heat_requirement",heat);}
        if(bulk||entity) {
            int min=integer(recipe,type,"minHeat"),max=integer(recipe,type,"maxHeat");if(min>max)throw new IllegalArgumentException("Minimum foundry heat exceeds maximum");
            json.addProperty("minHeatRequirement",min);json.addProperty("maxHeatRequirement",max);
        }
        if(entity) {
            String id=recipe.param(type,"entityId");if(ResourceLocation.tryParse(id)==null)throw new IllegalArgumentException("An entity registry ID is required");
            int damage=integer(recipe,type,"entityDamage");
            if(damage<0)throw new IllegalArgumentException("Entity damage must be nonnegative");
            var value=new JsonObject();value.addProperty("type",id);value.addProperty("damage",damage);json.add("entity",value);
        }
        return json;
    }
    private static List<SlotContent> populated(List<SlotContent> slots){return slots==null?List.of():slots.stream().filter(s->s!=null&&!s.isEmpty()).toList();}
    private static int positive(int value,String label){if(value<=0)throw new IllegalArgumentException(label+" must be positive");return value;}
    private static int integer(RecipeInstance recipe,RecipeTypeDefinition type,String key){try{return Integer.parseInt(recipe.param(type,key));}catch(NumberFormatException e){throw new IllegalArgumentException(key+" must be a whole number");}}
    private static void validate(SlotContent content) {
        if(ResourceLocation.tryParse(content.id())==null)throw new IllegalArgumentException("Invalid resource ID");
        if(content.components()!=null&&!content.components().isBlank())throw new IllegalArgumentException("Metallurgy component-bearing entries are not supported by this editor");
        if(!Float.isFinite(content.chance())||content.chance()<=0||content.chance()>1)throw new IllegalArgumentException("Probability must be in (0,1]");
    }
}
