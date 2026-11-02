# Mekanism Physical Progression

Mekanism progression is carried by manufactured components and Create Encased
recipe families. It does not require a MineColonies research stage to remain in
order.

## Construction families

| Encased family | Canonical Mekanism outputs |
| --- | --- |
| Brass | Energy Tablet |
| Railway | Metallurgic Infuser; Basic Control Circuit |
| Industrial Iron | Steel Casing; Basic Tier Installer; Enrichment Chamber; Combiner; Osmium Compressor; Advanced Control Circuit; Basic Energy Cube; Basic Induction Cell; Basic Induction Provider |
| Weathered Iron | Electrolytic Separator; Chemical Oxidizer; Chemical Infuser; Rotary Condensentrator; Pressurized Reaction Chamber; Purification Chamber; Chemical Injection Chamber; Chemical Dissolution Chamber; Chemical Washer; Chemical Crystallizer; Advanced Tier Installer; Elite Control Circuit; Advanced and Elite Energy Cubes; Advanced and Elite Induction Cells; Advanced and Elite Induction Providers |
| Refined Radiance | Isotopic Centrifuge; Elite and Ultimate Tier Installers; Ultimate Control Circuit; Ultimate Energy Cube; Ultimate Induction Cell; Ultimate Induction Provider; Induction Casing; Induction Port |

Every Sequenced Assembly runs at least two loops. Every Mechanical Crafting
recipe is a complete 5x5 pattern. Each recipe consumes the casing material or
component corresponding to its Encased family, as well as TFMG electronics,
AE2 processors, and earlier Mekanism components where appropriate.

## Factory rule

All 36 stock `mekanism:mek_data` Factory recipes are removed. The four
Smelting Factory recipes stay retired because scalable Create fan
smelting/blasting is the intended heat route. The other 32 outputs—Combining,
Compressing, Crushing, Enriching, Infusing, Injecting, Purifying, and Sawing at
Basic, Advanced, Elite, and Ultimate—use source-owned, filled 5x5 Create
Mechanical Crafting recipes.

These are **direct-empty-5x5 upgrades**. Each recipe consumes its corresponding
single-block machine at Basic or the immediate same-process prior Factory at a
later tier, plus the matching Tier Installer, alloy, control circuit, precision
component, process anchor, TFMG heavy construction, Steel Casings, and a Steel
Mechanism. Mechanical Crafting cannot copy Mekanism attachments or block-entity
state, so players must drain and empty the predecessor first. The produced
Factory begins with fresh inventories, tanks, energy, upgrades, side settings,
ownership, and security state.

Tier Installers cannot be an alternate acquisition path. The project-owned
`mekanism:blacklist/installer_upgradeable` block tag contains exactly 49
values with `replace: false`: nine base Factory machines, all 36 tier/process
Factory blocks, and the four Energy Cubes. This closes all hard-recipe and
Smelting-retirement bypasses. No tiered transmitter is included: the installed
Universal Cable, Mechanical Pipe, Pressurized Tube, Logistical Transporter,
and Thermodynamic Conductor builders attach `AttributeTier` but not
`AttributeUpgradeable`, so `ItemTierInstaller` cannot act on them.

The active runtime upgrade sources among those 49 values are the nine base
machines, the 27 Basic/Advanced/Elite Factories, and the three
Basic/Advanced/Elite Energy Cubes. Ultimate Factories are terminal and the
Ultimate Energy Cube has no next-block supplier; the ten terminal values remain
named as narrow owned-family guards.

## Nuclear boundary

This slice does not add or alter any uranium or Yellorium material recipe.
Yellorium continues to flow only forward into the dedicated Mekanism enrichment
and reactor-fuel chain.

## Validation

Run:

```powershell
python tools/validate_mekanism_physical_progression.py --instance "<instance>"
```

The validator checks unique active producers, exact canonical recipe IDs,
Encased family and casing agreement, sequence loop counts, exact 5x5 pattern
shape, direct factory bypasses, and nuclear-boundary isolation. The dedicated
Factory contract is checked separately with:

```powershell
python tools/validate_mekanism_factory_restoration_audit.py
python tools/test_validate_mekanism_factory_restoration_audit.py
```

That audit pins all 36 installed source payloads and the reviewed installer
runtime classes, compiles the 32 proposed/managed cards in temporary storage,
checks the eight acyclic tier ladders and assignment phases, retains exactly
four Smelting retirements, and validates the exact live 49-block blacklist.
