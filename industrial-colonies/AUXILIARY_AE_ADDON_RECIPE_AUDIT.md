# Auxiliary AE Addon Recipe Audit

This audit covers the installed NeoForge 1.21.1 builds of Applied
Mekanistics (`appmek`), AE2WTLib (`ae2wtlib`), ME Requester
(`merequester`), AE2 Crafting Tree (`ae2ct`), Applied Schematicannon, and
Polymorphic Energistics (`polyeng`). It deliberately excludes core AE2,
MEGA Cells, ExtendedAE, AdvancedAE, and Applied Create because those families
have separate recipe-design owners.

## Decision

No new managed recipe transform is warranted for this slice.

The only proven Applied Mekanistics bypasses are its arbitrary cross-tier
`ae2:storage_cell_upgrade` recipes. Those exact 20 recipe IDs are already in
`additional_removals`. Adding a second module to claim them would duplicate an
existing correction. The remaining stock recipes are either meaningful
assemblies whose cost already comes from managed upstream components, lossless
disassembly routes, or custom terminal conversions that must retain their
component-aware serializers.

This negative result is intentional: it follows the rule that an unchanged
stock recipe must not be copied into the managed recipe set.

## Applied Mekanistics

- `appmek:chemical_cell_housing` is already manufactured by
  `industrial_colonies:digital_core/chemical_cell_housing` in the Copper
  electronics environment. It uses quartz glass, TFMG plastic, osmium,
  TFMG copper wire, and a TFMG circuit board.
- `appmek:chemical_storage_cell_{1k,4k,16k,64k,256k}` combine the managed
  chemical housing with the corresponding AE2 cell component. These are
  appropriate lossless final-assembly conversions and inherit the difficulty
  of both inputs.
- `appmek:portable_chemical_cell_{1k,4k,16k,64k,256k}` additionally require an
  AE2 chest and energy cell. They are coherent portable-device assemblies, not
  shortcuts.
- `appmek:cell_upgrade/*` recipes are disassembly/salvage serializers. They
  return the component and housing (plus the chest and energy cell for portable
  cells), so preserving them does not create material or skip a tier.
- All 20 `appmek:upgrade/*` cross-tier shortcuts are already retired by the
  seed. No duplicate removal owner was added here.
- `appmek:chemical_p2p_tunnel` intentionally has no crafting JSON. It is the
  chemical attunement of AE2's base P2P tunnel; the installed attunement tag
  accepts Mekanism chemical tanks. A synthetic crafting recipe would bypass
  AE2's P2P mechanic.

## AE2WTLib

- The two wireless pattern terminals require the corresponding wired terminal,
  an AE2 wireless receiver, and an AE2 dense energy cell. The wired pattern
  encoding terminal and dense cell are already managed factory outputs, so the
  stock wireless assemblies inherit the intended progression.
- `ae2wtlib:pattern_encoding/upgrade_wireless_pattern_encoding_terminal` is a
  legitimate late conversion from a wireless crafting terminal plus an
  engineering processor. The engineering processor is already High-Energy
  Grid production, so it cannot bypass the earlier Mekanized acquisition
  boundary.
- `ae2wtlib:magnet_card` consumes an advanced card, an annihilation plane, five
  iron blocks, a redstone block, and a lapis block. It is not a cheap bypass.
- `ae2wtlib:quantum_bridge_card` consumes three quantum rings, a quantum link,
  and an advanced card. It already inherits the quantum-infrastructure gate.
- `ae2wtlib:combine` and `ae2wtlib:upgrade` recipes for the universal terminal
  are custom component-aware conversions. Replacing them with generic shaped
  or sequenced recipes risks losing installed-terminal data and is outside a
  recipe-gap correction.

## ME Requester

- `merequester:requester` already requires an AE2 interface, two crafting
  accelerators, an engineering processor, iron, copper, and amethyst. The
  accelerators, interface, and engineering processor are managed factory
  outputs, making this a strong functional block recipe without additional
  filler.
- `merequester:requester_terminal` is the expected illuminated-panel and logic
  processor conversion of the requester block.
- `merequester:wireless/wireless_requester_terminal` requires the wired
  requester terminal, a wireless receiver, and a dense energy cell. Its
  `ae2wtlib:combine` and `ae2wtlib:upgrade` routes preserve terminal contents
  and should remain stock.

## Addons Without Craftable Content

- AE2 Crafting Tree is a client/UI integration and registers no items, blocks,
  or recipes.
- Applied Schematicannon is a Schematicannon mixin/integration. Its JAR contains
  no item/block models or recipe resources; the language file's example keys
  are placeholders rather than registered content.
- Polymorphic Energistics is an AE2 terminal GUI/mixin integration. It contains
  no item/block registry assets or recipe resources.

## Static Validation

- All concrete item and stock recipe IDs above were checked against
  `outputs/recipe-catalog-current/recipe_catalog.sqlite` and the installed JAR
  resources.
- The current recipe-design seed passes the full in-memory static audit: 712
  explicit recipes, 68 generated machine-family recipes, 780 unique managed
  outputs, no errors, and only the expected stale-catalog warning for custom
  `industrial_colonies` items.
- Since this audit adds no transform, there is no new mutation requiring an
  idempotence exception or main-driver integration.
