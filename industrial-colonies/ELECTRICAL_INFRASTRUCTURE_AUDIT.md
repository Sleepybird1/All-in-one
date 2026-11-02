# Electrical infrastructure progression audit

## Scope and source

This audit uses the installed NeoForge 1.21.1 pack data from:

- `tfmg-1.2.0.jar`;
- `createaddition-1.6.0.jar` (Create Crafts & Additions);
- `electroenergetics-1.21.1-1.1.1.jar`;
- `Mekanism-1.21.1-10.7.19.85.jar`;
- the live Create Crafts & Additions and Electro Energetics server configs; and
- the 77-node/99-edge authoritative Draw.io export.

The Draw.io file itself was not edited.

## Intended electrical ladder

| Draw.io node | Intended family | Boundary |
|---|---|---|
| `CR01 — Early Electricity Technology` | TFMG generator and electric motor | pre-steel electromechanical conversion inside one factory |
| `CR01 — Early Power Cables` | TFMG connector/hub; CreateAddition relay, light, and contraption-only utilities | canonical short local delivery plus non-duplicate augment utilities |
| `CR01 — Chemical Processing` | TFMG lead-acid accumulator | chemical bulk storage after sulfuric acid and steel converge |
| `CR01 — Grid Engineering` | first Electro Energetics connectors, 128-block wire, alternator, accumulator | utility-grid entry upgraded from the TFMG machine stack |
| `CR01 — High-Voltage Systems` | Electro Energetics transformers, regulation, breaker and insulation | voltage conversion/control |
| `CR01 — Extreme Power Transmission` | protected high-energy Electro Energetics equipment | late overhead transmission |
| `CR01 — Reinforced Systems` through `Precision Engineering` | Mekanism advanced/elite block cables | dense in-factory distribution |
| `CR01 — High-Energy Distribution` | Mekanism ultimate cable and induction storage after both branches converge | ultimate local distribution/storage |

The installed behavior materially supports the local/grid split. TFMG's cable
connector is an electrical block entity with explicit cable connections, while
its copper cable hub is a local cable-network block. Create Crafts & Additions'
generic FE endpoints are true overlapping wire nodes (configured for 16/32
blocks), so their craft routes are retired under the TFMG-default rule. Electro
Energetics allows its ordinary grid wire to span 128 blocks and models
resistance, overload breakage, electrocution, component damage, voltage, and
current. Mekanism universal cables are contiguous blocks, not
endpoint-to-endpoint overhead spans.

## Duplicate same-tier systems

### Early generation and storage

The user's TFMG-default rule is implemented. TFMG now owns rotation-to-FE,
FE-to-rotation, bulk local storage, and generic local wiring. Create Crafts &
Additions no longer supplies a parallel machine or generic connector stack.

The installed TFMG recipes could not occupy the authoritative pre-steel node:

- `tfmg:sequenced_assembly/generator` consumes steel plate,
  `tfmg:steel_mechanism`, `tfmg:capacitor_item`, and a `tfmg:winding` step.
- `tfmg:sequenced_assembly/motor` consumes `tfmg:steel_mechanism` and uses the
  same winding process.
- Winding equipment belongs to the child node `CR01 — Electronics
  Manufacturing`; the TFMG capacitor belongs to its later `CR01 — Early
  Circuitry` descendant; steel is reached through the child `CR01 — The Steel
  Age`.
- `tfmg:crafting/materials/accumulator` consumes sulfuric acid and an industrial
  aluminum casing. Sulfuric acid belongs to the later Chemical Processing path.

The replacement generator and electric-motor recipes use brass casing, copper,
iron, shafts, Precision Mechanisms, and the preceding TFMG generator. They use
no steel, cast iron, winding, capacitor, rubber, aluminum, sulfuric acid, or
descendant machine. Cast iron was intentionally excluded even though it is
thematically plausible: this graph owns it at the child `CR01 — The Steel Age`,
so using it would recreate the cycle.

The Create Crafts & Additions `alternator` and `electric_motor` source recipes
are retired. A scan of all 20,396 installed recipe JSONs found no other recipe
that consumes either machine, so no compatibility recipe was lost.

TFMG's accumulator remains chemical rather than being artificially made
pre-steel. Its two installed aluminum/lithium recipes are replaced by one
lead-acid recipe at `CR01 — Chemical Processing`, using canonical TFMG steel,
sulfuric acid, lead, and copper. Create Crafts & Additions'
`modular_accumulator` is retired; the same installed-recipe scan found no other
consumer, and the Electro Energetics grid upgrade now consumes the TFMG
accumulator.

### Storage bypasses

Mekanism still provides basic through ultimate energy cubes alongside the TFMG
and Electro Energetics accumulators. Energy cubes currently have no explicit
University assignment. Their recipes are therefore an ungoverned storage
bypass. No cube was retired or reassigned in this slice because deciding whether
they become Mekanism-tier local buffers or are removed in favor of TFMG/EE
storage changes the later Mekanism balance and is separable from retiring the
proven-safe Create Crafts & Additions duplicates.

## Transmission conflicts and direct crafting bypasses

### Early Power Cables

- TFMG's installed cable-connector recipe used steel nuggets and a fired
  insulator. Its staged replacement is genuinely pre-steel, using canonical
  brass plate, copper wire, and iron nuggets. The focused validator checks both
  exact item IDs and canonical tag IDs, so a steel tag cannot silently bypass
  this material boundary.
- TFMG's copper cable hub is staged at the same node from canonical copper
  ingot/wire tags. Both Electro Energetics construction steps that formerly
  consumed `createaddition:large_connector` now consume this TFMG hub.
- TFMG's cable tube is not valid at the pre-steel connector node: its recipe
  consumes `tfmg:rubber_sheet`; the only installed rubber recipe uses sulfur
  dust and heavy oil in a heated TFMG vat. The tube and rubber-sheet ownership
  are therefore moved to `CR01 — Chemical Processing`, and the tube's exact
  shaped recipe is staged there with rubber, canonical steel, and copper wire.
- Create Crafts & Additions' generic `connector` and `large_connector` are
  retired and hidden from the recipe viewer. The installed small connector had
  exactly two consumers: the redstone relay and small light connector. Those
  specialized, non-equivalent utilities remain visible and are rebuilt from
  the TFMG cable connector at this exact stage. The portable energy interface
  also remains because it is a moving-contraption interface rather than a TFMG
  cable endpoint.

### Electro Energetics grid

The native first-grid recipes were all ordinary crafting from Andesite alloy,
copper, terracotta, wood, or iron. In particular,
`electroenergetics:crafting/connector` produced four utility-grid endpoints
without any steel, chemical, local-network, or Grid Engineering prerequisite.
That made the 128-block grid available effectively in the Andesite/Brass era.

The implemented first slice replaces seven source recipes:

| Output | New exact recipe | Construction role |
|---|---|---|
| `electroenergetics:empty_spool` | `industrial_colonies:grid/empty_spool` | durable grid spool hardware |
| `electroenergetics:connector` | `industrial_colonies:grid/connector` | upgrades the TFMG connector and copper cable hub into a grid endpoint |
| `electroenergetics:copper_wire_spool` | `industrial_colonies:grid/copper_wire_spool` | canonical TFMG copper wire on the staged spool |
| `electroenergetics:accumulator` | `industrial_colonies:grid/accumulator` | 5x5 upgrade from the TFMG chemical accumulator, steel casings, connectors and spools |
| `electroenergetics:alternator_rotor` | `industrial_colonies:grid/alternator_rotor` | 5x5 grid alternator upgrade from TFMG generation and steel mechanisms |
| `electroenergetics:alternator_brushes` | `industrial_colonies:grid/alternator_brushes` | two-loop Sequenced Assembly from local connector hardware |
| `electroenergetics:resistor` | `industrial_colonies:grid/resistor` | grid connectors and cast-iron thermal structure |

Every exact ingredient belongs to Grid Engineering or an authoritative Draw.io
ancestor. Connector-to-double/triple/quad crafting remains intact. The three
reverse reclamation recipes also remain because they can only consume a
connector variant ultimately built from the staged base connector; they are
declared, reviewed policy survivors rather than raw-material bypasses.

### High voltage and extreme transmission

The High-Voltage Systems assignments are conceptually ordered, but their native
recipes are not exact-stage gated. Examples:

- transformer lamination is one iron plate in a stonecutter;
- transformer core and miniature breaker use native Sequenced Assembly IDs;
- transformer, current transformer, and voltage regulator are ordinary shaped
  crafting;
- insulated wire is eight copper wires plus dried kelp.

The new staged copper spool prevents these items from appearing before Grid
Engineering, but they can still be crafted immediately after Grid Engineering
without completing High-Voltage Systems. A second Electro Energetics slice must
rewrite/map that complete family together. The same applies to Extreme Power
Transmission's heavily insulated spool, high-voltage switch/capacitor, SF6
breaker, hanging insulator, and ground rod.

### Mekanism local transmission

The five basic Mekanism transmitter families are now assigned to Modular
Machinery and rebuilt as deliberate eight-segment batches. Their exact stock
recipes are retired. The new recipes converge the earlier TFMG factory,
Create handling/fluid infrastructure, Electro Energetics grid components, and
first-tier Mekanism infusion without consuming any future-tier ingredient.
Advanced, elite, and ultimate universal cables remain assigned to later
factory/grid phases and continue to consume the preceding cable tier.

Recipe progression cannot enforce a physical maximum network length, so the
unique value of Electro Energetics remains its 128-block endpoint span,
overhead construction, and electrical hazards rather than an absolute ban on
long Mekanism cable runs. See `MEKANISM_TRANSMISSION_FOUNDATION.md` for the
exact five-recipe contract and infinite-source-cell retirement policy.

## Verification

`tools/validate_tfmg_early_electricity.py` locks the TFMG source-recipe evidence,
exact-and-tag pre-steel ingredient boundary, chemical accumulator placement,
five exact retirement policies, recipe-viewer cleanup, all 20,396 installed
recipe consumers, two specialized compatibility ports, and four TFMG grid
ports. `tools/validate_electrical_grid_progression.py` locks the installed
recipe/config evidence, exact Draw.io edges, seven grid replacement IDs,
dependency rows, construction policies, and the deliberately surviving
connector reclamation recipes. `tools/validate_machine_recipe_progression.py`
independently rejects any downstream or sibling ingredient introduced by the
replacements.
