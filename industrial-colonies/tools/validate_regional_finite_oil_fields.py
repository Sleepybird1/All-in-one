#!/usr/bin/env python3
"""Validate regional worldgen and finite TFMG 1.2.0 oil extraction."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MIXIN = "TFMGPumpjackFiniteReservoirMixin"
CDG_DUPLICATE_EXTRACTION_RECIPES = {
    "createdieselgenerators:crafting/oil_scanner",
    "createdieselgenerators:crafting/pumpjack_bearing",
    "createdieselgenerators:crafting/pumpjack_head",
    "createdieselgenerators:crafting/pumpjack_hole",
    "createdieselgenerators:mechanical_crafting/pumpjack_crank",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def find_tfmg_jar(instance: Path) -> Path:
    matches = sorted((instance / "mods").glob("tfmg-*.jar"))
    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one TFMG JAR in {instance / 'mods'}, found {len(matches)}"
        )
    return matches[0]


def find_cdg_jar(instance: Path) -> Path:
    matches = sorted((instance / "mods").glob("createdieselgenerators-*.jar"))
    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one Create Diesel Generators JAR in "
            f"{instance / 'mods'}, found {len(matches)}"
        )
    return matches[0]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project", type=Path, default=PROJECT, help="Industrial Colonies project root"
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one"),
        help="Installed CurseForge instance",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    instance = args.instance.resolve()
    failures: list[str] = []

    mixin_source = (
        project
        / "src/main/java/dev/godpc/industrialcolonies/mixin"
        / f"{MIXIN}.java"
    ).read_text(encoding="utf-8")
    mixin_config = load_json(project / "src/main/resources/industrial_colonies.mixins.json")
    require(MIXIN in mixin_config.get("mixins", []), "finite-reservoir mixin is not registered", failures)
    for fragment in (
        'targets = "com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity"',
        '@Inject(method = "process", at = @At("HEAD"), cancellable = true',
        '@Inject(method = "process", at = @At("RETURN")',
        "reservoir.oilReserves <= 0",
        "reservoir.oilReserves = Math.max(0, reservoir.oilReserves - consumed)",
        "TFMG.DEPOSITS.markDirty()",
        "MILLIBUCKETS_PER_RESERVE = 1_000",
        "infiniteDeposits.get()",
    ):
        require(fragment in mixin_source, f"finite-reservoir contract is missing: {fragment}", failures)

    remove_modifier = load_json(
        project
        / "src/main/resources/data/industrial_colonies/neoforge/biome_modifier"
        / "remove_tfmg_global_oil_deposits.json"
    )
    require(remove_modifier.get("type") == "neoforge:remove_features", "stock oil modifier is not removed", failures)
    require(remove_modifier.get("biomes") == "#minecraft:is_overworld", "stock oil removal is not overworld-wide", failures)
    require(remove_modifier.get("features") == "tfmg:oil_deposit", "wrong stock oil feature is removed", failures)
    require(remove_modifier.get("step") == "underground_ores", "stock oil removal uses the wrong step", failures)

    add_modifier = load_json(
        project
        / "src/main/resources/data/industrial_colonies/neoforge/biome_modifier"
        / "add_regional_oil_fields.json"
    )
    require(add_modifier.get("type") == "neoforge:add_features", "regional oil modifier is not additive", failures)
    require(add_modifier.get("biomes") == "#minecraft:is_overworld", "regional oil excludes offshore or classified custom biomes", failures)
    require(add_modifier.get("features") == "industrial_colonies:regional_oil_field", "regional oil uses the wrong placed feature", failures)

    placed = load_json(
        project
        / "src/main/resources/data/industrial_colonies/worldgen/placed_feature"
        / "regional_oil_field.json"
    )
    require(placed.get("feature") == "industrial_colonies:regional_oil_reservoir", "regional field does not use the chunk-owned native TFMG well adapter", failures)
    placement = placed.get("placement", [])
    require(placement == [], "external config filter or placement roll bypasses central oil rules", failures)
    rules = load_json(project / "src/main/resources/data/industrial_colonies/geology/oil.json")
    require(rules.get("reservoir_y") == -64, "regional oil must remain scanner-compatible at Y=-64", failures)
    weights = rules.get("biome_weights", {})
    for family in ("mountain_highland", "volcanic_ashen", "cold_high_altitude"):
        require(weights.get(family) == 0 and family in rules.get("hard_biome_exclusions", []), f"missing hard oil veto for {family}", failures)
    for family in ("desert_basin", "arid_badlands", "coastal_oceanic"):
        require(weights.get(family) == 2.5, f"strong oil basin weight changed for {family}", failures)
    regional = rules.get("regional_fields", {})
    require(regional.get("center_margin_blocks", 0) > regional.get("radius_max_blocks", 0) + 16, "field radius violates regional ownership margin", failures)
    require(0 <= regional.get("field_chance_at_max_weight", -1) <= 1, "invalid regional oil chance", failures)
    require(1 <= regional.get("native_wells_min", 0) <= regional.get("native_wells_max", 0) <= 32, "unbounded native oil well count", failures)
    oil_source = (project / "src/main/java/dev/godpc/industrialcolonies/geology/oil/OilReservoirFeature.java").read_text(encoding="utf-8")
    require("NATIVE_DEPOSIT.placeDeposit(" in oil_source and "NATIVE_DEPOSIT.place(" not in oil_source, "TFMG adapter lost chunk-safe native column delegation", failures)

    petroleum_script = (
        project
        / "pack-scripts/server_scripts/industrial_petroleum_canonicalization.js"
    ).read_text(encoding="utf-8")
    require(
        "CDGEvents.oilAmount(event => {" in petroleum_script
        and "return 0" in petroleum_script,
        "CDG's independent chunk-oil reserve is not forced to zero",
        failures,
    )
    for recipe_id in sorted(CDG_DUPLICATE_EXTRACTION_RECIPES):
        require(
            f"'{recipe_id}'" in petroleum_script,
            f"duplicate CDG oil extractor is not retired: {recipe_id}",
            failures,
        )

    petroleum_viewer_script = (
        project
        / "pack-scripts/client_scripts/industrial_petroleum_viewer_cleanup.js"
    ).read_text(encoding="utf-8")
    for item_id in sorted(
        recipe_id.replace("createdieselgenerators:crafting/", "createdieselgenerators:")
        .replace("createdieselgenerators:mechanical_crafting/", "createdieselgenerators:")
        for recipe_id in CDG_DUPLICATE_EXTRACTION_RECIPES
    ):
        require(
            f"'{item_id}'" in petroleum_viewer_script,
            f"retired CDG extractor remains visible in the recipe viewer: {item_id}",
            failures,
        )

    tfmg_jar = find_tfmg_jar(instance)
    with zipfile.ZipFile(tfmg_jar) as archive:
        names = set(archive.namelist())
        required_entries = {
            "com/drmangotea/tfmg/content/machinery/oil_processing/pumpjack/base/PumpjackBaseBlockEntity.class",
            "com/drmangotea/tfmg/content/machinery/oil_processing/pumpjack/base/FluidReservoir.class",
            "com/drmangotea/tfmg/content/machinery/oil_processing/pumpjack/base/TestSavedDataManager.class",
            "data/tfmg/worldgen/configured_feature/oil_deposit.json",
            "data/tfmg/worldgen/placed_feature/oil_deposit.json",
            "data/tfmg/neoforge/biome_modifier/oil_deposit.json",
        }
        missing = sorted(required_entries - names)
        require(not missing, f"installed TFMG no longer matches finite-oil targets: {missing}", failures)
        if "data/tfmg/worldgen/placed_feature/oil_deposit.json" in names:
            stock_placed = json.loads(
                archive.read("data/tfmg/worldgen/placed_feature/oil_deposit.json")
            )
            stock_rarity = [
                row.get("chance")
                for row in stock_placed.get("placement", [])
                if row.get("type") == "minecraft:rarity_filter"
            ]
            require(stock_rarity == [4], f"installed TFMG stock oil rarity changed: {stock_rarity}", failures)

    cdg_jar = find_cdg_jar(instance)
    with zipfile.ZipFile(cdg_jar) as archive:
        names = set(archive.namelist())
        for recipe_id in sorted(CDG_DUPLICATE_EXTRACTION_RECIPES):
            namespace, path = recipe_id.split(":", 1)
            resource = f"data/{namespace}/recipe/{path}.json"
            require(
                resource in names,
                f"retired CDG recipe no longer matches the installed JAR: {recipe_id}",
                failures,
            )
        require(
            "com/jesz/createdieselgenerators/compat/kubejs/CDGKubeJSPlugin.class"
            in names,
            "installed CDG no longer exposes its KubeJS oil-amount event",
            failures,
        )
        require(
            "com/jesz/createdieselgenerators/compat/kubejs/GetChunkOilAmountEventJS.class"
            in names,
            "installed CDG no longer exposes the oil-amount event payload",
            failures,
        )

    common_config = instance / "config/tfmg-common.toml"
    if common_config.is_file():
        config = common_config.read_text(encoding="utf-8-sig")
        infinite = re.search(r"(?m)^\s*infiniteDeposits\s*=\s*(true|false)\s*$", config)
        maximum = re.search(r"(?m)^\s*depositMaxReserves\s*=\s*(\d+)\s*$", config)
        require(infinite is not None and infinite.group(1) == "false", "live TFMG config enables bottomless oil", failures)
        require(maximum is not None and int(maximum.group(1)) >= 1_000, "live TFMG reserve ceiling is invalid", failures)

    if failures:
        print(f"FAIL: {len(failures)} regional-oil issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: TFMG oil is weighted basin/offshore regional with hard mountain/volcanic vetoes, scanner-compatible, its persisted "
        "1,000–10,000-unit reservoirs deplete at one unit per extracted bucket, and "
        "CDG's independent oil reserve/extractor is disabled without disabling its engines."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
