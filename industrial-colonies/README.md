# Industrial Colonies

Industrial Colonies is a NeoForge 1.21.1 companion mod and KubeJS layer for
the **All in One** modpack. Its current job is to:

- compile the large factory progression from a reviewable design seed and the
  installed pack's actual recipes;
- replace stock construction paths by exact recipe ID, never by wiping a
  whole mod or output namespace;
- let KJSGen authors route a Create recipe to one exact compatible machine;
- retain the pack's explicit material, fuel, compatibility, and capstone
  policies;
- turn TFMG's unfinished reservoir bookkeeping into regional, genuinely
  finite oil fields that create prospecting and freight demand;
- make the Industrial Star the physical boundary for constructed orbital
  craft, canonical launch propellants, modular propulsion, and the canonical
  Ad Astra Moon/Mars/Venus/Mercury surface routes and canonical deep-space
  asteroid eligibility; and
- keep MineColonies research available for colony gameplay without using it
  to lock, hide, or authorize factory recipes.

The managed set now spans Create and Create Encased manufacturing, TFMG
electronics/heavy industry, AE2 and ComputerCraft logistics, Mekanism machine
tiers, power infrastructure, reactor construction, and late megaproject
components. Stock paths are removed by exact source ID only after a generated
replacement exists and passes schema, dependency, runtime-registry, and
installed-recipe validation. Unmanaged content remains on its stock baseline.
The oil-field contract and existing-world behavior are documented in
`REGIONAL_OIL_FIELDS.md`. The first post-Star orbital boundary, onboard flight
computer, launch-fluid ownership, exact stock deferrals, propulsion slice, and
single-owner Moon/Mars/Venus/Mercury destination bridge are documented in
`SPACE_ENTRY_BOUNDARY.md`. The first source-owned orbital pressure and habitat
equipment branch is documented in `ORBITAL_LIFE_SUPPORT_AUDIT.md`.
The source-owned navigation instruments, four-channel docking pair, and first
factory-scale station-material batches are documented in
`ORBITAL_DOCKYARD_STATION_AUDIT.md`.
Moon/Mars outpost utilities and the source-owned Venus/Calorite continuation
are documented in `PLANETARY_OUTPOST_COMMISSIONING_AUDIT.md` and
`VENUS_CALORITE_EXPEDITION_AUDIT.md`. The Mercury route, physical navigation
authority, repaired deep-space asteroid eligibility, and observation-only
freight handoff are documented in `MERCURY_ASTEROID_FREIGHT_AUDIT.md`.

## KJSGen machine-specific authoring

KJSGen presents one editor entry for each supported Create process, such as
**Create Pressing**. After opening that recipe type, choose the actual
compatible machine in the selector at the upper-left of the recipe canvas.

The selected machine is routing metadata, not an ingredient. It is not added
to the recipe inputs and is not consumed. An authored recipe is available
only in the exact selected block:

- selecting the normal Create Mechanical Press locks it to that press;
- selecting the Create Encased Copper Press locks it to the Copper Press; and
- selecting another supported encased press locks it to that exact variant.

Choosing a Copper Press therefore does not allow the normal Mechanical Press
or any other encased press to run the recipe. Native recipes supplied by
Create and other mods are not automatically restricted; this exact-machine
routing applies to recipes explicitly authored with the selector.

In JEI, a machine-bound recipe stays inside Create's normal process page. The
page renders the exact selected machine (for example, the Copper Press or
Copper Deployer) and includes a required-machine cue in the upper-left. A
native, unbound Create recipe continues to render Create's normal machine.
The JEI presentation is driven by the same runtime binding as execution, so it
does not merely relabel a recipe that another machine can still run.

Sequenced Assembly exposes an exact machine selector on every Pressing,
Deploying, Cutting, and Filling row. The exported inner operation uses the
selected hidden machine-bound recipe type, runtime lookup accepts it only while
that exact Press, Deployer, Saw, or Spout is processing the item, and JEI renders
the selected machine in that step. Clearing a selector safely returns that row
to the native Create machine; moving or deleting a row moves or deletes its
machine selection as well.

`src/main/resources/data/industrial_colonies/tier_recipe_environments.json`
is the machine compatibility catalog. It determines which machine items are
valid for each process, so the editor does not offer unrelated blocks.

The mod still registers the former 170 tier/family recipe IDs so recipes
created by earlier builds continue to load. Those IDs are hidden
backward-compatibility plumbing, not 170 separate KJSGen picker entries. New
recipes should start with the single process entry and its in-canvas machine
selector. Explicit base-machine routes use hidden `base_<process>` IDs; valid
encased selections route through the matching legacy-compatible ID.

## Manifest-managed recipes and retained policy

Project-owned scripts that formerly removed or replaced complete machine
families remain same-named no-ops unless a focused progression slice explicitly
reactivates them. Keeping those files overwrites stale live-pack copies without
silently reviving retired broad rewrites. The user's own
`kubejs/server_scripts/kjsgen_recipes.js` is not a project-owned deployment
file and must be preserved.

Recipes that need to remain editable in KJSGen's Project screen use the native
project fragment and conservative deployment merge described in
`KJSGEN_PROJECT_SYNC.md`. The merge preserves the live project's settings and
all unrelated recipe/removal UIDs; it does not try to reverse-parse exported
JavaScript.

Only focused, explicitly retained rules are allowed to alter the stock
baseline:

- TFMG diesel and gasoline remain the only petroleum fuels accepted by Create
  Diesel Generators engines. CDG's data-driven biodiesel, ethanol, and plant
  oil fuel types are overridden onto the intentionally empty
  `industrial_colonies:disabled_cdg_engine_fuels` fluid tag; their unrelated
  fluid tags and processing recipes are left intact for non-engine uses.
- Sulfur and sulfuric-acid production follow the retained controlled chemistry
  routes.
- Yellorium may feed forward into uranium processing, but uranium or finished
  reactor fuel may not be converted back into Yellorium.
- Allthemodium, Vibranium, Unobtainium, and their alloys are manufactured
  progression currencies; their ore, loot, standalone equipment ladder,
  Teleport Pad, and shortcut sources stay disabled.
- Confirmed convenience, chemistry, mobility, mining, and instant-logistics
  bypasses are retired by exact ID as documented in
  `PROGRESSION_BYPASS_RETIREMENT.md`; legitimate industrial alternatives are
  protected from accidental removal.
- Narrow Create Metallurgy and MEGA compatibility repairs remain enabled.
- The Black Hole, Industrial Reserve Core, and Industrial Star remain the
  three project-owned endgame supply-chain items.
- Because Mekanism Generators is intentionally absent, one exact TFMG-acid
  dissolution route converts spent Big Reactors Blutonium into Mekanism
  Nuclear Waste. The retained stock waste-to-Plutonium and
  Plutonium-to-Pellet recipes then make the Reserve Core and Star physically
  reachable without adding a second waste-source bypass.

The exact capstone inputs and production totals are documented in
`INDUSTRIAL_MEGAPROJECTS.md`. FTB Quests contains 70 non-gating factory quests
from the primitive start through nuclear engineering, 12 optional dungeon
expeditions, the unchanged three-item capstone chain, and ten post-Star
Orbital Engineering observations spanning flight authorization, propulsion,
habitat readiness, ground-side ship construction, navigation, docking, and
station-material commissioning. The Planetary Industry chapter then
observes Moon/Mars/Venus/Mercury landfall, Desh/Ostrum/Calorite and asteroid
freight, three physical metallurgy lines, outpost utilities, all three
navigation computers, the automated heat-resistant expedition suit, station
commissioning, gas-giant extraction, returned condensate, and the physical
warp-charge precursor. Its final observations cover lunar Moon Crystal
finishing, the Interstellar Navigation Computer, exact route-crystal signing,
the Warp Drive, a single-use charge, canonical Glacio landfall, and a retained
Glacio sample. The resulting book is 10 chapters, 124 quests, and 256
non-gating tasks. It does not mirror the former research tree
or authorize recipes.

## Progression authority and historical artifacts

The immutable Draw.io source, MineColonies generators, research costs, former
77-node export, and `progression/physical_recipe_tiers.json` are preserved as
historical design and migration material. They are not the authority for the
current stock-recipe/editor build and are excluded from the runtime where
applicable.

`tools/validate_physical_progression.py` has been modernized as the composite
acceptance check for the current recipe-authored progression. It first runs the
managed manifest/compiler/removal/DAG proof, then verifies the phase spine,
TFMG-first electronics, Create Encased machine routes, ComputerCraft reactor
instrumentation, canonical-material owners, inactive research gates, and the
non-gating quest guide. `tools/validate_physical_tier_migration.py` validates
the Copper-to-Refined-Radiance manufacturing-family chain and large-grid
machine construction. The older `tools/validate-tier-recipes.mjs` still
describes the retired 170-picker design and is not a current acceptance check.

## Validation and build

Use Java 21. The current source-level acceptance checks are:

```powershell
python tools/test_build_managed_recipe_manifest.py
python tools/test_physical_progression_validators.py
python tools/test_late_digital_gateways.py
python tools/test_ftbquests_guidance_campaign.py
python tools/test_ftb_post_diesel_guidance_audit.py
python tools/test_validate_live_runtime_log.py
python tools/test_validate_regional_finite_oil_fields.py
python tools/test_validate_processing_component_hardening.py
python tools/test_power_backbone_progression.py
python tools/test_early_manufacturing_progression.py
python tools/test_validate_tfmg_heavy_electrical_redesign_audit.py
python tools/test_validate_digital_core_peripherals_audit.py
python tools/test_validate_mekanism_pre_nuclear_machine_chain_audit.py
python tools/test_validate_steelworks_manufacturing_audit.py
python tools/test_validate_tfmg_fluid_infrastructure_audit.py
python tools/test_validate_high_voltage_repair_audit.py
python tools/test_extreme_transmission_audit.py
python tools/test_mekanism_storage_ladder_audit.py
python tools/test_induction_matrix_completion_audit.py
python tools/test_mekanism_transmitter_upgrade_audit.py
python tools/test_validate_mekanism_universal_cable_tail_audit.py
python tools/test_validate_mekanism_factory_restoration_audit.py
python tools/test_validate_stock_utility_restoration_audit.py
python tools/test_validate_foundry_route_parity_audit.py
python tools/test_validate_bigreactors_bulk_structures_audit.py
python tools/test_validate_automatic_recipe_backlog_closure.py
python tools/test_validate_cross_pack_progression_loophole_closure.py
python tools/test_validate_capstone_reachability.py
python tools/test_validate_stock_recipe_restoration.py
python tools/test_validate_computercraft_dependency_scan.py
python tools/test_validate_space_entry_boundary.py
python tools/test_validate_space_destination_bridge.py
python tools/test_validate_orbital_flight_gate.py
python tools/test_validate_orbital_ambient_kinetics.py
python tools/test_validate_orbital_propulsion_slice.py
python tools/test_validate_orbital_life_support_slice.py
python tools/test_validate_orbital_construction_slice.py
python tools/test_validate_orbital_dockyard_slice.py
python tools/test_validate_planetary_industry_slice.py
python tools/test_validate_venus_calorite_slice.py
python tools/validate_venus_calorite_slice.py
python tools/test_validate_mercury_asteroid_slice.py
python tools/validate_mercury_asteroid_slice.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
python tools/test_validate_outer_station_extraction_slice.py
python tools/validate_outer_station_extraction_slice.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
python tools/test_validate_interstellar_escape_isolated.py
python tools/validate_interstellar_escape_isolated.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods" --jar build/libs/industrial_colonies-0.4.0.jar
python tools/build_planetary_structure_overrides.py --check
python tools/build_managed_recipe_manifest.py --check
python tools/generate_managed_recipe_overhaul.py --check
python tools/generate_ftbquests_native.py --check
python tools/validate_managed_recipe_overhaul.py
python tools/validate_physical_progression.py
python tools/validate_physical_tier_migration.py
python tools/validate_mekanism_transmission_foundation.py
python tools/validate_mekanism_transmitter_upgrade_audit.py
python tools/validate_mekanism_universal_cable_tail_audit.py
python tools/validate_mekanism_factory_restoration_audit.py
python tools/validate_late_digital_gateways.py
python tools/validate_world_loading_progression.py
python tools/validate_petroleum_engine_progression.py
python tools/validate_regional_finite_oil_fields.py
python tools/validate_processing_component_hardening.py
python tools/validate_power_backbone_progression.py
python tools/validate_early_manufacturing_progression.py
python tools/validate_tfmg_heavy_electrical_redesign_audit.py
python tools/validate_digital_core_peripherals_audit.py --managed progression/managed_recipe_overhaul.json
python tools/validate_mekanism_pre_nuclear_machine_chain_audit.py
python tools/validate_steelworks_manufacturing_audit.py
python tools/validate_tfmg_fluid_infrastructure_audit.py
python tools/validate_high_voltage_repair_audit.py
python tools/validate_extreme_transmission_audit.py
python tools/validate_mekanism_storage_ladder_audit.py
python tools/validate_induction_matrix_completion_audit.py
python tools/validate_stock_utility_restoration_audit.py
python tools/validate_foundry_route_parity_audit.py
python tools/build_foundry_route_parity_audit.py --check
python tools/build_bigreactors_bulk_structures_audit.py --check
python tools/validate_bigreactors_bulk_structures_audit.py
python tools/validate_automatic_recipe_backlog_closure.py --require-closed
python tools/validate_cross_pack_progression_loophole_closure.py
python tools/validate_capstone_reachability.py --catalog "C:\path\to\recipe-catalog-current" --mods "C:\path\to\instance\mods"
python tools/validate_dungeon_tool_loot.py
python tools/validate_dungeon_exploration_audit.py
python tools/validate_ftbquests_native.py
python tools/validate_ftb_post_diesel_guidance_audit.py --self-test
python tools/validate_progression_bypass_retirement.py
python tools/validate_allthemodium_currency.py
python tools/validate_stock_recipe_restoration.py
python tools/validate_machine_recipe_environments.py
python tools/validate_space_entry_boundary.py --catalog "C:\path\to\recipe-catalog-current"
python tools/validate_space_destination_bridge.py --mods "C:\path\to\instance\mods"
python tools/validate_orbital_flight_gate.py --mods "C:\path\to\instance\mods"
python tools/validate_orbital_ambient_kinetics.py --mods "C:\path\to\instance\mods" --project-jar build\libs\industrial_colonies-0.4.0.jar
python tools/validate_orbital_propulsion_slice.py --catalog "C:\path\to\recipe-catalog-current"
python tools/validate_orbital_life_support_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_orbital_construction_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_orbital_dockyard_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_planetary_industry_slice.py --catalog "C:\path\to\recipe-catalog-current" --manifest progression/managed_recipe_overhaul.json --compiled pack-kjsgen/default.managed.json
python tools/validate_jei_machine_visuals.py
python tools/validate_kjsgen_sequenced_deployer.py
python tools/validate_kjsgen_removal_export.py
python tools/validate_kjsgen_mekanism_infusing_codegen.py
python tools/validate_managed_electronics_slice.py `
  "C:\Users\GodPC\curseforge\minecraft\Instances\All in one" `
  --catalog "C:\path\to\ALL_IN_ONE_MODS_ITEMS_BLOCKS.txt"
.\tools\test_merge_kjsgen_project.ps1
.\gradlew.bat build
```

After an unattended launch has entered and saved the runtime-test world, run
`python tools/validate_live_runtime_log.py`. This core check does not require
manual JEI interaction. Use `--require-jei-probes` only for the separate
interactive Copper Press Uses/U-key acceptance pass.

`tools/deploy_live_pack.ps1` runs the managed-recipe build/check/validation
sequence automatically before it merges KJSGen data or writes any live file.
It discovers Python and adjacent catalogs when possible; use
`-PythonExecutable`, `-RecipeCatalog`, and `-RuntimeItemCatalog` to supply
explicit paths on another machine. `-PlanOnly` still performs every preflight
and stages the merge, but never modifies the live pack.

The Create dependency and APIs from the target instance are compile-only and
are not bundled. The result is
`build/libs/industrial_colonies-0.4.0.jar`.
