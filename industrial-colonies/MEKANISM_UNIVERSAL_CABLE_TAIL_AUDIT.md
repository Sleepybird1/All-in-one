# Mekanism Universal Cable tail audit

## Decision

**IMPLEMENTED IN THE AUTHORITATIVE SEED.**

Replace the three generic automatic Universal Cable rings with three explicit,
source-owned Encased compacting contracts. Every contract consumes one complete
eight-segment run and emits exactly eight segments, so run length is preserved.
The recipes now read as cable manufacturing rather than eight copies of tier A
around one tier-B alloy.

This audit is authoritative for these outputs only:

- `mekanism:advanced_universal_cable`
- `mekanism:elite_universal_cable`
- `mekanism:ultimate_universal_cable`

It explicitly supersedes the preserve-automatic Universal Cable language in
`MEKANISM_TRANSMITTER_UPGRADE_AUDIT`. That older audit remains authoritative for
its twelve Logistical Transporter, Mechanical Pipe, Pressurized Tube, and
Thermodynamic Conductor contracts.

## Installed source and alternate-producer audit

`Mekanism-1.21.1-10.7.19.85.jar` contains exactly one static producer for each
target. All three are shaped 3x3 rings, output eight, and have no alternate
catalog producer:

| Output | Exact stock ID | Stock inputs | Source SHA-256 |
|---|---|---|---|
| `8x mekanism:advanced_universal_cable` | `mekanism:transmitter/universal_cable/advanced` | `8x basic_universal_cable` + `#mekanism:alloys/infused` | `72C44C4E6FD20B2FE45DA27189DFF8AB18DF91954ED6AF0D1224F4C08B7A272E` |
| `8x mekanism:elite_universal_cable` | `mekanism:transmitter/universal_cable/elite` | `8x advanced_universal_cable` + `#mekanism:alloys/reinforced` | `8F7AEA93CA7B73AF232D30BE79940E178136306A3E498C574D2383D3E013BE32` |
| `8x mekanism:ultimate_universal_cable` | `mekanism:transmitter/universal_cable/ultimate` | `8x elite_universal_cable` + `#mekanism:alloys/atomic` | `ABC62FC98D4F1E7C865FFB74CFB7F494141570835E9F330A30522625393B7846` |

The installed catalog exposes only two static target consumers: Advanced is
consumed by the stock Elite recipe and Elite by the stock Ultimate recipe.
Ultimate has no installed static consumer. The authoritative seed adds four
current consumers: Advanced and Elite Induction Providers use four matching
cables, the Induction Port pattern uses four Ultimate cables, and the Ultimate
Induction Provider uses four Ultimate cables.

The automatic audit named `electroenergetics:extreme_wire` and
`tfmg:sulfur_hexafluoride_bucket` as conceptual prerequisites, but neither ID
exists in the installed builds. The real protected-grid contracts are
`electroenergetics:heavily_insulated_wire` and
`electroenergetics:sulfur_hexafluoride_breaker`; using those exact installed
outputs prevents a phantom dependency.

## Implemented manufacturing contracts

| Order | Source-owned ID / output | Placement | Exact environment | Manufacturing bill |
|---:|---|---|---|---|
| 10 | `industrial_colonies:mekanism/transmission/advanced_universal_cable`<br>`8x mekanism:advanced_universal_cable` | CR01 — Reinforced Systems<br>Mekanized Industry | `createcasing:copper_press` | `8x basic_universal_cable`, `4x alloy_infused`, `2x advanced_control_circuit`, `4x tfmg:aluminum_wire`, `2x tfmg:aluminum_cable_hub`, `4x tfmg:rubber_sheet` |
| 60 | `industrial_colonies:mekanism/transmission/elite_universal_cable`<br>`8x mekanism:elite_universal_cable` | CR01 — Precision Engineering<br>High-Energy Grid | `createcasing:weathered_iron_press` | `8x advanced_universal_cable`, `4x alloy_reinforced`, `2x elite_control_circuit`, `4x tfmg:aluminum_wire`, `2x tfmg:glass_cable_insulator`, `2x tfmg:steel_cable_hub` |
| 110 | `industrial_colonies:mekanism/transmission/ultimate_universal_cable`<br>`8x mekanism:ultimate_universal_cable` | CR01 — High-Energy Distribution<br>High-Energy Grid | `createcasing:weathered_iron_press` | `8x elite_universal_cable`, `4x alloy_atomic`, `2x ultimate_control_circuit`, `4x tfmg:aluminum_wire`, `2x tfmg:glass_cable_insulator`, `2x tfmg:steel_cable_hub`, `4x electroenergetics:heavily_insulated_wire`, `sulfur_hexafluoride_breaker` |

Each recipe removes only its exact matching stock recipe ID and claims its
output exclusively. Advanced stays reachable because the Copper Press is
source-owned in Steam & Brass, before Mekanized Industry. Elite upgrades the
line to glass standoffs and steel terminations on Weathered Iron. Only Ultimate
crosses into Extreme Power Transmission, consuming the completed protected
wire and SF6-named breaker contracts. Neither Advanced nor Elite contains an
Electro Energetics or SF6 input.

The tier-installer blacklist does not change. Mekanism transmitters carry
`AttributeTier`, not `AttributeUpgradeable`, so `ItemTierInstaller` cannot use
them as an upgrade bypass. Adding them to `installer_upgradeable.json` would
contradict the audited runtime semantics.

## Exact dependency migration

The ID map is:

| Retired automatic ID | New source-owned ID |
|---|---|
| `industrial_colonies:auto/mekanism/advanced_universal_cable` | `industrial_colonies:mekanism/transmission/advanced_universal_cable` |
| `industrial_colonies:auto/mekanism/elite_universal_cable` | `industrial_colonies:mekanism/transmission/elite_universal_cable` |
| `industrial_colonies:auto/mekanism/ultimate_universal_cable` | `industrial_colonies:mekanism/transmission/ultimate_universal_cable` |

Two authoritative seed dependency edges that required the retired Ultimate ID
were moved atomically with the recipe append:

- `/recipes/68/depends_on/3`, owned by
  `industrial_colonies:mekanism/induction/port`
- `/recipes/76/depends_on/3`, owned by
  `industrial_colonies:mekanism/induction/ultimate_provider`

The Induction Matrix audit plan repeats that dependency at
`/external_prerequisites/3/recipe_id`,
`/replacement_contracts/1/depends_on_batch/3`, and
`/replacement_contracts/9/depends_on_batch/3`. Its active validator repeats it
once in `EXTERNAL_OUTPUTS["mekanism:ultimate_universal_cable"]`. The integration
maps all six non-generated references to the new Ultimate ID.

Assignment metadata was already correct and received zero changes. No
authoritative generated artifact or deployed file was hand-edited. An isolated
build from seed produced 329 managed recipes (83 automatic), 397 compiled
KJSGen cards, 661 exact removals, and 33 intentional skips with no warning.
The implemented seed SHA-256 is
`D34BB136243F77BA8786053F2CD422AB57860D051B90280EE4638144B777A923`;
the unchanged assignment SHA-256 is
`329FA3F02EFDF9544CC3F4923FFF995EB8C3502401526A6521449134CDCCE24E`.

## Review package and validation

`tools/build_mekanism_universal_cable_tail_patch_plan.py` emits a deterministic
historical patch artifact and verifies the already-applied append plus two seed
dependency rewrites. It has no apply mode. The validator proves exact JAR bytes, one
static producer per output, installed and managed consumers, ingredient and
machine existence, assignment placement, predecessor availability, acyclic
Advanced → Elite → Ultimate order, the exact stock-removal set, automatic-owner
suppression, compiled batch-of-eight cards, and complete Induction dependency
mapping. The mutation suite contains 27 focused failure cases.

Run:

```powershell
python tools/validate_mekanism_universal_cable_tail_audit.py
python -m unittest tools/test_validate_mekanism_universal_cable_tail_audit.py
python tools/build_mekanism_universal_cable_tail_patch_plan.py
```
