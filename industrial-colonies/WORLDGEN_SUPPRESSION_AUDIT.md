# Overworld geology: default-generation suppression audit

Audit date: 2026-09-08. Scope: the installed `All in one` pack, Minecraft 1.21.1, NeoForge 21.1.248.
Authoritative design: `C:\Users\GodPC\.codex\attachments\34fe6255-ad44-4a38-a19a-72fbd308315e\pasted-text.txt`.

## What this change does

The new geology data removes **68 named default placed features** from **all 11 decoration steps** of `#minecraft:is_overworld`.
It does not unregister blocks/items, remove recipes, change machine progression, edit live pack files, or alter existing chunks.

The shared Java/data manifest is:

```
#industrial_colonies:geology/default_ore_features
```

It consists of the ten per-source tags in `data/industrial_colonies/tags/worldgen/placed_feature/geology/`.
Mod-specific entries use `required: false` so a missing optional placed feature does not invalidate the tag.
Vanilla feature IDs are required and verified against the exact 1.21.1 client JAR.

The new `geology_remove_default_ores.json` uses the NeoForge **`steps`** field, plural. The installed NeoForge source codec defaults to every decoration step if `steps` is omitted.
The old project's singular `step` fields on remove modifiers are ignored by this codec but effectively fall back to all steps; they were not changed in this task.

## Reproducible static audit

```powershell
python tools/audit_geology_worldgen.py --summary
python tools/audit_geology_worldgen.py --validate-project .
```

Use the project's available Python runtime if `python` is not on PATH.
The tool reads all **239 active top-level mod JARs**, the Minecraft client JAR, nested JAR resources, and bundled datapack paths without extracting or modifying them.
The expanded catalog contains **4,536 JSON registry/tag/surface-rule records**.
It distinguishes configured features from placed features and follows configured-feature references when finding candidates.
Broad-name matches are diagnostic candidates, not automatic removal decisions: silver birch trees, cobalt-earlight plants, weapons, and decorative features must not be removed just because a name matches.

Static validation passes:

- All 68 forbidden IDs exist as placed-feature definitions in the audited installed inputs.
- No duplicate manifest entries.
- All mod-specific manifest references are optional.
- Emerald, lapis, fluorite, quartz, salt, fossil placements and identified non-Overworld feature IDs are not in the manifest.
- The exact biome tag and all 11 decoration steps match the intended removal scope.
- Both mineral-free stratum copies equal their installed source definitions after only the documented output-state substitutions.
- Stratum placement count/rarity, height distribution, filters, size, layer count, weights and ordering are unchanged.
- RU's overridden redstone-cave surface rule no longer returns raw redstone.

This is **not** a claim that an in-game reload/new-world test or a complete bytecode semantic audit has passed.
Custom-generation hooks and resource-priority behavior still require the root integration/build and runtime checks.

## Exact suppressed placed-feature IDs

| Source | Installed version | Count |
| --- | --- | ---: |
| Vanilla / Tectonic overrides | Minecraft 1.21.1; Tectonic 3.0.26 | 16 |
| Create | 6.0.10 | 2 |
| TFMG | 1.2.0 | 4 |
| Mekanism | 10.7.19.85 | 16 |
| NuclearCraft | 1.3.0-rc1 | 11 |
| Immersive Engineering | 12.4.2-194 | 7 |
| Regions Unexplored | 0.6.2 | 6 |
| Cosmonautics | 26.08.307 | 1 |
| Stellaris | 1.4.25 | 2 |
| Existing progression exclusions | Extreme Reactors 2.4.28; Allthemodium 3.0.1 | 3 |

### Vanilla (including same-key Tectonic overrides)

```text
minecraft:ore_coal_lower
minecraft:ore_coal_upper
minecraft:ore_copper
minecraft:ore_copper_large
minecraft:ore_diamond
minecraft:ore_diamond_buried
minecraft:ore_diamond_large
minecraft:ore_diamond_medium
minecraft:ore_gold
minecraft:ore_gold_extra
minecraft:ore_gold_lower
minecraft:ore_iron_middle
minecraft:ore_iron_small
minecraft:ore_iron_upper
minecraft:ore_redstone
minecraft:ore_redstone_lower
```

Coal and gold retain their recognizable blocks, but ordinary placement is replaced by the new seam/district system.
Diamond is restricted to the custom graphite-related or explicitly permitted trace contexts.

### Create and TFMG

```text
create:zinc_ore
create:striated_ores_overworld
tfmg:lead_ore
tfmg:lithium_ore
tfmg:nickel_ore
tfmg:tfmg_striated_ores_overworld
```

Create's striated ore feature is economic, not merely decorative: it includes crimsite, asurine, veridium and ochrum.
TFMG's mixed feature includes bauxite, galena and lignite, and its fireclay pattern also includes a thin crimsite layer.
Leaving these features untouched would supply competing iron/zinc/copper/gold/aluminum/lead/coal sources.

### Mekanism

```text
mekanism:ore_lead_normal
mekanism:ore_lead_normal_retrogen
mekanism:ore_osmium_middle
mekanism:ore_osmium_middle_retrogen
mekanism:ore_osmium_small
mekanism:ore_osmium_small_retrogen
mekanism:ore_osmium_upper
mekanism:ore_osmium_upper_retrogen
mekanism:ore_tin_large
mekanism:ore_tin_large_retrogen
mekanism:ore_tin_small
mekanism:ore_tin_small_retrogen
mekanism:ore_uranium_buried
mekanism:ore_uranium_buried_retrogen
mekanism:ore_uranium_small
mekanism:ore_uranium_small_retrogen
```

### NuclearCraft

```text
nuclearcraft:boron_ore
nuclearcraft:cobalt_ore
nuclearcraft:lead_ore
nuclearcraft:lithium_ore
nuclearcraft:magnesium_ore
nuclearcraft:platinum_ore
nuclearcraft:silver_ore
nuclearcraft:thorium_ore
nuclearcraft:tin_ore
nuclearcraft:uranium_ore
nuclearcraft:zinc_ore
```

These are the eleven actual ore placed features in the installed NuclearCraft JAR.
Its wasteland structures/decorations are not silently classified as mineral deposits.

### Immersive Engineering

```text
immersiveengineering:bauxite
immersiveengineering:deep_nickel
immersiveengineering:lead
immersiveengineering:mineral_veins
immersiveengineering:nickel
immersiveengineering:silver
immersiveengineering:uranium
```

`mineral_veins` creates **virtual excavator deposits**, not visible blocks.
It must also be removed in the Overworld or the excavator can independently source the old economy.
Its original biome modifier targets any biome; our removal does not target Nether/End/space biomes.
Already saved IE mineral-vein records are not erased. Existing-world deposits require a separate deliberate migration decision.

### Regions Unexplored

```text
regions_unexplored:patch/redstone_bud
regions_unexplored:patch/redstone_bulb
regions_unexplored:special/large_pointed_redstone
regions_unexplored:special/ore_redstone_large
regions_unexplored:special/pointed_redstone
regions_unexplored:special/pointed_redstone_cluster
```

### Additional industrial defaults / pre-existing exclusions

```text
rocketnautics:titanium_ore
stellaris:steel_ore
stellaris:steel_ore_deepslate
bigreactors:yellorite_ore
bigreactors:yellorite_deepslate_ore
allthemodium:allthemodium_ore
```

Cosmonautics explicitly adds titanium to `#minecraft:is_overworld`.
Stellaris `add_overworld_ores.json` adds its two steel placements to `#c:is_overworld`.
Its Moon steel feature and other planetary resources remain untouched.
Yellorite/Allthemodium already have older project removal modifiers; including their same IDs in the runtime guard manifest does not restore or change their recipes.

## Preserve fireclay and non-resource decorative strata

Two new mineral-free features replace the removed mixed strata:

- `industrial_colonies:geology_create_decorative_strata`
- `industrial_colonies:geology_tfmg_fireclay_strata`

They copy the installed configured and placed features exactly, except:

1. Rename the replacement placed feature's configured-feature reference.
2. Replace output states `create:crimsite`, `create:asurine`, `create:veridium`, `create:ochrum`, `tfmg:bauxite`, `tfmg:galena`, `tfmg:lignite` with their native target stone or Y-oriented deepslate.
3. Attach the new feature to Overworld biomes.

Both keep size32, rarity18, uniform Y[-30,70], and the Create config filter.
Create retains all six layer patterns; TFMG retains all four.
Exactly eight state entries change in each configured feature.
Fireclay, sand, gravel, scoria, limestone, calcite, tuff, dripstone and other non-resource states are preserved, as are all pattern choices and weights.
Consequently removing the bauxite/galena/lignite economy does **not** multiply fireclay's pattern selection probability.

Source configured-feature SHA-256:

```text
Create: a14f9f05d736a54dd874f868a06f4837173c62d0c15ac9a6b7a843f9d1fee98f
TFMG:   6d1d5eebfd6249f17d32f4705be63c887c4bf72290354d5ad20b84e710edcfe9
```

## Non-placed-feature bypasses and integration requirements

### Vanilla large copper/iron noise veins — root hook required

`NoiseGeneratorSettings.oreVeinsEnabled` / `OreVeinifier` can place copper/iron ores and raw-metal blocks during noise filling.
They are not biome placed features, so JSON feature removal cannot disable them.
The root implementation must gate this path by actual `Level.OVERWORLD` and `GeologyConfig.suppressDefaultOres()`.
Do not replace the entire noise-settings resource: that would discard Tectonic terrain integration.

### Fossil ore overlay — dedicated mixin supplied

`GeologyFossilOverlayMixin` redirects **only ordinal1** of
`StructureTemplate.placeInWorld(ServerLevelAccessor, BlockPos, BlockPos, StructurePlaceSettings, RandomSource, int)`
inside `FossilFeature.place`.
The first call places bone skeletons; the second places coal/diamond overlay templates.
When suppression is enabled in the actual Overworld, only the second call is skipped.
`minecraft:fossil_upper` / `minecraft:fossil_lower` remain attached; Nether fossils are untouched.

### Quark fairy rings — optional dedicated mixin supplied

Quark uses `org.violetmoon.quark.content.world.gen.FairyRingGenerator.spawnFairyRing`, not a registered ore placed feature.
It directly writes a selected ore below flowers.
The live config has `Ores = ["minecraft:emerald_ore", "minecraft:diamond_ore"]` at `config/quark-common.toml:1136`, with Overworld dimensions at1140.
`GeologyQuarkFairyRingMixin` is `@Pseudo` and has no Quark imports.
It redirects the method's `WorldGenLevel.setBlock` calls and refuses diamond/deepslate-diamond only when suppression is enabled in the Overworld.
Flowers, mushrooms, host terrain and emerald outcomes remain untouched; a rejected diamond roll does not become extra emerald.

### RU surface-generated raw redstone — narrow data override supplied

RU directly emits `regions_unexplored:raw_redstone_block` through:

```
data/regions_unexplored/lithostitched/surface_rule/overworld/caves/redstone_caves.json
```

The override preserves the exact redstone-cave biome constraint and both source noise thresholds.
Only the final output changes to stone above Y0 / deepslate below Y0.
RU's biome, terrain, cave shape and other surface rules remain.
The rule is referenced by RU's Overworld surface composition, not its Nether composition.

### Mekanism / IE retrogen — root runtime feature guard required

Mekanism and IE can call `PlacedFeature.place` directly during retrogen, bypassing a removed biome feature list.
The root feature-placement guard must use the shared `#industrial_colonies:geology/default_ore_features` tag and actual dimension.
The manifest includes Mekanism's registered retrogen variants and IE's original features/mineral-vein feature.
Live configs currently disable retrogen; the guard protects against later config changes without globally disabling salt/fluorite.

### Configuration toggle caveat

The standard NeoForge removal JSON and the RU data override are unconditional build policy.
Turning off the Java suppression flag alone does not restore the old biome feature lists or undo the surface-rule override.
This is intentional: `enabled=false` stops the custom geological feature and its Java suppression hooks; `suppressDefaultOres=false` stops only the Java suppression hooks while leaving geological generation enabled. Neither setting is a restore-default-worldgen switch. Restoring the stock distribution would require an explicit data-policy change to the biome modifiers and RU surface override, followed by a new-world/ungenerated-chunk test. Existing generated chunks remain unchanged either way.

## Terrain and dimension compatibility

- RU appends `#regions_unexplored:all_overworld` to `#minecraft:is_overworld`.
- Quark appends `quark:glimmering_weald`; Vanilla Backport appends `minecraft:pale_garden` and `minecraft:sulfur_caves`.
- The same strict Overworld biome tag therefore covers these installed biomes without replacing their biome definitions.
- Tectonic's ore-fix datapack overrides vanilla diamond/gold/redstone placed-feature **keys**. Removing those keys catches either definition without changing its terrain/noise router.
- The installed Tectonic config currently has `caves.ore_fix=false` at `config/tectonic.json:26`; this is not relied upon for suppression.
- Vanilla/TFMG/Create Nether striated features, Create Metallurgy Nether wolframite, Modern Foundry Nether cobalt/ichor geodes, Ad Astra/Stellaris planetary ores, Rocketnautics moon resources, Deeper and Darker's Otherside and Allthemodium mining-dimension ore features are not removed by name.
- A biome tag is not a dimension key. A custom dimension that reuses an actual Overworld biome object shares that biome's feature list. Runtime Java guards additionally check the actual dimension; the supplied data intentionally follows the required `#minecraft:is_overworld` scope. No installed planet-specific biome was found in that tag.

## Deliberately retained and scope limitations

Retained ordinary resources: emerald, lapis, fluorite, quartz, salt; vanilla decorative stone/clay/gravel; RU terrain/decorative rocks; Quark corundum and other unrelated decorative/cave content; Vanilla Backport terrain content; AE2 meteors/budding Certus.
Iron's Spellbooks `irons_spellbooks:ore_mithril_placement` is an unrelated magic-mod resource, not silently renamed into an approved industrial host.
No unapproved native ore family is registered by this suppression task.

Ordinary chunk-generation deposits are the scope; existing mined items, crafted items, chest loot, structure treasures, player-built blocks, machine processing/byproducts, trades and previously saved chunks are not deleted.
The separate oil implementation owns oil features/deposits; the old oil-removal files were not modified here.

Relevant live configuration observations (read only):

- `config/create-common.toml:7`: `disableWorldGen=false`; do not turn this on globally because it also removes retained decorations.
- `config/Mekanism/world.toml:2`: `enableRegeneration=false`.
- Mekanism tin generation true at11; osmium true at104; uranium true at241; fluorite true at334; lead false at427/432; salt true at476.
- `config/immersiveengineering-server.toml:428`: excavator retrogen false; all six physical-ore retrogen flags false at463/491/519/547/575/603.
- `config/tfmg-common.toml:145`: oil deposits finite, unrelated to this mineral suppression.
- No active custom placed-feature/biome modifier definitions were found in loose KubeJS data, defaultconfigs or world datapack folders; no KubeJS worldgen-event hook was found by the scoped JS/JSON search.
- No generated NuclearCraft worldgen configuration was present in the scoped config folder at audit time; the installed JAR's eleven data-defined ore placements are therefore explicitly covered rather than assuming a config disables them.

## Handoff checklist

1. Root registers both dedicated mixin class names in the existing mixin configuration.
2. Root adds `GeologyConfig.suppressDefaultOres()`, the OreVeinifier guard and the runtime placed-feature guard.
3. Build once after other parallel Java work finishes.
4. In a throwaway NEW world / previously ungenerated chunks, check no default resource veins or RU raw-redstone surfaces, and confirm fireclay/non-resource strata still exist.
5. Confirm emerald/lapis/fluorite/salt remain, a bone fossil remains without its ore overlay, and a Quark fairy ring still has flowers/possible emerald.
6. Check Nether/planet generation and Tectonic/RU terrain remain unaffected.
7. Do not claim existing world chunks or saved excavator reserves were migrated; none were.
