// Optional legacy AlltheOres integrations cannot target items absent from this pack.
function IC_MustJs_missingLegacyItem(value) {
    return typeof value === 'string' && value.indexOf('alltheores:') === 0 && !Item.exists(value);
}

/**
 * Removes all recipes that produce a specified output item.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} list - Array of item identifiers used to filter recipe outputs.
 *
 * Usage example: RemoveOutput(
 *     e,
 *     [
 *         "minecraft:iron_ingot",
 *         "minecraft:gold_ingot"
 *     ]
 * )
 * - Removes all recipes that produce any of the specified output items.
 */
function RemoveOutput(e, list) {
    list.forEach((item) => {
        e.remove({output: item});
    })
}

/**
 * Removes all recipes that use a specified input item.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} list - Array of item identifiers used to filter recipe inputs.
 *
 * Usage example: RemoveInput(
 *     e,
 *     [
 *         "minecraft:iron_ore",
 *         "minecraft:gold_ore"
 *     ]
 * )
 * - Removes all recipes that use any of the specified input items.
 */
function RemoveInput(e, list) {
    list.forEach((item) => {
        e.remove({input: item});
    })
}

/**
 * Removes all recipes from a specified mod.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} list - Array of mod identifiers used to filter recipes.
 *
 * Usage example: RemoveMod(
 *     e,
 *     [
 *         "create",
 *         "ae2"
 *     ]
 * )
 * - Removes all recipes belonging to the specified mods.
 */
function RemoveMod(e, list) {
    list.forEach((item) => {
        e.remove({mod: item});
    })
}

/**
 * Removes all recipes of a specified recipe type.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} list - Array of recipe type identifiers used to filter recipes.
 *
 * Usage example: RemoveType(
 *     e,
 *     [
 *         "minecraft:smelting",
 *         "minecraft:blasting"
 *     ]
 * )
 * - Removes all recipes matching any of the specified recipe types.
 */
function RemoveType(e, list) {
    list.forEach((item) => {
        e.remove({type: item});
    })
}

/**
 * Removes recipes with specified recipe identifiers.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} list - Array of recipe identifiers to remove.
 *
 * Usage example: RemoveId(
 *     e,
 *     [
 *         "minecraft:iron_ingot_from_smelting_iron_ore",
 *         "minecraft:gold_ingot_from_smelting_gold_ore"
 *     ]
 * )
 * - Removes all recipes matching the specified recipe identifiers.
 */
function RemoveId(e, list) {
    list.forEach((item) => {
        e.remove({id: item});
    })
}

/**
 * Replaces a specified recipe input with a new ingredient.
 *
 * @param {Object} e - The recipe event object.
 * @param {string} input - The item identifier to search for in recipe inputs.
 * @param {string} new_input - The new item or ingredient to use as the replacement.
 *
 * Usage example: ReplaceInput(
 *     e,
 *     "minecraft:iron_ingot",
 *     "minecraft:copper_ingot"
 * )
 * - Replaces the specified input item with the new input ingredient.
 */
function ReplaceInput(e, input, new_input) {
    if (IC_MustJs_missingLegacyItem(input) || IC_MustJs_missingLegacyItem(new_input)) {
        console.info("Skipping unavailable legacy AlltheOres replacement");
        return;
    }
    e.replaceInput(
        { input: input },
        input,
        Ingredient.of(new_input)
    )
}

/**
 * Replaces a specified recipe output with a new item.
 *
 * @param {Object} e - The recipe event object.
 * @param {string} output - The item identifier to search for in recipe outputs.
 * @param {string} new_output - The new item to use as the replacement.
 *
 * Usage example: ReplaceOutput(
 *     e,
 *     "minecraft:iron_ingot",
 *     "minecraft:copper_ingot"
 * )
 * - Replaces the specified output item with the new output item.
 */
function ReplaceOutput(e, output, new_output) {
    if (IC_MustJs_missingLegacyItem(output) || IC_MustJs_missingLegacyItem(new_output)) {
        console.info("Skipping unavailable legacy AlltheOres replacement");
        return;
    }
    e.replaceOutput(
        { output: output },
        output,
        Ingredient.of(new_output).first
    )
}

/**
 * Replaces both the input and output of recipes using the specified item.
 *
 * @param {Object} e - The recipe event object.
 * @param {string} item - The item identifier to search for in recipe inputs and outputs.
 * @param {string} new_item - The new item to use as the replacement.
 *
 * Usage example: ReplaceItem(
 *     e,
 *     "minecraft:iron_ingot",
 *     "minecraft:copper_ingot"
 * )
 * - Replaces the specified item wherever it appears as a recipe input or output.
 * - Applies both ReplaceInput() and ReplaceOutput() to the specified item.
 */
function ReplaceItem(e, item, new_item) {
    ReplaceInput(e, item, new_item);
    ReplaceOutput(e, item, new_item);
}
