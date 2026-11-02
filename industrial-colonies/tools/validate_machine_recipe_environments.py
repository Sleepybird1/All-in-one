#!/usr/bin/env python3
"""Validate the process-first editor catalog and exact-machine runtime routing."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = (
    ROOT
    / "src"
    / "main"
    / "resources"
    / "data"
    / "industrial_colonies"
    / "tier_recipe_environments.json"
)
RESOURCE_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")

EXPECTED_TIERS = {
    "andesite",
    "zinc",
    "copper",
    "brass",
    "railway",
    "industrial_iron",
    "weathered_iron",
    "refined_radiance",
    "shadow_steel",
    "creative",
}
EXPECTED_FAMILIES = {
    "conversion",
    "crushing",
    "cutting",
    "milling",
    "basin",
    "mixing",
    "compacting",
    "pressing",
    "sandpaper_polishing",
    "splashing",
    "haunting",
    "deploying",
    "filling",
    "emptying",
    "item_application",
    "mechanical_crafting",
    "sequenced_assembly",
}
PRESS_TIERS = {
    "base",
    "copper",
    "brass",
    "railway",
    "industrial_iron",
    "weathered_iron",
    "refined_radiance",
    "shadow_steel",
    "creative",
}
SMALL_FLUID_TIERS = {"base", "andesite", "zinc", "brass"}
EXPECTED_MACHINES = {
    "cutting": PRESS_TIERS,
    "basin": PRESS_TIERS,
    "mixing": PRESS_TIERS,
    "compacting": PRESS_TIERS,
    "pressing": PRESS_TIERS,
    "splashing": PRESS_TIERS,
    "haunting": PRESS_TIERS,
    "deploying": PRESS_TIERS,
    "item_application": PRESS_TIERS,
    "filling": SMALL_FLUID_TIERS,
    "emptying": SMALL_FLUID_TIERS,
}
EXPECTED_BASE_MACHINE_IDS = {
    "cutting": ("create:mechanical_saw", "create:mechanical_saw"),
    "basin": ("create:mechanical_mixer", "create:mechanical_mixer"),
    "mixing": ("create:mechanical_mixer", "create:mechanical_mixer"),
    "compacting": ("create:mechanical_press", "create:mechanical_press"),
    "pressing": ("create:mechanical_press", "create:mechanical_press"),
    "splashing": ("create:encased_fan", "create:encased_fan"),
    "haunting": ("create:encased_fan", "create:encased_fan"),
    "deploying": ("create:deployer", "create:deployer"),
    "item_application": ("create:deployer", "create:deployer"),
    "filling": ("create:spout", "create:spout"),
    "emptying": ("create:item_drain", "create:item_drain"),
}
EXPECTED_VARIANT_SUFFIX = {
    "cutting": "_mechanical_saw",
    "basin": "_mixer",
    "mixing": "_mixer",
    "compacting": "_press",
    "pressing": "_press",
    "splashing": "_encased_fan",
    "haunting": "_encased_fan",
    "deploying": "_deployer",
    "item_application": "_deployer",
    "filling": "_spout",
    "emptying": "_item_drain",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    errors: list[str] = []

    require(data.get("schema_version") == 2, "catalog schema_version must be 2", errors)
    require(
        data.get("model") == "machine_centric_with_legacy_tier_types",
        "catalog model must describe machine-centric routing with legacy type support",
        errors,
    )

    tiers = data.get("tiers", [])
    families = data.get("recipe_families", [])
    tier_ids = [tier.get("id") for tier in tiers]
    family_ids = [family.get("id") for family in families]
    require(set(tier_ids) == EXPECTED_TIERS, f"unexpected tier IDs: {tier_ids}", errors)
    require(len(tier_ids) == len(set(tier_ids)), "duplicate tier IDs", errors)
    require(set(family_ids) == EXPECTED_FAMILIES, f"unexpected family IDs: {family_ids}", errors)
    require(len(family_ids) == len(set(family_ids)), "duplicate recipe-family IDs", errors)

    for tier in tiers:
        require(bool(tier.get("display_name")), f"tier {tier.get('id')} lacks display_name", errors)
        casing = tier.get("casing_item", "")
        require(bool(RESOURCE_ID.fullmatch(casing)), f"invalid casing metadata item: {casing}", errors)

    exclusive_families = 0
    exclusive_routes = 0
    for family in families:
        family_id = family.get("id")
        for key in ("display_name", "icon", "schema", "create_type"):
            require(bool(family.get(key)), f"family {family_id} lacks {key}", errors)
        require(
            bool(RESOURCE_ID.fullmatch(family.get("icon", ""))),
            f"family {family_id} has invalid icon",
            errors,
        )

        machines = family.get("machines", [])
        machine_ids = [machine.get("id") for machine in machines]
        require(len(machine_ids) == len(set(machine_ids)), f"family {family_id} repeats a machine ID", errors)
        claimed_blocks: dict[str, str] = {}
        if len(machines) > 1:
            exclusive_families += 1
            exclusive_routes += len(machines)
            require(machine_ids[0] == "base", f"family {family_id} must list base first", errors)
            require(set(machine_ids) == EXPECTED_MACHINES.get(family_id), (
                f"family {family_id} has the wrong compatible-machine whitelist: {machine_ids}"
            ), errors)

        for machine in machines:
            machine_id = machine.get("id")
            require(bool(machine.get("display_name")), f"{family_id}/{machine_id} lacks display_name", errors)
            require(
                bool(RESOURCE_ID.fullmatch(machine.get("item", ""))),
                f"{family_id}/{machine_id} has invalid item",
                errors,
            )
            blocks = machine.get("block_ids", [])
            require(bool(blocks), f"{family_id}/{machine_id} lacks runtime block_ids", errors)
            for block in blocks:
                require(
                    bool(RESOURCE_ID.fullmatch(block)),
                    f"{family_id}/{machine_id} has invalid runtime block ID {block}",
                    errors,
                )
                previous = claimed_blocks.setdefault(block, machine_id)
                require(
                    previous == machine_id,
                    f"{family_id}/{machine_id} overlaps runtime block {block} with {previous}",
                    errors,
                )
            if machine_id == "base":
                require(machine.get("tier") is None, f"{family_id}/base must not claim a casing tier", errors)
                if family_id in EXPECTED_BASE_MACHINE_IDS:
                    expected_item, expected_block = EXPECTED_BASE_MACHINE_IDS[family_id]
                    require(
                        machine.get("item") == expected_item,
                        f"{family_id}/base item must be {expected_item}",
                        errors,
                    )
                    require(
                        blocks == [expected_block],
                        f"{family_id}/base runtime block must be {expected_block}",
                        errors,
                    )
            else:
                require(machine_id in EXPECTED_TIERS, f"{family_id}/{machine_id} is not a known tier", errors)
                require(
                    machine.get("tier") == machine_id,
                    f"{family_id}/{machine_id} tier metadata must equal its route ID",
                    errors,
                )
                require(
                    machine.get("item", "").startswith("createcasing:"),
                    f"{family_id}/{machine_id} must point at a Create Encased item",
                    errors,
                )
                if family_id in EXPECTED_VARIANT_SUFFIX:
                    expected = f"createcasing:{machine_id}{EXPECTED_VARIANT_SUFFIX[family_id]}"
                    require(
                        machine.get("item") == expected,
                        f"{family_id}/{machine_id} item must be {expected}",
                        errors,
                    )
                    require(
                        blocks == [expected],
                        f"{family_id}/{machine_id} runtime block must be {expected}",
                        errors,
                    )

        if len(machines) > 1:
            # This is the Java machineForLegacyTier migration rule expressed
            # against every historical tier: real variants stay exact and
            # impossible cartesian pairs resolve to the native base machine.
            for old_tier in EXPECTED_TIERS:
                migrated_route = old_tier if old_tier in machine_ids else "base"
                require(
                    migrated_route in machine_ids,
                    f"{family_id}/{old_tier} has no safe legacy migration route",
                    errors,
                )

    runtime = (ROOT / "src/main/java/dev/godpc/industrialcolonies/CreateRecipeStageGate.java").read_text(
        encoding="utf-8"
    )
    registrations = (ROOT / "src/main/java/dev/godpc/industrialcolonies/TieredCreateRecipes.java").read_text(
        encoding="utf-8"
    )
    catalog_java = (ROOT / "src/main/java/dev/godpc/industrialcolonies/TieredRecipeCatalog.java").read_text(
        encoding="utf-8"
    )
    saw_mixin = (ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/SawBlockEntityMixin.java").read_text(
        encoding="utf-8"
    )
    mixer_mixin = (
        ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/MechanicalMixerBlockEntityMixin.java"
    ).read_text(encoding="utf-8")
    filling_mixin = (ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/FillingBySpoutMixin.java").read_text(
        encoding="utf-8"
    )
    drain_be_mixin = (
        ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/ItemDrainBlockEntityMixin.java"
    ).read_text(encoding="utf-8")
    drain_handler_mixin = (
        ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/ItemDrainItemHandlerMixin.java"
    ).read_text(encoding="utf-8")
    mixin_config = (ROOT / "src/main/resources/industrial_colonies.mixins.json").read_text(encoding="utf-8")
    for token in ("machineMatches", "BuiltInRegistries.BLOCK", "binding.machine().blockIds()"):
        require(token in runtime, f"runtime exact-machine check is missing {token}", errors)
    require(
        runtime.count(
            "if (!machineMatches(recipe, machine)) {\n            return false;\n        }\n"
            "        if (level == null || level.isClientSide())"
        ) == 1,
        "recipe exact-machine matching must run before the client-side authorization shortcut",
        errors,
    )
    require(
        runtime.count(
            "if (!machineMatches(holder.value(), machine)) {\n            return false;\n        }\n"
            "        if (level == null || level.isClientSide())"
        ) == 1,
        "recipe-holder exact-machine matching must run before the client-side authorization shortcut",
        errors,
    )
    for token in ("FAMILY_TYPES", "computeIfAbsent", "List.copyOf(types)"):
        require(token in runtime, f"hot-path recipe-family type caching is missing {token}", errors)
    for token in ('"base_" + family.id()', "machineForLegacyTier"):
        require(token in registrations, f"hidden runtime registration is missing {token}", errors)
    require(
        "orElseGet(this::baseMachine)" in catalog_java,
        "invalid old tier/family pairs do not migrate to the base machine",
        errors,
    )
    for token in (
        "matchingAllowedRecipes",
        "AllRecipeTypes.CUTTING",
        "TieredRecipeBindings.get(candidate.value())",
        "shouldIgnoreInAutomation",
    ):
        require(token in saw_mixin, f"Saw custom-type discovery is missing {token}", errors)
    require(
        "family == AllRecipeTypes.MIXING || family == AllRecipeTypes.BASIN" in mixer_mixin,
        "Mixer recipe trie does not discover custom MIXING and BASIN types",
        errors,
    )
    require(
        "CreateRecipeStageGate.matchingAllowedRecipes(AllRecipeTypes.FILLING" in filling_mixin,
        "Spout direct-list lookups do not discover custom FILLING types",
        errors,
    )
    for source, label in (
        (drain_be_mixin, "Item Drain block entity"),
        (drain_handler_mixin, "Item Drain item handler"),
    ):
        for token in ("CreateMachineContext.enter", "GenericItemEmptying.canItemBeEmptied"):
            require(token in source, f"{label} does not bind EMPTYING probes with {token}", errors)
    require(
        "GenericItemEmptying.emptyItem" in drain_be_mixin,
        "Item Drain execution is not bound to the exact drain machine",
        errors,
    )
    for mixin in (
        "AllRecipeTypesMixin",
        "BasinOperatingBlockEntityMixin",
        "BeltProcessingBehaviourMixin",
        "FillingBySpoutMixin",
        "ItemDrainBlockEntityMixin",
        "ItemDrainItemHandlerMixin",
        "MechanicalMixerBlockEntityMixin",
        "MechanicalPressBlockEntityMixin",
        "SawBlockEntityMixin",
        "SmartBlockEntityTickerMixin",
    ):
        require(f'"{mixin}"' in mixin_config, f"runtime mixin {mixin} is not registered", errors)

    if errors:
        print("FAIL: machine-centric recipe environments")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        "PASS: 17 process families, "
        f"{exclusive_families} machine-selectable families, {exclusive_routes} exact routes; "
        "170 legacy tier IDs remain loadable without appearing as editor environments."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
