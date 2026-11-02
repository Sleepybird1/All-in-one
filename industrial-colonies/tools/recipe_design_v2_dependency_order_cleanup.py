#!/usr/bin/env python3
"""Make explicit same-phase recipe prerequisites appear before consumers.

Several recipe waves correctly used an item produced by another managed
recipe, but retained an older display order.  The resulting KubeJS Gen cards
could present the consumer before the component that makes it possible.  This
pass changes only ``order`` and ``depends_on`` on the affected existing
recipes.  It does not read or write files and is safe to apply repeatedly.

The dependency table intentionally excludes cross-phase progression.  It does
include the two Create Encased acquisition recipes which are consumed as
literal ingredients by later same-phase machines; those are physical recipe
dependencies, not a general casing-tier policy.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any


Recipe = MutableMapping[str, Any]

# ``expand_machine_family`` currently emits family cards without an ``order``
# field, so KubeJS Gen sorts them at its normal fallback order.  A few recipes
# consume those machine blocks as ingredients.  We model the emitted cards
# here instead of pretending they exist in the seed's explicit recipe list.
FAMILY_GENERATED_ORDER = 999


# Consumer -> exact managed recipes that produce its same-phase prerequisites.
# Engine-cylinder entries form a deliberate chain:
# spark plug / diesel cylinder -> engine cylinder -> radial engine, while the
# diesel-specific cylinder independently gates the diesel engine.
ORDER_DEPENDENCIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Digital Logistics: make the two AE cores before the devices that consume
    # them.  The core recipes were added after the original terminal wave and
    # retained later display orders even though they became hard ingredients.
    (
        "industrial_colonies:digital_core/terminal",
        (
            "industrial_colonies:ae2_coverage/annihilation_core_batch",
            "industrial_colonies:ae2_coverage/formation_core_batch",
        ),
    ),
    (
        "industrial_colonies:digital_core/import_bus",
        ("industrial_colonies:ae2_coverage/annihilation_core_batch",),
    ),
    (
        "industrial_colonies:digital_core/interface",
        (
            "industrial_colonies:ae2_coverage/annihilation_core_batch",
            "industrial_colonies:ae2_coverage/formation_core_batch",
        ),
    ),
    (
        "industrial_colonies:digital_core/molecular_assembler",
        (
            "industrial_colonies:ae2_coverage/annihilation_core_batch",
            "industrial_colonies:ae2_coverage/formation_core_batch",
        ),
    ),
    # Electrical Manufacturing.
    (
        "industrial_colonies:electronics/polarizer",
        ("industrial_colonies:electronics/capacitor",),
    ),
    (
        "industrial_colonies:electronics/advanced_stress_processor",
        ("industrial_colonies:ae2/logic_processor",),
    ),
    (
        "industrial_colonies:digital_core/peripheral_casing",
        ("industrial_colonies:ae2/engineering_processor",),
    ),
    (
        "industrial_colonies:digital_core/block_reader",
        ("industrial_colonies:digital_core/peripheral_casing",),
    ),
    (
        "industrial_colonies:digital_core/energy_detector",
        ("industrial_colonies:digital_core/peripheral_casing",),
    ),
    (
        "industrial_colonies:digital_core/pattern_provider",
        ("industrial_colonies:ae2/calculation_processor",),
    ),
    (
        "industrial_colonies:extreme_grid/high_voltage_switch",
        ("industrial_colonies:high_voltage/miniature_circuit_breaker",),
    ),
    (
        "industrial_colonies:appliedcreate/me_gearbox",
        (
            "industrial_colonies:ae2_high_energy/me_p2p_tunnel",
            "industrial_colonies:appliedcreate/stress_storage_component_1k",
        ),
    ),
    (
        "industrial_colonies:advanced_ae/reaction_chamber",
        ("industrial_colonies:ae2_coverage/condenser",),
    ),
    # High-Energy Grid: induction and storage assemblies consume the completed
    # grid hardware shown here, so their cards must follow those components.
    (
        "industrial_colonies:mekanism/induction/casing",
        ("industrial_colonies:extreme_grid/heavily_insulated_wire",),
    ),
    (
        "industrial_colonies:extreme_grid/heavily_insulated_wire_spool",
        ("industrial_colonies:extreme_grid/heavily_insulated_wire",),
    ),
    (
        "industrial_colonies:extreme_grid/heavily_insulated_wire",
        ("industrial_colonies:high_voltage/insulated_wire",),
    ),
    (
        "industrial_colonies:mekanism/induction/port",
        (
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:high_voltage/voltage_regulator",
            "industrial_colonies:extreme_grid/high_voltage_capacitor",
            "industrial_colonies:mekanism/transmission/ultimate_universal_cable",
        ),
    ),
    (
        "industrial_colonies:mekanism/induction/basic_cell",
        ("industrial_colonies:mekanism/induction/casing",),
    ),
    (
        "industrial_colonies:mekanism/induction/basic_provider",
        ("industrial_colonies:mekanism/induction/casing",),
    ),
    (
        "industrial_colonies:mekanism/induction/advanced_cell",
        ("industrial_colonies:mekanism/induction/basic_cell",),
    ),
    (
        "industrial_colonies:mekanism/induction/advanced_provider",
        ("industrial_colonies:mekanism/induction/basic_provider",),
    ),
    (
        "industrial_colonies:mekanism/storage/ultimate_energy_cube",
        (
            "industrial_colonies:mekanism/ultimate_control_circuit",
            "industrial_colonies:extreme_grid/sulfur_hexafluoride_breaker",
        ),
    ),
    # Mekanized Industry: conductor upgrades consume their basic predecessor,
    # chemical machines consume actual tank blocks, and the Combiner consumes
    # the family-generated Industrial Iron press as its physical tool head.
    (
        "industrial_colonies:mekanism/storage/basic_energy_cube",
        ("industrial_colonies:mekanism/basic_control_circuit",),
    ),
    (
        "industrial_colonies:mekanism/transmission/advanced_universal_cable",
        (
            "industrial_colonies:mekanism/advanced_control_circuit",
            "industrial_colonies:mekanism/transmission/basic_universal_cable",
        ),
    ),
    (
        "industrial_colonies:mekanism/transmission/advanced_logistical_transporter",
        ("industrial_colonies:mekanism/transmission/basic_logistical_transporter",),
    ),
    (
        "industrial_colonies:mekanism/combiner",
        ("industrial_colonies:manufacturing/industrial_iron/press",),
    ),
    (
        "industrial_colonies:mekanism_pre_nuclear/chemical_oxidizer",
        ("industrial_colonies:mekanism_components/basic_chemical_tank",),
    ),
    (
        "industrial_colonies:mekanism_pre_nuclear/chemical_infuser",
        ("industrial_colonies:mekanism_components/basic_chemical_tank",),
    ),
    (
        "industrial_colonies:mekanism_pre_nuclear/pressurized_reaction_chamber",
        (
            "industrial_colonies:mekanism_components/basic_fluid_tank",
            "industrial_colonies:mekanism_components/basic_chemical_tank",
            "industrial_colonies:mekanism_components/dynamic_tank_batch",
        ),
    ),
    # Nuclear reactor interfaces are built from the matching completed casing,
    # rather than being displayed hundreds of cards before that casing batch.
    (
        "industrial_colonies:nuclear/basic_reactor_controller",
        ("industrial_colonies:bigreactors/basic_reactor/casing",),
    ),
    (
        "industrial_colonies:nuclear/basic_reactor_redstone_port",
        ("industrial_colonies:bigreactors/basic_reactor/casing",),
    ),
    (
        "industrial_colonies:nuclear/basic_reactor_power_tap",
        ("industrial_colonies:bigreactors/basic_reactor/casing",),
    ),
    (
        "industrial_colonies:nuclear/reinforced_reactor_controller",
        ("industrial_colonies:bigreactors/reinforced_reactor/casing",),
    ),
    (
        "industrial_colonies:nuclear/reinforced_computer_port",
        ("industrial_colonies:bigreactors/reinforced_reactor/casing",),
    ),
    # Orbital and interstellar assemblies consume these navigation/conductor
    # subassemblies directly.
    (
        "industrial_colonies:space_coverage/vector_thruster",
        ("industrial_colonies:space/navigation/gimbal_sensor",),
    ),
    (
        "industrial_colonies:space/station/cable_duct",
        ("industrial_colonies:space_coverage/steel_cable",),
    ),
    (
        "industrial_colonies:interstellar/unsigned_route_crystal",
        ("industrial_colonies:space_coverage/warp_memory_card",),
    ),
    # Create/TFMG bootstrap and petroleum hardware.
    (
        "industrial_colonies:manufacturing/copper_deployer",
        ("industrial_colonies:brass/deployer",),
    ),
    (
        "industrial_colonies:manufacturing/brass_deployer",
        ("industrial_colonies:manufacturing/copper_deployer",),
    ),
    (
        "industrial_colonies:create_core/contraption_controls",
        ("industrial_colonies:create_core/redstone_link_pair",),
    ),
    (
        "industrial_colonies:petroleum/steel_distillation_controller",
        ("industrial_colonies:fluid_infrastructure/industrial_pipe",),
    ),
    (
        "industrial_colonies:petroleum/steel_distillation_output",
        (
            "industrial_colonies:fluid_infrastructure/industrial_pipe",
            "industrial_colonies:tfmg_coverage/steel_fluid_valve",
        ),
    ),
    (
        "industrial_colonies:engines/engine_turbocharger",
        ("industrial_colonies:fluid_infrastructure/aluminum_pipe",),
    ),
    (
        "industrial_colonies:engines/turbine_engine",
        (
            "industrial_colonies:fluid_infrastructure/aluminum_pipe",
            "industrial_colonies:engines/engine_turbocharger",
        ),
    ),
    (
        "industrial_colonies:engines/diesel_engine",
        (
            "industrial_colonies:tfmg_heavy_electrical/diesel_engine_cylinder",
            "industrial_colonies:diesel_generators_coverage/engine_piston",
        ),
    ),
    (
        "industrial_colonies:engines/large_diesel_engine",
        (
            "industrial_colonies:engines/diesel_engine",
            "industrial_colonies:diesel_generators_coverage/engine_piston",
        ),
    ),
    (
        "industrial_colonies:engines/huge_diesel_engine",
        (
            "industrial_colonies:diesel_generators_coverage/engine_piston",
            "industrial_colonies:engines/large_diesel_engine",
        ),
    ),
    # The user's approved v3 Engine Cylinder is bound to Industrial Iron and
    # therefore intentionally crosses out of this legacy Steel & Petroleum
    # ordering group.  The v3 reference module moves it and both consumers as
    # one reviewed unit after this same-phase cleanup runs.
    (
        "industrial_colonies:foundry_routes/create_metallurgy_foundry_mixer",
        ("industrial_colonies:create_addons/sturdy_whisk",),
    ),
    (
        "industrial_colonies:create_addons/experience_hatch",
        ("industrial_colonies:tfmg_coverage/plastic_fluid_valve",),
    ),
    (
        "industrial_colonies:big_cannons/cannon_loader",
        ("industrial_colonies:big_cannons/recoil_spring",),
    ),
    (
        "industrial_colonies:big_cannons/cannon_drill",
        ("industrial_colonies:createcasing/railway/drill",),
    ),
    (
        "industrial_colonies:big_cannons/cannon_mount_extension",
        ("industrial_colonies:manufacturing/railway/gearbox",),
    ),
    (
        "industrial_colonies:simulated/portable_engine",
        ("industrial_colonies:simulated/throttle_lever",),
    ),
)


def _recipe_index(data: MutableMapping[str, Any]) -> dict[str, Recipe]:
    """Return a strict index of explicit and emitted family recipe cards."""

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise ValueError("Recipe seed must contain a recipes list")

    indexed: dict[str, Recipe] = {}
    for position, recipe in enumerate(recipes):
        if not isinstance(recipe, MutableMapping):
            raise ValueError(f"recipes[{position}] is not a mutable mapping")
        recipe_id = recipe.get("id")
        if not isinstance(recipe_id, str) or not recipe_id:
            raise ValueError(f"recipes[{position}] has no valid managed recipe ID")
        if recipe_id in indexed:
            raise ValueError(f"Managed recipe is duplicated: {recipe_id}")
        indexed[recipe_id] = recipe

    families = data.get("machine_families", [])
    if not isinstance(families, list):
        raise ValueError("Recipe seed machine_families must be a list")
    for family_position, family in enumerate(families):
        if not isinstance(family, Mapping):
            raise ValueError(
                f"machine_families[{family_position}] is not a mapping"
            )
        tier = family.get("tier")
        phase = family.get("phase")
        if not isinstance(tier, str) or not tier:
            raise ValueError(f"machine_families[{family_position}] has no tier")
        if not isinstance(phase, str) or not phase:
            raise ValueError(f"machine family {tier!r} has no phase")

        # Mirror normalize_machine_families: generated ``kinds`` establish the
        # defaults and an explicit entry with the same kind replaces one.
        family_entries: dict[str, Mapping[str, Any]] = {}
        kinds = family.get("kinds", [])
        if not isinstance(kinds, list):
            raise ValueError(f"machine family {tier!r} kinds is not a list")
        for kind in kinds:
            if not isinstance(kind, str) or not kind:
                raise ValueError(f"machine family {tier!r} has an invalid kind")
            if kind in family_entries:
                raise ValueError(f"machine family {tier!r} repeats kind {kind!r}")
            family_entries[kind] = {"kind": kind}

        explicit_entries = family.get("recipes", [])
        if not isinstance(explicit_entries, list):
            raise ValueError(f"machine family {tier!r} recipes is not a list")
        explicit_kinds: set[str] = set()
        for entry_position, entry in enumerate(explicit_entries):
            if not isinstance(entry, Mapping):
                raise ValueError(
                    f"machine family {tier!r} recipe {entry_position} is not a mapping"
                )
            kind = entry.get("kind")
            if not isinstance(kind, str) or not kind:
                raise ValueError(
                    f"machine family {tier!r} recipe {entry_position} has no kind"
                )
            if kind in explicit_kinds:
                raise ValueError(
                    f"machine family {tier!r} repeats explicit kind {kind!r}"
                )
            explicit_kinds.add(kind)
            family_entries[kind] = entry

        for kind, entry in family_entries.items():
            recipe_id = entry.get(
                "id", f"industrial_colonies:manufacturing/{tier}/{kind}"
            )
            if not isinstance(recipe_id, str) or not recipe_id:
                raise ValueError(
                    f"machine family {tier!r} kind {kind!r} has no valid recipe ID"
                )
            if recipe_id in indexed:
                raise ValueError(f"Managed recipe is duplicated: {recipe_id}")
            # Do not mutate this descriptor: it represents the card emitted by
            # expand_machine_family, whose current schema has no per-card order
            # or depends_on fields.  Consumers can still depend on its stable
            # managed ID and can be placed after its effective fallback order.
            indexed[recipe_id] = {
                "id": recipe_id,
                "phase": phase,
                "order": FAMILY_GENERATED_ORDER,
                "exclusive_output": True,
                "family_generated": True,
            }
    return indexed


def _required_recipe(indexed: Mapping[str, Recipe], recipe_id: str) -> Recipe:
    """Resolve one policy recipe, failing instead of silently skipping it."""

    try:
        return indexed[recipe_id]
    except KeyError as error:
        raise ValueError(f"Required managed recipe is missing: {recipe_id}") from error


def _order(recipe: Mapping[str, Any], recipe_id: str) -> int | float:
    value = recipe.get("order")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{recipe_id} has a non-numeric order: {value!r}")
    return value


def _deduplicated_dependencies(recipe: Mapping[str, Any], recipe_id: str) -> list[str]:
    raw = recipe.get("depends_on", [])
    if not isinstance(raw, list):
        raise ValueError(f"{recipe_id} has a non-list depends_on value: {raw!r}")

    result: list[str] = []
    seen: set[str] = set()
    for dependency in raw:
        if not isinstance(dependency, str) or not dependency:
            raise ValueError(f"{recipe_id} has an invalid depends_on entry: {dependency!r}")
        if dependency not in seen:
            seen.add(dependency)
            result.append(dependency)
    return result


def _mutate_existing_recipe(
    indexed: Mapping[str, Recipe],
    consumer_id: str,
    prerequisite_ids: tuple[str, ...],
) -> None:
    """Add dependencies and place one consumer after all its prerequisites."""

    consumer = _required_recipe(indexed, consumer_id)
    prerequisites = [
        _required_recipe(indexed, prerequisite_id) for prerequisite_id in prerequisite_ids
    ]

    consumer_phase = consumer.get("phase")
    if not isinstance(consumer_phase, str) or not consumer_phase:
        raise ValueError(f"{consumer_id} has no valid phase")
    dependencies = _deduplicated_dependencies(consumer, consumer_id)
    for prerequisite_id in prerequisite_ids:
        if prerequisite_id not in dependencies:
            dependencies.append(prerequisite_id)
    consumer["depends_on"] = dependencies

    # This legacy pass only repairs display order inside one phase.  Design-v3
    # deliberately moves several manufacturing environments to later phases;
    # their cross-phase dependencies remain explicit but are aligned by the v3
    # phase pass instead of being rejected here.
    same_phase = [
        (prerequisite_id, prerequisite)
        for prerequisite_id, prerequisite in zip(
            prerequisite_ids, prerequisites, strict=True
        )
        if prerequisite.get("phase") == consumer_phase
    ]
    if same_phase:
        latest_prerequisite = max(
            _order(prerequisite, prerequisite_id)
            for prerequisite_id, prerequisite in same_phase
        )
        if _order(consumer, consumer_id) <= latest_prerequisite:
            consumer["order"] = latest_prerequisite + 1


def _apply_in_dependency_order(
    indexed: Mapping[str, Recipe],
    policies: Mapping[str, tuple[str, ...]],
) -> None:
    """Apply policy targets topologically so chained moves propagate."""

    complete: set[str] = set()
    active: list[str] = []

    def visit(consumer_id: str) -> None:
        if consumer_id in complete:
            return
        if consumer_id in active:
            cycle = " -> ".join(active[active.index(consumer_id) :] + [consumer_id])
            raise ValueError(f"Dependency-order cleanup policy contains a cycle: {cycle}")

        active.append(consumer_id)
        prerequisite_ids = policies[consumer_id]
        for prerequisite_id in prerequisite_ids:
            if prerequisite_id in policies:
                visit(prerequisite_id)
        _mutate_existing_recipe(indexed, consumer_id, prerequisite_ids)
        active.pop()
        complete.add(consumer_id)

    for consumer_id in policies:
        visit(consumer_id)


def _audit_targets(
    indexed: Mapping[str, Recipe],
    policies: Mapping[str, tuple[str, ...]],
) -> None:
    """Verify the in-memory result before returning it to the caller."""

    for consumer_id, prerequisite_ids in policies.items():
        consumer = _required_recipe(indexed, consumer_id)
        dependencies = _deduplicated_dependencies(consumer, consumer_id)
        if dependencies != consumer.get("depends_on"):
            raise ValueError(f"{consumer_id} still has duplicate dependency IDs")

        consumer_order = _order(consumer, consumer_id)
        for prerequisite_id in prerequisite_ids:
            prerequisite = _required_recipe(indexed, prerequisite_id)
            if prerequisite_id not in dependencies:
                raise ValueError(
                    f"{consumer_id} is missing explicit prerequisite {prerequisite_id}"
                )
            if (
                prerequisite.get("phase") == consumer.get("phase")
                and consumer_order <= _order(prerequisite, prerequisite_id)
            ):
                raise ValueError(
                    f"{consumer_id} order {consumer_order} is not after "
                    f"{prerequisite_id} order {_order(prerequisite, prerequisite_id)}"
                )


def apply(data: MutableMapping[str, Any]) -> None:
    """Apply this side-effect-free, idempotent ordering cleanup in memory."""

    indexed = _recipe_index(data)
    policies: dict[str, tuple[str, ...]] = {}
    for consumer_id, prerequisite_ids in ORDER_DEPENDENCIES:
        if consumer_id in policies:
            raise ValueError(f"Cleanup policy duplicates consumer: {consumer_id}")
        if not prerequisite_ids:
            raise ValueError(f"Cleanup policy has no prerequisites for {consumer_id}")
        policies[consumer_id] = prerequisite_ids

    _apply_in_dependency_order(indexed, policies)
    _audit_targets(indexed, policies)
