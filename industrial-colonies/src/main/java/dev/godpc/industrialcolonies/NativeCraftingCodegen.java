package dev.godpc.industrialcolonies;

import com.google.gson.*;
import com.zizazr.kjsgen.codegen.*;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Preserves imported crafting conditions and Mekanism's native data-transfer serializer. */
public record NativeCraftingCodegen(RecipeCodegen delegate) implements RecipeCodegen {
    public static final String NATIVE_TYPE = "__nativeCraftingType";
    public static final String CONDITIONS = "__nativeConditions";

    private static boolean active(RecipeInstance recipe) {
        return !recipe.paramRaw(NATIVE_TYPE).isBlank() || !recipe.paramRaw(CONDITIONS).isBlank();
    }

    private static String nativeType(RecipeInstance recipe) {
        if (recipe.typeId().equals("kjsgen:create_mechanical_crafting")) {
            if (!recipe.paramRaw(NATIVE_TYPE).equals("create:mechanical_crafting"))
                throw new IllegalArgumentException("Mechanical import requires its exact native serializer");
            return "create:mechanical_crafting";
        }
        boolean shaped = recipe.typeId().equals("kjsgen:shaped");
        if (!shaped && !recipe.typeId().equals("kjsgen:shapeless"))
            throw new IllegalArgumentException("Native crafting metadata requires an ordinary crafting card");
        String type = recipe.paramRaw(NATIVE_TYPE);
        if (type.isBlank()) return shaped ? "minecraft:crafting_shaped" : "minecraft:crafting_shapeless";
        if (type.equals(shaped ? "minecraft:crafting_shaped" : "minecraft:crafting_shapeless")) return type;
        if (shaped && type.equals("mekanism:mek_data")) return type;
        throw new IllegalArgumentException("Unsupported native crafting serializer: " + type);
    }

    private static JsonObject ingredient(SlotContent slot) {
        JsonObject value = new JsonObject();
        if (slot.kind() == ContentKind.ITEM) value.addProperty("item", slot.id());
        else if (slot.kind() == ContentKind.ITEM_TAG) value.addProperty("tag", slot.id());
        else throw new IllegalArgumentException("Crafting requires an item or item tag");
        if (slot.count() < 1) throw new IllegalArgumentException("Ingredient count must be positive");
        return value;
    }

    public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
        if (!active(recipe)) return delegate.generate(recipe, type);
        JsonObject data = new JsonObject();
        data.addProperty("type", nativeType(recipe));
        if (!recipe.group().isBlank()) data.addProperty("group", recipe.group());
        String conditions = recipe.paramRaw(CONDITIONS);
        if (!conditions.isBlank()) {
            JsonElement parsed = JsonParser.parseString(conditions);
            if (!parsed.isJsonArray()) throw new IllegalArgumentException("Conditions must be a JSON array");
            for (JsonElement value : parsed.getAsJsonArray()) {
                if (!value.isJsonObject() || !value.getAsJsonObject().has("type")
                    || !value.getAsJsonObject().get("type").isJsonPrimitive()
                    || !value.getAsJsonObject().get("type").getAsString().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                    throw new IllegalArgumentException("Every native condition must have a namespaced type");
            }
            data.add("neoforge:conditions", parsed);
        }
        boolean mechanical = recipe.typeId().equals("kjsgen:create_mechanical_crafting");
        int width=3, height=3;
        if (mechanical) {
            width=recipe.paramInt(type,"gridW",3); height=recipe.paramInt(type,"gridH",3);
            if(width<1 || width>7 || height<1 || height>7)throw new IllegalArgumentException("Mechanical grid must be 1..7 on each axis");
            String mirrored=recipe.paramRaw("__acceptMirrored");
            if(!mirrored.equals("true") && !mirrored.equals("false"))throw new IllegalArgumentException("Explicit mirror policy required");
            data.addProperty("accept_mirrored",Boolean.parseBoolean(mirrored));
        }
        Set<String> represented=new HashSet<>();represented.add("output");
        for(int y=0;y<height;y++)for(int x=0;x<width;x++)represented.add(mechanical?"cell_"+y+"_"+x:"in"+(y*3+x));
        for (var entry : recipe.slots().entrySet()) {
            if (entry.getValue().kind() != ContentKind.EMPTY && !entry.getKey().equals("output")
                && !represented.contains(entry.getKey()))
                throw new IllegalArgumentException("Unrepresented crafting slot: " + entry.getKey());
        }
        if (recipe.typeId().equals("kjsgen:shaped") || mechanical) {
            JsonArray pattern = new JsonArray(); JsonObject key = new JsonObject();
            for (int y = 0; y < height; y++) {
                StringBuilder row = new StringBuilder();
                for (int x = 0; x < width; x++) {
                    int index = y * width + x; SlotContent slot = recipe.slot(mechanical?"cell_"+y+"_"+x:"in" + index);
                    if (slot.kind() == ContentKind.EMPTY) { row.append(' '); continue; }
                    if (slot.count() != 1) throw new IllegalArgumentException("Shaped slot must contain one ingredient");
                    String symbol = Character.toString((char) ('A' + index));
                    row.append(symbol); key.add(symbol, ingredient(slot));
                }
                pattern.add(row.toString());
            }
            if (key.size() == 0) throw new IllegalArgumentException("Empty crafting pattern");
            data.add("pattern", pattern); data.add("key", key);
        } else {
            JsonArray ingredients = new JsonArray();
            for (int i = 0; i < 9; i++) {
                SlotContent slot = recipe.slot("in" + i);
                if (slot.kind() == ContentKind.EMPTY) continue;
                JsonObject value = ingredient(slot);
                if (slot.count() > 9 - ingredients.size()) throw new IllegalArgumentException("Too many crafting ingredients");
                for (int n = 0; n < slot.count(); n++) ingredients.add(value.deepCopy());
            }
            if (ingredients.isEmpty()) throw new IllegalArgumentException("Empty crafting recipe");
            data.add("ingredients", ingredients);
        }
        SlotContent output = recipe.slot("output");
        if (output.kind() != ContentKind.ITEM || output.count() < 1)
            throw new IllegalArgumentException("Native crafting requires an exact item output");
        JsonObject result = new JsonObject(); result.addProperty("id", output.id()); result.addProperty("count", output.count());
        data.add("result", result);
        String code = "event.custom(" + data + ")";
        if (!recipe.recipeId().isBlank()) code += ".id(" + JsUtil.quote(recipe.recipeId()) + ")";
        return code;
    }

    public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
        return active(recipe) ? Optional.of(nativeType(recipe)) : delegate.removeTypeId(recipe, type);
    }
}
