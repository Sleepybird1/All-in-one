#!/usr/bin/env python3
"""Validate staged dungeon-tool loot against the Primitive Age boundary."""

from __future__ import annotations

import argparse
import json
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/main/resources/data"
MODS_TOML = ROOT / "src/main/templates/META-INF/neoforge.mods.toml"
MIXIN_CONFIG = ROOT / "src/main/resources/industrial_colonies.mixins.json"
MIXIN_SOURCE = (
    ROOT
    / "src/main/java/dev/godpc/industrialcolonies/mixin"
    / "DungeonCrawlRandomItemsMixin.java"
)
DEFAULT_INSTANCE = Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one")

TABLES: dict[str, tuple[int, ...]] = {
    "dungeonnowloading/loot_table/chests/labyrinth/rewards/gears.json": (14,),
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/normal_puzzle.json": (5,),
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/hard_puzzle.json": (3,),
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/hard_combat.json": (5,),
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/normal_combat.json": (8,),
    "betterdungeons/loot_table/zombie_dungeon/chests/common.json": (7, 15, 10, 3),
    "betterdungeons/loot_table/zombie_dungeon/chests/special.json": (7, 15, 10, 3),
    "betterdungeons/loot_table/zombie_dungeon/chests/tombstone.json": (5,),
}

DIAMOND_TOOLS = {
    f"minecraft:diamond_{kind}"
    for kind in ("sword", "pickaxe", "axe", "shovel", "hoe")
}
LOW_MID_EQUIPMENT = {
    f"minecraft:{material}_{kind}"
    for material in ("stone", "iron")
    for kind in ("sword", "pickaxe", "axe", "shovel", "hoe")
} | {"minecraft:bow", "minecraft:crossbow", "minecraft:shield"}

COMMON_TABLES = {
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/normal_puzzle.json",
    "dungeonnowloading/loot_table/chests/temple_of_duality/equipment/normal_combat.json",
    "betterdungeons/loot_table/zombie_dungeon/chests/common.json",
    "betterdungeons/loot_table/zombie_dungeon/chests/tombstone.json",
}
RARE_DIAMOND_TABLES = set(TABLES) - COMMON_TABLES


def item_entries(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if value.get("type") == "minecraft:item" and isinstance(value.get("name"), str):
            yield value
        for child in value.values():
            yield from item_entries(child)
    elif isinstance(value, list):
        for child in value:
            yield from item_entries(child)


def has_set_damage(entry: dict[str, Any], *, maximum: float) -> bool:
    for function in entry.get("functions", []):
        if not isinstance(function, dict) or function.get("function") != "minecraft:set_damage":
            continue
        damage = function.get("damage")
        if not isinstance(damage, dict):
            return False
        if damage.get("type") != "minecraft:uniform":
            return False
        minimum = damage.get("min")
        upper = damage.get("max")
        return (
            isinstance(minimum, (int, float))
            and isinstance(upper, (int, float))
            and 0 < float(minimum) <= float(upper) <= maximum
        )
    return False


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def fail(errors: list[str]) -> int:
    print("FAIL: dungeon tool loot progression")
    for error in errors:
        print(f" - {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    args = parser.parse_args()

    errors: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}

    require(MODS_TOML.is_file(), "missing NeoForge mod metadata template", errors)
    if MODS_TOML.is_file():
        metadata = MODS_TOML.read_text(encoding="utf-8")
        for mod_id in ("dungeonnowloading", "betterdungeons", "dungeoncrawl"):
            dependency = f'modId="{mod_id}"'
            require(dependency in metadata, f"missing optional load-order edge for {mod_id}", errors)
            if dependency in metadata:
                block = metadata.split(dependency, 1)[1].split("[[dependencies.", 1)[0]
                require('type="optional"' in block, f"{mod_id} dependency is not optional", errors)
                require('ordering="AFTER"' in block, f"companion mod does not load after {mod_id}", errors)

    for relative, expected_entries in TABLES.items():
        path = DATA / relative
        require(path.is_file(), f"missing exact loot override {relative}", errors)
        if not path.is_file():
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON in {relative}: {exc}")
            continue
        require(isinstance(document, dict), f"{relative} is not a JSON object", errors)
        if not isinstance(document, dict):
            continue
        loaded[relative] = document

        pools = document.get("pools")
        require(isinstance(pools, list), f"{relative} has no pools array", errors)
        if not isinstance(pools, list):
            continue
        counts = tuple(
            len(pool.get("entries", [])) if isinstance(pool, dict) else -1
            for pool in pools
        )
        require(
            counts == expected_entries,
            f"{relative} changed upstream pool topology: expected {expected_entries}, got {counts}",
            errors,
        )

        entries = list(item_entries(document))
        names = {entry["name"] for entry in entries}
        require(
            bool(names & LOW_MID_EQUIPMENT),
            f"{relative} no longer offers a low/mid-tier exploration tool or weapon",
            errors,
        )
        require(
            "apotheosis:" not in path.read_text(encoding="utf-8"),
            f"{relative} unexpectedly introduces Apotheosis loot",
            errors,
        )

        diamond_entries = [entry for entry in entries if entry["name"] in DIAMOND_TOOLS]
        if relative in COMMON_TABLES:
            require(
                not diamond_entries,
                f"common table {relative} still exposes diamond tools",
                errors,
            )
        else:
            require(
                bool(diamond_entries),
                f"rare/dangerous table {relative} lost every high-tier find",
                errors,
            )

        for entry in diamond_entries:
            require(
                entry.get("weight", 1) == 1,
                f"{relative} gives {entry['name']} more than rare weight 1",
                errors,
            )
            require(
                has_set_damage(entry, maximum=0.2),
                f"{relative} gives an undamaged or insufficiently worn {entry['name']}",
                errors,
            )

        for pool_index, pool in enumerate(pools):
            if not isinstance(pool, dict):
                continue
            pool_entries = [entry for entry in item_entries(pool.get("entries", []))]
            diamond_weight = sum(
                float(entry.get("weight", 1))
                for entry in pool_entries
                if entry["name"] in DIAMOND_TOOLS
            )
            total_weight = sum(float(entry.get("weight", 1)) for entry in pool_entries)
            if diamond_weight:
                share = diamond_weight / total_weight if total_weight else 1.0
                require(
                    share <= 0.10,
                    f"{relative} pool {pool_index} diamond-tool weight share {share:.1%} exceeds 10%",
                    errors,
                )

    require(len(loaded) == 8, f"loaded {len(loaded)} of 8 exact overrides", errors)

    damaged_mid_tables = 0
    for relative, document in loaded.items():
        if any(
            entry["name"] in LOW_MID_EQUIPMENT and has_set_damage(entry, maximum=0.35)
            for entry in item_entries(document)
        ):
            damaged_mid_tables += 1
    require(
        damaged_mid_tables >= 4,
        "fewer than four tables retain deliberately worn low/mid-tier tool finds",
        errors,
    )

    require(MIXIN_CONFIG.is_file(), "missing mixin configuration", errors)
    require(MIXIN_SOURCE.is_file(), "missing Dungeon Crawl dynamic-loot mixin", errors)
    if MIXIN_CONFIG.is_file():
        mixin_config = json.loads(MIXIN_CONFIG.read_text(encoding="utf-8"))
        require(
            "DungeonCrawlRandomItemsMixin" in mixin_config.get("mixins", []),
            "Dungeon Crawl dynamic-loot mixin is not registered",
            errors,
        )
    if MIXIN_SOURCE.is_file():
        source = MIXIN_SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "@Pseudo",
            'targets = "xiroc.dungeoncrawl.dungeon.treasure.RandomItems"',
            '@Inject(method = "generate", at = @At("RETURN")',
            "!stack.isDamageableItem()",
            "0.10D + (0.04D * boundedLevel)",
            "0.20D + (0.05D * boundedLevel)",
            "stack.setDamageValue",
        ):
            require(fragment in source, f"dynamic-loot mixin lacks {fragment!r}", errors)

    mods = args.instance.resolve() / "mods"
    dungeon_crawl_jars = sorted(mods.glob("DungeonCrawl-*.jar"))
    require(
        len(dungeon_crawl_jars) == 1,
        f"expected one installed Dungeon Crawl JAR, found {len(dungeon_crawl_jars)}",
        errors,
    )
    if len(dungeon_crawl_jars) == 1:
        with zipfile.ZipFile(dungeon_crawl_jars[0]) as archive:
            names = set(archive.namelist())
            require(
                "xiroc/dungeoncrawl/dungeon/treasure/RandomItems.class" in names,
                "installed Dungeon Crawl no longer exposes the dynamic equipment target",
                errors,
            )
            for level in range(1, 6):
                path = f"data/dungeoncrawl/treasure/stage_{level}.json"
                require(path in names, f"installed Dungeon Crawl lacks {path}", errors)
            random_item_tables = 0
            for name in names:
                if (
                    name.startswith("data/dungeoncrawl/loot_table/chests/")
                    and name.endswith(".json")
                    and b"dungeoncrawl:random_item" in archive.read(name)
                ):
                    random_item_tables += 1
            require(
                random_item_tables == 7,
                "Dungeon Crawl random-item chest topology changed: "
                f"expected 7 tables, got {random_item_tables}",
                errors,
            )

    if errors:
        return fail(errors)
    print(
        "PASS: 8 exact Dungeon Now Loading/YUNG loot overrides preserve their pool topology; "
        "common chests expose no diamond tools, rare finds are weight <= 10% and heavily worn, "
        f"{damaged_mid_tables} tables retain damaged low/mid-tier gear, and Dungeon Crawl's "
        "7 dynamic equipment tables now return progressively worn finds."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
