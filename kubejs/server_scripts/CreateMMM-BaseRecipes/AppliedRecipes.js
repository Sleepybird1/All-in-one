ServerEvents.recipes(e => {
    const baseMaterial = [
        'ae2:silicon',
        'minecraft:gold_ingot',
        'ae2:certus_quartz_crystal',
        'minecraft:diamond'
    ]
    const printedMaterial = [
        'ae2:printed_silicon',
        'ae2:printed_logic_processor',
        'ae2:printed_calculation_processor',
        'ae2:printed_engineering_processor'
    ]
    const press = [
        'ae2:silicon_press',
        'ae2:logic_processor_press',
        'ae2:calculation_processor_press',
        'ae2:engineering_processor_press'
    ]
    sequenceDeploy(e, printedMaterial, baseMaterial, press)

    const circuit = [
        'ae2:printed_engineering_processor',
        'ae2:printed_calculation_processor',
        'ae2:printed_logic_processor'
    ]
    const processors = [
        'ae2:engineering_processor',
        'ae2:calculation_processor',
        'ae2:logic_processor'
    ]
    processorForge(e, processors, circuit)
})