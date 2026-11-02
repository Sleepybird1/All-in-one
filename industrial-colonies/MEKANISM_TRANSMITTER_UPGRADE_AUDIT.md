# Mekanism transmitter-upgrade audit

## Decision

**IMPLEMENTED IN THE AUTHORITATIVE SEED after Extreme Power Transmission.**

The fifteen installed Advanced, Elite, and Ultimate transmitter recipes all
collapse eight prior-tier segments around one alloy. They preserve run length,
but they do not represent electrical, item, fluid, chemical, and heat networks
as different factory systems. Twelve non-Universal replacements are now
source-owned in `progression/managed_recipe_overhaul.seed.json`. The three
already-stable Universal Cable managed routes remain generator-owned. Together
they keep every output at eight and form five independent three-tier ladders.

The five existing Basic transmitter recipes remain authoritative and are not
removed or rewritten by this batch. Direct inspection verifies that each emits
eight segments and retires only its matching Basic stock ID.

## Manufacturing language

- Advanced upgrades run on `createcasing:industrial_iron_press` in Mekanized
  Industry. They consume eight Basic segments, Infused Alloy, Advanced control,
  and family-specific TFMG/Create infrastructure.
- Elite upgrades run on `createcasing:weathered_iron_press` in High-Energy Grid.
  They consume eight Advanced segments, Reinforced Alloy, Elite control, and a
  stronger version of the corresponding factory subsystem.
- Ultimate upgrades stay on the Weathered Iron press. Refined Radiance belongs
  to Nuclear Engineering and is explicitly excluded.

Every recipe emits exactly eight segments and consumes exactly eight of the
prior tier. There are no generic alloy-only cards and no cross-family upgrade
edges.

## Family identities

- Universal Cable uses TFMG wire, cable hubs, insulation, and ultimately the
  completed Electro Energetics SF6 breaker. This is the one category where the
  Extreme Transmission convergence is physically meaningful.
- Logistical Transporter uses chutes, tunnels, filters, stock sensing, and
  Create's factory-package network. It does not consume arbitrary power-grid
  hardware.
- Mechanical Pipe uses Create fluid components, then TFMG steel/industrial pipe
  and dedicated pumps.
- Pressurized Tube uses glass/rubber containment, then petroleum-made plastic
  pressure sections, valves, and smart monitoring pipe.
- Thermodynamic Conductor uses copper spreaders, aluminum/industrial channels,
  constantan junctions, and active fan cooling.

The three current managed Universal Cable IDs are retained without copying them
into the seed:

- `industrial_colonies:auto/mekanism/advanced_universal_cable`
- `industrial_colonies:auto/mekanism/elite_universal_cable`
- `industrial_colonies:auto/mekanism/ultimate_universal_cable`

That preserves KJSGen identity and keeps the reviewed Induction Matrix
dependency on the Ultimate ID valid. Their mechanical-crafting recipes and
one-to-one stock removals are asserted as preservation contracts; the twelve
other upgrades use the exact Encased compacting environments described above.

## Assignments and safety

The three Universal Cable outputs already occupy Reinforced Systems, Precision
Engineering, and High-Energy Distribution. Four non-Universal outputs were
appended, without reordering existing entries, to each of those same nodes in
`progression/machine_node_assignments.json`. This is metadata alignment, not a
reactivation of the discarded MineColonies research gate.

All fifteen stock recipes are verified directly in
`Mekanism-1.21.1-10.7.19.85.jar` as shaped recipes with output count eight.
Each route retires exactly one matching stock ID. Every source-owned recipe
uses installed ingredients, an exact Encased press, and an explicit dependency
chain; all fifteen reviewed contracts compile through the current KJSGen
generator and remain acyclic.

The isolated implementation build contains 346 managed recipes, including 177
automatic recipes, and compiles to 414 KJSGen cards with 730 exact removals.
Its managed graph has 890 inferred item edges and zero warnings. The build was
intentionally kept outside the shared generated artifacts.

This batch closes the reviewed recipe routes only. Mekanism's tier-installer
`AttributeUpgradeable` path is a separate non-recipe surface and is not claimed
closed here; its exact `installer_upgradeable` blacklist resource must be
integrated and validated independently.

Run `tools/validate_mekanism_transmitter_upgrade_audit.py` to repeat the JAR,
catalog, authoritative-Basic, seed/assignment parity, stable-Universal,
machine, family-semantic, KJSGen, predecessor, and mutation checks. The focused
unit suite is `tools/test_mekanism_transmitter_upgrade_audit.py`.
