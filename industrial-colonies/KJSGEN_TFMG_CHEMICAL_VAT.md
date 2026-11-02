# KJSGen TFMG Chemical Vat editor

Industrial Colonies adds one visual KJSGen recipe type for the TFMG 1.2.0
Chemical Vat:

- card type: `industrial_colonies:tfmg_chemical_vat`
- runtime recipe type: `tfmg:vat_machine_recipe`
- layout resource: `assets/industrial_colonies/kjsgen_layouts/tfmg_chemical_vat.json`
- code generator: `TfmgChemicalVatCodegen`

The card describes the verified 1.2.0 API rather than a future TFMGJS API. It
emits `event.custom({...}).id('<recipe id>')`, so every visual card keeps its
exact managed identity and can be removed or replaced safely.

## Visual contract

The canvas has one mixed list for ingredients and one mixed list for results.
This is a deliberately bounded subset of the Vat codec: each side accepts one
through four total visible mixed rows. The exporter also enforces the codec's
separate limits of four expanded item entries and four fluid entries on each
side.

Ingredients may be concrete items, item tags, concrete fluids, or fluid tags.
TFMG's item-ingredient codec has no count field, so an item count is exported
as repeated ingredient objects. For example, one visual `3x tfmg:sulfur_dust`
slot becomes three `{ item: 'tfmg:sulfur_dust' }` entries. A single `5x` input
is rejected because expansion would exceed the four-item limit. Fluids use the
NeoForge ingredient codec:

- concrete: `{ type: 'neoforge:single', fluid: '...', amount: N }`
- tag: `{ type: 'neoforge:tag', tag: '...', amount: N }`

Results may be concrete items or concrete fluids. Item results support count
and chance. Fluid results support amount but reject chance. Tags and item
components are rejected on outputs.

The verified selector presets are intentionally narrow:

| Editor value | Exported TFMG value |
| --- | --- |
| `vatMode=steel` | `allowed_vat_types: ['tfmg:steel_vat']` |
| `vatMode=firebrick` | `allowed_vat_types: ['tfmg:firebrick_lined_vat']` |
| `vatMode=both` | both IDs, in that order |
| `machineMode=mixing` | `machines: ['tfmg:mixing']` |
| `machineMode=two_electrodes` | two ordered `tfmg:electrode` entries |

`heat=none` omits `heat_requirement`; `heated` and `superheated` emit the
literal field. `minSize=0` omits `min_size`, while positive values emit it.
`processingTime` is always a positive integer and defaults to 100 ticks.

Pressure is not exposed. The installed TFMG 1.2.0 Vat codec does not support
the pressure API guarded by newer TFMGJS releases. The internal `heat_level`
codec field is also intentionally not exposed by this bounded editor.

## Managed-manifest form

The recipe compiler now accepts `type: "tfmg_vat"`:

```json
{
  "id": "industrial_colonies:chemistry/example",
  "phase": "steelworks",
  "type": "tfmg_vat",
  "comment": "Example only",
  "inputs": [
    {"kind": "ITEM", "id": "tfmg:sulfur_dust", "count": 3},
    {"kind": "FLUID", "id": "minecraft:water", "amount": 1000}
  ],
  "outputs": [
    {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 500}
  ],
  "vat": "both",
  "machine": "mixing",
  "heat": "none",
  "min_size": 1,
  "processing_time": 100
}
```

The project-preferred manifest vocabulary is `inputs`, `outputs`, `vat`, and
`machine`, matching the rest of the recipe seed. The compiler also accepts the
internal canonical names `ingredients`, `results`, `vat_mode`, and
`machine_mode`. Defining both forms is allowed only when their values are
identical; conflicting aliases fail compilation and managed validation.

This change supplies infrastructure only. It does not add Desh, Ostrum, or
other planetary Chemical Vat recipes, and it does not deploy anything to the
live pack.

## Validation

`tools/validate_kjsgen_tfmg_chemical_vat.py` pins the JSON layout, Java
registration and code-generation markers, Python compiler branch, managed
validator support, installed TFMG 1.2.0 Vat bytecode hashes and stock codec
examples, plus the packaged candidate JAR. Its companion mutation suite covers
19 independent regressions, including a single `5x` ingredient bypass attempt
and missing/conflicting manifest aliases.

The preflight also runs the six-test Mekanism regression suite. The custom
metallurgic-infusing exporter now appends the KJSGen card's explicit recipe ID
instead of leaving identity assignment to export order.
