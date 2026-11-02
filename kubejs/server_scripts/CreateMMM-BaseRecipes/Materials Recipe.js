ServerEvents.recipes(e => {
    //Ruber Recipe:
    mixing(
        e,
        [
            itemOutput('createmechanisms:rubber'),
            itemOutputChance('createmechanisms:rubber', 0.25),
        ],
        [
            itemInput('minecraft:kelp'),
            itemInput('minecraft:kelp'),
            itemInput('minecraft:kelp'),
            itemInput('minecraft:kelp'),
            fluidInput('minecraft:water', 250)
        ],
        false
    );

    //Cured Rubber Recipe:
    smoking(
        e,
        itemOutput("createmechanisms:cured_rubber"),
        itemInput("createmechanisms:rubber"),
        0.2,
        200
    )

    //Enderiam Rubber Recipe:
    filling(
        e,
        itemOutput('createmechanisms:enderiam_rubber'),
        itemInput('createmechanisms:rubber'),
        fluidInput('createmechanisms:enderiam_fluid', 200)
    )

    //Cured Enderiam Rubber Recipe:
    haunting(
        e,
        [
            itemOutput('createmechanisms:cured_enderiam_rubber'),
        ],
        itemInput('createmechanisms:enderiam_rubber')
    )

    //Bronze recipes:
    mixing(
        e,
        [
            itemOutput('createmechanisms:bronze')
        ],
        [
            itemInput('minecraft:copper_ingot'),
            itemInput('minecraft:iron_ingot')
        ],
        'heated'
    )
    mixing(
        e,
        [
            itemOutputChance('createmechanisms:bronze', 0.1)
        ],
        [
            itemInput('minecraft:copper_ingot'),
            itemInput('minecraft:iron_ingot')
        ],
        false
    )

    //Enderiam Fluid Recipe:
    mixing(
        e,
        [
            fluidOutput('createmechanisms:enderiam_fluid', 250)
        ],
        [
            fluidInput('minecraft:lava', 100),
            itemInput('alltheores:enderium_dust'),
            itemInput('minecraft:ender_pearl'),
            itemInput('minecraft:ender_pearl')
        ],
        "heated"
    )

    //Silicon Recipe:
    blasting(
        e,
        itemOutput('ae2:silicon'),
        itemInputTag('createmechanisms:quartz'),
        0.1,
        20
    )
    smelting(
        e,
        itemOutput('ae2:silicon'),
        itemInputTag('createmechanisms:quartz'),
        0.1,
        20
    )

    //Enderiam Energy Cell Recipe:
    filling(
        e,
        itemOutput('createmechanisms:enderiam_cell'),
        itemInput('createmechanisms:energy_cell'),
        fluidInput('createmechanisms:enderiam_fluid', 250)
    )

    const materials = [
        'c:ingots/netherite',
        'c:ingots/constantan',
        'c:ingots/signalum',
        'c:ingots/lumium',
        'c:ingots/enderium',
        'c:gems/diamond',
        'c:ingots/steel',
        'c:ingots/invar',
        'c:ingots/electrum',
        'c:ingots/bronze',
        'c:ingots/nickel',
        'c:ingots/lead',
        'c:ingots/aluminum',
        'c:ingots/iridium',
        'c:ingots/osmium',
        'c:ingots/platinum',
        'c:ingots/silver',
        'c:ingots/tin',
        'c:ingots/uranium',
        'c:ingots/zinc'
    ]
    const plates = [
        'alltheores:netherite_plate',
        'alltheores:constantan_plate',
        'alltheores:signalum_plate',
        'alltheores:lumium_plate',
        'alltheores:enderium_plate',
        'alltheores:diamond_plate',
        'alltheores:steel_plate',
        'alltheores:invar_plate',
        'alltheores:electrum_plate',
        'alltheores:bronze_plate',
        'alltheores:nickel_plate',
        'alltheores:lead_plate',
        'alltheores:aluminum_plate',
        'alltheores:iridium_plate',
        'alltheores:osmium_plate',
        'alltheores:platinum_plate',
        'alltheores:silver_plate',
        'alltheores:tin_plate',
        'alltheores:uranium_plate',
        'alltheores:zinc_plate'
    ]

    pressingPairs(e, plates, materials)
})