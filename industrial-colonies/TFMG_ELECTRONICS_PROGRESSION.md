# Reachable TFMG Electronics Progression

The Industrial Electronics branch keeps the exact authoritative Draw.io
topology:

`Early Electricity Technology → Electronics Manufacturing → Early Circuitry → Advanced Electronics Manufacturing → Advanced Circuitry → Early Chips`

No node or edge was added, removed, or moved. The recipes were rebuilt around
the materials that are actually available through each node's strict Draw.io
ancestors.

## Electronics Manufacturing

This node now bootstraps a pre-steel electrical workshop:

- Create cutting turns ordinary planks into TFMG empty spools.
- The retained TFMG copper-spool recipe uses canonical TFMG copper wire.
- A Create mechanical-crafting line builds the winding machine from brass,
  copper, an early electric motor, and precision mechanics.
- The voltmeter uses copper, zinc, redstone, and a compass. It no longer needs
  a magnet, breaking the stock `voltmeter → magnet → polarizer → voltmeter`
  loop.
- The polarizer uses that reachable voltmeter, copper spools, the winding
  machine, an early generator, brass, and precision mechanics. It consumes no
  resistor or capacitor from the child node.
- The electrode holder uses brass, iron, and canonical copper wire rather than
  steel, lead, or a heavy machinery casing.
- Copper and zinc electrode stonecutting recipes are retained but research
  staged here.

## Early Circuitry

The early line deliberately represents pre-silicon electronics:

- Quartz cores and copper winding produce wirewound resistors in the TFMG
  winding machine; constantan is not required.
- Create sequenced assembly layers iron, copper, and paper into capacitors.
- Quartz, redstone, zinc, and copper become point-contact-style transistors.
- Paper, copper, pressing, and green dye make board blanks.
- Deployers populate those blanks with the same-node resistor, capacitor,
  transistor, and copper wire to make the first hand-routed circuit boards.

The stock recipes that required plastic, steel, silicon, semiconductors,
constantan, or a later etched board are removed.

## Advanced Electronics Manufacturing

TFMG's gold-coating deployer recipe remains intact and is staged at this node.
The stock sulfuric-acid vat etch is removed. A TFMG polarizer now performs
electrical board etching, so the electronics branch does not borrow chemistry
from a sibling branch. The industrial mixer is mechanically crafted from
reachable brass-age mechanics, an early motor, and Early Circuitry boards.

Sulfuric acid is not synthesized, substituted, or unlocked anywhere in this
electronics slice. Its canonical production path remains the TFMG Chemical Vat
behind the chemical progression.

## Enforcement and validation

`industrial_electronics_progression.js` removes each conflicting stock recipe
by exact ID and registers the replacement paths. Every replacement and retained
electronics recipe is assigned to its exact MineColonies/FTB Team research
stage through `machine_recipe_dependencies.json` or
`additional_recipe_stages.json`.

Run the targeted validation with:

```powershell
python tools/validate_tfmg_electronics_progression.py `
  "C:\Users\GodPC\curseforge\minecraft\Instances\All in one" `
  --drawio-export "..\industrial-audit\drawio-export\drawio_tree.json"
```
