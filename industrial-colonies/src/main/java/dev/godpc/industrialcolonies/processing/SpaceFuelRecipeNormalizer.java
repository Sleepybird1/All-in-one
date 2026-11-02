package dev.godpc.industrialcolonies.processing;

import com.google.gson.*;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.RecipeHolder;

/** Atomic identity-only publication of existing reviewed space fuel recipes. */
public final class SpaceFuelRecipeNormalizer {
    public record Result(Map<ResourceLocation,RecipeHolder<?>> recipes,Map<String,String> status,int changed,boolean held) {}
    public static boolean enabled(){
        return Boolean.getBoolean("industrial_colonies.canonicalSpaceRecipes")
            &&Boolean.getBoolean("industrial_colonies.canonicalSpaceOil")&&StellarisDieselIdentity.enabled();
    }
    public static Result normalize(Map<ResourceLocation,RecipeHolder<?>> original,HolderLookup.Provider registries){
        var status=new LinkedHashMap<String,String>();
        try(var stream=SpaceFuelRecipeNormalizer.class.getResourceAsStream("/industrial_colonies/space-fuel-rule.json")){
            if(stream==null)throw new IllegalStateException("Missing qualified space fuel rule");
            var rules=new JsonArray();rules.add(JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)));
            var refinery=EffectiveFluidNormalizer.normalize(original,registries,rules);status.putAll(refinery.status());
            var module=SpaceFuelModuleRecipe.normalize(original.get(SpaceFuelModuleRecipe.ID),registries);
            status.put(SpaceFuelModuleRecipe.ID.toString(),module.status());
            if(status.values().stream().anyMatch(s->s.startsWith("HELD")))return new Result(original,Map.copyOf(status),0,true);
            var result=new LinkedHashMap<>(refinery.recipes());int changed=refinery.changed();
            if(module.status().equals("CHANGED")){result.put(SpaceFuelModuleRecipe.ID,module.holder());changed++;}
            return new Result(Collections.unmodifiableMap(result),Map.copyOf(status),changed,false);
        }catch(Exception error){
            status.put("space_fuel","HELD: "+error.getMessage());return new Result(original,Map.copyOf(status),0,true);
        }
    }
}
