package dev.godpc.industrialcolonies.processing;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;

/** Identity-only compatibility for the exact reviewed, already present module recipe. */
public final class SpaceFuelModuleRecipe {
    public static final ResourceLocation ID=ResourceLocation.parse("stellaris:misc/modules/fuel_module");
    private static final String BEFORE="35e054383786693a0231adf215ff13ebf603d64fc712af3d6b2f4aa6a46647b8";
    private static final String AFTER="7ce8c15add24354fa8ca78e391e23b6fa29e8f7a18467cd14f5b5409a566be7b";
    public record Result(RecipeHolder<?> holder,String status) {}

    public static Result normalize(RecipeHolder<?> original,HolderLookup.Provider registries){
        if(original==null) return new Result(null,"ABSENT");
        try{
            if(!original.id().equals(ID)||original.value().getClass()!=ShapelessRecipe.class)
                throw new IllegalArgumentException("Recipe identity/class changed");
            var ops=RegistryOps.create(JsonOps.INSTANCE,registries);
            var before=Recipe.CODEC.encodeStart(ops,original.value()).getOrThrow();
            var hash=EffectiveFluidNormalizer.fingerprint(before);
            if(hash.equals(AFTER)) return new Result(original,"ALREADY_CANONICAL");
            if(!hash.equals(BEFORE)) throw new IllegalArgumentException("Effective source changed");
            var edited=before.getAsJsonObject().deepCopy();
            var alternatives=new JsonArray();
            for(String id:new String[]{"stellaris:fuel_bucket","ad_astra:fuel_bucket"}){
                var ingredient=new JsonObject();ingredient.addProperty("item",id);alternatives.add(ingredient);
            }
            edited.getAsJsonArray("ingredients").set(1,alternatives);
            if(!EffectiveFluidNormalizer.fingerprint(edited).equals(AFTER))
                throw new IllegalArgumentException("Unqualified edit");
            var replacement=Recipe.CODEC.parse(ops,edited).getOrThrow();
            if(replacement.getClass()!=ShapelessRecipe.class
                    ||!edited.equals(Recipe.CODEC.encodeStart(ops,replacement).getOrThrow()))
                throw new IllegalArgumentException("Native codec changed recipe");
            return new Result(new RecipeHolder<>(ID,replacement),"CHANGED");
        }catch(RuntimeException error){return new Result(original,"HELD: "+error.getMessage());}
    }
}
