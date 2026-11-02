package dev.godpc.industrialcolonies.processing;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.util.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;
import net.neoforged.neoforge.common.conditions.ConditionalOps;
import net.neoforged.neoforge.common.conditions.ICondition;
import modernmods.hilt.recipe.helper.LoggingRecipeSerializer;

/** Detached, explicitly supplied item rules only. No event hook or automatic activation. */
public final class EffectiveItemNormalizer {
    public record Result(Map<ResourceLocation, RecipeHolder<?>> recipes, Map<String,String> status, int changed) {}

    public static Result normalize(Map<ResourceLocation,RecipeHolder<?>> originals,
                                   HolderLookup.Provider registries, JsonArray rules) {
        var output = new LinkedHashMap<>(originals);
        var status = new LinkedHashMap<String,String>();
        // IE evaluates secondary-output conditions while decoding. Plain RegistryOps
        // supplies an empty condition context and can discard valid byproducts.
        // Resolve actual current tags; never assume a condition is true to pass an edit.
        var ops = new ConditionalOps<>(RegistryOps.create(JsonOps.INSTANCE, registries), new ICondition.IContext() {
            @Override
            public <T> Map<ResourceLocation, Collection<Holder<T>>> getAllTags(ResourceKey<? extends Registry<T>> key) {
                Map<ResourceLocation, Collection<Holder<T>>> tags = new HashMap<>();
                registries.lookupOrThrow(key).listTags().forEach(tag ->
                        tags.put(tag.key().location(), tag.stream().toList()));
                return Collections.unmodifiableMap(tags);
            }
        });
        var seen = new HashSet<String>();
        boolean held = false;
        int changed = 0;
        for (var element : rules) {
            var rule = element.getAsJsonObject();
            String id = rule.get("id").getAsString();
            var key = ResourceLocation.parse(id);
            if (!seen.add(id)) throw new IllegalArgumentException("Duplicate item rule " + id);
            var holder = originals.get(key);
            if (holder == null) { status.put(id,"ABSENT"); continue; }
            try {
                var original = holder.value();
                if (!original.getClass().getName().equals(rule.get("class").getAsString())) throw new IllegalArgumentException("class changed");
                var before = Recipe.CODEC.encodeStart(ops,original).getOrThrow();
                String hash = EffectiveFluidNormalizer.fingerprint(before);
                if (hash.equals(rule.get("afterSHA256").getAsString())) { status.put(id,"ALREADY_CANONICAL"); continue; }
                if (!hash.equals(rule.get("beforeSHA256").getAsString())) throw new IllegalArgumentException("effective source changed");
                var edited = before.deepCopy();
                for (var entry : rule.getAsJsonArray("changes")) {
                    var change = entry.getAsJsonObject();
                    if (!change.get("registry").getAsString().equals("item")) throw new IllegalArgumentException("not an item rule");
                    String canonical = change.get("canonical").getAsString();
                    if (!BuiltInRegistries.ITEM.containsKey(ResourceLocation.parse(canonical))) throw new IllegalArgumentException("item absent");
                    replace(edited,change.get("pointer").getAsString(),change.get("before"),change.get("after"));
                }
                if (!EffectiveFluidNormalizer.fingerprint(edited).equals(rule.get("afterSHA256").getAsString())) throw new IllegalArgumentException("unqualified edit");
                // Hilt's generic codec has no recipe-ID context. Its public loader
                // supplies that context, just as the native recipe manager does.
                Recipe<?> replacement = original.getSerializer() instanceof LoggingRecipeSerializer<?> loader
                        ? loader.fromJson(key,edited.getAsJsonObject())
                        : Recipe.CODEC.parse(ops,edited).getOrThrow();
                if (original.getClass()!=replacement.getClass()) throw new IllegalArgumentException("codec class changed");
                if (!edited.equals(Recipe.CODEC.encodeStart(ops,replacement).getOrThrow())) throw new IllegalArgumentException("codec changed other fields");
                output.put(key,new RecipeHolder<>(key,replacement));
                status.put(id,"CHANGED"); changed++;
            } catch (RuntimeException error) { held=true; status.put(id,"HELD: "+error.getMessage()); }
        }
        // Do not publish half a producer/consumer family when a present source differs.
        if (held) {
            status.replaceAll((id,value)->value.equals("CHANGED")?"HELD_BATCH":value);
            return new Result(Collections.unmodifiableMap(new LinkedHashMap<>(originals)),Collections.unmodifiableMap(status),0);
        }
        return new Result(Collections.unmodifiableMap(output),Collections.unmodifiableMap(status),changed);
    }

    private static void replace(JsonElement root,String pointer,JsonElement expected,JsonElement replacement) {
        if (!pointer.startsWith("/")) throw new IllegalArgumentException("invalid pointer");
        var parts=pointer.substring(1).split("/",-1);
        JsonElement parent=root;
        for(int i=0;i<parts.length-1;i++) parent=child(parent,decode(parts[i]));
        String last=decode(parts[parts.length-1]);
        if(!child(parent,last).equals(expected)) throw new IllegalArgumentException("item field changed");
        if(parent.isJsonArray()) parent.getAsJsonArray().set(Integer.parseInt(last),replacement.deepCopy());
        else parent.getAsJsonObject().add(last,replacement.deepCopy());
    }
    private static String decode(String part){return part.replace("~1","/").replace("~0","~");}
    private static JsonElement child(JsonElement parent,String key){return parent.isJsonArray()?parent.getAsJsonArray().get(Integer.parseInt(key)):Objects.requireNonNull(parent.getAsJsonObject().get(key));}
}
