#!/usr/bin/env python3
"""Prove legacy script names cannot conflict with the managed recipe overhaul.

The pack intentionally keeps a small set of primitive-progression,
canonicalization, compatibility, endgame, and exact non-recipe policy scripts. Every former broad
machine/electronics/construction script must remain present as a same-named
migration no-op so deployment overwrites older live copies. Replacement
recipes and exact removals are now owned by the managed KJSGen project.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESTORATION_MARKERS = {
    "industrial_ae2_me_basics.js",
    "industrial_ae2_processor_construction.js",
    "industrial_computercraft_hardware.js",
    "industrial_early_electricity_construction.js",
    "industrial_electronics_progression.js",
    "industrial_factory_installer_progression.js",
    "industrial_grid_engineering_construction.js",
    "industrial_machine_construction_01.js",
    "industrial_machine_construction_02.js",
    "industrial_machine_construction_03.js",
    "industrial_machine_construction_04.js",
    "industrial_machine_construction_05.js",
    "industrial_machine_construction_06.js",
    "industrial_machine_retirement_01.js",
    "industrial_mekanism_physical_progression.js",
    "industrial_nuclear_advanced_fuel_01.js",
    "industrial_nuclear_construction_01.js",
    "industrial_nuclear_construction_02.js",
    "industrial_nuclear_construction_03.js",
    "industrial_nuclear_construction_04.js",
    "industrial_nuclear_plutonium_01.js",
    "industrial_nuclear_reprocessing_01.js",
    "industrial_oil_field_construction.js",
    "industrial_tier_installer_construction.js",
}

ALLOWED_MUTATION_SCRIPTS = {
    # Deliberate early-game tool bootstrap.
    "industrial_primitive_tool_progression.js",
    # Explicit canonical material/fuel policy.
    "industrial_allthemodium_currency.js",
    "industrial_cast_iron_canonicalization.js",
    "industrial_copper_wire_canonicalization.js",
    "industrial_lead_canonicalization.js",
    "industrial_nuclear_fuel_01.js",
    # One exact chemical bridge is required because Mekanism Generators is not
    # installed. tools/validate_capstone_reachability.py owns its full recipe
    # shape, source exclusivity, and downstream reachability contract.
    "industrial_nuclear_actinides_01.js",
    "industrial_petroleum_canonicalization.js",
    "industrial_steel_canonicalization.js",
    "industrial_sulfur_canonicalization.js",
    "industrial_uranium_yellorium_separation.js",
    "industrial_yellorium_refinement.js",
    # Temporary physical boundary while the authored spaceflight expansion is deferred.
    "industrial_space_entry_deferred.js",
    # Narrow codec/dependency repairs.
    "industrial_megacells_radioactive_compat.js",
    "industrial_metallurgy_casting_compat.js",
    # Endgame project items, not stock machine replacement.
    "industrial_black_hole_megaproject.js",
    "industrial_reserve_core_megaproject.js",
    "industrial_star_megaproject.js",
}

# This is not a recipe owner. It is a single exact item-tag policy which makes
# the manufactured ME Gearbox the only stress-P2P attunement key. Keep it out
# of ALLOWED_MUTATION_SCRIPTS so no recipe mutation is accidentally authorized
# under the tag-policy exception.
FOCUSED_NON_RECIPE_POLICIES = {
    "industrial_appliedcreate_kinetic_network.js": {
        "event": "ServerEvents.tags('item'",
        "tag": "appliedcreate:p2p_attunements/stress_p2p_tunnel",
        "remove": "event.removeAll(stressAttunement)",
        "add": "event.add(stressAttunement, 'appliedcreate:me_gearbox')",
    }
}

MUTATION = re.compile(
    r"\bevent\.(?:remove|removeAll|replaceInput|replaceOutput|custom|shaped|"
    r"shapeless|smelting|blasting|recipes)\s*\("
)

# Representative IDs and whole families that were previously deleted.  The
# no-op scripts must not target any of them, even if a future edit accidentally
# reintroduces a removal through a helper.
FORMERLY_REMOVED_TARGETS = (
    "ae2:network/blocks/inscribers",
    "ae2:inscriber/",
    "computercraft:computer_normal",
    "computercraft:monitor_normal",
    "computercraft:turtle_normal",
    "tfmg:sequenced_assembly/generator",
    "tfmg:sequenced_assembly/motor",
    "tfmg:crafting/machinery/winding_machine",
    "mekanism:crusher",
    "mekanism:precision_sawmill",
    "mekanism:energized_smelter",
    "mekanism:formulaic_assemblicator",
    "mekanism:factory/",
    "mekanism:control_circuit/",
    "mekanism:energy_cube/",
    "mekanism:tier_installer/",
    "mekanism:radioactive_waste_barrel",
    "mekanism:solar_neutron_activator",
    "bigreactors:reactor/basic/",
    "bigreactors:reactor/reinforced/",
)


def validate_script_authority(name: str, text: str) -> list[str]:
    """Classify one script without creating a filename-wide recipe bypass."""

    errors: list[str] = []
    policy = FOCUSED_NON_RECIPE_POLICIES.get(name)
    if policy is None:
        if MUTATION.search(text) and name not in ALLOWED_MUTATION_SCRIPTS:
            errors.append(
                f"{name}: recipe mutation is outside the "
                "primitive/canonical/compat/endgame allowlist"
            )
        return errors

    if text.count(policy["event"]) != 1 or "ServerEvents.recipes" in text:
        errors.append(f"{name}: focused policy must contain one item-tag event and no recipe event")
    if text.count(policy["tag"]) != 1:
        errors.append(f"{name}: focused stress-P2P tag identity changed")
    if text.count(policy["remove"]) != 1 or text.count("event.removeAll(") != 1:
        errors.append(f"{name}: focused policy must clear exactly its reviewed tag")
    if text.count(policy["add"]) != 1 or text.count("event.add(") != 1:
        errors.append(f"{name}: focused policy must add only the manufactured ME Gearbox")
    for forbidden in (
        "event.remove(",
        "event.replaceInput(",
        "event.replaceOutput(",
        "event.custom(",
        "event.shaped(",
        "event.shapeless(",
        "event.smelting(",
        "event.blasting(",
        "event.recipes(",
        "'create:shaft'",
        "'create:cogwheel'",
        "'create:large_cogwheel'",
        "'create:gearbox'",
        "'create:hand_crank'",
    ):
        if forbidden in text:
            errors.append(f"{name}: focused tag policy contains forbidden token {forbidden}")
    return errors


def validate_project(project_root: Path) -> list[str]:
    script_root = project_root.resolve() / "pack-scripts" / "server_scripts"
    client_marker = (
        project_root.resolve()
        / "pack-scripts"
        / "client_scripts"
        / "industrial_machine_retirement_viewer_cleanup.js"
    )
    errors: list[str] = []

    found = {path.name for path in script_root.glob("*.js")}
    missing = sorted(RESTORATION_MARKERS - found)
    if missing:
        errors.append("Missing same-name restoration markers: " + ", ".join(missing))

    for name in sorted(RESTORATION_MARKERS & found):
        path = script_root / name
        text = path.read_text(encoding="utf-8-sig")
        if "Managed-overhaul migration marker" not in text:
            errors.append(f"{name}: missing documented managed-overhaul migration marker")
        mutations = MUTATION.findall(text)
        if mutations:
            errors.append(f"{name}: still emits {len(mutations)} recipe mutation(s)")
        targets = [target for target in FORMERLY_REMOVED_TARGETS if target in text]
        if targets:
            errors.append(f"{name}: still targets former stock IDs: {', '.join(targets)}")

    for path in sorted(script_root.glob("*.js")):
        text = path.read_text(encoding="utf-8-sig")
        errors.extend(validate_script_authority(path.name, text))

    if not client_marker.is_file():
        errors.append("Missing same-name machine-retirement viewer restoration marker")
    else:
        client_text = client_marker.read_text(encoding="utf-8-sig")
        if "Managed-overhaul migration marker" not in client_text:
            errors.append("Machine-retirement viewer migration marker is undocumented")
        if re.search(r"\bevent\.remove\s*\(", client_text):
            errors.append("Machine-retirement viewer marker still hides stock entries")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    errors = validate_project(args.project_root)

    if errors:
        print("FAIL: stock recipe restoration contract violated", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(
        "PASS: managed-recipe ownership is isolated; "
        f"{len(RESTORATION_MARKERS)} legacy same-name scripts are mutation-free, "
        "only primitive/canonical/compat/endgame scripts still mutate recipes, "
        f"and {len(FOCUSED_NON_RECIPE_POLICIES)} exact non-recipe tag policy is isolated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
