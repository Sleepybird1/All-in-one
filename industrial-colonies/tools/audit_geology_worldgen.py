"""Read-only inventory of installed geological placement definitions.

Prints candidate definitions; does not modify installed mods, configs or worlds.
Output JSON is supplied on stdout so it can also be consumed as a diagnostic tool.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

PATTERN = re.compile(r"(?:^|[:_/])(?:iron|copper|redstone|coal|diamond|gold|zinc|lead|nickel|lithium|tin|osmium|uranium|thorium|titanium|tungsten|alumin(?:um|ium)|cobalt|platinum|iridium|boron|beryllium|magnesium|silver|chromium|bauxite|galena|lignite|hematite|magnetite|cassiterite|ilmenite|wolframite|crimsite|asurine|ochrum|veridium|steel|yellorite|allthemodium|mithril)(?:$|[_/])", re.I)
DATA = re.compile(r"(?:^|/)data/([^/]+)/(worldgen/(?:configured_feature|placed_feature|biome|noise_settings|configured_carver|processor_list)|neoforge/biome_modifier|forge/biome_modifier|lithostitched/(?:worldgen_modifier|surface_rule)|tags/worldgen/(?:placed_feature|biome))/(.+)\.json$")
STEPS = {"raw_generation", "lakes", "local_modifications", "underground_structures", "surface_structures", "strongholds", "underground_ores", "underground_decoration", "fluid_springs", "vegetal_decoration", "top_layer_modification"}
STRATA_RESOURCES = {"create:asurine", "create:crimsite", "create:ochrum", "create:veridium", "tfmg:bauxite", "tfmg:galena", "tfmg:lignite"}

def resources(path: Path):
    with zipfile.ZipFile(path) as archive:
        yield from archive_resources(archive, path.name)


def archive_resources(archive, source):
    """Include bundled datapack paths and jar-in-jar resources, without extraction."""
    for name in archive.namelist():
        if name.endswith(".jar"):
            with zipfile.ZipFile(io.BytesIO(archive.read(name))) as nested:
                yield from archive_resources(nested, source + "!/" + name)
        match = DATA.search(name)
        if not match:
            continue
        raw = archive.read(name)
        try:
            content = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        yield {"jar": source, "path": name, "id": match[1]+":"+match[3], "kind": match[2], "sha256": hashlib.sha256(raw).hexdigest(), "data": content}

def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value: yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values(): yield from strings(item)

def audit(pack: Path, minecraft: Path):
    jars = sorted((pack/"mods").glob("*.jar"))
    records = [row for jar in [minecraft, *jars] for row in resources(jar)]
    configured = [r for r in records if r["kind"] == "worldgen/configured_feature"]
    candidates = {r["id"] for r in configured if PATTERN.search(r["id"]) or any(PATTERN.search(s) for s in strings(r["data"]))}
    placed = [r for r in records if r["kind"] == "worldgen/placed_feature"]
    hits = [r for r in placed if PATTERN.search(r["id"]) or any(s in candidates or PATTERN.search(s) for s in strings(r["data"]))]
    placed_ids = {r["id"] for r in hits}
    related = [r for r in records if r["kind"] not in {"worldgen/configured_feature", "worldgen/placed_feature"} and (any(s in placed_ids for s in strings(r["data"])) or any(PATTERN.search(s) for s in strings(r["data"])) or "noise_settings" in r["kind"])]
    return {"pack": str(pack), "minecraft": str(minecraft), "jar_count": len(jars), "registry_resource_count": len(records), "candidate_configured": [r for r in configured if r["id"] in candidates], "candidate_placed": hits, "related": related, "all_registry_resources": records}


def filtered_strata(original):
    """Keep geometry/probabilities; erase only economic output states, not layers."""
    result = copy.deepcopy(original)
    changes = 0
    for pattern in result["config"]["layer_patterns"]:
        for layer in pattern:
            for targets in layer["targets"]:
                for target in targets:
                    if target["state"]["Name"] not in STRATA_RESOURCES:
                        continue
                    base = target["target"]["tag"]
                    if base == "minecraft:stone_ore_replaceables":
                        target["state"] = {"Name": "minecraft:stone"}
                    elif base == "minecraft:deepslate_ore_replaceables":
                        target["state"] = {"Name": "minecraft:deepslate", "Properties": {"axis": "y"}}
                    else:
                        raise ValueError(f"Unknown native host target: {base}")
                    changes += 1
    return result, changes


def project_validation(result, project):
    """Static validation only; runtime datapack order, mixins and chunks still need checks."""
    data = project / "src/main/resources/data"
    errors = []

    def resolve(tag, visited=()):
        if tag in visited:
            raise ValueError(f"Circular feature tag: {visited} -> {tag}")
        ns, path = tag.split(":", 1)
        content = json.loads((data/ns/"tags/worldgen/placed_feature"/(path+".json")).read_text())
        ids = []
        for entry in content["values"]:
            value = entry if isinstance(entry, str) else entry["id"]
            if value.startswith("#"):
                ids.extend(resolve(value[1:], (*visited, tag)))
            else:
                if not value.startswith("minecraft:") and (not isinstance(entry, dict) or entry.get("required") is not False):
                    errors.append("Optional mod feature must have required=false: " + value)
                ids.append(value)
        return ids

    ids = resolve("industrial_colonies:geology/default_ore_features")
    if len(ids) != len(set(ids)):
        errors.append("Duplicate forbidden feature IDs")
    registry_ids = {r["id"] for r in result["all_registry_resources"] if r["kind"] == "worldgen/placed_feature"}
    for missing in sorted(set(ids) - registry_ids):
        errors.append("Not present in audited installed registry JSON: " + missing)
    for forbidden in ids:
        if any(part in forbidden for part in ("emerald", "lapis", "fluorite", "quartz", "salt", "fossil", ":nether/", ":moon_", ":mars_", ":venus_", ":glacio_", ":mercury_")):
            errors.append("Protected feature or non-Overworld placement in suppression: " + forbidden)
    modifier = json.loads((data/"industrial_colonies/neoforge/biome_modifier/geology_remove_default_ores.json").read_text())
    if modifier["biomes"] != "#minecraft:is_overworld" or set(modifier["steps"]) != STEPS:
        errors.append("Suppression must use strict Overworld biome tag and every decoration step")
    if modifier["features"] != "#industrial_colonies:geology/default_ore_features":
        errors.append("Biome removal and Java guard must share the same feature tag")
    strata = []
    for ns, jar, original, replacement in [
        ("create", "create-1.21.1-6.0.10.jar", "striated_ores_overworld", "geology_create_decorative_strata"),
        ("tfmg", "tfmg-1.2.0.jar", "tfmg_striated_ores_overworld", "geology_tfmg_fireclay_strata"),
    ]:
        rows = {r["kind"]: r for r in result["all_registry_resources"] if r["jar"] == jar and r["id"] == ns+":"+original}
        expected, count = filtered_strata(rows["worldgen/configured_feature"]["data"])
        actual = json.loads((data/"industrial_colonies/worldgen/configured_feature"/(replacement+".json")).read_text())
        if actual != expected:
            errors.append("Stratum geometry/probability or non-resource material changed: " + ns)
        expected_placed = copy.deepcopy(rows["worldgen/placed_feature"]["data"])
        expected_placed["feature"] = "industrial_colonies:" + replacement
        actual_placed = json.loads((data/"industrial_colonies/worldgen/placed_feature"/(replacement+".json")).read_text())
        if actual_placed != expected_placed:
            errors.append("Stratum placement probability/height changed: " + ns)
        strata.append({"mod": ns, "replaced_state_entries": count, "patterns": len(actual["config"]["layer_patterns"]), "size": actual["config"]["size"]})
    ru = json.loads((data/"regions_unexplored/lithostitched/surface_rule/overworld/caves/redstone_caves.json").read_text())
    if "regions_unexplored:raw_redstone_block" in set(strings(ru)):
        errors.append("RU surface rule still generates raw redstone")
    return {"valid": not errors, "errors": errors, "forbidden_feature_count": len(ids), "forbidden_features": sorted(ids), "strata": strata, "scope": "static registry/data validation, not runtime world-generation verification"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, default=Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one"))
    parser.add_argument("--minecraft", type=Path, default=Path(r"C:\Users\GodPC\curseforge\minecraft\Install\versions\1.21.1\1.21.1.jar"))
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--validate-project", type=Path, metavar="PROJECT")
    args = parser.parse_args()
    result = audit(args.pack, args.minecraft)
    if args.validate_project:
        validation = project_validation(result, args.validate_project)
        print(json.dumps(validation, indent=2))
        raise SystemExit(0 if validation["valid"] else 1)
    elif args.summary:
        print(f"{result['jar_count']} active JARs; {result['registry_resource_count']} registry resources")
        for jar in sorted({r["jar"] for r in result["candidate_placed"]}):
            print("\n" + jar)
            for row in result["candidate_placed"]:
                if row["jar"] == jar:
                    print("  " + row["id"])
    else:
        print(json.dumps(result, indent=2))
