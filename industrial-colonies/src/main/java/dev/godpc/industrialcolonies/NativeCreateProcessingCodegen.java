package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Imported field shapes preserve native JSON; all values come from editable slots. */
public final class NativeCreateProcessingCodegen implements RecipeCodegen {
 public static final String META="__nativeProcessing";
 private static final Set<String> FAMILIES=Set.of("milling","crushing","cutting","splashing","haunting","pressing","sandpaper_polishing","mixing","compacting","deploying","filling");
 public String generate(RecipeInstance recipe,RecipeTypeDefinition type){
  return generate(recipe,type,"create:"+family(recipe));
 }
 private static String family(RecipeInstance recipe){
  String prefix="kjsgen:create_";
  if(!recipe.typeId().startsWith(prefix)||!FAMILIES.contains(recipe.typeId().substring(prefix.length())))throw new IllegalArgumentException("Unsupported Create process");
  return recipe.typeId().substring(prefix.length());
 }
 public String generate(RecipeInstance recipe,RecipeTypeDefinition type,String runtimeType){
  String family=family(recipe);
  if(!runtimeType.equals("create:"+family)&&!(runtimeType.startsWith("industrial_colonies:")&&runtimeType.endsWith("_"+family)))throw new IllegalArgumentException("Mismatched routed process");
  JsonObject meta=JsonParser.parseString(recipe.paramRaw(META)).getAsJsonObject();
  JsonObject data=new JsonObject();data.addProperty("type",runtimeType);
  Set<String> represented=new HashSet<>();
  for(String field:List.of("ingredients","results")){
   boolean output=field.equals("results");JsonArray values=new JsonArray();
   for(JsonElement entry:meta.getAsJsonArray(field)){
    JsonObject shape=entry.getAsJsonObject();String key=shape.get("slot").getAsString();
    if(!represented.add(key))throw new IllegalArgumentException("Repeated native slot");
    SlotContent slot=recipe.slot(key);values.add(encode(slot,shape,output));
   }
   if(values.isEmpty())throw new IllegalArgumentException("Missing native "+field);
   data.add(field,values);
  }
  for(var e:recipe.slots().entrySet())if(!e.getValue().isEmpty()&&!represented.contains(e.getKey())){
   // The integration validates this exact catalyst through MachineRecipeRouting first.
   if(!e.getKey().equals("__machine_process_"+family))throw new IllegalArgumentException("Unrepresented processing slot: "+e.getKey());
  }
  if(meta.has("processing_time")||(meta.has("defaultTime")&&!recipe.param(type,"processingTime").equals(meta.get("defaultTime").getAsString()))){
   int duration=recipe.paramInt(type,"processingTime",-1);
   if(duration<0)throw new IllegalArgumentException("Processing time must be nonnegative");
   data.addProperty("processing_time",duration);
  }
  String heat=recipe.param(type,"heat");
  if(!heat.isBlank()&&!Set.of("none","heated","superheated").contains(heat))throw new IllegalArgumentException("Unsupported heat requirement");
  if(meta.has("heat_requirement")||(!heat.isBlank()&&!heat.equals("none")))data.addProperty("heat_requirement",heat.isBlank()?"none":heat);
  String keep=recipe.param(type,"keepHeldItem");
  if(!keep.isBlank()&&!Set.of("true","false").contains(keep))throw new IllegalArgumentException("Invalid keep-held flag");
  if(meta.has("keep_held_item")||keep.equals("true"))data.addProperty("keep_held_item",keep.equals("true"));
  String raw=recipe.paramRaw("__nativeConditions");
  if(!raw.isBlank()){
   JsonElement conditions=JsonParser.parseString(raw);
   if(!conditions.isJsonArray())throw new IllegalArgumentException("Native conditions must be an array");
   for(JsonElement condition:conditions.getAsJsonArray())if(!condition.isJsonObject()||!condition.getAsJsonObject().has("type")||!condition.getAsJsonObject().get("type").isJsonPrimitive()||!condition.getAsJsonObject().get("type").getAsString().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Namespaced condition required");
   data.add("neoforge:conditions",conditions);
  }
  if(recipe.recipeId().isBlank())throw new IllegalArgumentException("Recipe ID required");
  return "event.custom("+data+").id("+JsUtil.quote(recipe.recipeId())+")";
 }
 private static JsonObject encode(SlotContent slot,JsonObject shape,boolean output){
  if(slot.isEmpty()||!slot.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))throw new IllegalArgumentException("Valid slot required");
  if(slot.components()!=null&&!slot.components().isBlank())throw new IllegalArgumentException("Unsupported components");
  if(!Float.isFinite(slot.chance())||slot.chance()<0||slot.chance()>1)throw new IllegalArgumentException("Invalid chance");
  boolean fluid=slot.kind()==ContentKind.FLUID;
  if(fluid!=shape.get("fluid").getAsBoolean())throw new IllegalArgumentException("Ingredient registry changed; use matching fluid/item field");
  JsonObject value=new JsonObject();
  if(fluid){value.addProperty("fluid",slot.id());value.addProperty("amount",slot.amount());}
  else if(slot.kind()==ContentKind.ITEM||(!output&&slot.kind()==ContentKind.ITEM_TAG)){
   if(!output&&slot.count()!=1)throw new IllegalArgumentException("Native item inputs do not encode counts");
   value.addProperty(slot.kind()==ContentKind.ITEM_TAG?"tag":output?"id":"item",slot.id());
   if(output&&(slot.count()!=1||shape.has("count")))value.addProperty("count",slot.count());
  }else throw new IllegalArgumentException("Wrong ingredient registry");
  if(!output&&slot.chance()!=1)throw new IllegalArgumentException("Input chance unsupported");
  if(output&&(slot.chance()!=1||shape.has("chance")))value.addProperty("chance",slot.chance());
  if(shape.has("type")){
   String kind=shape.get("type").getAsString();
   if(!fluid||!Set.of("fluid_stack","neoforge:single").contains(kind))throw new IllegalArgumentException("Unsupported fluid predicate");
   value.addProperty("type",kind);
  }
  return value;
 }
 public Optional<String> removeTypeId(RecipeInstance recipe,RecipeTypeDefinition type){return Optional.of("create:"+family(recipe));}
}
