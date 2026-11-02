===========================
README - Mod Usage Guide
===========================

📂 Structure
------------
The "MustJS" folder contains all required functions.
- Use it only as a library to create your recipes.
- DO NOT edit it directly, as it is updated multiple times during gameplay.

🛠️ Creating New Recipes
------------------------
To start a new recipe event, create a new .js file and use:

ServerEvents.recipes(event => {
    // your recipes here
})

IMPORTANT: Recipe generation functions require the "event" parameter to work properly.

📜 Function List
----------------

=== CreateBaseFunctions ===
- compacting (e, output, inputs, heat)
- crushing (e, output, input, time)
- cutting (e, output, input, time)
- deploying (e, output, held, base, keep)
- emptying (e, output_item, output_fluid, input)
- filling (e, output, input, fluid)
- haunting (e, output, input)
- item_application (e, output, input_block, input_item)
- mechanical_crafting (e, output, input, pattern)
- milling (e, output, input, time)
- mixing (e, output, input, heat)
- pressing (e, output, input)
- polishing (e, output, input)
- splashing (e, output, input)
- sequenced_assembly (e, output, input, transitional, loops, processing)

=== Auxiliary processing for sequenced assembly ===
- cuttingS (output, input, time)
- deployingS (output, held, base, keep)
- fillingS (output, input, fluid)
- pressingS (output, input)

=== FluidManipulator ===
- fluidOutput (fluid_id, fluid_amount)
- fluidInput (fluid_id, fluid_amount)

=== ItemManipulator ===
- itemOutput (id)
- itemOutputStack (id, count)
- itemOutputChance (id, chance)
- itemOutputChanceStack (id, chance, count)
- itemInput (item)
- itemInputTag (tag)
- itemInputKey (symbol, id)
- itemInputTagKey (symbol, tag)

===========================
End of README
===========================