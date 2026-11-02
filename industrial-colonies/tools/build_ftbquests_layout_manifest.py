#!/usr/bin/env python3
"""Build a lossless, renderer-neutral layout manifest from the Draw.io export.

This deliberately does not write FTB Quests SNBT.  FTB Quests 2101.1.34 has a
single scalar quest size and cubic-Bezier dependency control points, so writing
the rectangular geometry or orthogonal routes into native quest data would be
an inaccurate API guess.  The generated manifest is an input contract for a
future client-side layout renderer while native quest data remains standard.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT.parent
    / "industrial-audit"
    / "drawio-export"
    / "drawio_tree.json"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT.parent
    / "industrial-audit"
    / "ftb-quests-layout"
    / "drawio_layout_manifest.json"
)

SCHEMA_VERSION = 1
CONSUMER = "future-client-layout-addon"
REQUIRED_NODE_FIELDS = ("id", "label", "x", "y", "width", "height")
REQUIRED_EDGE_FIELDS = ("id", "source", "target", "style", "points")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_style(style: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for component in style.split(";"):
        if not component or "=" not in component:
            continue
        key, value = component.split("=", 1)
        values[key] = value
    return values


def float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    return float(value)


def anchor_from_style(style: dict[str, str], prefix: str) -> dict[str, float] | None:
    x = float_or_none(style.get(f"{prefix}X"))
    y = float_or_none(style.get(f"{prefix}Y"))
    if x is None or y is None:
        return None
    return {
        "x_ratio": x,
        "y_ratio": y,
        "dx": float_or_none(style.get(f"{prefix}Dx")) or 0.0,
        "dy": float_or_none(style.get(f"{prefix}Dy")) or 0.0,
    }


def slug(value: str) -> str:
    normalized = value.lower().replace("—", "-").replace("–", "-")
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return normalized[:48] or "quest"


def layout_key(node_id: str, label: str) -> str:
    suffix = hashlib.sha1(node_id.encode("utf-8")).hexdigest()[:8]
    return f"{slug(label)}_{suffix}"


def require_fields(record: dict[str, Any], fields: tuple[str, ...], kind: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise ValueError(f"{kind} {record.get('id', '<unknown>')} missing {missing}")


def build_manifest(source_path: Path) -> dict[str, Any]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    raw_nodes = source.get("nodes", [])
    raw_edges = source.get("edges", [])

    nodes: list[dict[str, Any]] = []
    keys_by_id: dict[str, str] = {}
    for raw in raw_nodes:
        require_fields(raw, REQUIRED_NODE_FIELDS, "node")
        node_id = str(raw["id"])
        key = layout_key(node_id, str(raw["label"]))
        if node_id in keys_by_id:
            raise ValueError(f"duplicate Draw.io node id: {node_id}")
        if key in keys_by_id.values():
            raise ValueError(f"layout-key collision: {key}")
        keys_by_id[node_id] = key
        x = float(raw["x"])
        y = float(raw["y"])
        width = float(raw["width"])
        height = float(raw["height"])
        nodes.append(
            {
                "layout_key": key,
                "drawio_id": node_id,
                "label": str(raw["label"]),
                "bounds": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                },
                "center": {"x": x + width / 2.0, "y": y + height / 2.0},
                "drawio_style": str(raw.get("style", "")),
            }
        )

    edges: list[dict[str, Any]] = []
    edge_ids: set[str] = set()
    explicit_waypoint_edges = 0
    for raw in raw_edges:
        require_fields(raw, REQUIRED_EDGE_FIELDS, "edge")
        edge_id = str(raw["id"])
        if edge_id in edge_ids:
            raise ValueError(f"duplicate Draw.io edge id: {edge_id}")
        edge_ids.add(edge_id)
        source_id = str(raw["source"])
        target_id = str(raw["target"])
        if source_id not in keys_by_id or target_id not in keys_by_id:
            raise ValueError(
                f"edge {edge_id} has unresolved endpoint(s): {source_id} -> {target_id}"
            )
        style = parse_style(str(raw["style"]))
        if style.get("edgeStyle") != "orthogonalEdgeStyle":
            raise ValueError(f"edge {edge_id} is not orthogonalEdgeStyle")
        points = [
            {"x": float(point["x"]), "y": float(point["y"])}
            for point in raw.get("points", [])
        ]
        if points:
            explicit_waypoint_edges += 1
        edges.append(
            {
                "drawio_id": edge_id,
                "source": {
                    "layout_key": keys_by_id[source_id],
                    "drawio_id": source_id,
                    "anchor": anchor_from_style(style, "exit"),
                },
                "target": {
                    "layout_key": keys_by_id[target_id],
                    "drawio_id": target_id,
                    "anchor": anchor_from_style(style, "entry"),
                },
                "routing": "orthogonal",
                "route_resolution": (
                    "explicit_waypoints_preserved" if points else "router_required"
                ),
                "explicit_waypoints": points,
                "drawio_style": str(raw["style"]),
            }
        )

    widths = sorted({node["bounds"]["width"] for node in nodes})
    heights = sorted({node["bounds"]["height"] for node in nodes})
    return {
        "schema_version": SCHEMA_VERSION,
        "consumer": CONSUMER,
        "coordinate_space": "drawio_page_units",
        "contract": {
            "minecolonies_research_remains_authoritative_for_progression": True,
            "ftbquests_completion_must_not_grant_progression": True,
            "this_manifest_controls_client_layout_only": True,
            "unresolved_routes_must_not_be_treated_as_straight_lines": True,
            "router_required_meaning": (
                "Draw.io stored no explicit bends; a deterministic orthogonal router "
                "must resolve the path from bounds and entry/exit anchors."
            ),
        },
        "source_export": {
            "path": str(source_path.resolve()),
            "sha256": file_sha256(source_path),
            "authoritative_drawio_path": source.get("source"),
            "authoritative_drawio_sha256": source.get("source_sha256"),
            "diagram_name": source.get("diagram_name"),
        },
        "statistics": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "explicit_waypoint_edge_count": explicit_waypoint_edges,
            "router_required_edge_count": len(edges) - explicit_waypoint_edges,
            "node_widths": widths,
            "node_heights": heights,
        },
        "nodes": nodes,
        "edges": edges,
    }


def validate_manifest(manifest: dict[str, Any], source_path: Path) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if manifest.get("consumer") != CONSUMER:
        errors.append(f"consumer must be {CONSUMER!r}")
    source_export = manifest.get("source_export", {})
    if source_export.get("sha256") != file_sha256(source_path):
        errors.append("source export SHA-256 mismatch")

    nodes = manifest.get("nodes", [])
    edges = manifest.get("edges", [])
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if len(nodes) != len(source.get("nodes", [])):
        errors.append("node count does not match source export")
    if len(edges) != len(source.get("edges", [])):
        errors.append("edge count does not match source export")

    node_ids = {node.get("drawio_id") for node in nodes}
    layout_keys = {node.get("layout_key") for node in nodes}
    if len(node_ids) != len(nodes):
        errors.append("manifest contains duplicate node ids")
    if len(layout_keys) != len(nodes):
        errors.append("manifest contains duplicate layout keys")
    for edge in edges:
        if edge.get("routing") != "orthogonal":
            errors.append(f"edge {edge.get('drawio_id')} is not orthogonal")
        for endpoint in ("source", "target"):
            value = edge.get(endpoint, {})
            if value.get("drawio_id") not in node_ids:
                errors.append(
                    f"edge {edge.get('drawio_id')} has unknown {endpoint} node"
                )
            if value.get("layout_key") not in layout_keys:
                errors.append(
                    f"edge {edge.get('drawio_id')} has unknown {endpoint} layout key"
                )
        waypoints = edge.get("explicit_waypoints", [])
        expected_resolution = (
            "explicit_waypoints_preserved" if waypoints else "router_required"
        )
        if edge.get("route_resolution") != expected_resolution:
            errors.append(
                f"edge {edge.get('drawio_id')} has inconsistent route_resolution"
            )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate an existing output against the current source export",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if args.check:
        if not output_path.is_file():
            print(f"ERROR: manifest does not exist: {output_path}", file=sys.stderr)
            return 1
        manifest = json.loads(output_path.read_text(encoding="utf-8"))
    else:
        manifest = build_manifest(input_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    errors = validate_manifest(manifest, input_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    stats = manifest["statistics"]
    action = "validated" if args.check else "wrote"
    print(
        f"{action} {output_path}: {stats['node_count']} nodes, "
        f"{stats['edge_count']} edges, "
        f"{stats['router_required_edge_count']} router-required routes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
