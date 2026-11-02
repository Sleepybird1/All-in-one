# TFMG Fluid and Chemical Infrastructure Audit

Status: **IMPLEMENTED IN THE AUTHORITATIVE SEED.** No shared generated card,
deploy, quest, Draw.io, or live-instance file was changed by this batch.

The installed `tfmg-1.2.0.jar` exposes 28 in-scope functional outputs through
33 stock recipe IDs. The bounded repair now takes source ownership of 12
meaningful infrastructure outputs, removes their 15 exact stock recipe IDs,
and leaves 16 equivalent material or aesthetic variants stock. The 12 recipes
compile as exact-machine KJSGen compacting cards across three reachable
manufacturing environments: three native Mechanical Press cards, eight Brass
precision-pressure cards, and one Copper electrical card.

The machine-readable source of truth is `TFMG_FLUID_INFRASTRUCTURE_AUDIT.plan.json`. The focused validator rechecks the installed JAR/catalog, runtime resources, current automatic owners, assignments, DAG, and temporary KJSGen compilation.

## Go/no-go result

**IMPLEMENTED — GO_WITH_TWELVE_CONTRACT_CANONICAL_REPAIR.** The batch has no
steel-before-steel or machine-phase bootstrap cycle:

- The presteel capability is exactly cast-iron pipe, cast-iron tank, and cast-iron mechanical pump.
- Those three recipes consume cast iron, a barrel or Create mechanisms, and
  the Mechanical Press already owned in Mechanical Foundations. They consume
  no steel, heavy plate, heavy machinery casing, or aluminum.
- The project block-tag extension keeps `tfmg:cast_iron_pipe` valid in TFMG's industrial-pipe multiblock tag. This lets the existing Pumpjack recipe remain constructible before finished steel.
- Steel pipe is directly formed from steel stock after first steel. It does not convert cast-iron pipe into steel.
- Aluminum pipe is directly formed from aluminum stock after aluminum processing. It does not convert an earlier pipe material into aluminum.
- Every same-batch dependency points to an earlier contract, and the electrical
  pump is a later-phase upgrade from the already formed steel mechanical pump.
- The Steel-phase fireproof vat uses `create:precision_mechanism`, not the later
  `tfmg:circuit_board`; this removes the original backward edge into Electrical
  Manufacturing.

## What the installed blocks actually do

The installed bytecode does **not** define a flow-rate or capability ladder for the five colored pipe families. `TFMGPipes$PipeMaterial` stores only a material name, and the registrations reuse the same block/entity implementations:

| Family | Installed variants | Installed behavior | Audit treatment |
|---|---|---|---|
| General pipe | brass, cast iron, steel, aluminum, plastic | All extend Create `FluidPipeBlock` | Gate cast iron, steel, and aluminum where they are real construction stock; retain brass/plastic as alternatives |
| Mechanical pump | brass, cast iron, steel, aluminum, plastic | All reuse TFMG/Create `PumpBlock` behavior | Gate cast iron and steel; retain brass/aluminum/plastic |
| Smart fluid pipe | brass, cast iron, steel, aluminum, plastic | All reuse Create smart-pipe filtering behavior | Retain all five; no installed capability difference justifies five progression tiers |
| Fluid valve | brass, cast iron, steel, aluminum, plastic | All reuse Create valve behavior | Retain all five; no installed capability difference justifies five progression tiers |
| Fluid tank | cast iron, steel, aluminum | Cast iron/aluminum share the TFMG/Create tank entity; steel has a separate three-wide implementation using Create-config capacity | Gate cast iron and steel as construction stock; retain aluminum |
| Chemical vat | cast iron, steel, fireproof | Recipe-level vat-type restrictions establish real capability tiers | Gate all three |
| Electric pump | one block | Distinct electrical Create-pump entity with TFMG electrical state and 100-ohm resistance | Gate as an electrical upgrade |
| Industrial pipe | one block | Structural distillation/Pumpjack column block, not a general `FluidPipeBlock` | Gate as refinery construction stock |

The vat capability ladder is genuine:

- `tfmg:cast_iron_chemical_vat` can run recipes without `allowed_vat_types`, including installed neon separation and circuit-board etching.
- `tfmg:steel_chemical_vat` is explicitly accepted by the installed aluminum, concrete, naphtha cracking, plastic, rubber, and sulfuric-acid recipes; several require heat.
- `tfmg:fireproof_chemical_vat` is accepted by those processes and is uniquely required by the installed nine-block arc-furnace steel recipe.

The validator locks the hashes and relevant fields of all ten installed vat recipes, twelve functional classes, the installed industrial-pipe tag, and the project tag extension.

## Proposed source-owned contracts

Repeated entries below are intentional physical slots; the source plan never
uses unsupported counted-tag strings. Machine routing follows the casing
philosophy while remaining phase-reachable. Railway, Industrial Iron, and
Weathered Iron presses begin in Electrical, Mekanized, and High-Energy phases,
so none may be pulled backward into the Steel-phase pressure bootstrap.

| Order | Output / stock count | Exact machine | Node / phase | Physical inputs, in slot order | Exact stock recipe IDs removed |
|---:|---|---|---|---|---|
| 10 | `4x tfmg:cast_iron_pipe` | `create:mechanical_press` | The Steel Age / Steel & Petroleum | cast-iron plate, cast-iron ingot, cast-iron plate | `tfmg:crafting/materials/cast_iron_pipe`; `tfmg:crafting/materials/cast_iron_pipe_vertical` |
| 20 | `tfmg:cast_iron_fluid_tank` | `create:mechanical_press` | The Steel Age / Steel & Petroleum | barrel, cast-iron plate, cast-iron plate, cast-iron pipe | `tfmg:crafting/materials/cast_iron_fluid_tank` |
| 30 | `tfmg:cast_iron_mechanical_pump` | `create:mechanical_press` | The Steel Age / Steel & Petroleum | cast-iron pipe, Create cogwheel, Create precision mechanism, cast-iron plate | `tfmg:crafting/materials/cast_iron_mechanical_pump` |
| 40 | `tfmg:cast_iron_chemical_vat` | `createcasing:brass_press` | Chemical Processing / Steel & Petroleum | cast-iron tank, two cast-iron pipes, four cast-iron plates, two lead plates | `tfmg:crafting/materials/cast_iron_chemical_vat` |
| 50 | `4x tfmg:steel_pipe` | `createcasing:brass_press` | Chemical Processing / Steel & Petroleum | steel plate, steel ingot, steel plate | `tfmg:crafting/materials/steel_pipe`; `tfmg:crafting/materials/steel_pipe_vertical` |
| 60 | `2x tfmg:steel_fluid_tank` | `createcasing:brass_press` | Chemical Processing / Steel & Petroleum | barrel, two TFMG heavy plates, steel pipe | `tfmg:crafting/materials/steel_fluid_tank` |
| 70 | `tfmg:steel_mechanical_pump` | `createcasing:brass_press` | Chemical Processing / Steel & Petroleum | steel pipe, Create cogwheel, TFMG steel mechanism, steel plate | `tfmg:crafting/materials/steel_mechanical_pump` |
| 80 | `2x tfmg:steel_chemical_vat` | `createcasing:brass_press` | Chemical Processing / Steel & Petroleum | steel tank, two steel pipes, four TFMG heavy plates, two nickel plates | `tfmg:crafting/materials/steel_chemical_vat` |
| 90 | `8x tfmg:industrial_pipe` | `createcasing:brass_press` | Diesel Processing / Steel & Petroleum | two steel pipes, two TFMG heavy plates, two steel ingots, TFMG steel mechanism | `tfmg:industrial_pipe_from_ingots_steel_stonecutting` |
| 100 | `tfmg:fireproof_chemical_vat` | `createcasing:brass_press` | Advanced Alloy Mixing / Steel & Petroleum | steel vat, steel pipe, four TFMG fireproof bricks, TFMG heavy machinery casing, Create precision mechanism, TFMG rubber sheet | `tfmg:crafting/materials/fireproof_chemical_vat` |
| 110 | `4x tfmg:aluminum_pipe` | `createcasing:brass_press` | Heavy Diesel Engines / Steel & Petroleum | aluminum plate, aluminum ingot, aluminum plate | `tfmg:crafting/materials/aluminum_pipe`; `tfmg:crafting/materials/aluminum_pipe_vertical` |
| 120 | `tfmg:electric_pump` | `createcasing:copper_press` | Advanced Electronics Manufacturing / Electrical Manufacturing | steel mechanical pump, two TFMG electromagnetic coils, two TFMG magnets, TFMG circuit board, TFMG capacitor, copper wire, TFMG steel mechanism | `tfmg:crafting/materials/electric_pump` |

The three material-forming pipe recipes deliberately use their own material stock. The tank, pump, vat, industrial-pipe, and electric-pump recipes then consume the earlier same-family component where one is meaningful.

## Retained stock variants

These 16 outputs remain craftable by their installed recipes. They are functional, not disabled, but the installed runtime does not prove a performance difference worth fabricating a progression tier.

| Retained output | Exact installed source recipe ID(s) |
|---|---|
| `tfmg:brass_pipe` | `tfmg:crafting/materials/brass_pipe`; `tfmg:crafting/materials/brass_pipe_vertical` |
| `tfmg:brass_mechanical_pump` | `tfmg:crafting/materials/brass_mechanical_pump` |
| `tfmg:brass_smart_fluid_pipe` | `tfmg:crafting/materials/brass_smart_fluid_pipe` |
| `tfmg:brass_fluid_valve` | `tfmg:crafting/materials/brass_fluid_valve` |
| `tfmg:cast_iron_smart_fluid_pipe` | `tfmg:crafting/materials/cast_iron_smart_fluid_pipe` |
| `tfmg:cast_iron_fluid_valve` | `tfmg:crafting/materials/cast_iron_fluid_valve` |
| `tfmg:steel_smart_fluid_pipe` | `tfmg:crafting/materials/steel_smart_fluid_pipe` |
| `tfmg:steel_fluid_valve` | `tfmg:crafting/materials/steel_fluid_valve` |
| `tfmg:aluminum_fluid_tank` | `tfmg:crafting/materials/aluminum_fluid_tank` |
| `tfmg:aluminum_mechanical_pump` | `tfmg:crafting/materials/aluminum_mechanical_pump` |
| `tfmg:aluminum_smart_fluid_pipe` | `tfmg:crafting/materials/aluminum_smart_fluid_pipe` |
| `tfmg:aluminum_fluid_valve` | `tfmg:crafting/materials/aluminum_fluid_valve` |
| `tfmg:plastic_pipe` | `tfmg:crafting/materials/plastic_pipe`; `tfmg:crafting/materials/plastic_pipe_vertical` |
| `tfmg:plastic_mechanical_pump` | `tfmg:crafting/materials/plastic_mechanical_pump` |
| `tfmg:plastic_smart_fluid_pipe` | `tfmg:crafting/materials/plastic_smart_fluid_pipe` |
| `tfmg:plastic_fluid_valve` | `tfmg:crafting/materials/plastic_fluid_valve` |

No in-scope output is disabled or deferred.

## Implemented ownership and safe migration

Before this batch, the generated managed manifest had five automatic owners:

| Output | Retired automatic ID | Former type |
|---|---|---|
| `tfmg:cast_iron_pipe` | `industrial_colonies:auto/tfmg/cast_iron_pipe` | mechanical crafting |
| `tfmg:cast_iron_fluid_tank` | `industrial_colonies:auto/tfmg/cast_iron_fluid_tank` | mechanical crafting |
| `tfmg:cast_iron_mechanical_pump` | `industrial_colonies:auto/tfmg/cast_iron_mechanical_pump` | mechanical crafting |
| `tfmg:cast_iron_chemical_vat` | `industrial_colonies:auto/tfmg/cast_iron_chemical_vat` | mechanical crafting |
| `tfmg:steel_chemical_vat` | `industrial_colonies:auto/tfmg/steel_chemical_vat` | mechanical crafting |

The authoritative seed now has exactly one explicit source owner for each of the 12 outputs. A fresh isolated generation confirms that all five automatic owners are absent and that no duplicate managed owners remain. Existing user KJSGen files were not rewritten.

## Applied assignment additions

The currently assigned cast-iron pipe/tank/pump remain at `CR01 — The Steel Age`; the cast-iron and steel vats remain at `CR01 — Chemical Processing`.

The implementation appends exactly these seven unlock additions:

| Node | Add |
|---|---|
| `CR01 — Chemical Processing` | `tfmg:steel_pipe`, `tfmg:steel_fluid_tank`, `tfmg:steel_mechanical_pump` |
| `CR01 — Advanced Electronics Manufacturing` | `tfmg:electric_pump` |
| `CR01 — Diesel Processing` | `tfmg:industrial_pipe` |
| `CR01 — Advanced Alloy Mixing` | `tfmg:fireproof_chemical_vat` |
| `CR01 — Heavy Diesel Engines` | `tfmg:aluminum_pipe` |

The additions are applied without changing the order or content of the pre-existing assignment prefixes.

## Existing consumers protected by the proposal

The authoritative seed already uses these components in five later machines:

- `industrial_colonies:machine/oil_processing/pumpjack_base` consumes the cast-iron pipe, tank, and mechanical pump.
- `industrial_colonies:petroleum/steel_distillation_controller` consumes industrial pipe and the steel tank.
- `industrial_colonies:petroleum/steel_distillation_output` consumes industrial pipe, steel pipe, and the steel tank.
- `industrial_colonies:engines/engine_turbocharger` consumes aluminum and steel pipe.
- `industrial_colonies:engines/turbine_engine` consumes aluminum pipe.

The focused validator locks these consumer relationships so a later seed change cannot silently invalidate the audit.

## Validation

Run from the project root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/validate_tfmg_fluid_infrastructure_audit.py
& 'C:\Users\GodPC\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/test_validate_tfmg_fluid_infrastructure_audit.py -v
```

Passing proof after seed implementation:

- 28 functional outputs and all 33 stock recipes reconciled against the installed catalog/JAR.
- 12 proposed outputs map one-to-one to contracts; all 15 and only those exact stock IDs are removed.
- All 16 retained outputs and their 18 source recipes remain outside the removal set.
- All 12 contracts compile through the real managed-recipe generator to `kjsgen:create_compacting`: three pre-steel bootstrap recipes use the native Create press, eight pressure/refinery recipes use the Brass Press, and the electric pump uses the Copper Press. The compiler emits the exact 15 removal cards.
- Five automatic owners are retired, 12 source owners are unique, and all seven assignment additions are locked.
- Fresh isolated output contains 353 managed recipes (172 automatic), 421 compiled cards, and 739 exact removals.
- Managed progression validation resolves 922 inferred item edges with zero warnings; physical, Early Manufacturing, Steelworks, petroleum, transmission, Extreme Transmission, storage, and Induction regressions all pass.
- Twenty-one focused mutation tests cover source drift, duplicate ownership, partition leakage, removal broadening, batch-count loss, counted tags, machine drift, dependency order, phase reachability, predecessor use, steel bootstrap, assignment ordering, vat capability, project tag behavior, and compiled-card routing.
