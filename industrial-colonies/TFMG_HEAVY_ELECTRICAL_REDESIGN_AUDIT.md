# TFMG-first heavy and electrical redesign

Status: **implemented in the authoritative seed and assignment map**. This is
the priority-one implementation slice from `AUTOMATIC_RECIPE_QUALITY_AUDIT`.
The eight recipe contracts and one assignment move are source-owned; generated
artifacts, quests, the live pack, and Draw.io remain untouched by this batch.

## Outcome

Eight generic automatic 5x5 owners have exact source-owned replacements:

- one unique radial 5x5 machine assembly for the TFMG Centrifuge;
- three pre-Mekanism heavy-forming recipes on the Railway Press;
- three electrical/winding recipes on the Copper Press; and
- one digital integration recipe on the Brass Press.

The batch removes exactly eight installed recipe IDs. It deliberately restores
`tfmg:engine_cylinder_gas`, which the automatic exclusive owner currently
removes. That LPG recipe consumes the managed spark-ignition cylinder, so it is
a downstream state conversion rather than a shortcut.

## Why the heavy recipes do not use Industrial Iron

The quality audit's generic recommendation was Industrial Iron for heavy
parts. The actual physical tier data shows why that cannot be used here:

| Machine family | Construction phase | Batch decision |
| --- | --- | --- |
| Copper | Steam & Brass | Power windings, measurement, and the pre-circuit moving contact |
| Brass | Electrical Manufacturing | ComputerCraft/Create digital adapter |
| Railway | Electrical Manufacturing | Latest heavy-forming line available before Mekanism |
| Industrial Iron | Mekanized Industry | Rejected here: it consumes Mekanism control hardware downstream of TFMG engines |

Requiring `createcasing:industrial_iron_press` for the engine cylinders would
invert the intended TFMG-to-Mekanism order. The Railway Press is therefore the
audited heavy-industry environment for this batch.

## Exact replacement contracts

### `industrial_colonies:tfmg_heavy_electrical/centrifuge`

- Output: `tfmg:centrifuge`
- Node/phase: `CR01 — Chemical Processing` / `Steel & Petroleum`
- Process: Create Mechanical Crafting
- Exact removal: `tfmg:crafting/materials/centrifuge`
- Inputs: eight `tfmg:aluminum_bars`, four `tfmg:cast_iron_frame`, two
  `create:precision_mechanism`, two `create:large_cogwheel`, two
  `create:shaft`, and one `tfmg:steel_casing`
- Layout:

```text
 AFA
ARBRA
FSCSF
ARBRA
 AFA
```

`A` is aluminum bars, `F` is cast-iron frame, `B` is Precision Mechanism,
`R` is Large Cogwheel, `S` is Shaft, and `C` is Steel Casing. This is a radial
rotor/cage layout, not the automatic A/B perimeter.

### `industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder`

- Output: `tfmg:diesel_engine_cylinder` with the installed TFMG diesel fuel
  components preserved exactly
- Node/phase: `CR01 — Diesel Engines` / `Steel & Petroleum`
- Process: Compacting on `createcasing:railway_press`
- Inputs: `tfmg:cast_iron_frame`, four `#c:plates/aluminum`,
  `tfmg:steel_mechanism`, and two `tfmg:screw`
- Exact removal: `tfmg:engine_cylinder`

### `industrial_colonies:tfmg_heavy_electrical/engine_cylinder`

- Output: `tfmg:engine_cylinder` with the installed gasoline, kerosene, and
  naphtha TFMG fuel components preserved exactly
- Node/phase: `CR01 — Diesel Engines` / `Steel & Petroleum`
- Process: Compacting on `createcasing:railway_press`
- Inputs: the managed `tfmg:diesel_engine_cylinder`, `tfmg:spark_plug`,
  `tfmg:copper_wire`, and two `tfmg:screw`
- Exact removal: `tfmg:engine_cylinder_spark_plug`
- Nonexclusive by design: `tfmg:engine_cylinder_gas` stays stock and converts
  this managed cylinder into its LPG component variant

### `industrial_colonies:tfmg_heavy_electrical/electrode_holder`

- Output: `tfmg:electrode_holder`
- Node/phase: `CR01 — Electronics Manufacturing` / `Electrical Manufacturing`
- Process: Compacting on `createcasing:railway_press`
- Inputs: `tfmg:heavy_machinery_casing`, four `#c:ingots/steel`, two
  `#c:plates/lead`, and two canonical `tfmg:copper_wire`
- Exact removal: `tfmg:crafting/materials/electrode_holder`

This preserves the installed material quantities while moving high-current
structural assembly to the heavy line and making TFMG copper wire canonical.

### `industrial_colonies:tfmg_heavy_electrical/portable_energy_interface`

- Output: `createaddition:portable_energy_interface`
- Node/phase: `CR01 — Early Power Cables` / `Electrical Manufacturing`
- Process: Compacting on `createcasing:copper_press`
- Inputs: `create:brass_casing`, `create:chute`, `tfmg:copper_spool`,
  `tfmg:cable_connector`, and `create:precision_mechanism`
- Exact removal: `createaddition:crafting/portable_energy_interface`

The stock `createaddition:copper_spool` is intentionally not accepted here.
The interface joins Create transfer mechanics to the pack's canonical TFMG
local-power endpoint and winding chain.

### `industrial_colonies:tfmg_heavy_electrical/digital_adapter`

- Output: `createaddition:digital_adapter`
- Node/phase: `CR01 — Early Electronics` / `Digital Logistics`
- Process: Compacting on `createcasing:brass_press`
- Inputs: the canonical `computercraft:wired_modem`, `tfmg:circuit_board`,
  `create:brass_sheet`, `create:electron_tube`, `minecraft:redstone_torch`, and
  `tfmg:copper_wire`
- Exact removal: `createaddition:crafting/digital_adapter`

This makes the adapter an actual ComputerCraft-to-Create integration part while
keeping TFMG as the board and conductor owner. The Digital Logistics phase is
required because its hardened wired modem consumes AE2 printed logic; placing
the adapter in Electrical Manufacturing would create a backward phase edge.

### `industrial_colonies:tfmg_heavy_electrical/transformer`

- Output: `tfmg:transformer`
- Node/phase: `CR01 — Control Electronics` / `Electrical Manufacturing`
- Process: Compacting on `createcasing:copper_press`
- Inputs: `tfmg:steel_casing`, five `tfmg:magnetic_alloy_sheet`, one
  `#c:plates/nickel`, and two `tfmg:copper_spool`
- Exact removal: `tfmg:crafting/materials/transformer`

The two TFMG spools represent the primary and secondary windings. No
CreateAddition coil or Electro Energetics finished transformer is accepted.

### `industrial_colonies:tfmg_heavy_electrical/voltage_observer`

- Output: `tfmg:voltage_observer`
- Node/phase: `CR01 — Control Electronics` / `Electrical Manufacturing`
- Process: Compacting on `createcasing:copper_press`
- Inputs: `tfmg:industrial_aluminum_casing`, `tfmg:circuit_board`, two
  `tfmg:transistor_item`, two `tfmg:capacitor_item`, three
  `#c:dusts/redstone`, and `tfmg:copper_wire`
- Exact removal: `tfmg:crafting/materials/voltage_observer`

The populated TFMG board is the reusable control subassembly; no Mekanism or
AE2 logic is pulled backward into this analog stage.

## Exact assignment correction

`tfmg:engine_cylinder` moves from `CR01 — Early Combusion Engines` to immediately
after `tfmg:diesel_engine_cylinder` in `CR01 — Diesel Engines`. The managed
spark-ignition cylinder consumes that aluminum predecessor directly and is only
used by the later radial-engine line. Keeping both cylinders after Chemical
Processing also respects the steel-vat aluminum boundary. All seven other
outputs retain their current node assignments.

The implementation also removes the former
`source_recipe_overrides["tfmg:engine_cylinder"]` entry. An explicit seed owner
and an automatic source override cannot claim the same output.

## Installed evidence

The validator locks the exact installed JARs and source JSON:

| Source recipe | Disposition |
| --- | --- |
| `tfmg:crafting/materials/centrifuge` | Replace |
| `tfmg:engine_cylinder` | Replace, preserving diesel components |
| `tfmg:engine_cylinder_spark_plug` | Replace, preserving gasoline/kerosene/naphtha components |
| `tfmg:engine_cylinder_gas` | Retain as downstream LPG variant |
| `tfmg:crafting/materials/electrode_holder` | Replace |
| `tfmg:crafting/materials/transformer` | Replace |
| `tfmg:crafting/materials/voltage_observer` | Replace |
| `createaddition:crafting/digital_adapter` | Replace |
| `createaddition:crafting/portable_energy_interface` | Replace |

The exact per-file SHA-256 values, stock ingredient counts, result components,
automatic owner IDs, and installed item inventory are recorded in
`TFMG_HEAVY_ELECTRICAL_REDESIGN_AUDIT.plan.json`.

## Validation

The implemented batch passes:

- 9/9 installed source recipes and their hashes;
- 8/8 pinned generic automatic-owner classifications;
- all concrete modded items and all three exact Create Encased press IDs;
- exact authoritative-seed parity plus an isolated manifest build;
- 8/8 KJSGen cards: seven Compacting and one Mechanical Crafting;
- exact machine distribution: Railway 3, Copper 3, Brass 1;
- 8/8 exact removals with `tfmg:engine_cylinder_gas` absent from removals;
- exact TFMG item-component preservation for both managed cylinders; and
- 30/30 mutation tests, including implemented owner parity, duplicate-owner
  rejection, metadata locking, and the wired-modem phase boundary.

The isolated full manifest contains 385 recipes (164 automatic), compiles to
453 KJSGen cards and 738 exact removals, and reports zero dependency warnings.

Commands:

```powershell
python tools/validate_tfmg_heavy_electrical_redesign_audit.py
python -m unittest tools.test_validate_tfmg_heavy_electrical_redesign_audit -v
python tools/build_tfmg_heavy_electrical_patch_plan.py
```

The builder now validates the implemented source state and prints a
deterministic `implemented_source_owned_noop` report. It intentionally provides
no `--apply` mode, so rerunning it cannot duplicate recipes or repeat the
assignment move.
