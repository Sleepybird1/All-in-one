#!/usr/bin/env python3
"""Validate the source-owned Moon/Mars/Venus/Mercury destination bridge."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("src/main/resources/data")
MOD_METADATA = Path("src/main/templates/META-INF/neoforge.mods.toml")

MOON_UNIVERSE = Path("src/main/resources/data/rocketnautics/universe_planets/moon.json")
MARS_UNIVERSE = Path("src/main/resources/data/rocketnautics/universe_planets/mars.json")
VENUS_UNIVERSE = Path("src/main/resources/data/rocketnautics/universe_planets/venus.json")
MERCURY_UNIVERSE = Path("src/main/resources/data/rocketnautics/universe_planets/mercury.json")
MOON_PHYSICS = Path(
    "src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_moon.json"
)
MARS_PHYSICS = Path(
    "src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_mars.json"
)
VENUS_PHYSICS = Path(
    "src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_venus.json"
)
MERCURY_PHYSICS = Path(
    "src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_mercury.json"
)

DRAG_CURVE = [
    {"altitude": 4000.0, "slope": 0.0, "value": 1.0},
    {"altitude": 7000.0, "slope": -0.0006, "value": 0.0},
]

UNIVERSE_CONTRACTS: dict[Path, dict[str, Any]] = {
    MOON_UNIVERSE: {
        "parent": "overworld",
        "acceleration_at_surface": 1.622,
        "dimension_data": {
            "allowed_transfer": "all",
            "apply_gravity_correction_to_entities_in_dimension": False,
            "atmosphere_composition": {},
            "dimension_transfer_height": 20000,
            "entity_drag_multiplier": DRAG_CURVE,
            "linked_dimension": "ad_astra:moon",
            "render_universe_in_dimension": False,
        },
        "planet_extras": {"light_source_name": "sol", "has_clouds": False},
        "name": "moon",
        "planet_texture": {
            "type": "resloc",
            "texture": "ad_astra:textures/environment/moon.png",
        },
        "position": {
            "type": "circular_orbit_period",
            "orbit_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
            "period_seconds": 28800.0,
        },
        "priority": 2000,
        "radius": 750000.0,
        "rotation": {"type": "tidal_lock", "rotations_per_orbit": -1.0},
    },
    MARS_UNIVERSE: {
        "parent": "sol",
        "acceleration_at_surface": 3.72076,
        "dimension_data": {
            "allowed_transfer": "all",
            "apply_gravity_correction_to_entities_in_dimension": False,
            "atmosphere_composition": {},
            "dimension_transfer_height": 20000,
            "entity_drag_multiplier": DRAG_CURVE,
            "linked_dimension": "ad_astra:mars",
            "render_universe_in_dimension": False,
        },
        "planet_extras": {"light_source_name": "sol", "has_clouds": False},
        "name": "mars",
        "planet_texture": {
            "type": "resloc",
            "texture": "ad_astra:textures/environment/mars.png",
        },
        "position": {
            "type": "circular_orbit_period",
            "orbit_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
            "period_seconds": 1136400.0,
        },
        "priority": 2000,
        "radius": 1590000.0,
        "rotation": {
            "type": "period",
            "period_seconds": 1230.0,
            "rotation_axis": {"x": 0.0, "y": -1.0, "z": 0.0},
        },
    },
    VENUS_UNIVERSE: {
        "parent": "sol",
        "acceleration_at_surface": 8.87,
        "dimension_data": {
            "allowed_transfer": "all",
            "apply_gravity_correction_to_entities_in_dimension": False,
            "atmosphere_composition": {},
            "dimension_transfer_height": 20000,
            "entity_drag_multiplier": DRAG_CURVE,
            "linked_dimension": "ad_astra:venus",
            "render_universe_in_dimension": False,
        },
        "planet_extras": {"light_source_name": "sol", "has_clouds": False},
        "name": "venus",
        "planet_texture": {
            "type": "resloc",
            "texture": "ad_astra:textures/environment/venus.png",
        },
        "position": {
            "type": "circular_orbit_period",
            "orbit_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
            "period_seconds": 371700.0,
        },
        "priority": 2000,
        "radius": 2850000.0,
        "rotation": {
            "type": "period",
            "period_seconds": 12600.0,
            "rotation_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
        },
    },
    MERCURY_UNIVERSE: {
        "parent": "sol",
        "acceleration_at_surface": 3.7,
        "dimension_data": {
            "allowed_transfer": "all",
            "apply_gravity_correction_to_entities_in_dimension": False,
            "atmosphere_composition": {},
            "dimension_transfer_height": 20000,
            "entity_drag_multiplier": DRAG_CURVE,
            "linked_dimension": "ad_astra:mercury",
            "render_universe_in_dimension": False,
        },
        "planet_extras": {"light_source_name": "sol", "has_clouds": False},
        "name": "mercury",
        "planet_texture": {
            "type": "resloc",
            "texture": "ad_astra:textures/environment/mercury.png",
        },
        "position": {
            "type": "circular_orbit_period",
            "orbit_axis": {"x": 0.0, "y": 1.0, "z": 0.0},
            "period_seconds": 145600.0,
        },
        "priority": 2000,
        "radius": 1219850.0,
        "rotation": {
            "type": "period",
            "period_seconds": 2930.0,
            "rotation_axis": {"x": 0.0, "y": -1.0, "z": 0.0},
        },
    },
}

PHYSICS_CONTRACTS: dict[Path, dict[str, Any]] = {
    MOON_PHYSICS: {
        "dimension": "ad_astra:moon",
        "priority": 2000,
        "universal_drag": 0.0,
        "base_gravity": [0.0, -1.622, 0.0],
        "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    },
    MARS_PHYSICS: {
        "dimension": "ad_astra:mars",
        "priority": 2000,
        "universal_drag": 0.0,
        "base_gravity": [0.0, -3.72076, 0.0],
        "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    },
    VENUS_PHYSICS: {
        "dimension": "ad_astra:venus",
        "priority": 2000,
        "universal_drag": 0.0,
        "base_gravity": [0.0, -8.87, 0.0],
        "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    },
    MERCURY_PHYSICS: {
        "dimension": "ad_astra:mercury",
        "priority": 2000,
        "universal_drag": 0.0,
        "base_gravity": [0.0, -3.7, 0.0],
        "base_pressure": 0.0,
        "magnetic_north": [0.0, 0.0, 0.0],
    },
}

EXPECTED_LINKS = {
    "ad_astra:moon": MOON_UNIVERSE,
    "ad_astra:mars": MARS_UNIVERSE,
    "ad_astra:venus": VENUS_UNIVERSE,
    "ad_astra:mercury": MERCURY_UNIVERSE,
}
FORBIDDEN_DESTINATION_MARKERS = ("glacio", "warp")
INTERSTELLAR_UNIVERSE_RESOURCES = frozenset(
    {
        "src/main/resources/data/rocketnautics/universe_planets/glacio.json",
        "src/main/resources/data/rocketnautics/universe_planets/proxima_centauri.json",
    }
)
INTERSTELLAR_PHYSICS_RESOURCES = frozenset(
    {
        "src/main/resources/data/industrial_colonies/dimension_physics/ad_astra_glacio.json",
    }
)


def read_json(path: Path, label: str, failures: list[str]) -> Any | None:
    if not path.is_file():
        failures.append(f"missing {label}: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"invalid {label} {path}: {exc}")
        return None


def relative_to_project(path: Path, project: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()


def validate_ad_astra_dependency(project: Path, failures: list[str]) -> None:
    path = project / MOD_METADATA
    if not path.is_file():
        failures.append(f"missing mod metadata: {MOD_METADATA.as_posix()}")
        return
    source = path.read_text(encoding="utf-8-sig")
    blocks = re.findall(
        r"\[\[dependencies\.\$\{mod_id\}\]\](.*?)(?=\n\[\[|\Z)",
        source,
        flags=re.DOTALL,
    )
    matching = [block for block in blocks if re.search(r'\bmodId\s*=\s*"ad_astra"', block)]
    if len(matching) != 1:
        failures.append(
            "mod metadata must contain exactly one required ad_astra dependency; "
            f"found {len(matching)}"
        )
        return
    block = matching[0]
    required_fields = {
        "type": "required",
        "versionRange": "[1.16.22,1.17.0)",
        "ordering": "AFTER",
        "side": "BOTH",
    }
    for field, expected in required_fields.items():
        match = re.search(rf'\b{re.escape(field)}\s*=\s*"([^"]+)"', block)
        actual = match.group(1) if match else None
        if actual != expected:
            failures.append(
                f"ad_astra dependency {field} drifted: expected {expected!r}, found {actual!r}"
            )


def texture_jar_entry(resource_location: str) -> str:
    namespace, path = resource_location.split(":", 1)
    return f"assets/{namespace}/{path}"


def validate_installed_textures(mods: Path, failures: list[str]) -> None:
    if not mods.is_dir():
        failures.append(f"missing installed mods directory: {mods}")
        return
    candidates = sorted(
        path
        for path in mods.glob("*.jar")
        if re.match(r"^ad[_-]?astra-", path.name, flags=re.IGNORECASE)
        or path.name.lower().startswith("adastra-")
    )
    if len(candidates) != 1:
        failures.append(
            "expected exactly one active Ad Astra core JAR in installed mods; "
            f"found {[path.name for path in candidates]}"
        )
        return

    textures = {
        expected["planet_texture"]["texture"]
        for expected in UNIVERSE_CONTRACTS.values()
    }
    try:
        with zipfile.ZipFile(candidates[0]) as archive:
            entries = set(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append(f"cannot inspect installed Ad Astra JAR {candidates[0]}: {exc}")
        return
    for texture in sorted(textures):
        entry = texture_jar_entry(texture)
        if entry not in entries:
            failures.append(
                f"destination texture {texture} is missing from installed JAR "
                f"{candidates[0].name} (expected ZIP entry {entry})"
            )


def validate(project: Path, mods: Path | None = None) -> list[str]:
    failures: list[str] = []

    for relative, expected in UNIVERSE_CONTRACTS.items():
        payload = read_json(project / relative, "Rocketnautics universe override", failures)
        if payload is not None and payload != expected:
            failures.append(f"{relative.as_posix()} drifted from the exact destination contract")

    for relative, expected in PHYSICS_CONTRACTS.items():
        payload = read_json(project / relative, "Sable dimension-physics bridge", failures)
        if payload is not None and payload != expected:
            failures.append(f"{relative.as_posix()} drifted from the exact ship-physics contract")

    universe_root = project / DATA_ROOT
    universe_paths = sorted(universe_root.glob("*/universe_planets/*.json"))
    physics_paths = sorted(universe_root.glob("*/dimension_physics/*.json"))
    links: dict[str, list[str]] = defaultdict(list)

    for path in universe_paths:
        relative = relative_to_project(path, project)
        independently_validated = relative in INTERSTELLAR_UNIVERSE_RESOURCES
        payload = read_json(path, "source-owned universe resource", failures)
        if payload is None:
            continue
        normalized = json.dumps(payload, sort_keys=True).lower()
        if not independently_validated and any(
            marker in normalized or marker in relative.lower()
            for marker in FORBIDDEN_DESTINATION_MARKERS
        ):
            failures.append(f"Glacio/warp destination activation is outside this slice: {relative}")
        dimension_data = payload.get("dimension_data")
        if not isinstance(dimension_data, dict):
            continue
        linked = dimension_data.get("linked_dimension")
        if not isinstance(linked, str):
            continue
        links[linked].append(relative)
        expected_path = EXPECTED_LINKS.get(linked)
        if expected_path is None:
            if not independently_validated:
                failures.append(f"unreviewed survival destination link {linked} in {relative}")
        elif relative != expected_path.as_posix():
            failures.append(
                f"duplicate/noncanonical survival link {linked} in {relative}; "
                f"owner is {expected_path.as_posix()}"
            )

    for linked, expected_path in EXPECTED_LINKS.items():
        owners = links.get(linked, [])
        if owners != [expected_path.as_posix()]:
            failures.append(
                f"{linked} must have exactly one source-owned universe link at "
                f"{expected_path.as_posix()}; found {owners}"
            )
    for linked, owners in links.items():
        if len(owners) > 1:
            failures.append(f"duplicate survival link {linked}: {owners}")

    for path in physics_paths:
        relative = relative_to_project(path, project)
        independently_validated = relative in INTERSTELLAR_PHYSICS_RESOURCES
        payload = read_json(path, "source-owned dimension physics resource", failures)
        if payload is None:
            continue
        normalized = json.dumps(payload, sort_keys=True).lower()
        if not independently_validated and any(
            marker in normalized or marker in relative.lower()
            for marker in FORBIDDEN_DESTINATION_MARKERS
        ):
            failures.append(f"Glacio/warp physics activation is outside this slice: {relative}")

    validate_ad_astra_dependency(project, failures)
    if mods is not None:
        validate_installed_textures(mods, failures)
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument(
        "--mods",
        type=Path,
        help="Installed mods directory used to prove the selected Ad Astra textures exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(
        args.project.resolve(),
        args.mods.resolve() if args.mods is not None else None,
    )
    if failures:
        print("FAIL: Moon/Mars/Venus/Mercury destination bridge is invalid")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(
        "PASS: Rocketnautics owns exactly one Moon, Mars, Venus, and Mercury route into Ad Astra; "
        "Sable ship gravity is pinned without duplicate player gravity or atmosphere handling."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
