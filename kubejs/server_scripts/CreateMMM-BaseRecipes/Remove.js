ServerEvents.recipes(e => {
    RemoveOutput(e,
        [
            'ae2:printed_silicon',
            'ae2:printed_logic_processor',
            'ae2:printed_calculation_processor',
            'ae2:printed_engineering_processor'
        ]
    );
    RemoveId(
        e,
        [
            'alltheores:crafting/bronze/alloy_blending_from_dust',
            'ae2:blasting/silicon_from_certus_quartz_dust',
            'ae2:smelting/silicon_from_certus_quartz_dust'
        ]
    )

    ReplaceItem(e, 'alltheores:bronze_ingot','createmechanisms:bronze')
    ReplaceItem(e, 'alltheores:copper_plate', 'create:copper_sheet')
    ReplaceItem(e, 'alltheores:brass_plate', 'create:brass_sheet')
    ReplaceItem(e, 'alltheores:iron_plate', 'create:iron_sheet')
    ReplaceItem(e, 'alltheores:gold_plate', 'create:golden_sheet')
    ReplaceItem(e, 'alltheores:brass_ingot', 'create:brass_ingot')
    ReplaceItem(e, 'alltheores:zinc_ingot', 'create:zinc_ingot')

    ReplaceInput(e, 'ae2:engineering_processor', 'createmechanisms:storage_mechanism')
    ReplaceInput(e, 'ae2:logic_processor', 'createmechanisms:logic_mechanism')
    ReplaceInput(e, 'ae2:calculation_processor', 'createmechanisms:computing_mechanism')
})