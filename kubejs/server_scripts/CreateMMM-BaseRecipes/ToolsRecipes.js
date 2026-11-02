ServerEvents.recipes(e => {
    sawRecipe(
        e,
        [
            'createmechanisms:copper_saw',
            'createmechanisms:iron_saw',
            'createmechanisms:diamond_saw',
            'createmechanisms:netherite_saw'
        ],
        [
            itemInputKey('C', 'minecraft:copper_ingot'),
            itemInputKey('C', 'minecraft:iron_ingot'),
            itemInputKey('C', 'minecraft:diamond'),
            itemInputKey('C', 'minecraft:netherite_ingot')
        ]
    )
})