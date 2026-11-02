/**
 * Creates a simple item output JSON object.
 *
 * @param {string} id - The item identifier (e.g., "minecraft:iron_ingot").
 * @returns {Object} - JSON object representing the item output.
 *
 * Usage example: itemOutput("minecraft:iron_ingot")
 * A one iron ingot
 */
function itemOutput (id){
    if (typeof id !== "string" || id.trim() === "") {
        console.error("itemOutput: Invalid id: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    return { "id": id };
}

/**
 * Creates an item output JSON object with a stack count.
 *
 * @param {string} id - The item identifier.
 * @param {number} count - The number of items in the stack.
 * @returns {Object} - JSON object representing the item stack output.
 *
 * Usage example: itemOutputStack("minecraft:iron_ingot", 2)
 * Two iron ingots
 */
function itemOutputStack (id, count){
    if (typeof id !== "string" || id.trim() === "") {
        console.error("itemOutputStack: Invalid id: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    // Validate count
    if (typeof count !== "number" || count <= 0) {
        console.error("itemOutputStack: Invalid count: must be a positive number.");
        return null;
    }

    // Build item stack output JSON
    return {
        "count": count,
        "id": id
    };
}

/**
 * Creates an item output JSON object with a chance.
 *
 * @param {string} id - The item identifier.
 * @param {number} chance - The probability (0–1) of receiving the item.
 * @returns {Object} - JSON object representing the item output with chance.
 *
 * Usage example: itemOutputChance("minecraft:iron_ingot", 0.5)
 * A fifty percent chance of getting an iron ingot
 */
function itemOutputChance (id, chance){
    if (typeof id !== "string" || id.trim() === "") {
        console.error("itemOutputChance: Invalid id: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    if (typeof chance !== "number" || chance < 0 || chance > 1) {
        console.error("itemOutputChance: Invalid chance: must be a number between 0 and 1.");
        return null;
    }

    return {
        "chance": chance,
        "id": id
    };
}

/**
 * Creates an item output JSON object with both chance and stack count.
 *
 * @param {string} id - The item identifier.
 * @param {number} chance - The probability (0–1).
 * @param {number} count - The number of items in the stack.
 * @returns {Object} - JSON object representing the item output with chance and count.
 *
 * Usage example: itemOutputChance("minecraft:iron_ingot", 0.5, 3)
 * A fifty percent chance of getting three iron ingot
 */
function itemOutputChanceStack (id, chance, count){
    if (typeof id !== "string" || id.trim() === "") {
        console.error("itemOutputChanceStack: Invalid id: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    if (typeof chance !== "number" || chance < 0 || chance > 1) {
        console.error("itemOutputChanceStack: Invalid chance: must be a number between 0 and 1.");
        return null;
    }

    if (typeof count !== "number" || count <= 0) {
        console.error("itemOutputChanceStack: Invalid count: must be a positive number.");
        return null;
    }

    return {
        "chance": chance,
        "count": count,
        "id": id
    };
}

/**
 * Creates an item input JSON object.
 *
 * @param {string} item - The item identifier.
 * @returns {Object} - JSON object representing the item input.
 *
 * Usage example: itemInput("minecraft:iron_ingot")
 * sends an iron ingot
 */
function itemInput (item){
    if (typeof item !== "string" || item.trim() === "") {
        console.error("itemInput: Invalid item: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    return { "item": item };
}

/**
 * Creates an item input JSON object using a tag.
 *
 * @param {string} tag - The tag identifier (e.g., "forge:ingots/iron").
 * @returns {Object} - JSON object representing the item input by tag.
 *
 * Usage example: itemInput("minecraft:logs")
 * Sends an item from the minecraft:logs tag.
 */
function itemInputTag (tag){
    if (typeof tag !== "string" || tag.trim() === "") {
        console.error("itemInputTag: Invalid tag: must be a non-empty string (e.g., 'forge:ingots/iron').");
        return null;
    }

    return { "tag": tag };
}

/**
 * Creates a key mapping for an item input in mechanical crafting.
 * Used for recipes with a mechanical crafter.
 *
 * @param {string} symbol - The symbol used in the crafting pattern.
 * @param {string} id - The item identifier.
 * @returns {Object} - JSON object mapping the symbol to the item.
 *
 * Usage example: itemInputKey("A", "minecraft:iron_ingot")
 * send an iron ingot with the symbol A
 */
function itemInputKey (symbol, id){
    if (typeof symbol !== "string" || symbol.trim() === "") {
        console.error("itemInputKey: Invalid symbol: must be a non-empty string (e.g., 'A').");
        return null;
    }

    if (typeof id !== "string" || id.trim() === "") {
        console.error("itemInputKey: Invalid id: must be a non-empty string (e.g., 'minecraft:iron_ingot').");
        return null;
    }

    let obj = {};
    obj[symbol] = { "item": id };
    return obj;
}

/**
 * Creates a key mapping for a tag input in mechanical crafting.
 * Used for recipes with a mechanical crafter.
 *
 * @param {string} symbol - The symbol used in the crafting pattern.
 * @param {string} tag - The tag identifier.
 * @returns {Object} - JSON object mapping the symbol to the tag.
 *
 * Usage example: itemInputKey("A", "minecraft:iron_ingot")
 * Sends an item from the minecraft:logs tag, with the symbol A.
 */
function itemInputTagKey (symbol, tag){
    if (typeof symbol !== "string" || symbol.trim() === "") {
        console.error("itemInputTagKey: Invalid symbol: must be a non-empty string (e.g., 'A').");
        return null;
    }

    if (typeof tag !== "string" || tag.trim() === "") {
        console.error("itemInputTagKey: Invalid tag: must be a non-empty string (e.g., 'minecraft:logs').");
        return null;
    }

    let obj = {};
    obj[symbol] = { "tag": tag };
    return obj;
}