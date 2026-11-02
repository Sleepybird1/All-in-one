/**
 * Creates an AE2 Inscriber recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object} output - The recipe output item.
 * @param {Array<Object>} input - Array containing the bottom, middle, and top ingredients.
 * @param {string} mode - The Inscriber recipe mode (e.g., "inscribe", "press").
 *
 * Usage example:
 *  inscriberPress(
 *      e,
 *      itemOutput("ae2:printed_silicon"),
 *      [
 *          itemInput("ae2:silicon"),
 *          itemInput("minecraft:iron_ingot"),
 *          itemInput("ae2:silicon")
 *      ],
 *      "inscribe"
 *  )
 * - Creates an AE2 Inscriber recipe using the specified bottom, middle, and top ingredients.
 */
function inscriberPress(e, output, input, mode) {
    e.custom({
        "type": "ae2:inscriber",
        "ingredients": {
            "bottom": input[0],
            "middle": input[1],
            "top": input[2]
        },
        "mode": mode,
        "result": output
    });
}

/**
 * Creates an AE2 transformation recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object} output - The recipe output item.
 * @param {Array<Object>} input - Array containing the recipe input ingredients.
 *                              The first input must be 'ae2:charged_certus_quartz_crystal'.
 *
 * Usage example:
 *  transform(
 *      e,
 *      itemOutput("ae2:fluix_crystal"),
 *      [
 *          itemInput("ae2:charged_certus_quartz_crystal"),
 *          itemInput("minecraft:redstone"),
 *          itemInput("minecraft:quartz")
 *      ]
 *  )
 * - Transforms the specified ingredients into the output item.
 */
function transform(e, output, input) {
    e.custom({
        "type": "ae2:transform",
        "ingredients": input,
        "result": output
    });
}

/**
 * Creates an AE2 Charger recipe.
 *
 * @param {Object} e - The recipe event object.
 * @param {Object} output - The recipe output item.
 * @param {Object} input - The recipe input ingredient.
 *
 * Usage example:
 *  charger(
 *      e,
 *      itemOutput("ae2:charged_certus_quartz_crystal"),
 *      itemInput("ae2:certus_quartz_crystal")
 *  )
 * - Charges the specified input item and produces the output item.
 */
function charger(e, output, input) {
    e.custom({
        "type": "ae2:charger",
        "ingredient": input,
        "result": output
    });
}
