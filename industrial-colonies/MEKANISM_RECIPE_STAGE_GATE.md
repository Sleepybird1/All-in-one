# Mekanism machine recipe stage gate

Industrial Colonies generates
`data/industrial_colonies/progression/recipe_stages.json` by merging 78
construction dependency rows from `tools/machine_recipe_dependencies.json`
with 43 existing source-processing IDs from
`tools/additional_recipe_stages.json`. The construction rows resolve to 77
unique IDs; the complete runtime map contains 120 unique exact recipe IDs. Node
labels are resolved through the generated research translations so every value
is the exact MineColonies research resource ID used by the University tree.

The manifest is reloaded on every server datapack reload. Immediately before a
Mekanism `RecipeCacheLookupMonitor` processes its cached recipe, its specialized
adapter resolves the exact holder ID and checks the owning `TileEntityMekanism`
UUID against the shared gate. The adapter then resolves that player's FTB Team
and tests the required research ID in the team's native stage set. A mapped
recipe is denied when the machine has no owner, the team manager/team is
unavailable, or the team lacks the stage. Recipes absent from the manifest
continue normally; recipes are never removed globally.

The same manifest service is also consumed by the player-crafting and Create
machine enforcement layers; the Mekanism owner and cache behavior is otherwise
unchanged. Rebuild the mod after changing either source manifest. In a running
pack, `/reload` refreshes the bundled map, while a full restart is recommended
after replacing the mod JAR or changing mod dependencies.
