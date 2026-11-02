# Cross-pack progression loophole closure

Status: **green**.

This is the final composite safety net for the industrial progression overhaul. It reuses the authoritative domain validators and adds a catalog-wide direct-producer census over every exclusive seed output, canonical/deprecated material surface, manufactured-currency form, and explicitly retired bypass output.

## Coverage

- 594 unique protected outputs.
- 992 exact recipe-removal IDs from source policy.
- 26086 catalog rows; 25961 backed by currently installed JARs.
- 865 installed rows touch protected outputs.
- 0 protected outputs have unmanaged residual producers.

## Authoritative validators

| Validator | Result | Purpose |
|---|---|---|
| `canonical_materials_and_engine_fuels` | PASS | TFMG petroleum/steel/sulfur canonicalization and CDG fuel registry |
| `petroleum_engine_progression` | PASS | TFMG crude, diesel, gasoline, and engine construction |
| `nuclear_chemistry_boundaries` | PASS | Chemical Vat sulfuric acid and forward-only Yellorium/uranium route |
| `allthemodium_currency` | PASS | manufactured ATM/Vibranium/Unobtainium currency and shortcut retirement |
| `confirmed_bypass_retirement` | PASS | Digital Miner, smelting factories, equipment, mines, and teleport bypasses |
| `tfmg_steelworks` | PASS | canonical coke/hot-blast/industrial-blasting/TFMG casting chain |
| `bigreactors_release_integrity` | PASS | 27 reviewed Big Reactors bulk/controller contracts are present in the released seed |
| `managed_manifest_freshness` | PASS | released seed compiles to the committed managed manifest |
| `compiled_kjsgen_freshness` | PASS | committed managed manifest compiles to the committed KJSGen project |
| `managed_overhaul_integrity` | PASS | committed manifest and KJSGen project remain dependency-consistent |

## Locked progression conclusions

- Create Diesel Generators may burn only the canonical TFMG Diesel/Gasoline tags; biodiesel, ethanol, and plant oil fuel definitions remain disabled.
- Player-facing sulfuric acid is synthesized only by `tfmg:vat_machine_recipe/sulfuric_acid`; the approved Rotary Condensentrator bridge is conversion, not synthesis.
- Yellorium feeds forward into raw uranium and staged Mekanism enrichment; reverse conversion and furnace shortcuts remain rejected by the full active-JAR chemistry scan.
- Allthemodium, Vibranium, Unobtainium, and their alloys remain manufactured currency; ore placement, loot, stock furnace/Mekanism/TConstruct acquisition, normal smithing upgrades, compression aliases, and the Teleport Pad remain closed.
- Digital Miner, Energized Smelter and all four Smelting Factory entrances, Mekanism teleport/QIO entrances, and Quantum Entangloporter remain physically retired.
- TFMG steel remains the sole solid steel family, and AE2 Printed Silicon is Brass-press compacted from `tfmg:silicon_ingot` with both stock AE2 and ExtendedAE shortcuts removed.

## Residual producer classifications

- `canonical_stock_route`: 20
- `display_only_impostor`: 36
- `exactly_removed`: 789
- `explicit_downconversion_closure`: 4
- `inactive_conditioned_definition`: 12
- `self_transform_closure`: 8
- `storage_recovery_closure`: 13

## Release gate

All closure checks are green. The report is ready for serialized README/deploy wiring.

## Commands

```powershell
python tools/validate_cross_pack_progression_loophole_closure.py --write --allow-pending
python tools/validate_cross_pack_progression_loophole_closure.py
python -m unittest tools.test_validate_cross_pack_progression_loophole_closure
```
