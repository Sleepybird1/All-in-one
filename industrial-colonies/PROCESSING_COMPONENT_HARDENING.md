# Processing Component Hardening

Five component gaps from `PROCESSING_COMPONENT_AUDIT.md` are now authored in
`progression/managed_recipe_overhaul.seed.json`. They are source-owned recipes;
the live pack is unchanged until the normal reviewed deployment runs.

| Output | New manufacturing route | Exact stock recipe(s) retired |
|---|---|---|
| `tfmg:empty_spool` | Hardened TFMG planks cut on the Copper Mechanical Saw | `tfmg:empty_spool_from_hardened_planks_stonecutting` |
| `megacells:accumulation_processor` | Two Copper-Deployer loops add a coated TFMG board, printed silicon, capacitor, and fluix to the printed accumulation circuit; Brass Press finish | `megacells:inscriber/accumulation_processor`, `extendedae:assembler/accumulation_processor` |
| `electroenergetics:transformer_core_lamination` | One steel plate stamped into two laminations by the Railway Press | `electroenergetics:stonecutting/transformer_core_lamination` |
| `electroenergetics:transformer_core` | Four laminations and two Electro Energetics copper-wire spools assembled and closed on the Railway/Copper analog line | `electroenergetics:sequenced_assembly/transformer_core` |
| `electroenergetics:miniature_circuit_breaker` | Ceramic body populated with Electro Energetics protection hardware, insulated lead, copper winding, and a precision mechanism before Brass pressing | `electroenergetics:sequenced_assembly/miniature_circuit_breaker` |

The two Electroenergetics sequences reuse their installed incomplete items.
The accumulation sequence reuses the installed printed accumulation processor
as both input and visible workpiece, so this batch adds no orphaned custom
transitional item. The stock Crystal Assembler accumulation recipe is removed
because it bypasses the TFMG board line; a future batch accelerator should be
added only when the managed-recipe/KJSGen schema can represent and validate the
ExtendedAE Crystal Assembler recipe environment directly.

Run the focused checks against the seed alone:

```powershell
python tools/validate_processing_component_hardening.py
python -m unittest tools/test_validate_processing_component_hardening.py
```

For release preflight, first assemble and compile into temporary files, then
pass those paths with `--manifest`, `--compiled`, and the current static catalog
with `--catalog`. Do not overwrite shared generated outputs merely to run this
validator.
