/**
 * Creates a fluid input JSON object.
 *
 * @param {string} fluid_id - The fluid identifier (e.g., "minecraft:water").
 * @param {number} fluid_amount - The amount of fluid in millibuckets.
 * @returns {Object} - JSON object representing the fluid input.
 *
 * Usage example: fluidInput("minecraft:lava", 1000)
 * - A 1000mb of lava (one bucket)
 */
function fluidInput (fluid_id, fluid_amount){
    if (typeof fluid_id !== "string" || fluid_id.trim() === "") {
        console.error("fluidInput: Invalid fluid_id: must be a non-empty string (e.g., 'minecraft:water').");
        return null;
    }

    if (typeof fluid_amount !== "number" || fluid_amount <= 0) {
        console.error("fluidInput: Invalid fluid_amount: must be a positive number (millibuckets).");
        return null;
    }

    return {
        "type": "neoforge:single",
        "amount": fluid_amount,
        "fluid": fluid_id
    };
}

/**
 * Creates a fluid output JSON object.
 *
 * @param {string} fluid_id - The fluid identifier.
 * @param {number} fluid_amount - The amount of fluid in millibuckets.
 * @returns {Object} - JSON object representing the fluid output.
 *
 * Usage example: fluidOutput("minecraft:lava", 1000)
 * - A 1000mb of lava (one bucket)
 */
function fluidOutput (fluid_id, fluid_amount){
    if (typeof fluid_id !== "string" || fluid_id.trim() === "") {
        console.error("fluidOutput: Invalid fluid_id: must be a non-empty string (e.g., 'minecraft:lava').");
        return null;
    }

    if (typeof fluid_amount !== "number" || fluid_amount <= 0) {
        console.error("fluidOutput: Invalid fluid_amount: must be a positive number (millibuckets).");
        return null;
    }

    return {
        "amount": fluid_amount,
        "id": fluid_id
    };
}