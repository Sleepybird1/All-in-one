# Primitive tool progression

## Opening loop

The pack now starts before the Andesite Age:

1. Break vanilla leaves for a guaranteed stick (or salvage sticks/tools from a
   structure). Normal plank/bamboo stick recipes are disabled, so scavenging is
   the real opening rather than flavor text.
2. Break gravel for vanilla flint. Modern Foundry's three-gravel fallback remains
   as deterministic bad-luck protection.
3. Craft three flint and two sticks into the owned Crude Flint Pickaxe.
4. Use its 48 durability and stone-equivalent harvest tier to reach stone,
   copper, and first iron.
5. Spend copper ingots on Modern Foundry's Part Builder and Tinker Station.
   Their original all-wood recipes are replaced so a wooden modular head cannot
   bypass the Primitive Age.
6. Replace the crude pick quickly with a modular Modern Foundry tool. Its flint, rock,
   copper, iron, bronze, steel, and later materials become the actual tool
   progression rather than five copies of the vanilla recipe.

The crude pickaxe is intentionally slow (2.5 mining speed) and nearly
unenchantable. It exists to prevent a spawn or bad-RNG softlock, not to compete
with the modular tool system.

## Removed crafting shortcuts

`industrial_primitive_tool_progression.js` removes the normal crafting recipes
for wooden, stone, iron, golden, and diamond pickaxes, axes, shovels, hoes, and
swords, plus all five netherite smithing upgrades. Quark's log-to-stick and
bamboo-to-stick shortcuts are removed as well.
Quark's five alternate stone-tool recipes and Apotheosis's stone-to-iron,
iron-to-gold, and gold-to-diamond vanilla-tool upgrades are also removed.

Modern Foundry's material system still permits wooden components once the
copper-gated workshop exists; that is useful for handles and no longer bypasses
the opening because the two required workstations cannot be built beforehand.

Structure-generated tools remain obtainable by design. This makes exploration
a valid alternate opening. The first loot-closure slice now overrides the five
Dungeon Now Loading and three YUNG's Better Dungeons tables that previously
offered ordinary diamond tools. Normal/common chests now yield stone or worn
iron gear instead. Dangerous Labyrinth/Temple rewards and the special zombie
dungeon chest retain only weight-1 diamond finds, each at 8-20% remaining
durability and no more than 10% of its pool's total weight. Other structure mods
still require their own focused review before the tool tier is considered fully
closed. Dungeon Crawl's nonstandard `dungeoncrawl:random_item` function is also
covered: its stage lists remain intact, but dynamically generated damageable
equipment now has 10-20% durability on the first floor and scales gradually to
30-45% in the deepest treasure rolls. That preserves the intended dungeon-crawl
alternate route without handing out pristine permanent tier skips.

The 15 AE2 Certus/Nether Quartz/Fluix tool recipes and 15 TFMG
aluminum/lead/steel tool recipes are now exact KJSGen removal cards. Their
materials remain useful, but they can no longer recreate the ordinary
pickaxe/axe/shovel/hoe/sword ladder beside Modern Foundry. This keeps the
modular tool workshop as the intended craftable progression while structure
loot remains the deliberate exploration alternative.

## Food progression boundary

Pam's HarvestCraft 2 Crops, Trees, Food Core, and Food Extended are installed,
alongside Farmer's Delight. They supply the ingredient and meal catalog, but no
installed mod currently rewards dietary diversity. Add exactly one nutrition
system and cap its health rewards; stacking several diet mods would double-count
the same hundreds of Pam's foods.


## September 21 starting-table correction

The user explicitly superseded the copper-gated station rule: remove copper from both starting tables to break the first-ingot dependency. Part Builder now uses two patterns and one planklike block; Tinker Station uses three patterns and four matching planklike blocks. Historical recipe IDs are retained, along with the Hilt texture serializer. Blank patterns already use planks/sticks. This narrow fix does not prove the complete first-Foundry acquisition chain. Evidence: `../workflow/early-survival/foundry-table-bootstrap/REPORT.md`.
