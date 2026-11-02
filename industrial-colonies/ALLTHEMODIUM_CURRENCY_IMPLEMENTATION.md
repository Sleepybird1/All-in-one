# Manufactured Allthemodium currency implementation

Source of truth: `../industrial-audit/ALLTHEMODIUM_CURRENCY_ROUTE_AUDIT.md` and its companion JSON, audited against `allthemodium-3.0.1_mc_1.21.1.jar` (SHA-256 `870004c1d6fbd0891ff322b9ff9e8d42c6aaa082ace7562e25948f1636b5c6f1`).

## Acquisition shutdown

- All six ore-placement paths are changed from `neoforge:add_features` to `neoforge:remove_features`: Deep Dark Allthemodium, Mining Dimension Allthemodium, Other Allthemodium, Nether Vibranium, Other Vibranium, and End Highlands Unobtainium. The mod ships both exact-path overrides and later Industrial Colonies removal modifiers.
- The five audited Allthemodium dungeon chest tables retain their ordinary treasure but no longer contain Allthemodium or Vibranium nuggets.
- All 59 audited ATM material/container output forms are removed before replacements are registered. This closes the 18 furnace recipes, raw/ore hammer processing, manual nugget/block/component conversions, and conditional item casting.
- All 57 active Mekanism ATM processing recipes are removed by exact ID. Ore/raw inputs can no longer enter enriching, purifying, injecting, dissolution, washing, crystallizing, or crushing chains.
- All 81 ATM-family AllTheCompressed aliases are removed as recipe outputs, closing all 162 recursive compression/decompression recipes without affecting the renewable bulk blocks used by the Black Hole quest item.
- All six TConstruct recipe types used by the 69 currently inactive integrations are removed for the Allthemodium namespace. Future installation of TConstruct cannot activate molten-alloy, Piglich-Heart casting, or equipment-salvage multiplication routes.
- ATM ore and raw forms are removed from their common ore/raw tags so generic tag-driven processors cannot rediscover them. Manufactured ingot/component tags remain intact for downstream recipes.
- The audited active recipe census contains no sawing recipe that acquires an ATM form. The validator pins that zero-route result so a future JAR change fails review instead of silently adding a sawmill loophole.

Existing ore blocks already saved in generated chunks are not deleted from the world. They drop inert ore/raw forms whose production routes and common processing tags are disabled.

## Controlled factory production

| Research node | Manufactured output | Factory proof |
|---|---|---|
| `CR01 — Exotic Metallurgy` | Allthemodium | Four-loop Create sequenced assembly using TFMG steel, Modern Foundry cobalt, Mekanism osmium, TFMG steel mechanisms, and pressing |
| `CR01 — Yellorium Refinement` | Vibranium | Four-loop Create sequenced assembly upgrading Allthemodium with the owned Yellorium compound line, cobalt, steel mechanisms, and pressing |
| `CR01 — The Nuclear Age` | Unobtainium | Four-loop Create sequenced assembly upgrading Vibranium with Refined Radiance, Yellorium compound, Ultimate control circuits, and pressing |
| `CR01 — The Nuclear Age` | Three pairwise alloy ingots | Superheated Create mixing of the two constituent elements with Atomic Alloy and Refined Radiance |

The stock plates/gears/rods and storage conversions are replaced with exact-stage Create recipes. Dust recycling is 1:1, nugget conversion is 1:9/9:1, and block storage is 9:1/1:9. No ore/raw/slurry form is reintroduced, and AllTheCompressed ATM storage stays disabled.

There are 45 exact staged recipe IDs: ten routes for each base element and five routes for each pairwise alloy. Unlock provenance is declared at the three nodes in `progression/machine_node_assignments.json`.

## Stock-consumer closure

Old worlds may already contain ingots, nuggets, blocks, or smithing templates. Those items cannot manufacture more currency because every audited producer/storage route is removed, but they could still feed the stock equipment ladder. The pack now uses physical recipe progression, so the runtime stage manifest is deliberately empty and cannot protect these consumers.

The managed KJSGen project therefore retires all thirty Allthemodium, Vibranium, and Unobtainium smithing upgrades by exact recipe ID. These metals are advanced industrial currency and future Modern Foundry modifiers, not a parallel standalone tool/armor ladder. The Allthemodium Teleport Pad is also retired because it would bypass trains and the deliberately deferred long-distance logistics layer.

The two template-duplication recipes and the Allthemodium apple/carrot remain available for later balance work; none of them recreates currency or restores the removed equipment/teleport routes. The old 35-entry stage list remains only as provenance for a possible optional research-gated module. `SmithingMenuMixin` stays structurally valid, but with the empty runtime stage map it is not claimed as the active progression boundary.

## Verification

Run:

```powershell
python tools/validate_allthemodium_currency.py
```

The validator binds this implementation back to the audited JAR hash and route census, checks every disabled form and processing suffix, verifies all 162 compression/decompression recipes, the zero active sawing-acquisition result, the five loot overrides, and the twelve worldgen controls. It proves the runtime stage map is empty, all thirty equipment upgrades and the Teleport Pad are physically retired in both managed and compiled KJSGen data, verifies the optional smithing hooks remain structurally valid, checks conservation ratios, and rejects any TConstruct/Piglich/molten-fluid dependency in the manufactured routes.
