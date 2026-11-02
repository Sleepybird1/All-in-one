package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonElement;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Emits TFMG 1.2.0 Chemical Vat recipes from the visual KJSGen layout. */
final class TfmgChemicalVatCodegen implements RecipeCodegen {
    static final String RECIPE_TYPE = "tfmg:vat_machine_recipe";
    static final int MAX_VISIBLE_SLOTS = 24;
    static final int MAX_INGREDIENT_UNITS = 128;

    @Override
    public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
        for (var entry : recipe.slots().entrySet()) {
            if (!entry.getValue().isEmpty() && !entry.getKey().matches(
                    "input[1-4]|output[1-4]|ingredients[0-9]+|results[0-9]+|additionalIngredients[0-9]+"))
                throw new IllegalArgumentException("Unrepresented Chemical Vat slot: " + entry.getKey());
        }
        List<SlotContent> ingredientSlots = selectedSlots(recipe,"input","ingredients");
        List<SlotContent> resultSlots = selectedSlots(recipe,"output","results");
        requireSlotCount(ingredientSlots, MAX_VISIBLE_SLOTS, "ingredients");
        requireSlotCount(resultSlots, 4, "results");
        requireDomainLimits(ingredientSlots, true, "ingredients");
        requireDomainLimits(resultSlots, false, "results");

        List<String> ingredients = new ArrayList<>();
        for (SlotContent content : ingredientSlots) {
            appendIngredient(ingredients, content);
        }

        List<String> results = new ArrayList<>();
        for (SlotContent content : resultSlots) {
            results.add(result(content));
        }

        List<String> fields = new ArrayList<>();
        fields.add("type: '" + RECIPE_TYPE + "'");
        fields.add("ingredients: [" + String.join(", ", ingredients) + "]");
        fields.add("results: [" + String.join(", ", results) + "]");
        String namedVat=KjsGenVatCanvasModel.namedVat(recipe.typeId());
        fields.add("allowed_vat_types: " + stringArray(namedVat!=null?List.of(namedVat):type.parameter("allowedVatTypes").isPresent()
                ? checkedValues(effective(recipe,type,"allowedVatTypes"),List.of("tfmg:steel_vat","tfmg:cast_iron_vat","tfmg:firebrick_lined_vat"))
                : vatTypes(recipe.param(type, "vatMode"))));
        fields.add("machines: " + stringArray(type.parameter("attachmentDrive").isPresent()
                ? machineValues(KjsGenVatCanvasModel.selectedMachines(effective(recipe,type,"attachmentDrive"),effective(recipe,type,"electrodeType"),Integer.parseInt(effective(recipe,type,"electrodeCount"))))
                : type.parameter("allowedVatTypes").isPresent()
                ? (type.parameter("machineSetup").isPresent()||recipe.parameters().containsKey("machineMode")?machineValues(effective(recipe,type,"machineSetup")):List.of())
                : machines(recipe.param(type, "machineMode"))));
        if(type.parameter("heatLevel").isPresent()){
            int heatLevel=recipe.paramInt(type,"heatLevel",0);
            if(heatLevel<0)throw new IllegalArgumentException("TFMG Chemical Vat heatLevel cannot be negative");
            fields.add("heat_level: "+heatLevel);
        }

        int minSize = recipe.paramInt(type, "minSize", 0);
        if (minSize < 0) {
            throw new IllegalArgumentException("TFMG Chemical Vat minSize cannot be negative");
        }
        if (minSize > 0) {
            fields.add("min_size: " + minSize);
        }

        int processingTime = recipe.paramInt(type, "processingTime", 100);
        if (processingTime <= 0) {
            throw new IllegalArgumentException("TFMG Chemical Vat processingTime must be positive");
        }
        fields.add("processing_time: " + processingTime);

        String heat = recipe.param(type, "heat");
        if (!"none".equals(heat)) {
            if (!"heated".equals(heat) && !"superheated".equals(heat)) {
                throw new IllegalArgumentException("Unsupported TFMG Chemical Vat heat mode: " + heat);
            }
            fields.add("heat_requirement: " + JsUtil.quote(heat));
        }

        String recipeId = KjsGenIntegration.requireRecipeId(recipe, "TFMG Chemical Vat");
        return "event.custom({ " + String.join(", ", fields) + " }).id("
                + JsUtil.quote(recipeId) + ")";
    }

    @Override
    public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
        return Optional.of(RECIPE_TYPE);
    }

    private static List<SlotContent> populated(List<SlotContent> contents) {
        if (contents == null) {
            return List.of();
        }
        return contents.stream().filter(content -> content != null && !content.isEmpty()).toList();
    }
    private static String effective(RecipeInstance recipe,RecipeTypeDefinition type,String key){
        String legacy=KjsGenVatCompatibility.legacyParameter(recipe,key);return legacy==null?recipe.param(type,key):legacy;
    }
    private static List<SlotContent> selectedSlots(RecipeInstance recipe,String fixed,String legacy){
        var numbered=populated(recipe.slots().entrySet().stream().filter(e->e.getKey().matches(fixed+"[1-4]")).map(java.util.Map.Entry::getValue).toList());
        var listed=populated(checkedList(recipe,legacy,fixed.equals("input")?MAX_VISIBLE_SLOTS:4));
        if(!numbered.isEmpty()&&!listed.isEmpty())throw new IllegalArgumentException("Ambiguous Chemical Vat "+fixed+" slot formats; preserve both and resolve before export");
        var result = new ArrayList<>(listed.isEmpty()?populated(java.util.stream.IntStream.rangeClosed(1,4).mapToObj(i->recipe.slot(fixed+i)).toList()):listed);
        if (fixed.equals("input")) {
            var extras = checkedList(recipe,"additionalIngredients",KjsGenVatCanvasModel.EXTRA_INPUT_SLOTS);
            if (extras.size() > KjsGenVatCanvasModel.EXTRA_INPUT_SLOTS)
                throw new IllegalArgumentException("Chemical Vat supports at most twenty additional feed rows");
            result.addAll(populated(extras));
        }
        return List.copyOf(result);
    }
    private static List<SlotContent> checkedList(RecipeInstance recipe,String prefix,int maximum) {
        var values=recipe.listSlots(prefix);
        if(values.size()>maximum)throw new IllegalArgumentException("Too many Chemical Vat "+prefix+" rows");
        for(String key:recipe.slots().keySet())if(key.matches(prefix+"[0-9]+")
                &&Integer.parseInt(key.substring(prefix.length()))>=values.size())
            throw new IllegalArgumentException("Sparse Chemical Vat "+prefix+" rows cannot be exported safely");
        return values;
    }

    private static void requireSlotCount(List<SlotContent> contents, int maximum, String label) {
        if (contents.isEmpty() || contents.size() > maximum) {
            throw new IllegalArgumentException(
                    "TFMG Chemical Vat requires 1-" + maximum + " " + label);
        }
    }

    private static void requireDomainLimits(
            List<SlotContent> contents, boolean expandItemCounts, String label
    ) {
        int items = 0;
        int fluids = 0;
        for (SlotContent content : contents) {
            if (content.kind() == ContentKind.ITEM || content.kind() == ContentKind.ITEM_TAG) {
                if (content.count() < 1 || content.count() > 64)
                    throw new IllegalArgumentException("Chemical Vat item count must be between one and 64 per row");
                items += expandItemCounts ? Math.max(1, content.count()) : 1;
            } else if (content.kind() == ContentKind.FLUID
                    || content.kind() == ContentKind.FLUID_TAG) {
                if (content.amount() <= 0)
                    throw new IllegalArgumentException("Chemical Vat fluid amount must be positive");
                fluids++;
            }
        }
        if (items > (expandItemCounts ? MAX_INGREDIENT_UNITS : 4) || fluids > 4) {
            throw new IllegalArgumentException(
                    "TFMG Chemical Vat supports at most " + (expandItemCounts ? MAX_INGREDIENT_UNITS : 4) + " item units and four fluids in "
                            + label);
        }
    }

    private static void appendIngredient(List<String> output, SlotContent content) {
        JsonObject components = itemComponents(content, "ingredient", false);
        requireCertain(content, "ingredient");
        switch (content.kind()) {
            case ITEM, ITEM_TAG -> {
                String key = content.kind() == ContentKind.ITEM ? "item" : "tag";
                // NeoForge's strict predicate compares the complete resulting ItemStack,
                // including the material identity of Foundry's shared fallback ingot.
                String encoded = components == null
                        ? "{ " + key + ": " + JsUtil.quote(content.id()) + " }"
                        : "{ type: 'neoforge:components', items: [" + JsUtil.quote(content.id())
                            + "], components: " + components + ", strict: true }";
                int copies = Math.max(1, content.count());
                for (int index = 0; index < copies; index++) {
                    output.add(encoded);
                }
            }
            case FLUID -> output.add("{ type: 'neoforge:single', fluid: "
                    + JsUtil.quote(content.id()) + ", amount: " + Math.max(1, content.amount()) + " }");
            case FLUID_TAG -> output.add("{ type: 'neoforge:tag', tag: "
                    + JsUtil.quote(content.id()) + ", amount: " + Math.max(1, content.amount()) + " }");
            default -> throw wrongKind("item/tag/fluid ingredient", content.kind());
        }
    }

    private static String result(SlotContent content) {
        JsonObject components = itemComponents(content, "result", true);
        return switch (content.kind()) {
            case ITEM -> {
                if (!Float.isFinite(content.chance()) || content.chance() <= 0 || content.chance() > 1)
                    throw new IllegalArgumentException("TFMG Chemical Vat item result chance must be in (0, 1]");
                StringBuilder encoded = new StringBuilder("{ id: ")
                        .append(JsUtil.quote(content.id()));
                if (content.count() > 1) {
                    encoded.append(", count: ").append(content.count());
                }
                if (components != null) encoded.append(", components: ").append(components);
                if (content.chance() < 1.0F) {
                    if (content.chance() <= 0.0F) {
                        throw new IllegalArgumentException(
                                "TFMG Chemical Vat item result chance must be in (0, 1]");
                    }
                    encoded.append(", chance: ").append(JsUtil.trimFloat(content.chance()));
                }
                yield encoded.append(" }").toString();
            }
            case FLUID -> {
                requireCertain(content, "fluid result");
                yield "{ id: " + JsUtil.quote(content.id())
                        + ", amount: " + Math.max(1, content.amount()) + " }";
            }
            default -> throw wrongKind("concrete item/fluid result", content.kind());
        };
    }

    private static List<String> vatTypes(String mode) {
        return switch (mode) {
            case "steel" -> List.of("tfmg:steel_vat");
            case "firebrick" -> List.of("tfmg:firebrick_lined_vat");
            case "both" -> List.of("tfmg:steel_vat", "tfmg:firebrick_lined_vat");
            default -> throw new IllegalArgumentException("Unsupported TFMG Chemical Vat vatMode: " + mode);
        };
    }
    private static List<String> checkedValues(String encoded,List<String> allowed){
        var values=KjsGenVatCanvasModel.values(encoded);
        if(values.isEmpty()||values.size()>3||!allowed.containsAll(values))
            throw new IllegalArgumentException("Unsupported Chemical Vat selection: "+encoded);
        return values;
    }
    private static List<String> machineValues(String encoded){
        return encoded==null||encoded.isBlank()||encoded.equals("none")?List.of():checkedValues(encoded,List.of("tfmg:mixing","tfmg:centrifuge","tfmg:electrode","tfmg:graphite_electrode"));
    }

    private static List<String> machines(String mode) {
        return switch (mode) {
            case "mixing" -> List.of("tfmg:mixing");
            case "two_electrodes" -> List.of("tfmg:electrode", "tfmg:electrode");
            default -> throw new IllegalArgumentException(
                    "Unsupported TFMG Chemical Vat machineMode: " + mode);
        };
    }

    private static String stringArray(List<String> values) {
        return "[" + values.stream().map(JsUtil::quote).reduce((left, right) -> left + ", " + right)
                .orElse("") + "]";
    }

    private static JsonObject itemComponents(SlotContent content, String role, boolean allowRemovals) {
        String encoded = content.components();
        if (encoded == null || encoded.isBlank()) {
            if (content.kind() == ContentKind.ITEM && content.id().equals("modernfoundry:fake_ingot"))
                throw new IllegalArgumentException("Modern Foundry's shared ingot requires its exact material components");
            return null;
        }
        if (content.kind() != ContentKind.ITEM)
            throw new IllegalArgumentException("TFMG Chemical Vat " + role + " components require a concrete item");
        if (encoded.length() > 1_048_576)
            throw new IllegalArgumentException("TFMG Chemical Vat " + role + " components are too large");
        try {
            var parsed = JsonParser.parseString(encoded);
            if (!parsed.isJsonObject()) throw new IllegalArgumentException("Item components must be a JSON object");
            requireLiteralSafe(parsed);
            var components = parsed.getAsJsonObject();
            for (var entry : components.entrySet()) {
                String key = entry.getKey();
                boolean removal = key.startsWith("!");
                String id = removal ? key.substring(1) : key;
                if (!id.matches("[a-z0-9_.-]+:[a-z0-9_./-]+") || entry.getValue().isJsonNull())
                    throw new IllegalArgumentException("Invalid item component: " + key);
                // DataComponentPredicate.CODEC is a map of present components, not
                // DataComponentPatch.CODEC: removing defaults cannot be weakened.
                if (removal && !allowRemovals)
                    throw new IllegalArgumentException("Chemical Vat ingredient component removals cannot be represented strictly");
            }
            if (components.isEmpty() && content.id().equals("modernfoundry:fake_ingot"))
                throw new IllegalArgumentException("Modern Foundry's shared ingot requires its exact material components");
            return components.isEmpty() ? null : components;
        } catch (RuntimeException invalid) {
            throw new IllegalArgumentException("Invalid TFMG Chemical Vat " + role + " components: " + invalid.getMessage(), invalid);
        }
    }

    private static void requireLiteralSafe(JsonElement value) {
        if (value.isJsonObject()) {
            for (var entry : value.getAsJsonObject().entrySet()) {
                if (entry.getKey().equals("__proto__"))
                    throw new IllegalArgumentException("Component key __proto__ cannot be emitted as a JavaScript object literal");
                requireLiteralSafe(entry.getValue());
            }
        } else if (value.isJsonArray()) {
            for (var child : value.getAsJsonArray()) requireLiteralSafe(child);
        }
    }

    private static void requireCertain(SlotContent content, String role) {
        if (content.chance() != 1.0F) {
            throw new IllegalArgumentException(
                    "TFMG Chemical Vat " + role + " does not support chance");
        }
    }

    private static IllegalArgumentException wrongKind(String expected, ContentKind actual) {
        return new IllegalArgumentException(
                "Expected TFMG Chemical Vat " + expected + " but found " + actual);
    }
}
