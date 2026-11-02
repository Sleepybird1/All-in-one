# Analog High-Voltage Repair

## Outcome

The authoritative recipe seed now source-owns the complete seven-output
`CR01 — High-Voltage Systems` family together. The repair removes the digital
AE2/Mekanism phase rings and sibling Control Electronics ingredients that
contradicted the actual research edge: High-Voltage Systems has only Grid
Engineering as its parent.

`HIGH_VOLTAGE_REPAIR_AUDIT.plan.json` defines a bounded, acyclic replacement
batch. It uses completed Grid Engineering equipment, earlier steel/rubber/Create
foundations, and outputs produced earlier inside this same analog node. It uses
no AE2 processor, Mekanism circuit/alloy, ComputerCraft component, Applied
Create processor, or other digital-network ingredient.

The implementation edits only
`progression/managed_recipe_overhaul.seed.json`, the plan, this record, and its
focused validator/tests. The generated manifest and KJSGen project were
intentionally not regenerated, so user-authored KJSGen work remains untouched;
deployment scripts, quests, the live pack, and Draw.io were not edited. Extreme
Power Transmission remains a separate seven-output follow-up.

## Installed source evidence

The installed source is
`electroenergetics-1.21.1-1.1.1.jar`, SHA-256
`EA5DF2C5100A4AA178BD0054779015D85C63DA221A782915240656601B51AEFD`.
All seven exact recipes exist at their NeoForge 1.21.1 singular `recipe/`
resource paths and match the current static catalog:

| Exact recipe ID | Installed type | Installed effective inputs | Output |
|---|---|---|---|
| `electroenergetics:stonecutting/transformer_core_lamination` | Stonecutting | 1 iron plate | 1 core lamination |
| `electroenergetics:crafting/insulated_wire` | Shaped crafting | 8 copper wires + dried kelp | 8 insulated wire |
| `electroenergetics:sequenced_assembly/transformer_core` | Sequenced assembly | 4 laminations + 2 copper-wire spools | 1 transformer core |
| `electroenergetics:sequenced_assembly/miniature_circuit_breaker` | Sequenced assembly | Terracotta, Precision Mechanism, copper nugget/wire, copper-wire spool | 1 miniature breaker |
| `electroenergetics:crafting/transformer` | Shaped crafting | 2 double connectors, 2 copper-wire spools, 2 laminations, transformer-oil bucket | 1 transformer |
| `electroenergetics:crafting/current_transformer` | Shaped crafting | 4 connectors, andesite-alloy block, wire spool, 2 terracotta, copper wire | 1 current transformer |
| `electroenergetics:crafting/voltage_regulator` | Shaped crafting | Precision Mechanism, 2 copper-wire spools, transformer core, transformer-oil bucket | 1 voltage regulator |

The plan records each exact JAR path and JSON SHA-256. The focused validator
reads the installed JAR itself, rather than trusting only the catalog summary.

## Repaired managed-layer problem

Before this batch, three outputs had explicit source-owned recipes:

- the steel-lamination recipe is suitable and can be retained unchanged;
- the transformer-core sequence adds `tfmg:transformer` and
  `mekanism:alloy_reinforced`; and
- the miniature breaker adds a TFMG coated board, capacitor, transistor, and
  Mekanism reinforced alloy.

The latter two cross into sibling electronics/Mekanism progression. The other
four outputs are still auto-generated 5x5 recipes. Every auto recipe adds both
`ae2:calculation_processor` and `mekanism:advanced_control_circuit` as generic
phase rings. Those items are not ancestors of High-Voltage Systems.

The repair reuses the three existing explicit IDs and adds four deliberate IDs:

- `industrial_colonies:high_voltage/transformer`
- `industrial_colonies:high_voltage/current_transformer`
- `industrial_colonies:high_voltage/voltage_regulator`
- `industrial_colonies:high_voltage/insulated_wire`

Each replacement removes exactly one installed source recipe and exclusively
owns one output. There is no namespace-wide or output-wide removal.

The source seed uses display orders 62–68. These values affect stable manifest
sorting only; the audited dependency order remains 10–70 and is derived from
the actual ingredients. The two installed incomplete items remain closed
transitionals: neither is produced by any seed recipe.

## Acyclic manufacturing order

The implemented order is intentionally a small branching analog factory:

```text
10 Steel laminations ──> 30 wound transformer core ──┬─> 50 transformer ───────┐
                                                    └─> 60 current transformer ├─> 70 voltage regulator
20 rubber-insulated wire ──> 40 miniature breaker ─────────────────────────────┘
```

Grid Engineering supplies connectors, double connectors, copper-wire spools,
accumulators, and resistors. Earlier factory progression supplies steel casing,
rubber sheet, copper wire, terracotta, Precision Mechanisms, and transformer
oil. A recipe may consume another item from this batch only when that producer
has a lower `batch_order`; the validator derives those edges from actual
ingredients and compares them with the declared dependency list.

## Replacement contracts

| Order | Source-owned output | Process/environment | Manufacturing contract |
|---:|---|---|---|
| 10 | `2x electroenergetics:transformer_core_lamination` | Railway Press | Stamp one steel plate into two laminations without crossing into Mekanism machinery. |
| 20 | `8x electroenergetics:insulated_wire` | Copper Press compacting | Laminate eight canonical copper wires with one TFMG rubber sheet. |
| 30 | `electroenergetics:transformer_core` | Railway/Copper sequenced assembly | Start with one lamination, deploy three more, wind two Grid copper spools, then press. |
| 40 | `electroenergetics:miniature_circuit_breaker` | Railway, Copper, and Brass sequence | Populate a ceramic body with a Grid resistor/connector, insulated lead, copper spool, and Precision Mechanism; Brass-press the result. |
| 50 | `electroenergetics:transformer` | 5x5 Mechanical Crafting | Build an oil-cooled steel transformer from a finished core, Grid accumulators, double connectors, copper spools, and insulation. |
| 60 | `electroenergetics:current_transformer` | Brass Press compacting | Press a finished core, Grid connectors/resistors, insulated leads, and ceramic isolation into an analog sensor. |
| 70 | `electroenergetics:voltage_regulator` | Brass Press compacting | Converge the transformer, current transformer, two miniature breakers, Grid passive components, and storage into the node capstone. |

The environments follow the pack's manufacturing language:

- Copper handles conductor insulation and winding;
- Brass handles precision measurement, switching, and regulation; and
- Railway handles transformer steel and heavy protective assembly while keeping the analog grid independent of Mekanism control circuits.

Both sequences use one six-operation loop. They preserve Electro Energetics'
real incomplete-item IDs and avoid leaking a craftable transitional item.

## Extreme Transmission was implemented as the separate follow-up

No Extreme Power Transmission output or removal is part of the seven-recipe
analog High-Voltage batch itself. The separately reviewed downstream batch is
now implemented with this exact protected-grid set:

- heavily insulated wire and its spool;
- high-voltage switch and capacitor;
- sulfur-hexafluoride breaker;
- hanging glass insulator; and
- ground rod.

That batch was deliberately audited after this one because its recipes consume
completed transformers, breakers, and regulators. Keeping the contracts
separate preserves clear ownership and cycle evidence while allowing both
batches to coexist in the authoritative seed.

## Validation

Run the read-only focused check from the project root:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\validate_high_voltage_repair_audit.py
```

The validator checks the installed JAR name/hash and all seven raw recipe
hashes, catalog recipe/output relations, concrete item and Create Encased
machine IDs, MineColonies node assignments, exact seed semantics and display
orders, one exclusive seed owner and exact stock removal per output, closed
transitionals, pattern shape, moderate sequence length, dependency order,
forbidden namespaces, and the separately implemented Extreme Transmission
follow-up set.

Run the focused mutation suite with:

```powershell
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\test_validate_high_voltage_repair_audit.py -v
```

The 12 focused tests pass. After the separate Extreme Transmission follow-up,
an isolated seed build produced 325 manifest recipes, 393 KJSGen cards, and 709
exact removals; the managed validator proved 821 inferred item edges with zero
cycles or warnings. The source-owned power
backbone validator also passes its 15-recipe contract. The broader physical
validator also passes: physical progression remains owned by the 391-recipe
managed DAG, with 707 exact removals and three non-gating endgame objectives.
