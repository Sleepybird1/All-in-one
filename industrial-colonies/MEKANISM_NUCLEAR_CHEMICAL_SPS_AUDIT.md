# Mekanism Nuclear Chemistry and SPS audit

Status: **implemented in the authoritative seed**. The twelve reviewed contracts are source-owned and assignments were intentionally unchanged. Generated/live, quest, deployment, and Draw.io files were not edited by this batch.

## Outcome

The twelve remaining automatic-owned nuclear outputs become three coherent physical lines: Industrial-Iron pressure equipment for ore chemistry, Refined-Radiance instrumentation for fissile/actinide work, and an SPS frame/port/coil chain that must run before antimatter equipment.

The design retains the existing Yellorium-to-uranium boundary. None of the first eight machine-construction contracts consumes uranium, fissile fuel, reactor waste, polonium, plutonium, antimatter, or sulfuric acid. SPS casing is the first construction contract allowed to consume reactor-derived actinides; the nucleosynthesizer is the only one allowed to consume an Antimatter Pellet.

## Exact replacement contracts

| Order | Output / managed ID | Existing node | Process | Physical inputs | Exact stock removal |
|---:|---|---|---|---|---|
| 400 | `mekanism:purification_chamber`<br>`industrial_colonies:mekanism_nuclear/purification_chamber` | CR01 — Chemical Separation<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:industrial_iron_deployer` → `createcasing:industrial_iron_press` | `mekanism:enrichment_chamber`<br>`mekanism:advanced_control_circuit`<br>`tfmg:circuit_board`<br>`mekanism:ingot_osmium`<br>`tfmg:steel_chemical_vat`<br>`tfmg:steel_pipe` | `mekanism:purification_chamber` |
| 410 | `mekanism:chemical_injection_chamber`<br>`industrial_colonies:mekanism_nuclear/chemical_injection_chamber` | CR01 — Chemical Separation<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:industrial_iron_deployer` → `createcasing:industrial_iron_press` | `mekanism:purification_chamber`<br>`mekanism:elite_control_circuit`<br>`tfmg:circuit_board`<br>`mekanism:basic_chemical_tank`<br>`tfmg:steel_chemical_vat`<br>`tfmg:steel_pipe` | `mekanism:chemical_injection_chamber` |
| 420 | `mekanism:chemical_dissolution_chamber`<br>`industrial_colonies:mekanism_nuclear/chemical_dissolution_chamber` | CR01 — Chemical Separation<br>Nuclear Engineering | `compacting`<br>`createcasing:industrial_iron_press` | `tfmg:steel_frame`<br>`2x mekanism:basic_chemical_tank`<br>`tfmg:steel_chemical_vat`<br>`create:mechanical_pump`<br>`2x tfmg:steel_pipe`<br>`tfmg:transformer`<br>`mekanism:ultimate_control_circuit`<br>`ae2:engineering_processor` | `mekanism:chemical_dissolution_chamber` |
| 430 | `mekanism:chemical_washer`<br>`industrial_colonies:mekanism_nuclear/chemical_washer` | CR01 — Chemical Separation<br>Nuclear Engineering | `compacting`<br>`createcasing:industrial_iron_press` | `tfmg:steel_frame`<br>`mekanism:basic_fluid_tank`<br>`mekanism:basic_chemical_tank`<br>`tfmg:steel_chemical_vat`<br>`tfmg:steel_fluid_tank`<br>`create:mechanical_pump`<br>`tfmg:steel_pipe`<br>`mekanism:ultimate_control_circuit` | `mekanism:chemical_washer` |
| 440 | `mekanism:chemical_crystallizer`<br>`industrial_colonies:mekanism_nuclear/chemical_crystallizer` | CR01 — Chemical Separation<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:industrial_iron_deployer` → `createcasing:industrial_iron_press` | `tfmg:steel_frame`<br>`tfmg:steel_chemical_vat`<br>`mekanism:basic_chemical_tank`<br>`mekanism:fluorite_gem`<br>`mekanism:ingot_refined_obsidian`<br>`mekanism:ultimate_control_circuit` | `mekanism:chemical_crystallizer` |
| 450 | `mekanism:isotopic_centrifuge`<br>`industrial_colonies:mekanism_nuclear/isotopic_centrifuge` | CR01 — Uranium Processing<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:refined_radiance_deployer` → `createcasing:refined_radiance_press` | `tfmg:centrifuge`<br>`mekanism:basic_chemical_tank`<br>`mekanism:ultimate_control_circuit`<br>`ae2:engineering_processor`<br>`tfmg:transformer`<br>`tfmg:steel_casing` | `mekanism:isotopic_centrifuge` |
| 460 | `2x mekanism:radioactive_waste_barrel`<br>`industrial_colonies:mekanism_nuclear/radioactive_waste_barrel_batch` | CR01 — Actinide Chemistry<br>Nuclear Engineering | `compacting`<br>`createcasing:industrial_iron_press` | `tfmg:steel_fluid_tank`<br>`tfmg:fireproof_chemical_vat`<br>`4x mekanism:ingot_lead`<br>`2x tfmg:heavy_plate`<br>`2x tfmg:steel_pipe`<br>`tfmg:steel_casing` | `mekanism:radioactive_waste_barrel` |
| 470 | `mekanism:solar_neutron_activator`<br>`industrial_colonies:mekanism_nuclear/solar_neutron_activator` | CR01 — Actinide Chemistry<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:refined_radiance_deployer` → `createcasing:refined_radiance_press` | `tfmg:steel_frame`<br>`mekanism:hdpe_sheet`<br>`tfmg:steel_chemical_vat`<br>`tfmg:transformer`<br>`ae2:engineering_processor`<br>`mekanism:ultimate_control_circuit` | `mekanism:solar_neutron_activator` |
| 480 | `4x mekanism:sps_casing`<br>`industrial_colonies:mekanism_nuclear/sps_casing_batch` | CR01 — The Nuclear Age<br>Nuclear Engineering | `compacting`<br>`createcasing:refined_radiance_press` | `4x mekanism:hdpe_sheet`<br>`3x mekanism:pellet_polonium`<br>`mekanism:pellet_plutonium`<br>`2x tfmg:heavy_plate`<br>`tfmg:steel_casing`<br>`tfmg:transformer`<br>`ae2:engineering_processor` | `mekanism:sps_casing` |
| 490 | `mekanism:sps_port`<br>`industrial_colonies:mekanism_nuclear/sps_port` | CR01 — The Nuclear Age<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:refined_radiance_deployer` → `createcasing:refined_radiance_press` | `mekanism:sps_casing`<br>`mekanism:ultimate_control_circuit`<br>`ae2:engineering_processor`<br>`tfmg:circuit_board`<br>`tfmg:transformer`<br>`tfmg:copper_wire` | `mekanism:sps_port` |
| 500 | `mekanism:supercharged_coil`<br>`industrial_colonies:mekanism_nuclear/supercharged_coil` | CR01 — The Nuclear Age<br>Nuclear Engineering | `compacting`<br>`createcasing:refined_radiance_press` | `mekanism:laser`<br>`mekanism:sps_casing`<br>`2x mekanism:pellet_polonium`<br>`mekanism:ultimate_control_circuit`<br>`ae2:engineering_processor`<br>`tfmg:transformer`<br>`tfmg:copper_wire`<br>`tfmg:capacitor_item` | `mekanism:supercharged_coil` |
| 510 | `mekanism:antiprotonic_nucleosynthesizer`<br>`industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer` | CR01 — The Nuclear Age<br>Nuclear Engineering | `sequenced_assembly`<br>`createcasing:refined_radiance_deployer` → `createcasing:refined_radiance_press` | `tfmg:steel_frame`<br>`mekanism:sps_port`<br>`mekanism:supercharged_coil`<br>`mekanism:pellet_antimatter`<br>`mekanism:ultimate_control_circuit`<br>`tfmg:transformer` | `mekanism:antiprotonic_nucleosynthesizer` |

All sequences run one pass and end in their casing-specific press. Compacting uses six to eight recognizable components. There are no generic 5x5 A/B gate rings.

The two-output waste-barrel contract supports practical decay arrays; the four-output SPS casing contract supports a large multiblock without repeating a one-block craft dozens of times.

## Forward dependency shape

- Purification physically upgrades a fresh Enrichment Chamber; Injection physically upgrades a fresh Purification Chamber.
- Dissolution, Washing, and Crystallization are ordered as a slurry-processing line but do not consume one another, because all three machines must coexist in the running factory.
- The Isotopic Centrifuge upgrades the earlier TFMG Centrifuge and requires the already-reviewed Chemical Infuser, Ultimate Control Circuit, Engineering Processor, and Transformer. It does not require fissile fuel or a reactor product to construct.
- Waste barrels precede the Solar Neutron Activator. The activator has no polonium input, so it can create the first legitimate polonium from reactor waste.
- SPS casing consumes reactor-derived polonium and plutonium; both SPS port and supercharged coil physically consume an SPS casing.
- The Antiprotonic Nucleosynthesizer physically consumes an SPS port, a supercharged coil, and an Antimatter Pellet, proving an operational SPS path before nucleosynthesis.

## Bypass audit

The two known Create Mekanism Improvements mixing bypass candidates are classified against both the current catalog and mods directory. An active definition is removed exactly; an inactive or catalog-absent candidate adds no removal operation:

- `create_mekanism_improvements:pollonium_pellet` (absent from the current catalog): bypasses reactor waste and Solar Neutron Activator; disposition `absent_from_catalog_no_patch`.
- `create_mekanism_improvements:antimatter_pellet` (absent from the current catalog): creates Antimatter Pellet without an operational SPS; disposition `absent_from_catalog_no_patch`.

In the active pack, the sole Polonium Pellet route is Mekanism PRC processing of Solar-Neutron-Activator polonium, and the sole Antimatter Pellet manufacturing route is crystallization of SPS-produced antimatter. All The Compressed may recover nine pellets from its Antimatter Block, but the paired block recipe consumes those same nine pellets, so this is a lossless storage closure rather than a bootstrap. The already-existing uranium boundary separately retires `create_mekanism_improvements:uranium_ingot` if that compatibility definition is present.

## Sulfuric acid and uranium boundaries

No construction recipe in this batch synthesizes or consumes sulfuric acid. The sole active JAR synthesis remains `tfmg:vat_machine_recipe/sulfuric_acid`; `industrial_colonies:sulfur/tfmg_acid_rotary_bridge` remains the approved TFMG-fluid to Mekanism-chemical phase conversion, not a second synthesis route.

The canonical forward fuel route remains: manufactured Yellorium compound -> raw uranium in the Enrichment Chamber -> uranium dust -> Osmium Compressor ingot -> Yellow Cake -> uranium oxide -> UF6 -> Isotopic Centrifuge fissile fuel. No proposed input points backward into Yellorium, and no pre-SPS recipe consumes an actinide or antimatter product.

## Producer, acquisition, and downstream audit

Each of the twelve target outputs has exactly one active installed recipe producer. Those twelve exact IDs are the complete active removal set implemented by this batch. Catalog rows whose source JAR is absent are never mislabeled as active producers.

All installed JARs were scanned outside recipe and descriptive data. Ordinary self-drop block loot is classified as non-acquisition; any external loot, trade, or structure occurrence is a validation failure.

Downstream consumers are classified rather than silently removed: the Injecting and Purifying factory closures are already owned in the shared seed, same-batch Injection/SPS Port sources are replaced here, and MEGA Cells' radioactive component remains outside this batch.

## State-transfer rule

Five stock sources use `mekanism:mek_data`: Purification, Injection, Dissolution, Washing, and the Isotopic Centrifuge. Create encased processing cannot merge Mekanism component data. Their replacements therefore create fresh, empty, unsecured, unupgraded machines; carrier machines/tanks used in upgrades must also be fresh and empty.

## Assignment and integration boundary

All twelve outputs already appear exactly once in their current nodes and all map to Nuclear Engineering. No assignment edit was needed. The historical patch locks the released AE2 seed and assignment hashes and records the twelve source-owned recipe specs. It added no global removal in the current installed-mod state.

## Validation

```powershell
python tools/build_mekanism_nuclear_chemical_sps_audit.py --check
python tools/validate_mekanism_nuclear_chemical_sps_audit.py
python tools/test_validate_mekanism_nuclear_chemical_sps_audit.py
python tools/validate_nuclear_chemistry_boundaries.py 'C:\Users\GodPC\curseforge\minecraft\Instances\All in one' --project .
```

Validation locks source JSON/JAR hashes, producer coverage, exact removals, non-recipe acquisition evidence, concrete item identities, machine environments, sequence moderation, dependency acyclicity, uranium/acid boundaries, SPS order, managed prerequisites, assignment parity, current automatic-owner retirement, patch parity, and deterministic regeneration.
