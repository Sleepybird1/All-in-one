/**
 * Creates multiple Create pressing recipes from pairs of outputs and item tags.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} outputs - Array of item identifiers corresponding to each input tag.
 * @param {Array<string>} inputs - Array of item tag identifiers used as recipe inputs.
 *
 * Usage example:
 *  pressingPairs(
 *      e,
 *      [
 *          "create:iron_sheet"
 *      ],
 *      [
 *          "c:ingots/iron"
 *      ]
 *  )
 * - Creates one pressing recipe for each input/output pair.
 * - Each input is converted into an item tag using itemInputTag().
 * - The output at each index is paired with the input tag at the same index.
 */
function pressingPairs(e, outputs, inputs) {
    inputs.forEach((input, i) => {
        pressing(e, itemOutput(outputs[i]), itemInputTag(input))
    })
}

/**
 * Creates multiple Create deploying recipes, optionally using Sequenced Assembly
 * for inputs with more than one required loop.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} outputs - Array of item identifiers representing the recipe outputs.
 * @param {Array<string>} inputs - Array of item identifiers representing the base inputs.
 * @param {Array<string>} press - Array of item identifiers representing the items used for deployment.
 * @param {Array<number>} loop - Array defining the number of Sequenced Assembly loops for each recipe.
 *
 * Usage example:
 * const mechanism = [
 *     'createmechanisms:storage_mechanism'
 * ]
 *
 * const processor = [
 *     'ae2:engineering_processor'
 * ]
 *
 * const base = [
 *     'createmechanisms:zinc_mechanism'
 * ]
 *
 * const loop = [1, 1, 1, 4]
 *
 * sequenceDeploy(e, processor, base, mechanism, loop)
 *
 * - Creates a deploying recipe for each input/output pair.
 * - If the corresponding loop value is greater than 1, a Sequenced Assembly recipe is created.
 * - If the loop value is 1 or lower, a standard deploying recipe is created.
 * - The item specified in press is used as the deploying ingredient.
 */
function sequenceDeploy(e, outputs, inputs, press, loop) {
    inputs.forEach((input, i) => {
        if (loop && loop[i] && loop[i] > 1){
            sequenced_assembly(
                e,
                [
                    itemOutput(outputs[i]),
                ],
                itemInput(input),
                itemOutput(input),
                loop[i],
                [
                    deployingS(itemOutput(input), itemInput(input), itemInput(press[i]), false)
                ]
            )
        } else {
            deploying(e, itemOutput(outputs[i]), itemInput(input), itemInput(press[i]), true)
        }
    })
}

/**
 * Creates multiple AE2 processor recipes using Create Sequenced Assembly.
 *
 * Each recipe starts with the specified input and sequentially deploys
 * 'ae2:printed_silicon' and 'minecraft:redstone' onto it.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} outputs - Array of item identifiers representing the final processor outputs.
 * @param {Array<string>} inputs - Array of item identifiers representing the initial printed circuit inputs.
 *
 * Usage example:
 * const circuit = [
 *     'ae2:printed_engineering_processor'
 * ]
 *
 * const processors = [
 *     'ae2:engineering_processor'
 * ]
 *
 * processorForge(e, processors, circuit)
 *
 * - Creates one Sequenced Assembly recipe for each input/output pair.
 * - The corresponding item in inputs is used as the starting item.
 * - 'ae2:printed_silicon' is deployed onto the item first.
 * - 'minecraft:redstone' is deployed onto the item afterward.
 * - Each recipe uses one processing loop.
 */
function processorForge(e, outputs, inputs) {
    inputs.forEach((input, i) => {
        sequenced_assembly(
            e,
            [
                itemOutput(outputs[i]),
            ],
            itemInput(input),
            itemOutput(input),
            1,
            [
                deployingS(itemOutput(input), itemInput(input), itemInput('ae2:printed_silicon'), false),
                deployingS(itemOutput(input), itemInput(input), itemInput('minecraft:redstone'), false)
            ]
        )
    })
}

/**
 * Creates multiple Enderiam-tier Sequenced Assembly recipes.
 *
 * Each recipe starts with an Enderium Plate and applies a sequence of
 * pressing, deploying, and filling operations to create the specified output.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} mechanismsI - Array of item identifiers representing
 *                                      the mechanisms used as deploying inputs.
 * @param {Array<string>} mechanismsO - Array of item identifiers representing
 *                                      the final recipe outputs.
 * @param {Array<string>} transitional - Array of item identifiers representing
 *                                       the transitional items used during the
 *                                       Sequenced Assembly process.
 *
 * Usage example:
 * enderiamTier(
 *     e,
 *     [
 *         'createmechanisms:advanced_fluid_mechanism'
 *     ],
 *     [
 *         'createmechanisms:enderiam_fluid_mechanism'
 *     ],
 *     [
 *         'createmechanisms:incomplete_enderiam_fluid_mechanism'
 *     ]
 * )
 *
 * - Creates one Sequenced Assembly recipe for each mechanism.
 * - Uses 'alltheores:enderium_plate' as the starting item.
 * - Presses the transitional item.
 * - Deploys the corresponding mechanism, Enderium Gear, and Enderiam Mechanism.
 * - Fills the transitional item with 1000mb of Enderiam Fluid twice.
 * - Uses one processing loop for each recipe.
 */
function enderiamTier(e, mechanismsI, mechanismsO, transitional) {
    mechanismsI.forEach((mechanism, i) => {
        sequenced_assembly(
            e,
            [
                itemOutput(mechanismsO[i]),
            ],
            itemInput('alltheores:enderium_plate'),
            itemOutput(transitional[i]),
            1,
            [
                pressingS(itemOutput(transitional[i]), itemInput(transitional[i])),
                deployingS(itemOutput(transitional[i]), itemInput(transitional[i]), itemInput(mechanism), false),
                deployingS(itemOutput(transitional[i]), itemInput(transitional[i]), itemInput('alltheores:enderium_gear'), false),
                deployingS(itemOutput(transitional[i]), itemInput(transitional[i]), itemInput('createmechanisms:enderiam_mechanism'), false),
                fillingS(itemOutput(transitional[i]), itemInput(transitional[i]), fluidInput('createmechanisms:enderiam_fluid', 1000)),
                fillingS(itemOutput(transitional[i]), itemInput(transitional[i]), fluidInput('createmechanisms:enderiam_fluid', 1000))
            ]
        )


    })
}

/**
 * Creates multiple shaped crafting recipes for different saw tiers.
 *
 * Each recipe combines a wooden slab tag, a wooden rod tag, and a tier-specific
 * material to produce the corresponding saw.
 *
 * @param {Object} e - The recipe event object.
 * @param {Array<string>} sawTier - Array of item identifiers representing the saw outputs.
 * @param {Array<Object>} materialInput - Array of recipe ingredients representing
 *                                        the material used for each saw tier.
 *
 * Usage example:
 * sawRecipe(
 *     e,
 *     [
 *         'createmechanisms:copper_saw'
 *     ],
 *     [
 *         itemInputKey('C', 'minecraft:copper_ingot')
 *     ]
 * )
 *
 * - Creates one shaped recipe for each saw tier.
 * - Uses 'minecraft:wooden_slabs' as the A ingredient.
 * - Uses 'c:rods/wooden' as the B ingredient.
 * - Uses the corresponding materialInput as the C ingredient.
 * - Produces one saw for each recipe.
 */
function sawRecipe(e, sawTier, materialInput){
    materialInput.forEach((input, i) => {
        shaped(
            e,
            itemOutputStack(sawTier[i], 1),
            Object.assign(
                {},
                itemInputTagKey('A', 'minecraft:wooden_slabs'),
                itemInputTagKey('B', 'c:rods/wooden'),
                input
            ),
            [
                "B  ",
                "CB ",
                " CA"
            ]
        )
    })
}
