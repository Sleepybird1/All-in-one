from __future__ import annotations

import argparse
import sys
from pathlib import Path

import audit_recipe_reachability as audit


EXPECTED: dict[str, tuple[str, str]] = {
    # Machine lineage
    "mekanism:metallurgic_infuser": ("industrial_colonies:machine/metallurgic_infuser", "railway_mechanical_crafting"),
    "mekanism:basic_tier_installer": ("industrial_colonies:machine/modular/basic_tier_installer", "industrial_iron_sequenced_assembly"),
    "mekanism:enrichment_chamber": ("industrial_colonies:machine/modular/enrichment_chamber", "industrial_iron_sequenced_assembly"),
    "mekanism:combiner": ("industrial_colonies:machine/modular/combiner", "industrial_iron_sequenced_assembly"),
    "mekanism:osmium_compressor": ("industrial_colonies:machine/modular/osmium_compressor", "industrial_iron_sequenced_assembly"),
    "mekanism:electrolytic_separator": ("industrial_colonies:machine/electrochemical/electrolytic_separator", "weathered_iron_mechanical_crafting"),
    "mekanism:chemical_oxidizer": ("industrial_colonies:machine/electrochemical/chemical_oxidizer", "weathered_iron_sequenced_assembly"),
    "mekanism:chemical_infuser": ("industrial_colonies:machine/electrochemical/chemical_infuser", "weathered_iron_mechanical_crafting"),
    "mekanism:rotary_condensentrator": ("industrial_colonies:machine/electrochemical/rotary_condensentrator", "weathered_iron_sequenced_assembly"),
    "mekanism:pressurized_reaction_chamber": ("industrial_colonies:machine/electrochemical/pressurized_reaction_chamber", "weathered_iron_sequenced_assembly"),
    "mekanism:purification_chamber": ("industrial_colonies:machine/chemical_separation/purification_chamber", "weathered_iron_sequenced_assembly"),
    "mekanism:chemical_injection_chamber": ("industrial_colonies:machine/chemical_separation/chemical_injection_chamber", "weathered_iron_sequenced_assembly"),
    "mekanism:chemical_dissolution_chamber": ("industrial_colonies:machine/chemical_separation/chemical_dissolution_chamber", "weathered_iron_mechanical_crafting"),
    "mekanism:chemical_washer": ("industrial_colonies:machine/chemical_separation/chemical_washer", "weathered_iron_mechanical_crafting"),
    "mekanism:chemical_crystallizer": ("industrial_colonies:machine/chemical_separation/chemical_crystallizer", "weathered_iron_mechanical_crafting"),
    "mekanism:isotopic_centrifuge": ("industrial_colonies:machine/uranium_processing/isotopic_centrifuge", "refined_radiance_mechanical_crafting"),
    # Installer lineage
    "mekanism:advanced_tier_installer": ("industrial_colonies:machine/installer/advanced", "weathered_iron_sequenced_assembly"),
    "mekanism:elite_tier_installer": ("industrial_colonies:machine/installer/elite", "refined_radiance_sequenced_assembly"),
    "mekanism:ultimate_tier_installer": ("industrial_colonies:machine/installer/ultimate", "refined_radiance_mechanical_crafting"),
    # Control electronics
    "mekanism:basic_control_circuit": ("mekanism:control_circuit/basic", "railway_sequenced_assembly"),
    "mekanism:advanced_control_circuit": ("mekanism:control_circuit/advanced", "industrial_iron_sequenced_assembly"),
    "mekanism:elite_control_circuit": ("mekanism:control_circuit/elite", "weathered_iron_sequenced_assembly"),
    "mekanism:ultimate_control_circuit": ("mekanism:control_circuit/ultimate", "refined_radiance_sequenced_assembly"),
    # Power storage
    "mekanism:energy_tablet": ("mekanism:energy_tablet", "brass_sequenced_assembly"),
    "mekanism:basic_energy_cube": ("mekanism:energy_cube/basic", "industrial_iron_mechanical_crafting"),
    "mekanism:advanced_energy_cube": ("mekanism:energy_cube/advanced", "weathered_iron_sequenced_assembly"),
    "mekanism:elite_energy_cube": ("mekanism:energy_cube/elite", "weathered_iron_sequenced_assembly"),
    "mekanism:ultimate_energy_cube": ("mekanism:energy_cube/ultimate", "refined_radiance_mechanical_crafting"),
    "mekanism:basic_induction_cell": ("mekanism:induction/cell/basic", "industrial_iron_sequenced_assembly"),
    "mekanism:advanced_induction_cell": ("mekanism:induction/cell/advanced", "weathered_iron_sequenced_assembly"),
    "mekanism:elite_induction_cell": ("mekanism:induction/cell/elite", "weathered_iron_sequenced_assembly"),
    "mekanism:ultimate_induction_cell": ("mekanism:induction/cell/ultimate", "refined_radiance_mechanical_crafting"),
    "mekanism:basic_induction_provider": ("mekanism:induction/provider/basic", "industrial_iron_sequenced_assembly"),
    "mekanism:advanced_induction_provider": ("mekanism:induction/provider/advanced", "weathered_iron_sequenced_assembly"),
    "mekanism:elite_induction_provider": ("mekanism:induction/provider/elite", "weathered_iron_sequenced_assembly"),
    "mekanism:ultimate_induction_provider": ("mekanism:induction/provider/ultimate", "refined_radiance_mechanical_crafting"),
    "mekanism:induction_casing": ("mekanism:induction/casing", "refined_radiance_mechanical_crafting"),
    "mekanism:induction_port": ("mekanism:induction/port", "refined_radiance_mechanical_crafting"),
}


CASING_INPUTS = {
    "brass": {"create:brass_casing"},
    "railway": {"create:railway_casing"},
    "industrial_iron": {"create:industrial_iron_block"},
    "weathered_iron": {"create:weathered_iron_block"},
    "refined_radiance": {"create:refined_radiance", "create:refined_radiance_casing"},
}


# These are the deliberate direct links that turn the old research ordering
# into a tangible component chain. Other manifest requirements may be satisfied
# through an immediate component (for example copper wire inside a spool), but
# these machine/circuit ancestors must appear in the recipe itself.
DIRECT_CHAIN_INPUTS: dict[str, set[str]] = {
    "mekanism:electrolytic_separator": {"tfmg:steel_frame", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_oxidizer": {"tfmg:steel_frame", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_infuser": {"tfmg:steel_frame", "mekanism:advanced_control_circuit"},
    "mekanism:rotary_condensentrator": {"tfmg:steel_frame", "mekanism:advanced_control_circuit"},
    "mekanism:pressurized_reaction_chamber": {"tfmg:steel_frame", "mekanism:advanced_control_circuit"},
    "mekanism:purification_chamber": {"mekanism:enrichment_chamber", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_injection_chamber": {"mekanism:purification_chamber", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_dissolution_chamber": {"mekanism:chemical_injection_chamber", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_washer": {"mekanism:chemical_dissolution_chamber", "mekanism:advanced_control_circuit"},
    "mekanism:chemical_crystallizer": {"mekanism:chemical_washer", "mekanism:advanced_control_circuit"},
    "mekanism:isotopic_centrifuge": {"mekanism:chemical_crystallizer", "mekanism:ultimate_control_circuit"},
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the stage-independent physical Mekanism construction DAG.")
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--instance", type=Path, required=True)
    parser.add_argument("--node", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    instance = args.instance.resolve()
    node = audit.find_node(project, args.node)
    errors: list[str] = []

    capture = audit.capture_kubejs(project, project / "pack-scripts" / "server_scripts", node)
    for error in capture.get("errors", []):
        fail(errors, f"KubeJS capture error: {error}")

    scan = audit.scan_jars(instance / "mods")
    audit.apply_tag_operations(scan["tags"], capture["operations"])
    recipes, _, _ = audit.apply_kubejs_recipes(scan["definitions"], capture["operations"], scan["tags"])

    producers: dict[str, list[audit.Recipe]] = {item_id: [] for item_id in EXPECTED}
    for recipe in recipes.values():
        for output in recipe.outputs:
            if not output.tag and output.kind == "item" and output.resource_id in producers:
                producers[output.resource_id].append(recipe)

    for output, (recipe_id, type_suffix) in EXPECTED.items():
        active = producers[output]
        if len(active) != 1:
            fail(errors, f"{output} has {len(active)} active producers; expected exactly one: {recipe_id}")
            continue
        recipe = active[0]
        expected_type = f"industrial_colonies:{type_suffix}"
        if recipe.recipe_id != recipe_id:
            fail(errors, f"{output} is produced by {recipe.recipe_id}; expected {recipe_id}")
        if recipe.recipe_type != expected_type:
            fail(errors, f"{recipe_id} uses {recipe.recipe_type}; expected {expected_type}")

        tier = type_suffix.removesuffix("_sequenced_assembly").removesuffix("_mechanical_crafting")
        input_ids = {
            resource.resource_id
            for group in recipe.inputs
            for resource in group
            if not resource.tag and resource.kind == "item"
        }
        required_casing = CASING_INPUTS[tier]
        if not input_ids.intersection(required_casing):
            fail(errors, f"{recipe_id} does not consume its {tier} casing/component: {sorted(required_casing)}")

        missing_chain_inputs = DIRECT_CHAIN_INPUTS.get(output, set()) - input_ids
        if missing_chain_inputs:
            fail(errors, f"{recipe_id} is missing direct physical ancestors: {sorted(missing_chain_inputs)}")

        if output == "mekanism:energy_tablet" and "mekanism:alloy_infused" in input_ids:
            fail(errors, "Brass Energy Tablet depends on Railway alloy_infused and creates a backward tier edge")

        if type_suffix.endswith("_mechanical_crafting"):
            pattern = recipe.data.get("pattern")
            if not isinstance(pattern, list) or len(pattern) != 5 or any(not isinstance(row, str) or len(row) != 5 for row in pattern):
                fail(errors, f"{recipe_id} is not a complete 5x5 Mechanical Crafting recipe")
            else:
                used = set("".join(pattern)) - {" "}
                defined = set(recipe.data.get("key", {}))
                if used != defined:
                    fail(errors, f"{recipe_id} pattern/key mismatch: used={sorted(used)} defined={sorted(defined)}")
        else:
            loops = recipe.data.get("loops")
            if not isinstance(loops, int) or loops < 2:
                fail(errors, f"{recipe_id} must run at least two Sequenced Assembly loops")

    # Stock mek_data Factory recipes must remain absent. Their source-owned
    # direct-empty 5x5 replacements are compiled by KJSGen and are validated by
    # validate_mekanism_factory_restoration_audit.py, outside this script scan.
    direct_factories = sorted(recipe_id for recipe_id in recipes if recipe_id.startswith("mekanism:factory/"))
    if direct_factories:
        fail(errors, f"Stock Mekanism Factory recipes remain active: {direct_factories}")

    physical_script = (project / "pack-scripts" / "server_scripts" / "industrial_mekanism_physical_progression.js").read_text(encoding="utf-8")
    for forbidden in ("uranium", "yellorium"):
        if forbidden in physical_script.lower():
            fail(errors, f"Physical machine script unexpectedly touches {forbidden}; nuclear material direction must remain isolated")

    if errors:
        print("Mekanism physical progression validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    sequence_count = sum(1 for _, recipe_type in EXPECTED.values() if recipe_type.endswith("_sequenced_assembly"))
    mechanical_count = sum(1 for _, recipe_type in EXPECTED.values() if recipe_type.endswith("_mechanical_crafting"))
    print(
        "Mekanism physical progression validation passed: "
        f"{len(EXPECTED)} unique hard-construction outputs "
        f"({sequence_count} sequenced, {mechanical_count} 5x5), "
        "zero surviving stock Factory recipe IDs, and no nuclear-direction edits."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
