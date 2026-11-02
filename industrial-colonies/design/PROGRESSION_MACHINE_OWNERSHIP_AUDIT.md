# Initial ownership/progression comparison — September 10, 2026

Historical pre-change snapshot. The user subsequently authorized implementation through the pre-semiconductor stage; that work is installed and documented in `PRE_SEMICONDUCTOR_IMPLEMENTATION.md`. Findings below describe the original comparison, not the current live recipe state.

Scope: recorded the user's design instructions and inspected the current live KJSGen default project read-only, alongside local processing source. No live recipes, configurations, JARs or saves changed. This is an initial conflict inventory, not certification of the effective loaded recipe set.

The snapshot contains 672 recipe cards, including 258 Mechanical Crafter cards. All 258 have explicit dimensions; none exceeds seven rows or columns. `machine_ownership_snapshot.json` records the source hash and selected cards. Reproduce with `tools/audit-machine-ownership.ps1`.

| Requirement | Observed evidence | Follow-through |
|---|---|---|
| Disable Mekanism Crusher | Current project defines `industrial_colonies:mekanism_pre_nuclear/crusher`, producing `mekanism:crusher` through Industrial Iron sequenced assembly. | Retire the competing producer and processing routes. Audit native recipes, factory variants, installers, conversions and existing machines before claiming complete disablement. |
| Foundry must not alloy | `tools/material_processing/policy.js` removes every `modernfoundry:alloy` recipe, including the normally excluded exotic namespace. | Preserve this enforcement. Verify effective recipes after any future export. |
| Weathered is first structural/TFMG industry | All six selected Weathered machine cards use sequenced final assembly. The deployer includes a circuit board, transistor, plastic and electric motor; its comment still says Electrical Manufacturing. | Redesign around structural parts and crafter assembly; check first-machine and first-TFMG acquisition. |
| Copper owns early electronics | `industrial_colonies:electronics/circuit_board` uses Copper Deployers for four assembly loops. | Preserve this compatible assignment while reviewing the rest of the electronics chain. |
| Industrial Iron needs Ti/W and advanced components | The selected Industrial Iron fan consumes Titanium, Tungsten, high-purity Silicon, advanced control circuit and calculation processor. | Preserve these material/capability gates while changing final assembly to Mechanical Crafters. |
| Chromium washing requires Industrial Iron Fan | The processing catalog uses `industrial_colonies:industrial_iron_splashing` on alkaline-roasted chromite. | Preserve the machine-bound recipe and wrong-tier rejection. Existing runtime implementation includes a fan rejection-cache repair. |
| Finished high-tier machines use Mechanical Crafters | Weathered and Industrial Iron machine cards include final sequenced assembly. | Components may remain sequenced; final machine recipes need conversion and alternate-route retirement. |
| Hard 7×7 maximum | All 258 current project Mechanical Crafter cards fit. | Retain a dimension check during future generation; use subassemblies to manage complexity. |

## Migration hazards and remaining audit scope

- The first Weathered Press/Deployer cannot depend solely on parts that require those same machines. Establish a reachable prior-tier construction path before moving component recipes.
- Weathered's move to the start of TFMG requires checking circuit boards, plastic, motors, vats and steel hardware together. Do not fix the machine recipe while leaving its inputs gated later.
- Keep pre-Industrial Titanium/Tungsten reagent infrastructure reachable. Existing material-bootstrap corrections intentionally moved selected chemical machines earlier for this reason.
- Historical `MEKANISM_FACTORY_RESTORATION_AUDIT.md` explicitly endorses Crushing and other factory lines. That design is superseded where it conflicts with these notes. The selected current project search did not find a crushing-factory card; this does not establish that native recipes or upgrade paths are disabled.
- The previously agreed low-yield Create Millstone PGM bootstrap is a specific material-processing route. Review it explicitly against the Crushing Wheels ownership language; do not silently remove the first Osmium source.
- Basic Create has earlier custom recipes and preservation rules. Audit each against the new preference for defaults before restoring or redesigning anything.
- Inspect competing melting/casting, washing, all alloy types, generic ore multiplication and nuclear processing in the effective runtime set. The existing material policy is broader than individual examples but is not a complete machine-disable system.
- The material system includes TFMG reagent operations and IE arc-furnace steps. “Primarily Mekanism” does not by itself authorize deleting every existing specialized chemistry route.
- Review electronics ingredients and Brass/Train power assignments separately. No full semiconductor redesign or future exotic-tier work is authorized by these notes.
- The historical managed seed under `progression/` is absent from this copied workspace. Before implementation, recover the exact current authoring source or establish a synchronized source from verified live cards. Do not regenerate the pack from stale historical tools or edit only an exported script that will be overwritten.

## Next implementation order

1. Establish synchronized recipe source and effective runtime inventory.
2. Retire conflicting machine families and their hidden acquisition/processing paths, preserving explicitly approved specialized routes.
3. Resolve Weathered/TFMG bootstrap, then manufacture its structural components and final crafter recipes.
4. Review Copper/Brass electronics and Brass/Train electrical manufacturing; convert final machines to crafter assembly.
5. Convert Industrial Iron final assembly while preserving reachable Ti/W chemistry and harsh-process capability gates.
6. Validate dimensions, dependency reachability, competing recipes, machine-tier execution and runtime reload; install the verified result with a backup.

The policy-recording/audit task is complete. The implementation migration above remains pending; the installed pack is still 0.5.2.
