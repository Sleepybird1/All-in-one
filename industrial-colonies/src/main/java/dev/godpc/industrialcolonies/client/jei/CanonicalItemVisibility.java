package dev.godpc.industrialcolonies.client.jei;

import com.google.gson.*;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import mezz.jei.api.*;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.ingredients.subtypes.UidContext;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

/** Explicit existing owners only; presentation opt-in never removes items or recipes. */
@JeiPlugin
public final class CanonicalItemVisibility implements IModPlugin {
    private static IJeiRuntime runtime;
    private static JsonObject report=new JsonObject();
    public static IJeiRuntime runtime(){return runtime;}
    public static JsonObject report(){return report.deepCopy();}
    public static Map<String,String> rules(){
        try(var in=CanonicalItemVisibility.class.getResourceAsStream("/industrial_colonies/item-visibility-owners.json")){
            if(in==null)throw new IllegalStateException("Missing item visibility policy");
            var json=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            var pairs=new TreeMap<String,String>();
            for(var e:json.getAsJsonArray("mappings")){
                var row=e.getAsJsonObject();String alias=row.get("alias").getAsString(),preferred=row.get("preferred").getAsString();
                ResourceLocation.parse(alias);ResourceLocation.parse(preferred);
                if(alias.equals(preferred)||pairs.putIfAbsent(alias,preferred)!=null)throw new IllegalStateException("Duplicate/self visibility owner");
            }
            for(String preferred:pairs.values())if(pairs.containsKey(preferred))throw new IllegalStateException("Unresolved visibility owner chain");
            return Collections.unmodifiableMap(pairs);
        }catch(java.io.IOException e){throw new IllegalStateException(e);}
    }
    @Override public ResourceLocation getPluginUid(){return ResourceLocation.parse("industrial_colonies:canonical_item_visibility");}
    @Override public void onRuntimeUnavailable(){runtime=null;report=new JsonObject();}
    @Override public void onRuntimeAvailable(IJeiRuntime value){
        runtime=value;report=new JsonObject();
        if(!Boolean.getBoolean("industrial_colonies.canonicalItemVisibility")){report.addProperty("status","DISABLED");return;}
        var items=new ArrayList<>(value.getIngredientManager().getAllItemStacks());
        var visibility=value.getIngredientVisibility();var rows=new JsonArray();int hidden=0;
        report.addProperty("registeredBefore",items.size());
        final Map<String,String> pairs;
        try{pairs=rules();}catch(Exception e){report.addProperty("status","HELD_INVALID_POLICY");report.addProperty("error",e.toString());return;}
        var listBefore=new BitSet(items.size());var recipeBefore=new BitSet(items.size());
        for(int i=0;i<items.size();i++){
            listBefore.set(i,visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,items.get(i),UidContext.Ingredient));
            recipeBefore.set(i,visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,items.get(i),UidContext.Recipe));
        }
        for(var entry:pairs.entrySet()){
            var row=new JsonObject();row.addProperty("alias",entry.getKey());row.addProperty("preferred",entry.getValue());rows.add(row);
            var aliasId=ResourceLocation.parse(entry.getKey());var preferredId=ResourceLocation.parse(entry.getValue());
            if(!BuiltInRegistries.ITEM.containsKey(aliasId)||!BuiltInRegistries.ITEM.containsKey(preferredId)){
                row.addProperty("status","HELD_MISSING_ITEM");continue;
            }
            var alias=BuiltInRegistries.ITEM.get(aliasId);var preferred=BuiltInRegistries.ITEM.get(preferredId);
            var aliasStacks=items.stream().filter(s->s.getItem()==alias).toList();
            if(aliasStacks.stream().anyMatch(s->!s.getComponentsPatch().isEmpty())){
                row.addProperty("status","HELD_REGISTERED_COMPONENT_VARIANT");continue;
            }
            boolean preferredVisible=items.stream().anyMatch(s->s.getItem()==preferred&&s.getComponentsPatch().isEmpty()&&visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,s,UidContext.Ingredient));
            if(!preferredVisible){row.addProperty("status","HELD_PREFERRED_NOT_VISIBLE");continue;}
            var hide=aliasStacks.stream().filter(s->visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,s,UidContext.Ingredient)).toList();
            var details=new JsonArray();for(var stack:hide){var d=new JsonObject();d.addProperty("recipeVisibleBefore",visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,stack,UidContext.Recipe));details.add(d);}
            if(!hide.isEmpty())visibility.hideIngredients(VanillaTypes.ITEM_STACK,hide,List.of(UidContext.Ingredient));
            hidden+=hide.size();row.add("hidden",details);row.addProperty("hiddenEntries",hide.size());
            row.addProperty("status",aliasStacks.isEmpty()?"NO_REGISTERED_ALIAS":hide.isEmpty()?"ALREADY_HIDDEN":"APPLIED");
        }
        report.addProperty("registeredAfter",value.getIngredientManager().getAllItemStacks().size());
        int unexpectedListChanges=0,recipeChanges=0;
        for(int i=0;i<items.size();i++){
            var stack=items.get(i);String id=BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
            if(!pairs.containsKey(id)&&listBefore.get(i)!=visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,stack,UidContext.Ingredient))unexpectedListChanges++;
            if(recipeBefore.get(i)!=visibility.isIngredientVisible(VanillaTypes.ITEM_STACK,stack,UidContext.Recipe))recipeChanges++;
        }
        report.addProperty("unexpectedListChanges",unexpectedListChanges);report.addProperty("recipeVisibilityChanges",recipeChanges);
        report.addProperty("hiddenEntries",hidden);report.add("mappings",rows);report.addProperty("status","APPLIED_EXPLICIT_OWNERS");
    }
}
