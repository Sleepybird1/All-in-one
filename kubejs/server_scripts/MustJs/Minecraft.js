/**
 * Creates a Minecraft smelting recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object|string} output - The recipe output item.
 * @param {Object} input - The recipe input ingredient.
 * @param {number} experience - The amount of experience granted when the recipe is completed.
 * @param {number} time - The cooking time in ticks.
 *
 * Usage example: smelting(
 *     e,
 *     itemOutput("minecraft:iron_ingot"),
 *     itemInput("minecraft:raw_iron"),
 *     0.7,
 *     200
 * )
 * - Smelts raw iron into an iron ingot.
 * - 200 ticks correspond to 10 seconds.
 */
function smelting(e, output, input, experience, time) {
    e.custom({
        "type": "minecraft:smelting",
        "ingredient": input,
        "result": output,
        "experience": experience,
        "cookingtime": time
    })
}

/**
 * Creates a Minecraft blasting recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object|string} output - The recipe output item.
 * @param {Object} input - The recipe input ingredient.
 * @param {number} experience - The amount of experience granted when the recipe is completed.
 * @param {number} time - The cooking time in ticks.
 *
 * Usage example: blasting(
 *     e,
 *     itemOutput("minecraft:iron_ingot"),
 *     itemInput("minecraft:raw_iron"),
 *     0.7,
 *     100
 * )
 * - Blasts raw iron into an iron ingot.
 * - 100 ticks correspond to 5 seconds.
 */
function blasting(e, output, input, experience, time) {
    e.custom({
        "type": "minecraft:blasting",
        "ingredient": input,
        "result": output,
        "experience": experience,
        "cookingtime": time
    })
}

/**
 * Creates a Minecraft smoking recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object|string} output - The recipe output item.
 * @param {Object} input - The recipe input ingredient.
 * @param {number} experience - The amount of experience granted when the recipe is completed.
 * @param {number} time - The cooking time in ticks.
 *
 * Usage example: smoking(
 *     e,
 *     itemOutput("minecraft:cooked_beef"),
 *     itemInput("minecraft:beef"),
 *     0.35,
 *     100
 * )
 * - Cooks beef into cooked beef using a smoker.
 * - 100 ticks correspond to 5 seconds.
 */
function smoking(e, output, input, experience, time) {
    e.custom({
        "type": "minecraft:smoking",
        "ingredient": input,
        "result": output,
        "experience": experience,
        "cookingtime": time
    })
}

/**
 * Creates a Minecraft shaped crafting recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object|string} output - The recipe output item.
 * @param {Object} input - Object containing the ingredients assigned to each pattern key.
 * @param {Array<string>} pattern - Array of strings representing the crafting pattern.
 *
 * Usage example: shaped(
 *     e,
 *     itemOutput("minecraft:iron_pickaxe"),
 *     Object.assign(
 *         {},
 *         itemInputKey('A', 'minecraft:iron_ingot'),
 *         itemInputTagKey('B', 'c:rods/wooden'),
 *     ),
 *     [
 *         "AAA",
 *         " B ",
 *         " B "
 *     ]
 * )
 * - Creates a shaped crafting recipe using the specified pattern and ingredients.
 * - Each character in the pattern corresponds to a key defined in the input object.
 * - itemInputKey() assigns a specific item to a pattern key.
 * - itemInputTagKey() assigns an item tag to a pattern key.
 */
function shaped(e, output, input, pattern) {
    e.custom({
        "type": "minecraft:crafting_shaped",
        "pattern": pattern,
        "key": input,
        "result": output
    })
}

/**
 * Creates a Minecraft shapeless crafting recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object|string} output - The recipe output item.
 * @param {Array<Object>} input - Array containing the recipe ingredients.
 *
 * Usage example: shapeless(
 *     e,
 *     itemOutput("minecraft:stick"),
 *     [
 *         itemInput("minecraft:planks"),
 *         itemInput("minecraft:planks")
 *     ]
 * )
 * - Creates a shapeless crafting recipe using the specified ingredients.
 * - The order of the ingredients does not matter.
 */
function shapeless(e, output, input) {
    e.custom({
        "type": "minecraft:crafting_shapeless",
        "ingredients": input,
        "result": output
    })
}

/**
 * Creates a Minecraft stonecutting recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object} input - The recipe input ingredient.
 * @param {Object|string} output - The recipe output item.
 *
 * Usage example: stonecutting(
 *     e,
 *     itemInput("minecraft:stone"),
 *     itemOutput("minecraft:stone_slab")
 * )
 * - Cuts the specified input item into the output item using a stonecutter.
 */
function stonecutting(e, input, output) {
    e.custom({
        "type": "minecraft:stonecutting",
        "ingredient": input,
        "result": output
    })
}

/**
 * Creates a Minecraft smithing transformation recipe.
 *
 * @param {Object|string} output - The recipe output item.
 * @param {Object} template - The smithing template ingredient.
 * @param {Object} base - The base item ingredient.
 * @param {Object} addition - The additional ingredient.
 *
 * Usage example: smithing(
 *     e,
 *     itemOutput("minecraft:netherite_sword"),
 *     itemInput("minecraft:netherite_upgrade_smithing_template"),
 *     itemInput("minecraft:diamond_sword"),
 *     itemInput("minecraft:netherite_ingot")
 * )
 * - Transforms the base item using the specified smithing template and addition.
 */
function smithing(e, output, template, base, addition) {
    e.custom({
        "type": "minecraft:smithing_transform",
        "template": template,
        "base": base,
        "addition": addition,
        "result": output
    })
}

/**
 * Adds items to a Minecraft item tag.
 *
 * @param {Object} e - The recipe event object.
 * @param {string} tagName - The identifier of the item tag to modify.
 * @param {Array<string>} itens - Array of item identifiers to add to the tag.
 *
 * Usage example: addTag(
 *     e,
 *     "c:ingots/iron",
 *     [
 *         "minecraft:iron_ingot",
 *         "examplemod:iron_ingot"
 *     ]
 * )
 * - Adds the specified items to the given item tag.
 * - Creates the tag if it does not already exist.
 */
function addTag(e, tagName, itens) {
    e.add(tagName, itens);
}
