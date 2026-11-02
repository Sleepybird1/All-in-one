ServerEvents.recipes(e => {
    //Wooden Mechanism Recipes:
    e.shaped(
        Item.of('createmechanisms:wooden_mechanism', 2),
        [
            'AB',
            'CD'
        ],
        {
            A: '#c:stripped_woods',
            B: '#createmechanisms:saw',
            C: '#minecraft:wooden_slabs',
            D: 'create:cogwheel'
        }
    )
    const trans_wooden = 'createmechanisms:incomplete_wooden_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:wooden_mechanism')
        ],
        itemInputTag('minecraft:wooden_slabs'),
        itemOutput('createmechanisms:incomplete_wooden_mechanism'),
        1,
        [
            deployingS(itemOutput(trans_wooden), itemInput(trans_wooden),itemInput('create:cogwheel'), false),
            deployingS(itemOutput(trans_wooden),itemInput(trans_wooden), itemInputTag('createmechanisms:saw'), false),
            pressingS(itemOutput(trans_wooden), itemInput(trans_wooden))
        ]
    )

    //Zinc Mechanism Recipes:
    e.shaped(
        Item.of('createmechanisms:zinc_mechanism'),
        [
            'ABA',
            'CDC',
            'ACA'
        ],
        {
            A: '#c:nuggets/zinc',
            B: 'create:large_cogwheel',
            C: '#c:ingots/zinc',
            D: 'createmechanisms:wooden_mechanism'
        }
    )
    const trans_zinc = 'createmechanisms:incomplete_zinc_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:zinc_mechanism')
        ],
        itemInputTag('c:ingots/zinc'),
        itemOutput(trans_zinc),
        1,
        [
            pressingS(itemOutput(trans_zinc), itemInput(trans_zinc)),
            deployingS(itemOutput(trans_zinc), itemInput(trans_zinc), itemInput('createmechanisms:wooden_mechanism'), false),
            deployingS(itemOutput(trans_zinc), itemInput(trans_zinc), itemInput('create:large_cogwheel'), false)
        ]
    )

    //Rubber Mechanism Recipes:
    e.shaped(
        Item.of('createmechanisms:rubber_mechanism'),
        [
            "ABA",
            "BCB",
            "DBD"
        ],
        {
            A: '#c:nuggets/copper',
            B: 'createmechanisms:cured_rubber',
            C: 'createmechanisms:wooden_mechanism',
            D: 'create:copper_sheet'
        }
    )
    const trans_rubber = 'createmechanisms:incomplete_rubber_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:rubber_mechanism')
        ],
        itemInput('createmechanisms:wooden_mechanism'),
        itemOutput(trans_rubber),
        3,
        [
            deployingS(itemOutput(trans_rubber), itemInput(trans_rubber), itemInput('createmechanisms:cured_rubber'),false),
            pressingS(itemOutput(trans_rubber), itemInput(trans_rubber)),
            deployingS(itemOutput(trans_rubber), itemInput(trans_rubber), itemInputTag('c:nuggets/copper'), false),
            pressingS(itemOutput(trans_rubber), itemInput(trans_rubber)),
            fillingS(itemOutput(trans_rubber), itemInput(trans_rubber), fluidInput('minecraft:water', 250))
        ]
    )

    //Redstone Mechanism Recipe:
    mixing(
        e,
        [itemOutput('createmechanisms:redstone_mechanism')],
        [
            itemInput('minecraft:stone_slab'),
            itemInputTag('c:gems/quartz'),
            itemInputTag('c:dusts/redstone')
        ],
        false
    )

    //Fluid Mechanism Recipe:
    const trans_fluid = 'createmechanisms:incomplete_fluid_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:fluid_mechanism')
        ],
        itemInput('createmechanisms:rubber_mechanism'),
        itemOutput(trans_fluid),
        2,
        [
            deployingS(itemOutput(trans_fluid), itemInput(trans_fluid), itemInput('create:fluid_pipe'), false),
            deployingS(itemOutput(trans_fluid), itemInput(trans_fluid), itemInput('create:fluid_tank'), false),
            deployingS(itemOutput(trans_fluid), itemInput(trans_fluid), itemInput('createmechanisms:cured_rubber'), false),
            pressingS(itemOutput(trans_fluid), itemInput(trans_fluid)),
            pressingS(itemOutput(trans_fluid), itemInput(trans_fluid))
        ]
    )

    //Heat Mechanism Recipe:
    const trans_heat = 'createmechanisms:incomplete_heat_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:heat_mechanism')
        ],
        itemInput('createmechanisms:bronze'),
        itemOutput(trans_heat),
        2,
        [
            pressingS(itemOutput(trans_heat), itemInput(trans_heat)),
            fillingS(itemOutput(trans_heat), itemInput(trans_heat), fluidInput('minecraft:lava', 500)),
            deployingS(itemOutput(trans_heat), itemInput(trans_heat), itemInput('minecraft:magma_block'), false),
            deployingS(itemOutput(trans_heat), itemInput(trans_heat), itemInput('createmechanisms:cured_rubber'), false),
            pressingS(itemOutput(trans_heat), itemInput(trans_heat))
        ]
    )

    //Low Heat Mechanism Recipe:
    const trans_low_heat = 'createmechanisms:incomplete_low_heat_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:low_heat_mechanism')
        ],
        itemInput('createmechanisms:heat_mechanism'),
        itemOutput(trans_low_heat),
        1,
        [
            fillingS(itemOutput(trans_low_heat), itemInput(trans_low_heat), fluidInput('minecraft:water', 250)),
            deployingS(itemOutput(trans_low_heat), itemInput(trans_low_heat), itemInput('minecraft:coal'), false),
            deployingS(itemOutput(trans_low_heat), itemInput(trans_low_heat), itemInput('create:cinder_flour'), false),
            deployingS(itemOutput(trans_low_heat), itemInput(trans_low_heat), itemInput('minecraft:blaze_powder'), false),
            fillingS(itemOutput(trans_low_heat), itemInput(trans_low_heat), fluidInput('minecraft:water', 250))
        ]
    )

    //
    const trans_enderiam = 'createmechanisms:incomplete_enderiam_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:enderiam_mechanism')
        ],
        itemInput('createmechanisms:advanced_precision_mechanism'),
        itemOutput(trans_enderiam),
        1,
        [
            deployingS(itemOutput(trans_enderiam), itemInput(trans_enderiam), itemInput('minecraft:ender_pearl'), false),
            fillingS(itemOutput(trans_enderiam), itemInput(trans_enderiam), fluidInput('createmechanisms:enderiam_fluid', 1000)),
            deployingS(itemOutput(trans_enderiam), itemInput(trans_enderiam), itemInput('createmechanisms:cured_enderiam_rubber'), false)
        ]
    )

    //
    const trans_advanced_precision = 'createmechanisms:incomplete_advanced_precision_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:advanced_precision_mechanism')
        ],
        itemInput('create:precision_mechanism'),
        itemOutput(trans_advanced_precision),
        1,
        [
            deployingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision), itemInput('createmechanisms:advanced_heat_mechanism'), false),
            pressingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision)),
            deployingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision), itemInput('createmechanisms:advanced_fluid_mechanism'), false),
            pressingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision)),
            deployingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision), itemInput('createmechanisms:advanced_storage_mechanism'), false),
            pressingS(itemOutput(trans_advanced_precision), itemInput(trans_advanced_precision))
        ]
    )
    inscriberPress(
        e,
        itemOutput('createmechanisms:advanced_precision_mechanism'),
        [
            itemInput('createmechanisms:advanced_fluid_mechanism'),
            itemInput('createmechanisms:advanced_storage_mechanism'),
            itemInput('createmechanisms:advanced_heat_mechanism')
        ],
        'press'
    )

    //Incomplete Advanced Storage Mechanism Recipe:
    inscriberPress(
        e,
        itemOutput('createmechanisms:incomplete_advanced_storage_mechanism'),
        [
            itemInput('createmechanisms:computing_mechanism'),
            itemInput('createmechanisms:storage_mechanism'),
            itemInput('createmechanisms:logic_mechanism')
        ],
        'press'
    )

    //Advanced Storage Mechanism Recipe:
    transform(
        e,
        itemOutput('createmechanisms:advanced_storage_mechanism'),
        [
            itemInput('ae2:charged_certus_quartz_crystal'),
            itemInput('createmechanisms:incomplete_advanced_storage_mechanism'),
            itemInput('ae2:fluix_crystal'),
            itemInput('ae2:fluix_crystal'),
            itemInput('ae2:fluix_crystal'),
            itemInput('ae2:fluix_crystal')
        ]
    )

    //Logistic Tag Mechanisms Recipe:
    const mechanism = [
        'createmechanisms:storage_mechanism',
        'createmechanisms:computing_mechanism',
        'createmechanisms:logic_mechanism',
        'createmechanisms:advanced_storage_mechanism'
    ]
    const processor = [
        'ae2:engineering_processor',
        'ae2:calculation_processor',
        'ae2:logic_processor',
        'ae2:fluix_crystal'
    ]
    const base = [
        'createmechanisms:zinc_mechanism',
        'createmechanisms:zinc_mechanism',
        'createmechanisms:zinc_mechanism',
        'createmechanisms:incomplete_advanced_storage_mechanism'
    ]
    const loop = [1,1,1,4]
    sequenceDeploy(e, mechanism, base, processor, loop)

    //Advanced Fluid Mechanism Recipe:
    const trans_advanced_fluid = 'createmechanisms:incomplete_advanced_fluid_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:advanced_fluid_mechanism')
        ],
        itemInput('create:brass_sheet'),
        itemOutput(trans_advanced_fluid),
        1,
        [
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('alltheores:steel_plate'), false),
            pressingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid)),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('createmechanisms:fluid_mechanism'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('alltheores:bronze_gear'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('ae2:certus_quartz_dust'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('createmechanisms:redstone_mechanism'), false)
        ]
    )

    //Advanced Heat Mechanism Recipe:
    const trans_advanced_heat = 'createmechanisms:incomplete_advanced_heat_mechanism'
    sequenced_assembly(
        e,
        [
            itemOutput('createmechanisms:advanced_heat_mechanism')
        ],
        itemInput('create:sturdy_sheet'),
        itemOutput(trans_advanced_fluid),
        1,
        [
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('alltheores:steel_plate'), false),
            pressingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid)),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('createmechanisms:heat_mechanism'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('alltheores:nickel_gear'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('ae2:certus_quartz_dust'), false),
            deployingS(itemOutput(trans_advanced_fluid), itemInput(trans_advanced_fluid), itemInput('createmechanisms:redstone_mechanism'), false)
        ]
    )

    //Enderiam Tier Mechanism:
    enderiamTier(
        e,
        [
            'createmechanisms:advanced_fluid_mechanism',
            'createmechanisms:advanced_heat_mechanism',
            'createmechanisms:advanced_storage_mechanism'
        ],
        [
            'createmechanisms:enderiam_fluid_mechanism',
            'createmechanisms:enderiam_heat_mechanism',
            'createmechanisms:enderiam_storage_mechanism'
        ],
        [
            'createmechanisms:incomplete_enderiam_fluid_mechanism',
            'createmechanisms:incomplete_enderiam_heat_mechanism',
            'createmechanisms:incomplete_enderiam_storage_mechanism'
        ]
    )
})