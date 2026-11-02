// Guard only unavailable optional AllTheOres literal items in these legacy recipes.
function IC_MustJs_missingAllTheOresItem(value) {
  if (!value || typeof value !== 'object') return false;
  if (Array.isArray(value)) return value.some(IC_MustJs_missingAllTheOresItem);
  if (typeof value.item === 'string' && value.item.indexOf('alltheores:') === 0 && !Item.exists(value.item)) return true;
  if (typeof value.id === 'string' && !('amount' in value) && value.id.indexOf('alltheores:') === 0 && !Item.exists(value.id)) return true;
  return Object.keys(value).some(key => IC_MustJs_missingAllTheOresItem(value[key]));
}
function IC_MustJs_optionalCustom(event, recipe) {
  if (IC_MustJs_missingAllTheOresItem(recipe)) {
    console.info('[Industrial Colonies] Skipped unavailable optional AllTheOres legacy recipe.');
    return;
  }
  return event.custom(recipe);
}

// === Recipe generation helper functions ===
/**
 * Creates a custom compacting recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipem, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Array} inputs - The list of ingredient items required for the recipe, more than one item can be used.
 *                          Use helper functions such as `itemInput()`, `itemInputTag()`, or `fluidInput()`.
 *                          All items must be wrapped inside an array [].
 * @param {boolean|string} heat - The heat requirement for the recipe.
 *                                Allowed values: false, "heated", "superheated".
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * compacting(
 *   itemOutput("minecraft:iron_ingot"),
 *   [
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget"),
 *      itemInput("minecraft:iron_nugget")
 *       ],
 *   "heated"
 * )
 *
 * Notes:
 * - If `heat` is false, the recipe will not require heat.
 * - If `heat` is "heated" or "superheated", the recipe will include a heat requirement.
 * - Invalid values for `heat` will trigger an error message in the console.
 */
function compacting (e, output, inputs, heat){
    const states = [false, "heated", "superheated"];
    if (typeof output !== "object" || !output.id) {
        console.error("Compacting: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (!Array.isArray(inputs) || inputs.length === 0) {
        console.error("Compacting: Invalid inputs: must be a non-empty array of itemInput(), itemInputTag(), or fluidInput().");
        return;
    }

    if (!inputs.every(i => typeof i === "object")) {
        console.error("Compacting: Invalid inputs: each ingredient must be an object.");
        return;
    }

    if (!states.includes(heat)) {
        console.error(`Compacting: Invalid heat value: ${heat}. Allowed values are "heated", "superheated" or false.`);
        return;
    }

    const recipe = {
        "type": "create:compacting",
        "ingredients": inputs,
        "results": [output]
    };
    if (heat !== false) recipe.heat_requirement = heat;

    IC_MustJs_optionalCustom(e, recipe);
}

/**
 * Creates a custom crushing recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array} output - The resulting items or blocks from the recipe, more than one item can be generated.
 *                         Use helper functions like `itemOutput()`, `itemOutputStack()`, `itemOutpuChance()` or `itemOutputChanceStack()`.
 *                         All items must be wrapped inside an array [].
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {number} time - The processing time (in ticks) for the recipe.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * crushing(
 *   [
 *      itemOutput("minecraft:gravel"),
 *      itemOutputChance("minecraft:gravel", 0.25)
 *   ],
 *   itemInput("minecraft:cobblestone"),
 *   200
 * )
 */
function crushing (e, output, input, time){
    if (!Array.isArray(output) || output.length === 0) {
        console.error("Crushing: Invalid output: must be a non-empty array of itemOutput(), itemOutputStack(), itemOutputChance(), or itemOutputChanceStack().");
        return;
    }

    if (!output.every(o => typeof o === "object")) {
        console.error("Crushing: Invalid output: each result must be an object.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Crushing: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof time !== "number" || time <= 0) {
        console.error("Crushing: Invalid time: must be a positive number (ticks).");
        return;
    }
    IC_MustJs_optionalCustom(e, {
        "type": "create:crushing",
        "ingredients": [input],
        "processing_time": time,
        "results": output
    });
}

/**
 * Creates a custom cutting recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {number} time - The processing time (in ticks) for the recipe.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * cutting(
 *   itemOutput("minecraft:oak_planks"),
 *   itemInput("minecraft:oak_log"),
 *   100
 * )
 */
function cutting (e, output, input, time){
    if (typeof output !== "object" || !output.id) {
        console.error("Cutting: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Cutting: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof time !== "number" || time <= 0) {
        console.error("Cutting: Invalid time: must be a positive number (ticks).");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:cutting",
        "ingredients": [input],
        "processing_time": time,
        "results": [output],
    });
}

/**
 * Creates a custom deploying recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} held - The held item used in the deploying process, only one item can be used.
 *                           Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {Object} base - The base item that will be modified, only one item can be used.
 *                           Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {boolean} keep - Whether the held item (`held`) should be kept after the process.
 *                         `true` keeps the item, `false` consumes it.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * deploying(
 *   itemOutput("minecraft:iron_door"),
 *   itemInput("minecraft:iron_ingot"),
 *   itemInput("minecraft:stick"),
 *   true
 * )
 */
function deploying (e, output, base, held, keep){
    if (typeof output !== "object" || !output.id) {
        console.error("Deploying: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (typeof held !== "object" || (!held.item && !held.tag)) {
        console.error("Deploying: Invalid held item: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof base !== "object" || (!base.item && !base.tag)) {
        console.error("Deploying: Invalid base item: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof keep !== "boolean") {
        console.error("Deploying: Invalid keep value: must be a boolean (true or false).");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:deploying",
        "ingredients": [base, held],
        "keep_held_item": keep,
        "results": [output]
    });
}

/**
 * Creates a custom emptying recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output_item - The resulting item after emptying, only one item can be generated.
 *                               Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} output_fluid - The resulting fluid after emptying, only one fluid can be generated.
 *                                Use the helper function `fluidOutput()`.
 * @param {Object} input - The ingredient item that will be emptied, only one item can be used.
 *                         Use helper functions such as `itemInput()`, `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * emptying(
 *   itemOutput("minecraft:bucket"),
 *   fluidOutput("minecraft:water", 1000),
 *   itemInput("minecraft:water_bucket")
 * )
 */
function emptying (e, output_item, output_fluid, input){
    if (typeof output_item !== "object" || !output_item.id) {
        console.error("Emptying: Invalid output_item: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (typeof output_fluid !== "object" || !output_fluid.id || typeof output_fluid.amount !== "number") {
        console.error("Emptying: Invalid output_fluid: must be an object created with fluidOutput().");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Emptying: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:emptying",
        "ingredients": [input],
        "results": [output_item, output_fluid]
    });
}

/**
 * Creates a custom filling recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input - The ingredient item that will be filled, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {Object} fluid - The fluid used in the filling process, only one fluid can be used.
 *                         Use the helper function `fluidInput()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * filling(
 *   itemOutput("minecraft:honey_bottle"),
 *   itemInput("minecraft:glass_bottle"),
 *   fluidInput("minecraft:honey", 250)
 * )
 */
function filling (e, output, input, fluid){
    if (typeof output !== "object" || !output.id) {
        console.error("Filling: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Filling: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof fluid !== "object" || !fluid.fluid || typeof fluid.amount !== "number") {
        console.error("Filling: Invalid fluid: must be an object created with fluidInput().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:filling",
        "ingredients": [input, fluid],
        "results": [output]
    });
}

/**
 * Creates a custom haunting recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array} output - The resulting items or blocks from the recipe, more than one item can be generated.
 *                         Use helper functions like `itemOutput()`, `itemOutputStack()`, `itemOutpuChance()` or `itemOutputChanceStack()`.
 *                         All items must be wrapped inside an array [].
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * haunting(
 *   [
 *      itemOutput("minecraft:soul_sand")
 *   ],
 *   itemInput("minecraft:sand")
 * )
 */
function haunting (e, output, input){
    if (!Array.isArray(output) || output.length === 0) {
        console.error("Haunting: Invalid output: must be a non-empty array of itemOutput(), itemOutputStack(), itemOutputChance(), or itemOutputChanceStack().");
        return;
    }

    if (!output.every(o => typeof o === "object")) {
        console.error("Haunting: Invalid output: each result must be an object.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Haunting: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:haunting",
        "ingredients": [input],
        "results": output
    });
}

/**
 * Creates a custom item application recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input_block - The block or base item that will receive the application.
 *                               Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {Object} input_item - The item applied to the block during the process.
 *                              Use helper functions such as `itemInput()` or `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * item_application(
 *   itemOutput("minecraft:grass_block"),
 *   itemInput("minecraft:dirt"),
 *   itemInput("minecraft:wheat_seeds")
 * );
 *
 * Notes:
 * - Automatically generates a deploying recipe.
 */
function item_application(e, output, input_block, input_item){
    if (typeof output !== "object" || !output.id) {
        console.error("Item_application: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (typeof input_block !== "object" || (!input_block.item && !input_block.tag)) {
        console.error("Item_application: Invalid input_block: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof input_item !== "object" || (!input_item.item && !input_item.tag)) {
        console.error("Item_application: Invalid input_item: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:item_application",
        "ingredients": [input_block, input_item],
        "results": [output],
    });
}

/**
 * Creates a custom mechanical crafting recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input - The key mapping of characters in the pattern to ingredients.
 *                         Each key should be wrapped in helper functions such as `itemInputKey()` or `itemInputTagKey()`.
 * @param {Array<string>} pattern - The crafting grid pattern represented as an array of strings.
 *                                  Each character corresponds to a key defined in `input`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * mechanical_crafting(
 *   itemOutputStack("minecraft:diamond_pickaxe", 1),
 *   Object.assign(
 *     {},
 *     itemInputKey("A", "minecraft:diamond"),
 *     itemInputTagKey("B", "minecraft:stick")
 *   ),
 *   [
 *     "AAA",
 *     " B ",
 *     " B "
 *   ]
 * )
 * Notes:
 * - If the output is a tool, the quantity must be 1. if it is an item or a block, it can be more.
 */
function mechanical_crafting (e, output, input, pattern){
    if (typeof output !== "object" || !output.id) {
        console.error("Mechanical_crafting: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (output.count !== undefined && (typeof output.count !== "number" || output.count <= 0)) {
        console.error("Mechanical_crafting: Invalid output count: must be a positive number.");
        return;
    }

    if (typeof input !== "object" || Object.keys(input).length === 0) {
        console.error("Mechanical_crafting: Invalid input: must be a non-empty object created with itemInputKey() or itemInputTagKey().");
        return;
    }

    for (const key in input) {
        let val = input[key]; // usar let em vez de const
        if (typeof val !== "object" || (!val.item && !val.tag)) {
            console.error(`Mechanical_crafting: Invalid input mapping for symbol '${key}': must contain 'item' or 'tag'.`);
            return;
        }
    }

    if (!Array.isArray(pattern) || pattern.length === 0) {
        console.error("Mechanical_crafting: Invalid pattern: must be a non-empty array of strings.");
        return;
    }

    if (!pattern.every(row => typeof row === "string" && row.length > 0)) {
        console.error("Mechanical_crafting: Invalid pattern: each row must be a non-empty string.");
        return;
    }

    const symbolsInPattern = new Set(pattern.join("").replace(/\s/g, ""));
    for (const symbol of symbolsInPattern) {
        if (!input[symbol]) {
            console.error(`Mechanical_crafting: Invalid pattern: symbol '${symbol}' is not defined in input mapping.`);
            return;
        }
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:mechanical_crafting",
        "accept_mirrored": false,
        "category": "misc",
        "key": input,
        "pattern": pattern,
        "result": output,
        "show_notification": false
    });
}

/**
 * Creates a custom milling recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array|Object} output - The resulting items or blocks from the recipe, more than one item can be generated.
 *                               Use helper functions like `itemOutput()`, `itemOutputStack()`, `itemOutpuChance()` or `itemOutputChanceStack()`.
 *                               All items must be wrapped inside an array [].
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()`, `itemInputTag()`.
 * @param {number} time - The processing time (in ticks) for the milling operation.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * milling([
 *   itemOutputStack("create:wheat_flour", 4),
 *   itemOutputChanceStack("create:wheat_flour", 2)
 * ],
 *   itemInput("minecraft:wheat"),
 *   200
 * )
 */
function milling (e, output, input, time){
    const results = Array.isArray(output) ? output : [output];

    if (!Array.isArray(results) || results.length === 0) {
        console.error("Milling: Invalid output: must be a non-empty array of itemOutput(), itemOutputStack(), itemOutputChance(), or itemOutputChanceStack().");
        return;
    }

    if (!results.every(o => typeof o === "object")) {
        console.error("Milling: Invalid output: each result must be an object.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Milling: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof time !== "number" || time <= 0) {
        console.error("Milling: Invalid time: must be a positive number (ticks).");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:milling",
        "ingredients": [input],
        "processing_time": time,
        "results": output
    });
}

/**
 * Creates a custom mixing recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array|Object} output - The resulting items or blocks from the recipe, more than one item can be used.
 *                                Use helper functions like `itemOutput()`, `itemOutputStack()`, `itemOutpuChance()` or `itemOutputChanceStack()`.
 *                                All items must be wrapped inside an array [].
 * @param {Array<Object>} input - The list of ingredient items required for the recipe, more than one item can be generated.
 *                                Use helper functions such as `itemInput()`, `itemInputTag()` or `fluidInput()`.
 *                                All items must be wrapped inside an array [].
 * @param {boolean|string} heat - The heat requirement for the recipe.
 *                                Allowed values: false, "heated", "superheated".
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * mixing(
 *   [itemOutputStack("minecraft:cookie", 8)],
 *   [
 *     itemInput("minecraft:wheat"),
 *     itemInput("minecraft:cocoa_beans")
 *   ],
 *   "heated"
 * );
 *
 * Notes:
 * - If `heat` is false, the recipe will not require heat.
 * - If `heat` is "heated" or "superheated", the recipe will include a heat requirement.
 * - Invalid values for `heat` will trigger an error message in the console.
 */
function mixing (e, output, input, heat){
    const states = [false, "heated", "superheated"];

    const results = Array.isArray(output) ? output : [output];

    if (!Array.isArray(results) || results.length === 0) {
        console.error("Mixing: Invalid output: must be a non-empty array of itemOutput(), itemOutputStack(), itemOutputChance(), or itemOutputChanceStack().");
        return;
    }
    if (!results.every(o => typeof o === "object")) {
        console.error("Mixing: Invalid output: each result must be an object.");
        return;
    }

    if (!Array.isArray(input) || input.length === 0) {
        console.error("Mixing: Invalid input: must be a non-empty array of itemInput(), itemInputTag(), or fluidInput().");
        return;
    }

    if (!input.every(i => typeof i === "object" && (i.item || i.tag || i.fluid))) {
        console.error("Mixing: Invalid input: each ingredient must be an object created with itemInput(), itemInputTag(), or fluidInput().");
        return;
    }

    if (!states.includes(heat)) {
        console.error(`Mixing: Invalid heat value: ${heat}. Allowed values are "heated", "superheated" or false.`);
        return;
    }

    const recipe = {
        "type": "create:mixing",
        "ingredients": input,
        "results": results
    };
    if (heat !== false) recipe.heat_requirement = heat;

    IC_MustJs_optionalCustom(e, recipe);
}

/**
 * Creates a custom pressing recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * pressing(
 *   itemOutput("minecraft:iron_plate"),
 *   itemInput("minecraft:iron_ingot")
 * )
 */
function pressing (e, output, input){
    if (typeof output !== "object" || !output.id) {
        console.error("Pressing: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (output.count !== undefined && (typeof output.count !== "number" || output.count <= 0)) {
        console.error("Pressing: Invalid output count: must be a positive number.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Pressing: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:pressing",
        "ingredients": [input],
        "results": [output]
    });
}

/**
 * Creates a custom sandpaper polishing recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Object} output - The resulting item or block from the recipe, only one item can be generated.
 *                          Use the helper function `itemOutput()` or `itemOutputStack()`.
 * @param {Object} input - The ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()`, `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * polishing(
 *   itemOutput("minecraft:polished_quartz"),
 *   itemInput("minecraft:quartz_block")
 * )
 */
function polishing (e, output, input){
    if (typeof output !== "object" || !output.id) {
        console.error("Polishing: Invalid output: must be an object created with itemOutput() or itemOutputStack().");
        return;
    }

    if (output.count !== undefined && (typeof output.count !== "number" || output.count <= 0)) {
        console.error("Polishing: Invalid output count: must be a positive number.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Polishing: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:sandpaper_polishing",
        "ingredients": [input],
        "results": [output]
    });
}

/**
 * Creates a custom splashing recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array|Object} output - The resulting items or blocks from the recipe.
 *                                Use helper functions like `itemOutput()`, `itemOutputStack()`, `itemOutpuChance()` or `itemOutputChanceStack()`.
 *                                All items must be wrapped inside an array [].
 * @param {Object} input - The ingredient item required for the recipe.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * splashing(
 *   [itemOutputStack("minecraft:clay_ball", 4)],
 *   itemInput("minecraft:sand")
 * )
 */
function splashing (e, output, input){
    const results = Array.isArray(output) ? output : [output];

    if (!Array.isArray(results) || results.length === 0) {
        console.error("Splashing: Invalid output: must be a non-empty array of itemOutput(), itemOutputStack(), itemOutputChance(), or itemOutputChanceStack().");
        return;
    }

    if (!results.every(o => typeof o === "object")) {
        console.error("Splashing: Invalid output: each result must be an object.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Splashing: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    IC_MustJs_optionalCustom(e, {
        "type": "create:splashing",
        "ingredients": [input],
        "results": output
    });
}

/**
 * Creates a custom sequenced assembly recipe using the Create mod.
 *
 * @param e - Recipe creation event, for example, `ServerEvents.recipes(event => {})`, pass in `event`
 *
 * @param {Array|Object} output - The resulting items or blocks from the recipe, only one item can be generated.
 *                                Use helper functions like `itemOutputStack()`.
 *                                All items must be wrapped inside an array [].
 * @param {Object} input - The base ingredient item required for the recipe, only one item can be used.
 *                         Use helper functions such as `itemInput()` or `itemInputTag()`.
 * @param {Object} transitional - The transitional item used during the assembly process, only one item can be used.
 *                                This item persists through each step until the final output.
 *                                Use helper functions like `itemOutput()`.
 *                                Note: Used as an input and output in all internal recipes.
 * @param {number} loops - The number of times the sequence should repeat.
 * @param {Array<Object>} processing - The sequence of processing steps (e.g., cutting, deploying, pressing).
 *                                     Each step should be defined using helper functions like `cuttingS()`, `deployingS()`, `fillingS()` or `pressingS()`.
 *
 * @returns {void} - This function does not return a value; it registers the recipe.
 *
 * Usage example:
 * sequenced_assembly([
 *     itemOutputChance("create:precision_mechanism", 0.5),
 *     itemOutputChance("create:iron_sheet", 0.5),
 *   ],
 *   itemInput("create:iron_sheet"),
 *   itemOutput("create:incomplete_precision_mechanism"),
 *   5,
 *   [
 *     deployingS(itemOutput("create:incomplete_precision_mechanism"), itemInput("create:incomplete_precision_mechanism"), itemInput("create:cogwheel"), true),
 *     pressingS(itemOutput("create:incomplete_precision_mechanism"), itemInput("create:incomplete_precision_mechanism")),
 *     cuttingS(itemOutput("create:incomplete_precision_mechanism"), itemInput("create:incomplete_precision_mechanism"), 100),
 *     fillingS(itemOutput("create:incomplete_precision_mechanism"), itemInput("create:incomplete_precision_mechanism"), fluidInput('minecraft:lava', 100))
 *   ]
 * )
 */
function sequenced_assembly(e, output, input, transitional, loops, processing) {
    const results = Array.isArray(output) ? output : [output];

    if (!Array.isArray(results) || results.length === 0 || !results.every(o => typeof o === "object" && o.id)) {
        console.error("Sequenced_assembly: Invalid output: must be a non-empty array of itemOutputStack() objects.");
        return;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Sequenced_assembly: Invalid input: must be an object created with itemInput() or itemInputTag().");
        return;
    }

    if (typeof transitional !== "object" || !transitional.id) {
        console.error("Sequenced_assembly: Invalid transitional item: must be an object created with itemOutput().");
        return;
    }

    if (typeof loops !== "number" || loops <= 0) {
        console.error("Sequenced_assembly: Invalid loops: must be a positive number.");
        return;
    }

    if (!Array.isArray(processing) || processing.length === 0 || !processing.every(p => typeof p === "object")) {
        console.error("Sequenced_assembly: Invalid processing: must be a non-empty array of step objects (cuttingS, deployingS, pressingS, fillingS).");
        return;
    }

    const recipe = {
        "type": "create:sequenced_assembly",
        "ingredient": input,
        "loops": loops,
        "results": results,
        "sequence": processing,
        "transitional_item": transitional
    };

    IC_MustJs_optionalCustom(e, recipe);
}


// === Auxiliary processing for sequenced assembly
/**
 * Returns a cutting recipe JSON object for use in sequenced assembly.
 *
 * @param {Object} output - The resulting item. Use `itemOutput(TransitionalItem)`.
 * @param {Object} input - The ingredient item. Use `itemInput(TransitionalItem)` or similar helpers.
 * @param {number} time - Processing time in ticks.
 * @returns {Object} - JSON object representing the cutting step.
 */
function cuttingS (output, input, time){
    if (typeof output !== "object" || !output.id) {
        console.error("Sequenced_assembly: cuttingS - Invalid output: must be an object created with itemOutput().");
        return null;
    }

    // Validate input
    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Sequenced_assembly: cuttingS - Invalid input: must be an object created with itemInput() or itemInputTag().");
        return null;
    }

    // Validate time
    if (typeof time !== "number" || time <= 0) {
        console.error("Sequenced_assembly: cuttingS - Invalid time: must be a positive number (ticks).");
        return null;
    }

    return {
        "type": "create:cutting",
        "ingredients": [input],
        "processing_time": time,
        "results": [output],
    };
}

/**
 * Returns a deploying recipe JSON object for use in sequenced assembly.
 *
 * @param {Object} output - The resulting item. Use `itemOutput(TransitionalItem)`.
 * @param {Object} held - The held item used in deploying. Use `itemInput(ExtraItem)`.
 * @param {Object} base - The base item being modified. Use `itemInput(TransitionalItem)`.
 * @param {boolean} keep - Whether the held item is preserved (`true`) or consumed (`false`).
 * @returns {Object} - JSON object representing the deploying step.
 */
function deployingS (output, base, held, keep){
    if (typeof output !== "object" || !output.id) {
        console.error("Sequenced_assembly: deployingS - Invalid output: must be an object created with itemOutput().");
        return null;
    }

    // Validate held
    if (typeof held !== "object" || (!held.item && !held.tag)) {
        console.error("Sequenced_assembly: deployingS - Invalid held item: must be an object created with itemInput() or itemInputTag().");
        return null;
    }

    // Validate base
    if (typeof base !== "object" || (!base.item && !base.tag)) {
        console.error("Sequenced_assembly: deployingS - Invalid base item: must be an object created with itemInput() or itemInputTag().");
        return null;
    }

    // Validate keep
    if (typeof keep !== "boolean") {
        console.error("Sequenced_assembly: deployingS - Invalid keep value: must be a boolean (true or false).");
        return null;
    }

    return {
        "type": "create:deploying",
        "ingredients": [base, held],
        "keep_held_item": keep,
        "results": [output]
    };
}

/**
 * Returns a filling recipe JSON object for use in sequenced assembly.
 *
 * @param {Object} output - The resulting item. Use `itemOutput(TransitionalItem)`.
 * @param {Object} input - The item to be filled. Use `itemInput(TransitionalItem)`.
 * @param {Object} fluid - The fluid used in filling. Use `fluidInput(ExtraFluid)`.
 * @returns {Object} - JSON object representing the filling step.
 */
function fillingS (output, input, fluid){
    if (typeof output !== "object" || !output.id) {
        console.error("Sequenced_assembly: fillingS - Invalid output: must be an object created with itemOutput().");
        return null;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Sequenced_assembly: fillingS - Invalid input: must be an object created with itemInput() or itemInputTag().");
        return null;
    }

    if (typeof fluid !== "object" || !fluid.fluid || typeof fluid.amount !== "number") {
        console.error("Sequenced_assembly: fillingS - Invalid fluid: must be an object created with fluidInput().");
        return null;
    }

    return {
        "type": "create:filling",
        "ingredients": [input, fluid],
        "results": [output]
    };
}

/**
 * Returns a pressing recipe JSON object for use in sequenced assembly.
 *
 * @param {Object} output - The resulting item. Use `itemOutput(TransitionalItem)`.
 * @param {Object} input - The ingredient item. Use `itemInput(TransitionalItem)`.
 * @returns {Object} - JSON object representing the pressing step.
 */
function pressingS (output, input){
    if (typeof output !== "object" || !output.id) {
        console.error("Sequenced_assembly: pressingS - Invalid output: must be an object created with itemOutput().");
        return null;
    }

    if (typeof input !== "object" || (!input.item && !input.tag)) {
        console.error("Sequenced_assembly: pressingS - Invalid input: must be an object created with itemInput() or itemInputTag().");
        return null;
    }
    return {
        "type": "create:pressing",
        "ingredients": [input],
        "results": [output]
    };
}