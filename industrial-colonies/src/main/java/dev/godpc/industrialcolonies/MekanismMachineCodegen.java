package dev.godpc.industrialcolonies;

import com.google.gson.JsonObject;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.google.gson.JsonParseException;
import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.core.*;
import java.util.*;

/** Codec JSON for the Mekanism processing families missing from KJSGen 2.0.5. */
public final class MekanismMachineCodegen implements RecipeCodegen {
    public static final String ID = "industrial_colonies:mekanism_machine";
    public static final Set<String> BUNDLED = Set.of("chemical_infusing", "combining", "compressing",
            "crushing", "crystallizing", "dissolution", "energy_conversion", "enriching", "injecting",
            "oxidizing", "purifying", "sawing", "smelting", "metallurgic_infusing");
    private static final Set<String> ITEM_CHEMICAL = Set.of("compressing", "dissolution", "injecting", "purifying", "metallurgic_infusing");
    private static final Set<String> FAMILIES = Set.of("activating", "centrifuging", "chemical_conversion",
            "evaporating", "nucleosynthesizing", "painting", "pigment_extracting", "pigment_mixing",
            "reaction", "rotary", "separating", "washing");

    private static String family(RecipeTypeDefinition type) {
        if (type.id().startsWith("kjsgen:mekanism_") && BUNDLED.contains(type.id().substring("kjsgen:mekanism_".length())))
            return type.id().substring("kjsgen:mekanism_".length());
        String prefix = "industrial_colonies:mekanism_";
        if (!type.id().startsWith(prefix) || !FAMILIES.contains(type.id().substring(prefix.length())))
            throw new IllegalArgumentException("Unsupported Mekanism editor: " + type.id());
        return type.id().substring(prefix.length());
    }

    @Override public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
        String family = family(type);
        if (!recipe.typeId().equals(type.id())) throw new IllegalArgumentException("Recipe and editor type differ");
        Set<String> represented = new HashSet<>();
        for (SlotDefinition slot : type.slots()) represented.add(slot.key());
        for (var entry : recipe.slots().entrySet())
            if (!entry.getValue().isEmpty() && !represented.contains(entry.getKey()))
                throw new IllegalArgumentException("Unrepresented Mekanism slot: " + entry.getKey());
        JsonObject data = new JsonObject(); data.addProperty("type", "mekanism:" + family);
        for (SlotDefinition slot : type.slots()) {
            SlotContent content = recipe.slot(slot.key());
            if (content == null || content.isEmpty()) {
                if (slot.required()) throw new IllegalArgumentException("Missing " + slot.key());
                continue;
            }
            if (!slot.accepts(content.kind())) throw new IllegalArgumentException("Wrong content type for " + slot.key());
            boolean output = slot.role() == SlotRole.OUTPUT;
            data.add(field(family, slot.key()), encode(content, output));
        }
        if (family.equals("energy_conversion")) data.addProperty("output", positiveLong(recipe.param(type,"energy"),"Energy"));
        if (family.equals("sawing") && data.has("secondary_output")) {
            double chance;
            try { chance=Double.parseDouble(recipe.param(type,"secondaryChance")); }
            catch(NumberFormatException e){throw new IllegalArgumentException("Secondary chance must be a number",e);}
            if(!Double.isFinite(chance) || chance<=0 || chance>1)throw new IllegalArgumentException("Secondary chance must be greater than zero and at most one");
            data.addProperty("secondary_chance",chance);
        }
        if (family.equals("rotary")) {
            boolean fluidToChemical = pair(data, "fluid_input", "chemical_output");
            boolean chemicalToFluid = pair(data, "chemical_input", "fluid_output");
            if (!fluidToChemical && !chemicalToFluid) throw new IllegalArgumentException("Rotary requires at least one complete conversion direction");
        }
        if (family.equals("reaction") && !data.has("item_output") && !data.has("chemical_output"))
            throw new IllegalArgumentException("Reaction requires an item or chemical output");
        if (family.equals("reaction") || family.equals("nucleosynthesizing")) {
            int duration;
            try {duration=Integer.parseInt(recipe.param(type,"duration"));}
            catch(NumberFormatException e){throw new IllegalArgumentException("Duration must be a whole number",e);}
            if (duration <= 0) throw new IllegalArgumentException("Duration must be positive");
            data.addProperty("duration", duration);
        }
        if (family.equals("painting") || family.equals("nucleosynthesizing") || ITEM_CHEMICAL.contains(family)) {
            String value=recipe.param(type,"perTickUsage");
            if(!value.equals("true") && !value.equals("false"))throw new IllegalArgumentException("Per-tick usage must be true or false");
            data.addProperty("per_tick_usage",Boolean.parseBoolean(value));
        }
        if (family.equals("reaction")) {
            long energy;
            try { energy = Long.parseLong(recipe.param(type, "energyRequired")); }
            catch (NumberFormatException e) { throw new IllegalArgumentException("Energy must be a nonnegative whole number", e); }
            if (energy < 0) throw new IllegalArgumentException("Energy must be nonnegative");
            data.addProperty("energy_required", energy);
        }
        if (family.equals("separating")) {
            long multiplier;
            try { multiplier = Long.parseLong(recipe.param(type, "energyMultiplier")); }
            catch (NumberFormatException e) { throw new IllegalArgumentException("Energy multiplier must be a positive whole number", e); }
            if (multiplier <= 0) throw new IllegalArgumentException("Energy multiplier must be positive");
            data.addProperty("energy_multiplier", multiplier);
        }
        String recipeId=KjsGenIntegration.requireRecipeId(recipe, family);
        if (!recipeId.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")) throw new IllegalArgumentException("Invalid recipe identity");
        return "event.custom(" + data + ").id(" + JsUtil.quote(recipeId) + ")";
    }

    private static long positiveLong(String value,String label) {
        try {long result=Long.parseLong(value);if(result>0)return result;}
        catch(NumberFormatException e){throw new IllegalArgumentException(label+" must be a positive whole number",e);}
        throw new IllegalArgumentException(label+" must be positive");
    }

    private static String field(String family,String key) {
        if(ITEM_CHEMICAL.contains(family))return switch(key){case "input"->"item_input";case "gas", "infusion"->"chemical_input";default->key;};
        if(family.equals("chemical_infusing"))return switch(key){case "left"->"left_input";case "right"->"right_input";default->key;};
        if(family.equals("combining"))return switch(key){case "input1"->"main_input";case "input2"->"extra_input";default->key;};
        if(family.equals("sawing"))return switch(key){case "output"->"main_output";case "extraOutput"->"secondary_output";default->key;};
        return key;
    }

    /** Preserve saved type/slot identities while replacing unsupported positional constructors. */
    public static RecipeTypeDefinition extendBundled(RecipeTypeDefinition source) {
        String family=family(source);
        var parameters=new ArrayList<>(source.parameters().stream().filter(p->!p.key().equals("__template")).toList());
        if(ITEM_CHEMICAL.contains(family) && parameters.stream().noneMatch(p->p.key().equals("perTickUsage")))
            parameters.add(ParameterDefinition.ofBool("perTickUsage",true));
        // The native energy-conversion codec stores Mekanism joules, not FE.
        var decorations=source.decorations().stream().map(d ->
            family.equals("energy_conversion") && "FE".equals(d.text())
                ? new LayoutDecoration(d.type(),d.x(),d.y(),"J") : d).toList();
        return new RecipeTypeDefinition(source.id(),source.modId(),source.iconItem(),source.canvasWidth(),source.canvasHeight(),
            source.slots().stream().map(s -> new SlotDefinition(s.key(),s.role(),s.x(),s.y(),s.required(),
                s.allowsItem(),s.allowsTag(),s.allowsFluid(),s.allowsChemical(),true,s.allowsChance(),s.list())).toList(),
            decorations,parameters,ID,source.requiresMod(),source.editorKind(),source.jeiCategory());
    }

    private static boolean pair(JsonObject data, String a, String b) {
        if (data.has(a) != data.has(b)) throw new IllegalArgumentException("Supply both " + a + " and " + b);
        return data.has(a);
    }

    private static JsonObject encode(SlotContent content, boolean output) {
        if (!content.id().matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
            throw new IllegalArgumentException("Invalid resource identity: " + content.id());
        boolean hasComponents=content.components()!=null&&!content.components().isBlank();
        if(hasComponents&&content.kind()!=ContentKind.ITEM)
            throw new IllegalArgumentException("Components require one concrete item; chemical/fluid/tag components are unsupported");
        if (content.chance() != 1.0f) throw new IllegalArgumentException("Mekanism output chance is not supported here");
        JsonObject result = new JsonObject();
        boolean item = content.kind() == ContentKind.ITEM || content.kind() == ContentKind.ITEM_TAG;
        boolean tag = content.kind() == ContentKind.ITEM_TAG || content.kind() == ContentKind.FLUID_TAG || content.kind() == ContentKind.CHEMICAL_TAG;
        String key = switch (content.kind()) {
            case ITEM -> "item";
            case ITEM_TAG, FLUID_TAG, CHEMICAL_TAG -> "tag";
            case FLUID -> "fluid";
            case CHEMICAL -> "chemical";
            default -> throw new IllegalArgumentException("Unsupported content kind: " + content.kind());
        };
        if (output && tag) throw new IllegalArgumentException("Output must be a concrete item, fluid or chemical");
        int amount = item ? content.count() : content.amount();
        if (amount <= 0) throw new IllegalArgumentException("Amounts must be positive");
        if(hasComponents&&!output){
            JsonElement components;
            try{components=JsonParser.parseString(content.components());}
            catch(JsonParseException e){throw new IllegalArgumentException("Input components must be JSON",e);}
            if(!components.isJsonObject()||components.getAsJsonObject().size()==0)
                throw new IllegalArgumentException("Input components must be a nonempty JSON object");
            // Mekanism ItemStackIngredient uses SizedIngredient.FLAT_CODEC.
            // Put the native NeoForge component predicate alongside count, never
            // silently erase the phase and accept any item of the same ID.
            result.addProperty("type","neoforge:components");
            var items=new com.google.gson.JsonArray();items.add(content.id());result.add("items",items);
            result.add("components",components);result.addProperty("strict",true);
            result.addProperty("count",amount);return result;
        }
        result.addProperty(output ? "id" : key, content.id());
        result.addProperty(item ? "count" : "amount", amount);
        if(hasComponents){
            JsonElement components;try{components=JsonParser.parseString(content.components());}
            catch(JsonParseException e){throw new IllegalArgumentException("Output components must be JSON",e);}
            if(!components.isJsonObject())throw new IllegalArgumentException("Output components must be a JSON object");
            result.add("components",components);
        }
        return result;
    }

    @Override public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
        return Optional.of("mekanism:" + family(type));
    }
}
