# Late-Digital Manufacturing Gateways

This slice keeps Applied Create, ExtendedAE, AdvancedAE, and MEGA Cells useful
without letting their small stock recipes bypass the pack's electrical and
high-energy factories. All seven replacement recipes remain editable cards in
the KubeJS Gen `default` project.

## Remote kinetic networking

| Output | Manufacturing contract |
|---|---|
| `appliedcreate:kinetic_energy_acceptor` | A 5x5 conversion cabinet built around the canonical TFMG Generator, TFMG Electric Motor, an AE2 Energy Acceptor, copper wiring, stress logic, and an Advanced Control Circuit. |
| `appliedcreate:stress_storage_component_1k` | A two-loop Weathered Iron Sequenced Assembly. It winds copper and capacitors around a 4k AE cell component and installs two stress processors. |
| `appliedcreate:me_gearbox` | A 5x5 remote-kinetic gateway containing physical Create gearboxes, ME P2P endpoints, dense smart cable, advanced stress processors, and the manufactured stress buffer. |

Applied Create normally allows early shafts, cogwheels, gearboxes, cranks, and
bearings to attune an ME P2P tunnel to stress. The owned
`industrial_appliedcreate_kinetic_network.js` tag rule clears that list and
makes the finished `appliedcreate:me_gearbox` the sole attunement key. This
means a player must build the remote-kinetic gateway before sending rotational
power through an ME P2P tunnel.

The attunement rule is not a recipe, so KubeJS Gen cannot represent it as a
recipe card. It is intentionally the one part of this slice kept in a small,
focused server-side tag script. The actual three Applied Create construction
recipes remain visible in KubeJS Gen.

`validate_stock_recipe_restoration.py` treats this filename as an exact
non-recipe policy, not as a general mutation allowlist. It requires one item
tag event, one clear, and one addition of `appliedcreate:me_gearbox`; any
recipe event, second tag addition, cheap attunement key, or unknown script
using the same mutation syntax remains a validation error.

## Extended digital manufacturing

| Output | Manufacturing contract |
|---|---|
| `extendedae:machine_frame` | A 5x5 Entro/TFMG steel chassis with quartz glass, smart cable, advanced control logic, and advanced stress processors. Both stock mirrored 3x3 frame recipes are removed. |
| `extendedae:crystal_assembler` | A 5x5 batch-processing machine built from the new frame, Create mechanical arms, AE terminals and tanks, Engineering Processors, TFMG boards, and advanced stress logic. |
| `advanced_ae:reaction_chamber` | A 5x5 cross-mod chamber that combines a Mekanism Pressurized Reaction Chamber, AE condensers/vibration chambers, ExtendedAE frames, and TFMG heavy casing. |
| `megacells:cell_component_1m` | A three-loop Weathered Iron Sequenced Assembly. The starting 256k component receives three additional 256k matrices, three accumulation processors, and three vibrant-glass layers, physically expressing its 1M capacity. |

The two Sequenced Assemblies use unique, unobtainable transitional items owned
by Industrial Colonies. Partially assembled stacks therefore cannot enter an
unrelated sequence or become a shortcut.

## Progression placement

- **P2P Tunneling Technology:** the three Applied Create remote-kinetic parts.
- **Enhanced ME System Upgrade:** the ExtendedAE frame and Crystal Assembler.
- **Overclocked Processors:** the AdvancedAE Reaction Chamber and first 1M
  MEGA cell component.

These labels document placement only. Physical ingredient dependencies remain
the authoritative progression enforcement.

## Regression contract

Run:

```powershell
python tools/validate_late_digital_gateways.py
python -m unittest tools/test_late_digital_gateways.py
```

The validator checks exact stock-recipe retirement, compiled KubeJS Gen parity,
5x5 grid size and ingredient diversity, sequence loop counts and exact machines,
node assignment, transitional item resources, and the restricted P2P attunement
tag.
