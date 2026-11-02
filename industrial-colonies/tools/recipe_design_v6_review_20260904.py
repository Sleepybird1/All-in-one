#!/usr/bin/env python3
"""Apply the 2026-09-04 in-game recipe review.

Deferred cards are deliberately out of scope: they are quarantine records, not
implicit approvals or redesign requests.  This pass restores stock utilities,
retires explicitly redundant blocks, fixes manufacturing environments, and
adds purpose-specific depth to rejected electronics and space hardware.
"""

from __future__ import annotations

from typing import Any


Recipe = dict[str, Any]

RESTORE_STOCK = frozenset({
    "industrial_colonies:create_addons/item_silo",
    "industrial_colonies:create_addons/mechanical_grindstone",
    "industrial_colonies:create_connected/andesite_encased_cross_connector",
    "industrial_colonies:create_connected/brass_encased_cross_connector",
    "industrial_colonies:create_core/controller_rail_batch",
    "industrial_colonies:create_core/portable_fluid_interface",
    "industrial_colonies:create_lowheated/basic_burner",
    "industrial_colonies:simulated/analog_transmission",
    "industrial_colonies:simulated/torsion_spring",
    "industrial_colonies:tfmg_canonical/grid_motor_adapter",
    "industrial_colonies:tfmg_canonical/redstone_potentiometer",
})

RETIRE = frozenset({
    "industrial_colonies:mekanism_pre_nuclear/fuelwood_heater",
})

MECHANICAL = {
    "industrial_colonies:electronics/rotor": ("industrial_iron", "RMR", "SCS", " R ", {
        "R": "tfmg:magnetic_alloy_sheet", "M": "tfmg:electric_motor", "S": "tfmg:steel_mechanism", "C": "tfmg:circuit_board"}),
    "industrial_colonies:fluid_infrastructure/electric_pump": ("industrial_iron", " VM ", "PSP ", " C  ", {
        "V": "tfmg:steel_fluid_valve", "M": "tfmg:electric_motor", "P": "tfmg:steel_mechanical_pump", "S": "tfmg:steel_mechanism", "C": "tfmg:circuit_board"}),
    "industrial_colonies:high_voltage/voltage_regulator": ("industrial_iron", " CT ", "WEW ", " H  ", {
        "C": "mekanism:advanced_control_circuit", "T": "tfmg:transformer", "W": "electroenergetics:heavily_insulated_wire", "E": "tfmg:electric_motor", "H": "tfmg:heavy_machinery_casing"}),
    "industrial_colonies:mekanism_nuclear/antiprotonic_nucleosynthesizer": ("refined_radiance", " QCU ", "RPLPR", "HNMNH", "RPLPR", " UCQ ", {
        "Q": "ae2:quantum_entangled_singularity", "C": "mekanism:ultimate_control_circuit", "U": "mekanism:ultimate_energy_cube", "R": "create:refined_radiance", "P": "mekanism:pellet_polonium", "L": "mekanism:laser", "H": "tfmg:heavy_machinery_casing", "N": "create:refined_radiance_casing", "M": "mekanism:supercharged_coil"}),
    "industrial_colonies:v3_ae2/quantum_core": ("railway", " FQF ", "CPPC ", "WECW ", " HHH ", {
        "F": "ae2:fluix_crystal", "Q": "ae2:quantum_entangled_singularity", "C": "mekanism:elite_control_circuit", "P": "ae2:engineering_processor", "W": "tfmg:copper_wire", "E": "megacells:accumulation_processor", "H": "tfmg:heavy_plate"}),
}

REFINED_RADIANCE = {
    "press": (" P ", "RCR", "AEA", "SIS", "HHH"),
    "deployer": (" A ", "RCR", "EPE", "SIS", "HHH"),
    "depot": ("RRRRR", " PEP ", " CFC ", " SIS ", "HHHHH"),
    "fan": (" F ", "RCR", "EME", "SIS", "HHH"),
    "mixer": (" W ", "RCR", "EME", "SIS", "HHH"),
    "saw": (" B ", "RCR", "EME", "SIS", "HHH"),
}

REFINED_KEYS = {
    "R": "create:refined_radiance", "C": "create:refined_radiance_casing",
    "E": "mekanism:elite_control_circuit", "A": "mekanism:alloy_atomic",
    "S": "tfmg:steel_mechanism", "I": "create:industrial_iron_block",
    "H": "tfmg:heavy_plate", "M": "tfmg:laminated_magnetic_alloy_block",
    "P": "createcasing:industrial_iron_press", "F": "createcasing:industrial_iron_encased_fan",
    "W": "createcasing:industrial_iron_mixer", "B": "createcasing:industrial_iron_mechanical_saw",
}

# Extra operations are functional subassemblies, not generic rings of expensive
# items.  They are appended before the final press of existing sequences.
HARDEN: dict[str, list[str]] = {
    "industrial_colonies:ae2/calculation_processor": ["tfmg:etched_circuit_board", "tfmg:capacitor_item"],
    "industrial_colonies:ae2_high_energy/export_bus": ["ae2:logic_processor", "tfmg:plastic_sheet"],
    "industrial_colonies:ae2_high_energy/mega_crafting_unit": ["ae2:crafting_unit", "megacells:accumulation_processor", "tfmg:plastic_sheet"],
    "industrial_colonies:digital_core/import_bus": ["ae2:logic_processor", "tfmg:plastic_sheet"],
    "industrial_colonies:extendedae_coverage/concurrent_processor": ["ae2:engineering_processor", "tfmg:etched_circuit_board", "tfmg:capacitor_item"],
    "industrial_colonies:extendedae_coverage/ex_molecular_assembler": ["ae2:molecular_assembler", "ae2:engineering_processor", "tfmg:electric_motor"],
    "industrial_colonies:extendedae_coverage/ex_pattern_provider": ["ae2:pattern_provider", "ae2:calculation_processor", "tfmg:etched_circuit_board"],
    "industrial_colonies:extendedae_coverage/ingredient_buffer": ["ae2:cell_component_16k", "ae2:calculation_processor", "tfmg:plastic_sheet"],
    "industrial_colonies:mekanism/elite_control_circuit": ["tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:capacitor_item"],
    "industrial_colonies:mekanism/ultimate_control_circuit": ["mekanism:elite_control_circuit", "ae2:engineering_processor", "tfmg:etched_circuit_board"],
    "industrial_colonies:mekanism_components/teleportation_core": ["ae2:quantum_entangled_singularity", "mekanism:elite_control_circuit", "tfmg:capacitor_item"],
    "industrial_colonies:mekanism_pre_nuclear/chemical_infuser": ["tfmg:steel_fluid_tank", "tfmg:steel_fluid_valve", "mekanism:advanced_control_circuit"],
    "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer": ["tfmg:steel_fluid_tank", "tfmg:steel_fluid_valve", "mekanism:advanced_control_circuit"],
    "industrial_colonies:mekanism_pre_nuclear/electrolytic_separator": ["tfmg:steel_fluid_tank", "tfmg:capacitor_item", "mekanism:advanced_control_circuit"],
    "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber": ["tfmg:steel_fluid_tank", "tfmg:steel_fluid_valve", "mekanism:elite_control_circuit"],
    "industrial_colonies:space_coverage/warp_memory_card": ["ae2:quantum_entangled_singularity", "mekanism:ultimate_control_circuit", "allthemodium:vibranium_allthemodium_alloy_ingot"],
    "industrial_colonies:interstellar/quantum_entangled_pair": ["mekanism:ultimate_control_circuit", "allthemodium:unobtainium_vibranium_alloy_ingot", "mekanism:pellet_antimatter"],
    "industrial_colonies:v3_ae2/accumulation_processor": ["tfmg:n_semiconductor", "tfmg:p_semiconductor", "tfmg:capacitor_item", "tfmg:transistor_item"],
    "industrial_colonies:v3_ae2/quantum_processor": ["ae2:engineering_processor", "mekanism:ultimate_control_circuit", "tfmg:etched_circuit_board"],
    "industrial_colonies:v3_ae2/quantum_unit": ["advanced_ae:quantum_core", "mekanism:ultimate_energy_cube", "megacells:accumulation_processor"],
}

TOO_CHEAP = frozenset({
    "industrial_colonies:appliedcreate/stress_storage_cell_1m",
    "industrial_colonies:appliedcreate/stress_storage_cell_64m",
    "industrial_colonies:appliedcreate/stress_storage_component_1m",
    "industrial_colonies:appliedcreate/stress_storage_component_16m",
    "industrial_colonies:appliedcreate/stress_storage_component_64k",
    "industrial_colonies:bigreactors/reprocessor/fluid_injector",
    "industrial_colonies:bigreactors/reprocessor/output_port",
    "industrial_colonies:bigreactors/reprocessor/power_port",
    "industrial_colonies:bigreactors/reprocessor/waste_injector",
    "industrial_colonies:create_addons/kinetic_bridge",
    "industrial_colonies:digital_storage/ae2_crafting_storage_256k",
    "industrial_colonies:digital_storage/assembler_matrix_frame_batch",
    "industrial_colonies:mekanism/induction/ultimate_provider",
    "industrial_colonies:mekanism/laser/tractor_beam",
    "industrial_colonies:mekanism_utility/ultimate_fluid_tank",
    "industrial_colonies:planetary/outpost/energizer",
    "industrial_colonies:planetary/outpost/gravity_normalizer",
    "industrial_colonies:simulated/gyroscopic_mechanism",
    "industrial_colonies:space/life_support/oxygen_sensor",
    "industrial_colonies:space/navigation/optical_sensor",
    "industrial_colonies:space_coverage/booster_thruster",
    "industrial_colonies:space_coverage/compressor",
    "industrial_colonies:space_coverage/magnetic_stabilizer",
    "industrial_colonies:space_coverage/rocket_thruster",
    "industrial_colonies:space_coverage/vector_thruster",
    "industrial_colonies:v3_ae2/cell_component_64k",
    "industrial_colonies:v3_ae2/cell_component_256k",
    "industrial_colonies:v3_ae2/item_storage_cell_64k",
    "industrial_colonies:v3_ae2/item_storage_cell_256k",
    "industrial_colonies:v3_ae2/mega_crafting_accelerator",
    "industrial_colonies:v3_ae2/mega_crafting_monitor",
    "industrial_colonies:v3_ae2/mega_pattern_provider",
    "industrial_colonies:v3_ae2/quantum_storage_component",
})


def _purpose_kit(recipe_id: str) -> list[str]:
    if "space" in recipe_id or "planetary" in recipe_id or "interstellar" in recipe_id:
        return ["tfmg:etched_circuit_board", "tfmg:capacitor_item", "tfmg:magnetic_alloy_sheet"]
    if "reprocessor" in recipe_id or "fluid" in recipe_id:
        return ["tfmg:steel_fluid_valve", "tfmg:plastic_pipe", "tfmg:steel_frame"]
    if "ae2" in recipe_id or "storage" in recipe_id or "stress" in recipe_id:
        return ["tfmg:etched_circuit_board", "tfmg:plastic_sheet", "tfmg:lithium_charge"]
    return ["tfmg:steel_frame", "tfmg:electric_motor", "tfmg:circuit_board"]


def _recipes(data: dict[str, Any]) -> list[Recipe]:
    value = data.setdefault("recipes", [])
    if not isinstance(value, list):
        raise TypeError("recipes must be a list")
    return value


def _restore_stock(data: dict[str, Any], recipe: Recipe) -> None:
    removals = set(recipe.get("remove", []))
    data["additional_removals"] = [x for x in data.get("additional_removals", []) if x not in removals]


def _output(recipe: Recipe) -> Any:
    return recipe.get("output") or recipe.get("outputs") or recipe.get("results")


def _replace_process(recipe: Recipe, process: Recipe) -> None:
    keep = {k: v for k, v in recipe.items() if k in {"id", "phase", "order", "node", "depends_on", "remove"}}
    recipe.clear()
    recipe.update(keep)
    recipe.update(process)
    recipe["exclusive_output"] = True


def _mechanical(recipe: Recipe, pattern: tuple[str, ...], key: dict[str, str], comment: str) -> None:
    used = {symbol for row in pattern for symbol in row if symbol != " "}
    _replace_process(recipe, {"type": "mechanical_crafting", "comment": comment,
                              "pattern": list(pattern), "key": {k: v for k, v in key.items() if k in used}, "output": _output(recipe)})


def _harden_sequence(recipe: Recipe, ingredients: list[str]) -> None:
    steps = recipe.get("steps")
    if not isinstance(steps, list):
        # For compacting/mixing recipes, meaningful extra BOM entries are direct inputs.
        target = recipe.get("inputs") or recipe.get("ingredients")
        if isinstance(target, list):
            for ingredient in ingredients:
                if ingredient not in target:
                    target.append(ingredient)
        return
    machine = "createcasing:brass_deployer"
    for step in steps:
        if step.get("op") == "deploying":
            machine = step.get("machine", machine)
            break
    at = len(steps)
    if steps and steps[-1].get("op") == "pressing":
        at -= 1
    known = {step.get("ingredient") for step in steps}
    for ingredient in ingredients:
        if ingredient not in known:
            steps.insert(at, {"op": "deploying", "ingredient": ingredient, "machine": machine})
            at += 1


def apply(data: dict[str, Any]) -> None:
    recipes = _recipes(data)
    by_id = {r.get("id"): r for r in recipes}

    for recipe_id in RESTORE_STOCK:
        recipe = by_id.get(recipe_id)
        if recipe is not None:
            _restore_stock(data, recipe)
    recipes[:] = [r for r in recipes if r.get("id") not in RESTORE_STOCK | RETIRE]

    for recipe_id, spec in MECHANICAL.items():
        recipe = by_id.get(recipe_id)
        if recipe is None:
            continue
        _, *parts = spec
        key = parts.pop()
        _mechanical(recipe, tuple(parts), key, "Mechanically assemble the functional subassemblies in their physical working layout")

    for name, pattern in REFINED_RADIANCE.items():
        recipe = by_id.get(f"industrial_colonies:manufacturing/refined_radiance/{name}")
        if recipe is not None:
            _mechanical(recipe, pattern, REFINED_KEYS, "Build the final-tier machine as a five-row radiance-shielded industrial assembly")

    spark = by_id.get("industrial_colonies:tfmg_coverage/spark_plug")
    if spark is not None:
        _replace_process(spark, {"type": "shaped", "comment": "Hand-assemble the ceramic plug around its electrode and copper terminal", "pattern": [" C ", " A ", " W "], "key": {"C": "tfmg:unfinished_insulator", "A": "tfmg:aluminum_nugget", "W": "tfmg:copper_wire"}, "output": _output(spark)})

    for recipe_id in (
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_connector",
        "industrial_colonies:machine/oil_processing/large_pumpjack_hammer_head",
        "industrial_colonies:machine/oil_processing/pumpjack_hammer_head",
    ):
        recipe = by_id.get(recipe_id)
        if recipe is not None:
            output = _output(recipe)
            _replace_process(recipe, {"type": "compacting", "comment": "Pressure-forge the pumpjack wear component on the Weathered-Iron line", "inputs": ["4x tfmg:cast_iron_ingot", "2x tfmg:heavy_plate", "tfmg:steel_mechanism", "2x tfmg:screw"], "machine": "createcasing:weathered_iron_press", "heat": "none", "output": output})

    for recipe_id, ingredients in HARDEN.items():
        recipe = by_id.get(recipe_id)
        if recipe is not None:
            _harden_sequence(recipe, ingredients)

    for recipe_id in TOO_CHEAP:
        recipe = by_id.get(recipe_id)
        if recipe is not None:
            _harden_sequence(recipe, _purpose_kit(recipe_id))

    # Semiconductor wafers remain TFMG-first and Chemical-Vat-only, but now need
    # a prepared substrate, dopant chemistry, etchant, and clean rinse.
    for kind, dopant in (("n", "tfmg:sulfur_dust"), ("p", "minecraft:redstone")):
        recipe = by_id.get(f"industrial_colonies:electronics/{kind}_semiconductor")
        if recipe is None:
            continue
        recipe["ingredients"] = [
            "2x tfmg:silicon_ingot", "tfmg:etched_circuit_board", dopant,
            {"kind": "FLUID", "id": "tfmg:sulfuric_acid", "amount": 500},
        ]
        recipe["processing_time"] = 600
        recipe["results"] = [{"kind": "ITEM", "id": f"tfmg:{kind}_semiconductor", "count": 2}]
        recipe["comment"] = "Etch, dope, and rinse a prepared silicon wafer batch in the heated TFMG Steel Chemical Vat"

    # Fluid cells use a real pressure manifold rather than merely copying item-cell electronics.
    for recipe in recipes:
        rid = str(recipe.get("id", ""))
        if rid.startswith("industrial_colonies:v3_ae2/mega_fluid_storage_cell_"):
            _harden_sequence(recipe, ["tfmg:steel_fluid_tank", "tfmg:steel_fluid_valve", "tfmg:plastic_pipe", "tfmg:electric_pump"])


def audit(data: dict[str, Any]) -> None:
    by_id = {r.get("id"): r for r in _recipes(data)}
    leaked = sorted((RESTORE_STOCK | RETIRE) & set(by_id))
    if leaked:
        raise AssertionError(f"restored/retired cards still managed: {leaked}")
    for recipe_id in MECHANICAL:
        if recipe_id in by_id and by_id[recipe_id].get("type") != "mechanical_crafting":
            raise AssertionError(f"{recipe_id} did not move to mechanical crafting")
    for name in REFINED_RADIANCE:
        recipe = by_id.get(f"industrial_colonies:manufacturing/refined_radiance/{name}")
        if recipe and recipe.get("type") != "mechanical_crafting":
            raise AssertionError(f"refined-radiance {name} is not mechanical crafting")
