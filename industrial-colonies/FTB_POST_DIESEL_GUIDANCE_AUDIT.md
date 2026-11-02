# Post-Diesel FTB Quests guidance audit

## Outcome

The physical progression after the first TFMG diesel engine now has a native
guidance campaign. Electrical, AE2, Mekanism, high-energy infrastructure, and
nuclear commissioning continue the early campaign without becoming recipe or
research gates.

The implemented follow-up is **five new non-gating chapters with 40 quests and
105 item-observation tasks**. This brings the native campaign from 3 chapters,
45 quests, and 76 tasks to 8 chapters, 85 quests, and 181 tasks. The existing
Factory Foundations, optional Dungeon Exploration, and three Industrial
Endgame quests remain unchanged.

The machine-readable plan is
`FTB_POST_DIESEL_GUIDANCE_AUDIT.plan.json`; its status is `implemented` and the
guidance source references it as a deterministic chapter extension. Recipe
sources, assignments, the live pack, and the old Draw.io/MineColonies tree were
not changed by this implementation.

## Implemented chapters

| Order | Chapter | Quests | Tasks | Physical story |
|---:|---|---:|---:|---|
| -80 | Electrical Manufacturing | 7 | 17 | TFMG generator/motor, electronics workshop, local cabling, circuit production, chemical storage, and the first Electro Energetics grid |
| -70 | Digital Logistics and AE2 | 6 | 14 | Inscription, logic/stress processors, starter ME power/storage, ComputerCraft control, and first autocrafting |
| -60 | Mekanized Industry | 8 | 23 | Metallurgic infusion, modular chassis, a drain-before-crafting Basic Factory lesson, base processing, all five Basic transmitters, reinforced controls, HDPE, and pattern automation |
| -50 | High-Energy Grid | 10 | 31 | Elite/ultimate controls, controller-class ME, kinetic P2P, ExtendedAE/MEGA manufacturing, analog and extreme grid work, a representative physical transmitter upgrade, cube storage, induction, and world loading |
| -40 | Nuclear Engineering | 9 | 20 | Yellorium-to-uranium feedstock, Refined Radiance, isotope fuel, reactor construction/instrumentation, Cyanite proof, actinides, reprocessing, and reinforced reactors |

The layout is intentionally branched. Electrical electronics and local power
rejoin at the utility grid. Digital networking and Mekanism controls develop in
parallel and converge at pattern automation and high-energy logic. Analog
high-voltage transmission remains independent of ME networking until both meet
at the Energy Cube/Induction storage path. Nuclear fuel, containment, and
instrumentation converge at first criticality rather than becoming one long
checklist.

## Evidence boundary

Every proposed objective resolves to an installed item and one of five explicit
source classes:

- a current `managed_recipe_overhaul.json` recipe;
- an `implemented_in_seed` reviewed contract from the Power Backbone,
  High-Voltage, Extreme Transmission, Energy Cube, or Induction audits;
- an exact controlled output in `physical_recipe_tiers.json`, used for the
  user-owned Metallurgic Infuser and script-owned Yellorium/uranium/fuel
  routes;
- the pinned Mekanism Factory restoration contract for the first Basic
  Enriching Factory, including its future deterministic managed recipe ID; or
- an installed machine recipe plus an audited node assignment, used only for
  HDPE and Plutonium Pellets.

`bigreactors:cyanite_ingot` is the one runtime-production observation. The
assignment for **First Criticality** already names Cyanite as tangible evidence
of reactor operation. The quest must still say that FTB Quests is observing the
byproduct, not detecting a live multiblock.

Tasks never consume the observed stacks. There are no rewards, commands,
stages, recipe locks, research locks, or checkbox-only objectives. Machine and
multiblock commissioning remains descriptive guidance; physical recipes and
machine behavior remain authoritative.

The **First Basic Factory** quest is explicit about Mekanism state transfer:
drain and empty the Enrichment Chamber first, then use that empty predecessor
and the Basic Tier Installer as consumed components in the 5x5 Mechanical
Crafting recipe. Runtime right-click installer upgrades are disabled for the
managed Factory and Energy Cube families, so the installer is manufacturing
stock rather than a shortcut tool.

## Objectives that must wait

The plan deliberately excludes these unstable or unsupported objectives:

1. **Allthemodium pairwise alloy milestones.** The three alloy ingots are
   currently owned by dynamic superheated-mixing IDs. The Industrial Star may
   continue consuming them, but a dedicated currency quest should wait for
   stable explicit recipe IDs.
2. **Advanced Electronics convergence.** `CR01 — Advanced Electronics` states
   that no registered cross-mod controller item exists. Do not invent a quest
   objective for it.
3. **Typed P2P tunnels.** Item, fluid, FE, and chemical variants have no stable
   static producer IDs in the managed report. The reviewed campaign uses the
   stable ME P2P tunnel and manufactured Applied Create ME Gearbox instead.
4. **Chemical-only observations.** Fissile Fuel, Nuclear Waste, and Plutonium
   are chemical registries, while this campaign intentionally supports item
   tasks only. Hardware and produced pellets provide tangible milestones until
   a native chemical-task design is reviewed.

## Endgame handoff

The endgame itself is not missing. Preserve these exact objectives and their
existing chain:

```text
Black Hole -> Industrial Reserve Core -> Industrial Star
```

The final Nuclear quest should point the player to `Industrial Endgame` in its
text, but must not duplicate those items or alter the three existing quest IDs
or dependencies. The Reserve Core recipe already forces Diesel, TFMG Sulfuric
Acid, HDPE, and Plutonium throughput; the Star recipe remains the physical
capstone and future space-expansion handoff.

## Generator implementation

`generate_ftbquests_native.py` keeps the existing hand-authored Factory
Foundations source and expands the five reviewed plan chapters at validation
time. It resolves their local and cross-chapter dependencies as one global DAG,
hashes both source files into the native manifest, and emits stable IDs without
changing any Foundation or Industrial Endgame IDs. `chapter_groups.snbt`
remains byte-for-byte unchanged.

## Validation

Run from the project root:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/validate_ftb_post_diesel_guidance_audit.py --self-test
```

The validator checks current campaign preservation, the 40-quest global DAG,
branch/convergence structure, exact counts, all 105 runtime item observations, every
managed/audited/physical/installed source contract, the four deferral classes,
and five focused mutations covering rewards, cycles, unknown items, deferred
objectives, and endgame-chain drift.
