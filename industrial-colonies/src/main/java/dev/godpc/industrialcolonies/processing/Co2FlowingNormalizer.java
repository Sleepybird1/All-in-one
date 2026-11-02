package dev.godpc.industrialcolonies.processing;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;

/** Exact existing consumers only; never rewrite producers or restore removed recipes. */
public final class Co2FlowingNormalizer {
    public record Result(Map<ResourceLocation,RecipeHolder<?>> recipes, Map<String,String> status, int changed, boolean held) {}
    public static JsonArray rules() {
        try(var in=Co2FlowingNormalizer.class.getResourceAsStream("/industrial_colonies/co2-flowing-rules.json")) {
            if(in==null)throw new IllegalStateException("Missing CO2 rules");
            return JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonArray();
        }catch(Exception e){throw new IllegalStateException(e);}
    }
    public static Result normalize(Map<ResourceLocation,RecipeHolder<?>> original, HolderLookup.Provider registries) {
        var output=new LinkedHashMap<>(original);var status=new LinkedHashMap<String,String>();
        var ops=RegistryOps.create(JsonOps.INSTANCE,registries);int changed=0;boolean held=false;
        for(var element:rules()) {
            var rule=element.getAsJsonObject();String id=rule.get("id").getAsString();var key=ResourceLocation.parse(id);
            var holder=original.get(key);if(holder==null){status.put(id,"ABSENT");continue;}
            try {
                var recipe=holder.value();
                if(!recipe.getClass().getName().equals(rule.get("recipeClass").getAsString()))throw new IllegalArgumentException("class changed");
                var before=Recipe.CODEC.encodeStart(ops,recipe).getOrThrow().getAsJsonObject();
                String field=rule.get("field").getAsString();int index=rule.get("index").getAsInt();
                var source=rule.getAsJsonObject("input");var compound=new JsonObject();
                compound.addProperty("type","neoforge:compound");var children=new JsonArray();
                for(String fluid:List.of("tfmg:carbon_dioxide","tfmg:flowing_carbon_dioxide")) {
                    var child=new JsonObject();child.addProperty("fluid",fluid);children.add(child);
                }
                compound.add("children",children);compound.add("amount",source.get("amount"));
                var edited=before.deepCopy();edited.getAsJsonArray(field).set(index,compound);
                var replacement=Recipe.CODEC.parse(ops,edited).getOrThrow();
                if(replacement.getClass()!=recipe.getClass())throw new IllegalArgumentException("codec class changed");
                var encoded=Recipe.CODEC.encodeStart(ops,replacement).getOrThrow().getAsJsonObject();
                // Native codecs may write explicit single types; verify all other fields exactly.
                var restored=encoded.deepCopy();restored.getAsJsonArray(field).set(index,source.deepCopy());
                if(!EffectiveFluidNormalizer.fingerprint(restored).equals(rule.get("beforeSHA256").getAsString()))throw new IllegalArgumentException("other recipe fields changed");
                if(before.equals(encoded)){status.put(id,"ALREADY_CANONICAL");continue;}
                if(!EffectiveFluidNormalizer.fingerprint(before).equals(rule.get("beforeSHA256").getAsString()))throw new IllegalArgumentException("source changed");
                output.put(key,new RecipeHolder<>(key,replacement));status.put(id,"CHANGED");changed++;
            }catch(RuntimeException e){held=true;status.put(id,"HELD: "+e.getMessage());}
        }
        return new Result(Collections.unmodifiableMap(held?original:output),Collections.unmodifiableMap(status),held?0:changed,held);
    }
}
