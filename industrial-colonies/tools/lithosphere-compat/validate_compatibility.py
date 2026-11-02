"""Read-only exact compatibility audit. No game, build, network, extraction or config writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ECONOMIC = {"wythers:ores/" + name for name in (
    "ore_coal_windswept", "ore_diamond_volcanic", "ore_gold_volcanic",
    "ore_iron_windswept", "ore_redstone_windswept")}
DECORATIVE_CONFIGURED = {"ore_andesite", "ore_diorite", "ore_granite", "ore_dirt", "ore_gravel"}
DECORATIVE_PLACED = {"ore_andesite_lower", "ore_andesite_upper", "ore_diorite_lower", "ore_diorite_upper",
                    "ore_granite_lower", "ore_granite_upper", "ore_dirt"}

def sha(data):
    return hashlib.sha256(data).hexdigest().upper()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--pack", type=Path, default=Path(r"C:\Users\GodPC\curseforge\minecraft\Instances\All in one"))
    args = parser.parse_args()
    project = args.project.resolve()
    resources = project / "src/main/resources"
    data = resources / "data/industrial_colonies"
    checks = 0
    def require(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)
    def read(path):
        return json.loads(path.read_text(encoding="utf-8-sig"))
    feature_root = data / "tags/worldgen/placed_feature/geology"
    tag = read(feature_root / "wwoo.json")
    require(tag["replace"] is False, "Do not replace unrelated feature tags")
    require({entry["id"] for entry in tag["values"]} == ECONOMIC, "WWOO suppression must be exactly five economic IDs")
    require(all(entry.get("required") is False for entry in tag["values"]), "WWOO remains optional")
    require("#industrial_colonies:geology/wwoo" in read(feature_root / "default_ore_features.json")["values"], "WWOO tag not connected")
    require(not any("lava" in value for value in ECONOMIC), "Non-resource lava suppression")

    baseline = project / "isolated-runtime/geology-gametest-20260909-001051-895/mods/industrial_colonies-0.4.0.jar"
    require(sha(baseline.read_bytes()) == "5A4CCD0BA37629225EE88996281FCA7F1A1B704E9E1EE5DC712ECB363EEFFFBA", "Original final evidence candidate changed")
    with zipfile.ZipFile(baseline) as old:
        for name in ("settings.json", "deposit_families.json", "oil.json"):
            require((data / "geology" / name).read_bytes() == old.read("data/industrial_colonies/geology/" + name), "Approved numerical worldgen changed: " + name)
        before = json.loads(old.read("data/industrial_colonies/geology/biome_families.json"))
        after = read(data / "geology/biome_families.json")
        require("minecraft:pale_garden" in after["ordinary_forest"], "Pale Garden not classified")
        after["ordinary_forest"].remove("minecraft:pale_garden")
        require(before == after, "Other biome mappings changed")
        preserved_textures = 0
        for entry in old.namelist():
            if entry.startswith("assets/industrial_colonies/textures/block/geology/") and entry.endswith(".png"):
                require((resources / entry).read_bytes() == old.read(entry), "Approved texture changed: " + entry)
                preserved_textures += 1
        require(preserved_textures == 42, "Unexpected approved texture baseline count")

    overlay = resources / "resourcepacks/ic_wwoo_decorative"
    manifest = read(overlay / "source_manifest.json")
    expected = {"data/minecraft/worldgen/configured_feature/" + name + ".json" for name in DECORATIVE_CONFIGURED}
    expected |= {"data/minecraft/worldgen/placed_feature/" + name + ".json" for name in DECORATIVE_PLACED}
    require({row["entry"] for row in manifest["resources"]} == expected, "Decorative override scope changed")
    require({path.relative_to(overlay).as_posix() for path in (overlay / "data").rglob("*.json")} == expected, "Unexpected data in builtin compatibility pack")
    minecraft = project.parent / "gradle-user-home/caches/neoformruntime/artifacts/minecraft_1.21.1_client.jar"
    require(hashlib.sha1(minecraft.read_bytes()).hexdigest().upper() == manifest["sourceSha1"], "Wrong vanilla source artifact")
    with zipfile.ZipFile(minecraft) as vanilla:
        for row in manifest["resources"]:
            raw = (overlay / row["entry"]).read_bytes()
            require(raw == vanilla.read(row["entry"]) and sha(raw) == row["sha256"], "Override is not exact original source: " + row["entry"])
    registration = (project / "src/main/java/dev/godpc/industrialcolonies/geology/GeologyCompatibilityPacks.java").read_text()
    require('isLoaded("wwoo")' in registration and "Pack.Position.TOP" in registration and "PackSource.BUILT_IN,true" in registration, "Conditional high-priority builtin pack registration missing")
    require("GeologyCompatibilityPacks::registerPacks" in (project / "src/main/java/dev/godpc/industrialcolonies/geology/GeologyBootstrap.java").read_text(), "Pack event not registered")

    wwoo_path = args.pack / "mods/wwoo-neoforge-2.6.7.jar"
    with zipfile.ZipFile(wwoo_path) as wwoo:
        for identifier in ECONOMIC:
            key = "resources/wwoo_main/data/wythers/worldgen/placed_feature/" + identifier.split(":", 1)[1] + ".json"
            require(key in wwoo.namelist(), "Suppressed source missing from installed WWOO: " + identifier)
        require("resources/wwoo_main/data/wythers/worldgen/placed_feature/ores/ore_lava_volcanic.json" in wwoo.namelist(), "Expected retained lava source missing")
        for name in ("spring_lava", "spring_lava_frozen"):
            key = "resources/wwoo_remove_ores/data/minecraft/worldgen/placed_feature/" + name + ".json"
            require(json.loads(wwoo.read(key))["placement"][0]["count"] == 0, "Audited lava policy changed")
            require(not (overlay / ("data/minecraft/worldgen/placed_feature/" + name + ".json")).exists(), "Compatibility overrode lava policy")
    print(json.dumps({"status": "PASS", "assertions": checks, "economic_features": len(ECONOMIC),
                      "decorative_source_exact_overrides": len(expected), "approved_textures_preserved": preserved_textures,
                      "numeric_worldgen_unchanged": True, "runtime_status": "NOT RUN by this static validator"}, indent=2))

if __name__ == "__main__":
    main()
