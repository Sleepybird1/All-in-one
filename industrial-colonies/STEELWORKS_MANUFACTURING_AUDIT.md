# TFMG Steelworks Manufacturing Audit

Status: **IMPLEMENTED IN THE AUTHORITATIVE SEED as a seven-contract repair.** The recipe seed and two Blast Furnace assignments were updated; shared generated files, deployment files, quests, Draw.io, and the live pack remain untouched pending authoritative regeneration.

The five requested machine outputs are not a complete bootstrap by themselves. Installed TFMG runtime tags prove that a regular Blast Furnace also requires `tfmg:fireproof_bricks` for its wall and `tfmg:fireproof_brick_reinforcement` for its support layer. Those two outputs must therefore enter the same bounded repair. They are not decorative additions.

`tfmg:blast_furnace_reinforcement` is different: it occurs only in the installed **reinforced** support tag. Its stock recipe consumes finished steel and heavy plate, so it must remain an optional upgrade after the first regular furnace is operational.

The machine-readable evidence and implemented contracts are in `STEELWORKS_MANUFACTURING_AUDIT.plan.json`.

## Installed baseline

Audited JAR: `tfmg-1.2.0.jar`

SHA-256: `FC824A91CFE22E137C9014ED608EE9BF35F16490D2162B687666332C6EB3A555`

The seven exact installed source recipes are:

| Installed recipe ID | JAR resource | Stock output | Role |
|---|---|---:|---|
| `tfmg:crafting/materials/coke_oven` | `data/tfmg/recipe/crafting/materials/coke_oven.json` | 2 `tfmg:coke_oven` | Steel Age coking multiblock |
| `tfmg:crafting/materials/fireproof_bricks` | `data/tfmg/recipe/crafting/materials/fireproof_bricks.json` | 1 `tfmg:fireproof_bricks` | Required regular-furnace wall |
| `tfmg:crafting/materials/fireproof_brick_reinforcement` | `data/tfmg/recipe/crafting/materials/fireproof_brick_reinforcement.json` | 6 `tfmg:fireproof_brick_reinforcement` | Required regular-furnace support |
| `tfmg:crafting/materials/blast_stove` | `data/tfmg/recipe/crafting/materials/blast_stove.json` | 2 `tfmg:blast_stove` | Hot-air production multiblock |
| `tfmg:crafting/materials/blast_furnace_hatch` | `data/tfmg/recipe/crafting/materials/blast_furnace_hatch.json` | 1 `tfmg:blast_furnace_hatch` | Hot-air tuyere and 4,000 mB tank |
| `tfmg:crafting/materials/blast_furnace_output` | `data/tfmg/recipe/crafting/materials/blast_furnace_output.json` | 1 `tfmg:blast_furnace_output` | Furnace controller/output boundary |
| `tfmg:crafting/materials/blast_furnace_reinforcement` | `data/tfmg/recipe/crafting/materials/blast_furnace_reinforcement.json` | 4 `tfmg:blast_furnace_reinforcement` | Optional reinforced-furnace support |

All seven paths, recipe types, output counts, and resource hashes are pinned in the plan and checked against both the installed JAR and the static catalog.

## Runtime multiblock proof

Static inspection of the installed classes and tags established the functional boundary:

- `BlastFurnaceOutputBlockEntity` validates a 3x3 tower, requires an operational height of at least three, locates exactly one hatch as its hot-air tuyere, and separates regular and reinforced wall/support modes.
- `data/tfmg/tags/block/blast_furnace_wall.json` contains `tfmg:blast_furnace_hatch` and `tfmg:fireproof_bricks`.
- `data/tfmg/tags/block/blast_furnace_support.json` contains only `tfmg:fireproof_brick_reinforcement`.
- `data/tfmg/tags/block/reinforced_blast_furnace_support.json` contains `tfmg:blast_furnace_reinforcement`, its rusted form, and `tfmg:steel_block`. This is why reinforcement cannot be a first-steel prerequisite.
- `BlastStoveBlockEntity` is a vertical fluid-processing multiblock. Its installed fuel tag accepts TFMG creosote and furnace gas, keeping useful byproducts inside the steelworks loop.
- `CokeOvenBlockEntity` forms a scalable shared-inventory/fluid multiblock.
- `TFMGLayeredPatterns` registers fireclay layer patterns, and the installed fireclay block loot table drops `tfmg:fireclay_ball`. The retained `tfmg:smelting/fireproof_brick` recipe then produces the refractory precursor without steel.

The validator pins the relevant class, tag, and loot-table hashes. If the installed mod changes, the audit fails instead of silently assuming the old multiblock semantics.

## Repaired project state

Before this repair, the generated managed recipe set had five automatic owners:

- `industrial_colonies:auto/tfmg/coke_oven`
- `industrial_colonies:auto/tfmg/blast_stove`
- `industrial_colonies:auto/tfmg/blast_furnace_hatch`
- `industrial_colonies:auto/tfmg/blast_furnace_output`
- `industrial_colonies:auto/tfmg/blast_furnace_reinforcement`

They are all large mechanical-crafting recipes with exact stock removals and preserve their stock batch counts. The reinforcement owner already consumes finished steel and heavy plate; that is valid only when treated as an optional post-first-steel upgrade.

Those five automatic owners are now retired by exact source-owned contracts.
The regular wall and support outputs also have source-owned Brass Press
contracts, closing their former stock-crafting bypass.

Current node boundaries are otherwise correct:

- `CR01 — The Steel Age`, phase `Steel & Petroleum`: cast-iron infrastructure, the Coke Oven, and coal coke.
- `CR01 — Blast Furnace`, phase `Steel & Petroleum`, direct child of The Steel Age: refractory construction, hot-air equipment, regular steel capability, and the later reinforcement upgrade.

`tfmg:fireproof_bricks` and `tfmg:fireproof_brick_reinforcement` were appended
after the seven pre-existing `CR01 — Blast Furnace` unlocks. No existing entry
was reordered or replaced.

## Implemented bounded repair

Every contract replaces one exact stock recipe, owns one output, and preserves the stock batch output. The plan uses the Brass Press for refractory/pressure assemblies because Brass precision manufacturing is already a prerequisite of the Steel Age; it does not introduce a later casing dependency.

| Order | Proposed source-owned ID | Factory language | Output | Same-batch dependency |
|---:|---|---|---:|---|
| 10 | `industrial_colonies:steelworks/coke_oven` | 5x5 cast-iron/industrial-iron mechanical construction | 2 Coke Ovens | none |
| 20 | `industrial_colonies:steelworks/fireproof_bricks` | Brass Press compacting of four fired refractory bricks | 1 wall block | none |
| 30 | `industrial_colonies:steelworks/fireproof_brick_reinforcement` | Brass Press compacting of six regular wall blocks | 6 support blocks | regular wall |
| 40 | `industrial_colonies:steelworks/blast_stove` | 5x5 pipe/tank/refractory hot-blast construction | 2 Blast Stoves | regular wall |
| 50 | `industrial_colonies:steelworks/blast_furnace_hatch` | Brass Press pressure assembly with plates, pipes, tank, and refractory | 1 hatch | regular wall |
| 60 | `industrial_colonies:steelworks/blast_furnace_output` | 5x5 cast-iron frame/pipe/refractory controller construction | 1 output controller | regular wall |
| 70 | `industrial_colonies:steelworks/blast_furnace_reinforcement` | Brass Press compacting of steel, heavy plate, and refractory | 4 reinforced supports | regular wall plus operational regular furnace |

The implemented recipes remain TFMG/Create-first: TFMG cast-iron frames, pipes, tanks, refractory bricks, heavy plate, and steel are combined with Create industrial iron and precision mechanisms. No Mekanism, AE2, digital processor, or post-Steel-Age casing is introduced.

## Bootstrap and cycle proof

The acyclic capability order is:

1. Pre-steel fireclay supplies `tfmg:fireclay_ball`; the retained smelting recipe supplies `tfmg:fireproof_brick`.
2. Contract 20 makes the regular wall block.
3. Contracts 30, 40, 50, and 60 consume only that earlier wall plus pre-steel cast-iron/precision parts.
4. The regular multiblock is now constructible without `steel`, `heavy_plate`, `steel_mechanism`, or `steel_casing` anywhere in its six required contracts.
5. The retained TFMG production chain runs: coking, Create crushing of coal coke, hot-blast production, TFMG industrial blasting, then TFMG casting to `tfmg:steel_ingot`.
6. Only after that capability exists may contract 70 consume steel and heavy plate for the reinforced-furnace upgrade.

Retained exact process IDs:

- `tfmg:coking/coal`
- `create:crushing/coal_coke`
- `tfmg:hot_blast/hot_air`
- `tfmg:industrial_blasting/steel`
- `tfmg:casting/steel`
- `tfmg:smelting/fireproof_brick`

Installed process tags further pin `tfmg:coal_coke_dust` as Blast Furnace fuel, TFMG limesand as flux, and creosote/furnace gas as Blast Stove fuels. These recipes and tags are not in the implemented removal set.

## Validation

Run:

```powershell
python tools/validate_steelworks_manufacturing_audit.py
python tools/test_validate_steelworks_manufacturing_audit.py -v
```

The focused validator checks:

- the installed TFMG JAR identity and all seven exact source recipes;
- class, structural tag, process tag, loot-table, and retained-process hashes;
- the current five automatic owners and two unmanaged required outputs;
- exact Steel Age/Blast Furnace branch and phase placement;
- seven one-to-one outputs and seven exact removals;
- stock batch-output preservation;
- concrete item and Brass Press IDs against the installed catalog/environment definition;
- strict 10–70 dependency ordering and declared/observed same-batch dependencies;
- six steel-free required contracts and one optional post-first-steel reinforcement contract;
- exclusion of reinforcement from regular-furnace capability construction.

The eighteen-test mutation suite additionally covers missing and drifted seed
owners, survival of retired automatic owners, and assignment append-order
regressions. The focused validator checks exact seed/manifest parity and KJSGen
compilation for all seven cards.

## Decision

**IMPLEMENTED** as exactly seven source-owned contracts. An isolated build
produced 334 managed recipes, 177 automatic recipes, 402 compiled cards, and
718 exact removals. The five-output-only alternative remains rejected because
it would leave the regular wall/support stock bypasses outside the actual
multiblock boundary.
