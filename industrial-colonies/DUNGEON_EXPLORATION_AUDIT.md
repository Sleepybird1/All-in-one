# Dungeon exploration audit

## Outcome

The installed dungeon set can support a clean optional exploration chapter without
turning exploration into a recipe gate. The right verifier is already present in
FTB Quests 2101.1.34: its native `structure` task checks whether the player is
physically inside a named structure. That is stronger than an item checklist and
works for Dungeon Crawl, which ships no advancements of its own.

The recommended first chapter is **Dungeon Expeditions**: 12 branched quests,
13 tasks, no rewards, no item consumption, no recipe unlocks, and no kill or
checkbox tasks. It covers all five YUNG structures, Dungeon Crawl, and entry-only
reconnaissance of Dungeon Now Loading's Labyrinth and Temple of Duality. It does
not require a final encounter, trophy, unique encounter drop, or anything from
Apotheosis.

This audit did not change the recipe seed, generated KJSGen files, existing quest
source or SNBT, deployment scripts, the live instance, or the old Draw.io tree.
The implementation-ready source model is in
`DUNGEON_EXPLORATION_AUDIT.plan.json`.

## Installed structure evidence

The placement distances provide a natural difficulty and travel curve. These are
the values in the installed structure-set JSON, not estimates from a wiki.

| Guidance role | Installed structure ID | Spacing / separation (chunks) | Verification available |
| --- | --- | ---: | --- |
| First compact dungeon | `betterdungeons:small_dungeon` | 10 / 6 | Native structure task; YUNG advancement |
| Major overworld branch | `betterdungeons:spider_dungeon` | 44 / 22 | Native structure task; YUNG advancement |
| Major overworld branch | `betterdungeons:skeleton_dungeon` | 46 / 23 | Native structure task; YUNG advancement |
| Major overworld branch | `betterdungeons:zombie_dungeon` | 48 / 24 | Native structure task; YUNG advancement |
| Nether follow-up | `betterdungeons:small_nether_dungeon` | 16 / 10 | Native structure task; YUNG advancement |
| Multi-floor descent | `dungeoncrawl:dungeon` | 32 / 12 | Native structure task only |
| Rare reconnaissance | `dungeonnowloading:temple_of_duality` | 64 / 16 | Native structure task; DNL find advancement |
| Rare reconnaissance | `dungeonnowloading:labyrinth` | 80 / 20 | Native structure task; DNL find advancement |

YUNG also supplies `betterdungeons:all_dungeons`, whose four criteria are the
small, skeleton, spider, and zombie overworld structures. It is a useful
non-arbitrary convergence task after the four individual branches. Dungeon Now
Loading has `find_labyrinth` and `find_temple_of_duality` advancements, but its
later story advancements move into encounter activation and unique drops. Those
later IDs should stay out of this chapter.

## Why native structure tasks should carry the chapter

Inspection of the installed `ftb-quests-neoforge-2101.1.34.jar` confirms both
`StructureTask` and `AdvancementTask`.

- A structure task serializes as `type: "structure"` with a `structure` field.
  It checks the player's current position every 20 ticks.
- An advancement task serializes as `type: "advancement"` with `advancement`
  and `criterion` fields. It checks saved advancement progress every five ticks.
- `StructureTask.checkOnLogin()` returns false. A structure quest therefore
  should be unlocked before the player is likely to enter it. Serial chains of
  structure visits would make players revisit places merely because the next
  node was locked during their first trip.

That last point determines the layout: after one concrete field-preparation
root, all overworld structure objectives fan out. The chapter records genuine
visits but does not impose an artificial order on discoveries. The rare DNL
structures share a separate equipment-preparation parent, while the YUNG
overworld branches converge on the installed `all_dungeons` advancement.

The current generator cannot emit this yet. It requires exactly one guidance
chapter, rejects every non-item task, and hard-codes `/item` into generated task
IDs. The safest implementation is a separate reviewable source,
`progression/ftbquests_dungeon_exploration.json`, followed by a small generator
extension for `item`, `structure`, and `advancement`. The factory source and the
existing three-item capstone source do not need to be rewritten.

## Recommended quest graph

The proposed graph has one root and three useful branches rather than a long
linear checklist.

| Quest | Verifier | Depends on | Purpose |
| --- | --- | --- | --- |
| Light for the Return Trip | 16 `minecraft:torch` | — | Concrete field preparation; items are not consumed |
| Upgraded Monster Room | `betterdungeons:small_dungeon` structure | Field lighting | Common first dungeon |
| Fortress of the Undead | `betterdungeons:skeleton_dungeon` structure | Field lighting | Major YUNG branch |
| Spider Cave | `betterdungeons:spider_dungeon` structure | Field lighting | Major YUNG branch |
| Zombie Catacomb | `betterdungeons:zombie_dungeon` structure | Field lighting | Major YUNG branch with controlled tool tables |
| Overworld Dungeon Survey | `betterdungeons:all_dungeons` advancement | All four YUNG overworld visits | Real convergence, not a checkbox |
| A Dungeon with Depth | `dungeoncrawl:dungeon` structure | Field lighting | Introduces staged multi-floor loot |
| Tool from the Rubble | `minecraft:stone_pickaxe` | Dungeon Crawl visit | Optional proof of the exploration tool route; gates nothing |
| Recovery Equipment | `minecraft:shield` and `minecraft:water_bucket` | Field lighting | Reusable preparation for rare structures |
| Labyrinth Reconnaissance | `dungeonnowloading:labyrinth` structure | Recovery equipment | Entry only; no final-room completion |
| Temple Reconnaissance | `dungeonnowloading:temple_of_duality` structure | Recovery equipment | Entry only; no encounter activation or unique drop |
| Nether Field Survey | `betterdungeons:small_nether_dungeon` structure | Overworld survey | Optional later exploration branch |

The new chapter contributes four item tasks, eight structure tasks, and one
advancement task. With the current 30 factory quests and preserved three-quest
endgame chain, deterministic generation would produce 3 chapters, 45 quests,
67 item tasks, 8 structure tasks, 1 advancement task, and 76 total tasks.

## Primitive-tool discovery

The present primitive script deliberately removes ordinary wooden, stone, iron,
golden, diamond, and netherite tool crafting while leaving structure loot as an
alternate opening. That makes a found vanilla tool meaningful instead of a
duplicate of an easy crafting recipe.

Dungeon Crawl is especially well aligned with this policy:

- `data/dungeoncrawl/treasure/stage_1.json` contains wooden and stone pickaxes
  and axes.
- `stage_2.json` introduces iron pickaxes and swords.
- The companion mixin intercepts stacks returned by
  `dungeoncrawl:random_item`. First-floor damageable equipment has only 10–20%
  durability remaining, scaling to 30–45% for the deepest rolls.
- Seven installed Dungeon Crawl chest tables call that dynamic function.

The optional stone-pickaxe quest is intentionally a dead-end branch. An FTB item
task can observe `minecraft:stone_pickaxe`, but it cannot prove which chest
created it or enforce the mixin's durability range. Random loot therefore must
not block later structure guidance. The main line uses structure visits instead.

## Effective loot audit

The existing focused validator passes against the installed pack:

> 8 exact Dungeon Now Loading/YUNG overrides preserve their pool topology;
> common chests expose no diamond tools, rare finds are at most 10% of pool
> weight and heavily worn, five tables retain damaged low/mid-tier gear, and
> Dungeon Crawl's seven dynamic equipment tables return progressively worn
> finds.

That is a solid first boundary, but it is not complete dungeon-equipment closure.

### Partial pristine-tool coverage

The DNL `easy_combat` and `easy_puzzle` equipment tables still contain direct
pristine iron tools. More importantly, the current `normal_combat` and
`normal_puzzle` overrides add worn alternatives while retaining substantially
higher-weight pristine enchanted iron tools. The validator currently proves
that a table has *some* deliberately worn low/mid-tier equipment; it does not
require every direct ordinary tool to be worn.

This does not invalidate exploration as an alternate start, but the prose in
`PRIMITIVE_TOOL_PROGRESSION.md` is stronger than the enforced rule. A future
loot-hardening batch should either wear every direct iron tool or explicitly
document pristine iron salvage as allowed.

### Armor remains a separate balance decision

Diamond mining tools in the audited DNL tables are controlled, but twelve direct
diamond-armor entries across the Labyrinth gear table and four Temple armor
tables have no `set_damage` function. This is not a primitive mining-tool bypass,
so it should not be silently changed as part of the quest chapter. Decide whether
rare pristine armor is an intended exploration reward, then encode that policy in
a dedicated validator.

### Dungeon Crawl direct entries

The dynamic mixin does not touch direct shield entries in the five stage chest
tables or the explicit iron equipment in the legacy `dungeoncrawl:chests/forge`
table. No direct diamond mining tool was found in those entries. They still need
a focused follow-up before the documentation claims complete equipment closure.

## Apotheosis conflict

Keeping Apotheosis out of quest titles and tasks is straightforward. Keeping it
out of the actual dungeon loot is not currently true.

The installed Apotheosis JAR registers global modifiers with empty conditions:

- `affix_loot_injection.json` matches non-Minecraft `chests.*` tables at 30%.
- `gem_loot_injection.json` matches non-Minecraft `chests.*` tables at 20%.
- `affix_conversion.json` has a 35% catch-all conversion entry outside its block
  exclusion.

Consequently, an authored loot table can contain no `apotheosis:` ID and still
produce Apotheosis content at runtime. The exploration chapter should not mention
or require that content. If “without Apotheosis” is intended to describe chest
output as well as the guide, retire or scope those global modifiers in a separate
tested batch; an FTB Quests edit cannot solve it.

## Explicit exclusions

The first exploration chapter should exclude:

- kill tasks and named boss objectives;
- DNL encounter-activation advancements;
- DNL unique encounter drops, trophies, and trophy icons;
- every `apotheosis:` item, advancement, affix, gem, mob, and icon;
- rewards, loot crates, commands, stages, item consumption, recipe unlocks, and
  checkbox tasks;
- a mandatory random-loot objective;
- dependencies from exploration back into factory recipes.

## Implementation status

The audited chapter is now implemented from
`progression/ftbquests_dungeon_exploration.json`. Deterministic generation emits
the 12 quests as four item, eight structure, and one advancement tasks while
preserving the existing 33 factory/endgame quests and every capstone ID. The
native validator resolves all eight structure paths and the advancement path in
the installed JARs, checks the installed FTB task classes, and verifies the
Dungeon Crawl stage-one stone-pickaxe evidence.

Pristine iron tools, diamond armor, Dungeon Crawl direct equipment, and
Apotheosis global injection remain separate loot-policy batches. This quest
implementation does not change those systems or claim they are closed.

The accompanying validator checks every installed structure, advancement, item,
loot-table override, and FTB task capability referenced by the plan. It does not
deploy or generate quests.
