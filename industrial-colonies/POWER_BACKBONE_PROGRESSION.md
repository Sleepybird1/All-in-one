# TFMG-first power backbone progression

## Implemented scope

The authoritative managed-recipe seed now owns the complete first power backbone from TFMG electromechanical conversion through Electro Energetics Grid Engineering. The implementation contains 15 deliberate recipes and five exact Create Crafts & Additions retirements.

This is a source-only change. Shared generated manifests, KJSGen projects, quests, deployment code, the live pack, Minecraft, and the Draw.io graph were not changed.

## Construction order

| Node | Managed recipe | Output |
|---|---|---|
| Early Electricity Technology | `industrial_colonies:early_electricity/generator` | `tfmg:generator` |
| Early Electricity Technology | `industrial_colonies:early_electricity/electric_motor` | `tfmg:electric_motor` |
| Early Power Cables | `industrial_colonies:early_power_cables/cable_connector` | `tfmg:cable_connector` |
| Early Power Cables | `industrial_colonies:early_power_cables/copper_cable_hub` | `2x tfmg:copper_cable_hub` |
| Early Power Cables | `industrial_colonies:early_power_cables/redstone_relay` | `createaddition:redstone_relay` |
| Early Power Cables | `industrial_colonies:early_power_cables/small_light_connector` | `createaddition:small_light_connector` |
| Chemical Processing | `industrial_colonies:chemical_processing/accumulator` | `tfmg:accumulator` |
| Chemical Processing | `industrial_colonies:chemical_processing/cable_tube` | `8x tfmg:cable_tube` |
| Grid Engineering | `industrial_colonies:grid/empty_spool` | `4x electroenergetics:empty_spool` |
| Grid Engineering | `industrial_colonies:grid/connector` | `2x electroenergetics:connector` |
| Grid Engineering | `industrial_colonies:grid/copper_wire_spool` | `electroenergetics:copper_wire_spool` |
| Grid Engineering | `industrial_colonies:grid/resistor` | `electroenergetics:resistor` |
| Grid Engineering | `industrial_colonies:grid/accumulator` | `electroenergetics:accumulator` |
| Grid Engineering | `industrial_colonies:grid/alternator_rotor` | `electroenergetics:alternator_rotor` |
| Grid Engineering | `industrial_colonies:grid/alternator_brushes` | `electroenergetics:alternator_brushes` |

The generator and motor no longer remain in `exclude_outputs`. The manifest builder forbids an output from being both explicitly source-owned and excluded; the explicit entries themselves prevent generic auto-generation from creating a competitor.

## Manufacturing language

### Pre-steel electromechanical conversion

The first generator and motor use brass casing, copper/iron, shafts, and Precision Mechanisms. They do not require steel, a winding machine, magnets, capacitors, AE2, or Mekanism. This makes the Early Electricity node physically reachable from its actual ancestors.

The motor consumes the first TFMG generator, so rotation-to-FE is established before the reverse conversion becomes available.

### Canonical local delivery

TFMG cable connectors and copper cable hubs use ordinary brass/copper/iron construction rather than the sibling Electronics Manufacturing branch's copper spool. The unique Create Crafts & Additions Redstone Relay and Small Light Connector remain useful, but their recipes now consume the TFMG connector.

The Portable Energy Interface remains available because it serves moving contraptions rather than duplicating a fixed cable endpoint.

### Chemical storage and insulation

The TFMG accumulator is now the intended lead-acid battery: sulfuric acid, lead plate/block, copper wiring, and a TFMG steel casing. Its two aluminum/lithium stock recipes are removed exactly.

Cable tubes are produced eight at a time from TFMG rubber sheet, canonical steel nuggets, and copper wire. This gives the Chemical Processing line a visible storage and insulation purpose.

### Long-span grid upgrade

Electro Energetics begins by upgrading the existing TFMG stack:

- its connector consumes a TFMG cable connector and copper cable hub;
- its accumulator consumes the TFMG lead-acid accumulator;
- its alternator rotor consumes the TFMG generator;
- its grid spool consumes canonical copper wire; and
- its two-loop brush assembly runs through Copper/Brass Create Encased Deployers and the Brass Press.

The base connector recipe removes only `electroenergetics:crafting/connector`. These three reclamation recipes are deliberately preserved:

- `electroenergetics:crafting/connector_from_double`
- `electroenergetics:crafting/connector_from_triple`
- `electroenergetics:crafting/connector_from_quad`

They only recover base connectors from already-manufactured variants and cannot create an early grid bypass.

## Exact duplicate retirements

The following recipes are retired through exact `additional_removals` entries:

| Removed recipe | Canonical system |
|---|---|
| `createaddition:mechanical_crafting/alternator` | `tfmg:generator` |
| `createaddition:mechanical_crafting/electric_motor` | `tfmg:electric_motor` |
| `createaddition:crafting/modular_accumulator` | `tfmg:accumulator` |
| `createaddition:crafting/connector` | `tfmg:cable_connector` |
| `createaddition:crafting/large_connector` | `tfmg:copper_cable_hub` |

No output-wide or namespace-wide removal was added.

## Verification

`tools/validate_power_backbone_progression.py` locks:

- all 15 recipe IDs, outputs, counts, layouts, and machine routes;
- exact stock-removal ownership;
- the five duplicate retirements appearing exactly once;
- all three EE connector reclamation recipes remaining unremoved;
- pre-steel generator/motor ingredients;
- absence of sibling AE2/Mekanism/copper-spool gates from local/grid recipes;
- MineColonies node assignment parity; and
- isolated generated-manifest parity.

`tools/test_power_backbone_progression.py` contains 11 mutation tests covering missing recipes, changed counts, changed removals, forbidden Mekanism and sibling ingredients, lost reclamation, missing/duplicate retirements, altered Create Encased routing, and explicit/excluded ownership conflicts.

The isolated temporary build produced:

- 335 managed manifest recipes, including 215 automatic recipes;
- 403 compiled KJSGen recipe cards;
- 725 exact KJSGen removals; and
- 37 intentionally reported skipped assignments.

Validation results:

- focused source and temporary-manifest validator: pass;
- 11 mutation tests: pass;
- managed manifest/compiler/removal/DAG validator: pass with zero warnings;
- full physical-progression validator: pass; and
- audit item/JAR referential validator: pass.

The authoritative shared generated files intentionally remain stale until the root integration pass performs one coordinated regeneration.

## Deferred boundaries

This implementation deliberately does not change Create Steam Engine construction, the seven High-Voltage outputs, the seven Extreme Transmission outputs, the four Mekanism energy cubes, the ten induction-matrix components, or any Immersive Engineering recipe. Those remain the separately ordered follow-up batches in `POWER_BACKBONE_AUDIT.plan.json`.
