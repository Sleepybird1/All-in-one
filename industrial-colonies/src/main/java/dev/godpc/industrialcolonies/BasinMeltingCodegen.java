package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Emits Create Metallurgy 1.0.3 basin melting recipes from the visual KJSGen layout. */
final class BasinMeltingCodegen implements RecipeCodegen {
    static final String RECIPE_TYPE = "createmetallurgy:melting";
    static final int MAX_VISIBLE_SLOTS = 4;

    @Override
    public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
        List<SlotContent> ingredientSlots = populated(recipe.listSlots("ingredients"));
        List<SlotContent> resultSlots = populated(recipe.listSlots("results"));
        requireSlotCount(ingredientSlots, "ingredients");
        requireSlotCount(resultSlots, "results");
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
        int processingTime = recipe.paramInt(type, "processingTime", 100);
        if (processingTime <= 0) {
            throw new IllegalArgumentException("Basin Melting processingTime must be positive");
        }
        fields.add("processing_time: " + processingTime);

        String heat = recipe.param(type, "heat");
        if (!"none".equals(heat)) {
            if (!"heated".equals(heat) && !"superheated".equals(heat)) {
                throw new IllegalArgumentException("Unsupported Basin Melting heat mode: " + heat);
            }
            fields.add("heat_requirement: " + JsUtil.quote(heat));
        }

        String recipeId = recipe.recipeId();
        if (recipeId == null || recipeId.isBlank()) {
            throw new IllegalArgumentException("Basin Melting requires an explicit recipe ID");
        }
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

    private static void requireSlotCount(List<SlotContent> contents, String label) {
        if (contents.isEmpty() || contents.size() > MAX_VISIBLE_SLOTS) {
            throw new IllegalArgumentException(
                    "Basin Melting requires 1-" + MAX_VISIBLE_SLOTS + " " + label);
        }
    }

    private static void requireDomainLimits(
            List<SlotContent> contents, boolean expandItemCounts, String label
    ) {
        int items = 0;
        int fluids = 0;
        for (SlotContent content : contents) {
            if (content.kind() == ContentKind.ITEM || content.kind() == ContentKind.ITEM_TAG) {
                items += expandItemCounts ? positive(content.count(), "item count") : 1;
            } else if (content.kind() == ContentKind.FLUID
                    || content.kind() == ContentKind.FLUID_TAG) {
                fluids++;
            }
        }
        if (items > (expandItemCounts ? 3 : 4) || fluids > (expandItemCounts ? 4 : 2)) {
            throw new IllegalArgumentException(
                    "Basin Melting supports three input items/four fluids and four output items/two fluids in "
                            + label);
        }
    }

    private static void appendIngredient(List<String> output, SlotContent content) {
        requireNoComponents(content, "ingredient");
        requireCertain(content, "ingredient");
        switch (content.kind()) {
            case ITEM, ITEM_TAG -> {
                String key = content.kind() == ContentKind.ITEM ? "item" : "tag";
                String encoded = "{ " + key + ": " + JsUtil.quote(content.id()) + " }";
                int copies = positive(content.count(), "item count");
                for (int index = 0; index < copies; index++) {
                    output.add(encoded);
                }
            }
            case FLUID -> output.add("{ type: 'neoforge:single', fluid: "
                    + JsUtil.quote(content.id()) + ", amount: " + positive(content.amount(), "fluid amount") + " }");
            case FLUID_TAG -> output.add("{ type: 'neoforge:tag', tag: "
                    + JsUtil.quote(content.id()) + ", amount: " + positive(content.amount(), "fluid amount") + " }");
            default -> throw wrongKind("item/tag/fluid ingredient", content.kind());
        }
    }

    private static String result(SlotContent content) {
        requireNoComponents(content, "result");
        return switch (content.kind()) {
            case ITEM -> {
                StringBuilder encoded = new StringBuilder("{ id: ")
                        .append(JsUtil.quote(content.id()));
                if (content.count() > 1) {
                    encoded.append(", count: ").append(content.count());
                }
                if (content.chance() < 1.0F) {
                    if (content.chance() <= 0.0F) {
                        throw new IllegalArgumentException(
                                "Basin Melting item result chance must be in (0, 1]");
                    }
                    encoded.append(", chance: ").append(JsUtil.trimFloat(content.chance()));
                }
                yield encoded.append(" }").toString();
            }
            case FLUID -> {
                requireCertain(content, "fluid result");
                yield "{ id: " + JsUtil.quote(content.id())
                        + ", amount: " + positive(content.amount(), "fluid amount") + " }";
            }
            default -> throw wrongKind("concrete item/fluid result", content.kind());
        };
    }

    private static int positive(int value, String label) {
        if (value <= 0) throw new IllegalArgumentException("Basin Melting " + label + " must be positive");
        return value;
    }

    private static void requireNoComponents(SlotContent content, String role) {
        if (content.components() != null && !content.components().isBlank()) {
            throw new IllegalArgumentException(
                    "Basin Melting " + role + " does not support item components");
        }
    }

    private static void requireCertain(SlotContent content, String role) {
        if (content.chance() < 1.0F) {
            throw new IllegalArgumentException(
                    "Basin Melting " + role + " does not support chance");
        }
    }

    private static IllegalArgumentException wrongKind(String expected, ContentKind actual) {
        return new IllegalArgumentException(
                "Expected Basin Melting " + expected + " but found " + actual);
    }
}
