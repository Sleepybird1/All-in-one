# Nested Recipe Progression Audit

Status: **green**.

The nested-aware catalog contains **125** embedded recipes from 4 namespaces. One is a direct progression boundary; the other **124** are explicitly inventoried in the JSON companion.

## Progression result

- `simulated:physics_assembler` was previously invisible because it lives in the Simulated JAR bundled inside Create Aeronautics.
- Its stock recipe costs only Andesite Alloy, an Andesite Casing, and a lever, so it is a direct early physics-ship bootstrap.
- The exact recipe ID is now deferred. No namespace-wide removal is used.
- `simulated:contraption_diagram` is downstream because it consumes the assembler; it cannot restore the bootstrap.
- The cross-pack closure scanned the same nested catalog and found zero unmanaged producers for its 567 protected outputs.
- The remaining embedded recipes are terrestrial/aeronautics components, cosmetics or reversible variants, and compatibility conversions. They do not grant orbital transfer; the physical onboard flight computer remains an independent fail-closed gate.

## Dispositions

| Disposition | Count |
|---|---:|
| `compatibility_conversion` | 1 |
| `contained_downstream_of_boundary` | 1 |
| `cosmetic_or_reversible_variant` | 72 |
| `critical_space_boundary` | 1 |
| `functional_vehicle_or_aeronautics_component` | 50 |

## Catalog identity

- Recipe rows: 26086
- `recipes.csv` SHA-256: `3F2B7E1D60E2578AA0B52A2B3825195766C3D0C099EE3EAC83EF3A6FA3BCA733`
- Embedded namespaces: `{"aeronautics": 45, "create": 1, "offroad": 7, "simulated": 72}`

The exhaustive 125-row inventory, source chain, recipe type, inputs, outputs, and disposition are stored in `NESTED_RECIPE_PROGRESSION_AUDIT.json`.
