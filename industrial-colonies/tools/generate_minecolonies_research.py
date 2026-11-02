from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_DRAWIO_SHA256 = "d941f52c1bdd8e0ab2fd30011a48b339abc526524cb6a3e314493e60a59560b5"
EXPECTED_NODES = 77
EXPECTED_EDGES = 99
EXPECTED_PRIMARY_EDGES = 61
EXPECTED_EXPLICIT_REQUIREMENTS = 99
EXPECTED_NONSTRUCTURAL_EDGES = 38
EXPECTED_MAX_DEPTH = 6
LAYOUT_SCHEMA_VERSION = 1


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"^CR\d+\s*(?:--|—)\s*", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("don't", "dont").replace("don’t", "dont")
    return re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_").lower()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def svg_tag(name: str) -> str:
    return f"{{http://www.w3.org/2000/svg}}{name}"


def parse_line_path(value: str) -> list[tuple[float, float]]:
    commands = re.findall(r"[A-Za-z]", value)
    if not commands or any(command not in {"M", "L"} for command in commands):
        raise ValueError(f"expected an absolute M/L Draw.io route, got: {value}")
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    matches = re.findall(rf"([ML])\s*({number})[\s,]+({number})", value)
    if len(matches) != len(commands):
        raise ValueError(f"could not parse every M/L coordinate in Draw.io route: {value}")
    return [(float(x), float(y)) for _, x, y in matches]


def append_distinct(points: list[dict[str, int]], point: dict[str, int]) -> None:
    if not points or points[-1] != point:
        points.append(point)


def snap_to_card_perimeter(
    center: dict[str, int],
    toward: dict[str, int],
    node_width: int,
    node_height: int,
) -> dict[str, int]:
    """Intersect a center-to-route ray with the actual integer BlockUI card rectangle."""
    node_x = center["x"] - node_width // 2
    node_y = center["y"] - node_height // 2
    dx = toward["x"] - center["x"]
    dy = toward["y"] - center["y"]
    candidates: list[tuple[float, str, int]] = []
    if dx:
        x_boundary = node_x + node_width if dx > 0 else node_x
        candidates.append(((x_boundary - center["x"]) / dx, "x", x_boundary))
    if dy:
        y_boundary = node_y + node_height if dy > 0 else node_y
        candidates.append(((y_boundary - center["y"]) / dy, "y", y_boundary))
    candidates = [candidate for candidate in candidates if candidate[0] > 0]
    if not candidates:
        raise ValueError(f"cannot snap a zero-length edge ray at {center}")
    distance, axis, boundary = min(candidates, key=lambda candidate: candidate[0])
    point = {
        "x": round(center["x"] + dx * distance),
        "y": round(center["y"] + dy * distance),
    }
    point[axis] = boundary
    return point


def point_on_card_perimeter(point: dict[str, int], node: dict[str, Any], width: int, height: int) -> bool:
    left = int(node["x"])
    top = int(node["y"])
    right = left + width
    bottom = top + height
    x = point["x"]
    y = point["y"]
    return left <= x <= right and top <= y <= bottom and (
        x in {left, right} or y in {top, bottom}
    )


def generate_client_layout(
    *,
    svg_path: Path,
    graph: dict[str, Any],
    resource_ids: dict[str, str],
    tree: dict[str, Any],
    output_path: Path,
    failures: list[str],
) -> dict[str, Any] | None:
    if not svg_path.is_file():
        failures.append(f"Missing rendered Draw.io SVG: {svg_path}")
        return None
    try:
        svg_root = ET.parse(svg_path).getroot()
    except (ET.ParseError, OSError) as exc:
        failures.append(f"Could not parse rendered Draw.io SVG {svg_path}: {exc}")
        return None
    try:
        view_box = [float(value) for value in svg_root.attrib["viewBox"].split()]
    except (KeyError, TypeError, ValueError):
        failures.append("Rendered Draw.io SVG has no four-number viewBox")
        return None
    if len(view_box) != 4:
        failures.append(f"Rendered Draw.io SVG viewBox is malformed: {view_box}")
        return None

    groups: dict[str, ET.Element] = {}
    for element in svg_root.iter(svg_tag("g")):
        cell_id = element.get("data-cell-id")
        if cell_id and cell_id not in groups:
            groups[cell_id] = element

    scale = float(tree["layout_scale"])
    margin = int(tree["layout_margin"])
    node_width = int(tree["node_width"])
    node_height = int(tree["node_height"])
    if scale <= 0 or margin < 0 or node_width <= 0 or node_height <= 0:
        failures.append("Client layout scale, margin, and node dimensions must be positive")
        return None

    id_to_node = {str(node["id"]): node for node in graph["nodes"]}
    node_centers: dict[str, dict[str, int]] = {}
    runtime_nodes: list[dict[str, Any]] = []
    for graph_node in graph["nodes"]:
        drawio_id = str(graph_node["id"])
        label = str(graph_node["label"])
        group = groups.get(drawio_id)
        rect = next(group.iter(svg_tag("rect")), None) if group is not None else None
        if rect is None:
            failures.append(f"Rendered SVG is missing node rectangle {drawio_id}: {label}")
            continue
        try:
            x = float(rect.attrib["x"])
            y = float(rect.attrib["y"])
            width = float(rect.attrib["width"])
            height = float(rect.attrib["height"])
        except (KeyError, ValueError):
            failures.append(f"Rendered SVG node rectangle is malformed {drawio_id}: {label}")
            continue
        center = {
            "x": margin + round((x + width / 2.0 - view_box[0]) * scale),
            "y": margin + round((y + height / 2.0 - view_box[1]) * scale),
        }
        node_centers[drawio_id] = center
        runtime_nodes.append(
            {
                "research": resource_ids[label],
                "drawio_id": drawio_id,
                "label": label,
                "x": center["x"] - node_width // 2,
                "y": center["y"] - node_height // 2,
                "center_x": center["x"],
                "center_y": center["y"],
            }
        )

    runtime_edges: list[dict[str, Any]] = []
    for graph_edge in graph["edges"]:
        edge_id = str(graph_edge["id"])
        source_id = str(graph_edge["source"])
        target_id = str(graph_edge["target"])
        group = groups.get(edge_id)
        path = next(group.iter(svg_tag("path")), None) if group is not None else None
        if path is None or not path.get("d"):
            failures.append(f"Rendered SVG is missing routed line for edge {edge_id}")
            continue
        if source_id not in id_to_node or target_id not in id_to_node:
            failures.append(f"Rendered SVG edge has unresolved graph endpoints: {edge_id}")
            continue
        try:
            raw_points = parse_line_path(path.attrib["d"])
        except ValueError as exc:
            failures.append(f"{edge_id}: {exc}")
            continue
        drawio_points = [
            {
                "x": margin + round((x - view_box[0]) * scale),
                "y": margin + round((y - view_box[1]) * scale),
            }
            for x, y in raw_points
        ]
        source_node = id_to_node[source_id]
        target_node = id_to_node[target_id]
        source_label = str(source_node["label"])
        target_label = str(target_node["label"])
        points: list[dict[str, int]] = []
        try:
            source_snap = snap_to_card_perimeter(
                node_centers[source_id], drawio_points[0], node_width, node_height
            )
            target_snap = snap_to_card_perimeter(
                node_centers[target_id], drawio_points[-1], node_width, node_height
            )
        except ValueError as exc:
            failures.append(f"{edge_id}: {exc}")
            continue
        append_distinct(points, source_snap)
        for point in drawio_points:
            append_distinct(points, point)
        append_distinct(points, target_snap)
        runtime_edges.append(
            {
                "drawio_id": edge_id,
                "from": resource_ids[source_label],
                "to": resource_ids[target_label],
                "points": points,
                "drawio_points": drawio_points,
            }
        )

    if len(runtime_nodes) != EXPECTED_NODES:
        failures.append(f"Runtime layout node count mismatch: {len(runtime_nodes)} != {EXPECTED_NODES}")
    if len(runtime_edges) != EXPECTED_EDGES:
        failures.append(f"Runtime layout edge count mismatch: {len(runtime_edges)} != {EXPECTED_EDGES}")
    runtime_node_by_research = {node["research"]: node for node in runtime_nodes}
    for edge in runtime_edges:
        source_node = runtime_node_by_research[edge["from"]]
        target_node = runtime_node_by_research[edge["to"]]
        if not point_on_card_perimeter(edge["points"][0], source_node, node_width, node_height):
            failures.append(f"Runtime edge source does not touch its card perimeter: {edge['drawio_id']}")
        if not point_on_card_perimeter(edge["points"][-1], target_node, node_width, node_height):
            failures.append(f"Runtime edge target does not touch its card perimeter: {edge['drawio_id']}")
        for first, second in zip(edge["drawio_points"], edge["drawio_points"][1:]):
            if first["x"] != second["x"] and first["y"] != second["y"]:
                failures.append(f"Draw.io interior route is not orthogonal: {edge['drawio_id']}")
                break

    result = {
        "schema_version": LAYOUT_SCHEMA_VERSION,
        "branch": f"industrial_colonies:{tree['id']}",
        "drawio_source_sha256": graph.get("source_sha256"),
        "rendered_svg_sha256": sha256(svg_path),
        "canvas": {
            "width": math.ceil(view_box[2] * scale) + margin * 2,
            "height": math.ceil(view_box[3] * scale) + margin * 2,
        },
        "scale": scale,
        "margin": margin,
        "node_width": node_width,
        "node_height": node_height,
        "nodes": runtime_nodes,
        "edges": runtime_edges,
    }
    write_json(output_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the one-tab, 77-node MineColonies University tree.")
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--drawio-export", type=Path, required=True)
    parser.add_argument("--drawio-svg", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--layout-output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    graph = load(args.drawio_export.resolve())
    mapping = load(project / "progression" / "machine_node_assignments.json")["nodes"]
    layout = load(project / "progression" / "minecolonies_branch_layout.json")
    cost_nodes = load(project / "progression" / "research_costs.json")["nodes"]
    output = (args.output or project / "src" / "generated" / "resources").resolve()
    research_root = output / "data" / "industrial_colonies" / "researches"
    tree = layout["tree"]
    tree_id = str(tree["id"])
    tree_resource = f"industrial_colonies:{tree_id}"
    svg_path = (
        args.drawio_svg
        or project.parent / "industrial-audit" / "drawio-export" / "tech_tree_rendered"
    ).resolve()
    layout_output = (
        args.layout_output
        or output / "assets" / "industrial_colonies" / "research_layout" / f"{tree_id}.json"
    ).resolve()

    failures: list[str] = []
    if graph.get("source_sha256") != EXPECTED_DRAWIO_SHA256:
        failures.append(
            f"Authoritative Draw.io hash changed: {graph.get('source_sha256')} != {EXPECTED_DRAWIO_SHA256}"
        )
    if tree_id != "tech_tree" or tree.get("name") != "Tech Tree":
        failures.append(f"Single University branch must be tech_tree / Tech Tree, got {tree_id} / {tree.get('name')}")

    id_to_label = {str(node["id"]): str(node["label"]) for node in graph["nodes"]}
    graph_labels = set(id_to_label.values())
    incoming: dict[str, set[str]] = defaultdict(set)
    graph_edges: set[tuple[str, str]] = set()
    for edge in graph["edges"]:
        source = id_to_label.get(str(edge["source"]))
        target = id_to_label.get(str(edge["target"]))
        if source is None or target is None:
            failures.append(f"Unresolved Draw.io edge: {edge}")
            continue
        incoming[target].add(source)
        graph_edges.add((source, target))
    if len(graph_labels) != EXPECTED_NODES:
        failures.append(f"Draw.io node count changed: {len(graph_labels)} != {EXPECTED_NODES}")
    if len(graph_edges) != EXPECTED_EDGES:
        failures.append(f"Draw.io edge count changed: {len(graph_edges)} != {EXPECTED_EDGES}")
    logical_roots = sorted(graph_labels - set(incoming))
    if len(logical_roots) != 1:
        failures.append(f"Draw.io graph must have one logical root, found {len(logical_roots)}: {logical_roots}")

    node_layout: dict[str, dict[str, Any]] = {}
    section_meta: dict[str, dict[str, Any]] = {}
    for section in layout["branches"]:
        section_id = str(section["id"])
        if section_id in section_meta:
            failures.append(f"Duplicate stable resource-path section id: {section_id}")
        section_meta[section_id] = section
        for index, entry in enumerate(section["nodes"]):
            label = str(entry["label"])
            if label in node_layout:
                failures.append(f"Node assigned to multiple resource-path sections: {label}")
            node_layout[label] = {**entry, "section": section_id, "section_index": index}

    for label in sorted(graph_labels - set(node_layout)):
        failures.append(f"Draw.io node missing from MineColonies layout: {label}")
    for label in sorted(set(node_layout) - graph_labels):
        failures.append(f"MineColonies layout node absent from Draw.io: {label}")
    for label in sorted(graph_labels - set(cost_nodes)):
        failures.append(f"Draw.io node missing from research cost map: {label}")
    for label in sorted(set(cost_nodes) - graph_labels):
        failures.append(f"Research cost map node absent from Draw.io: {label}")
    for label in sorted(graph_labels & set(cost_nodes)):
        costs = cost_nodes[label].get("costs", [])
        if not 1 <= len(costs) <= 3:
            failures.append(f"Research must have 1-3 cost entries: {label} has {len(costs)}")
        for cost in costs:
            if set(cost) != {"item", "count"}:
                failures.append(f"Malformed research cost entry for {label}: {cost}")
            if not isinstance(cost.get("item"), str) or ":" not in cost.get("item", ""):
                failures.append(f"Invalid research cost item for {label}: {cost.get('item')}")
            if not isinstance(cost.get("count"), int) or isinstance(cost.get("count"), bool) or cost.get("count", 0) <= 0:
                failures.append(f"Invalid research cost count for {label}: {cost.get('count')}")

    depths: dict[str, int] = {}
    visiting: set[str] = set()

    def depth(label: str) -> int:
        if label in depths:
            return depths[label]
        if label in visiting:
            failures.append(f"Structural-parent cycle: {label}")
            return EXPECTED_MAX_DEPTH + 1
        visiting.add(label)
        entry = node_layout[label]
        parent = entry.get("parent")
        value = 1
        if parent:
            if parent not in node_layout:
                failures.append(f"Unknown structural parent for {label}: {parent}")
            else:
                if node_layout[str(parent)]["section"] != entry["section"]:
                    failures.append(f"Structural parent crosses stable section for {label}: {parent}")
                if parent not in incoming.get(label, set()):
                    failures.append(f"Structural parent is not a Draw.io edge for {label}: {parent}")
                value = depth(str(parent)) + 1
        visiting.remove(label)
        depths[label] = value
        return value

    for label in node_layout:
        depth(label)

    resource_ids = {
        label: f"industrial_colonies:{entry['section']}/{slug(label)}"
        for label, entry in node_layout.items()
    }
    structural_edges = {
        (str(entry["parent"]), label)
        for label, entry in node_layout.items()
        if entry.get("parent")
    }
    nonstructural_edges = graph_edges - structural_edges
    explicit_requirement_count = sum(len(parents) for parents in incoming.values())
    for edge in sorted(structural_edges - graph_edges):
        failures.append(f"Structural edge absent from Draw.io: {edge[0]} -> {edge[1]}")
    if len(structural_edges) != EXPECTED_PRIMARY_EDGES:
        failures.append(f"Structural-parent edge count mismatch: {len(structural_edges)} != {EXPECTED_PRIMARY_EDGES}")
    if len(nonstructural_edges) != EXPECTED_NONSTRUCTURAL_EDGES:
        failures.append(
            f"Nonstructural edge count mismatch: {len(nonstructural_edges)} != {EXPECTED_NONSTRUCTURAL_EDGES}"
        )
    if explicit_requirement_count != EXPECTED_EXPLICIT_REQUIREMENTS:
        failures.append(
            f"Explicit research-requirement count mismatch: "
            f"{explicit_requirement_count} != {EXPECTED_EXPLICIT_REQUIREMENTS}"
        )
    if max(depths.values(), default=0) != EXPECTED_MAX_DEPTH:
        failures.append(f"Structural tree depth mismatch: {max(depths.values(), default=0)} != {EXPECTED_MAX_DEPTH}")

    generated_files: list[str] = []
    translations: dict[str, str] = {}
    branch_key = f"com.industrial_colonies.research.{tree_id}.name"
    translations[branch_key] = str(tree["name"])
    branch_path = research_root / f"{tree_id}.json"
    write_json(
        branch_path,
        {"base-time": 1.0, "branch-name": branch_key, "sortOrder": int(tree["sort_order"])},
    )
    generated_files.append(str(branch_path.relative_to(output)))
    for section_id in section_meta:
        stale_branch_path = research_root / f"{section_id}.json"
        if stale_branch_path != branch_path and stale_branch_path.is_file():
            stale_branch_path.unlink()

    node_geometry = {str(node["label"]): node for node in graph["nodes"]}
    for label, entry in node_layout.items():
        section_id = str(entry["section"])
        node_slug = slug(label)
        name_key = f"com.industrial_colonies.research.{section_id}.{node_slug}.name"
        subtitle_key = f"com.industrial_colonies.research.{section_id}.{node_slug}.subtitle"
        translations[name_key] = label
        translations[subtitle_key] = mapping[label]["role"]
        unlocks = mapping[label].get("unlocks", [])
        # Progression ownership can intentionally supersede a legacy Draw.io
        # icon when a node's material semantics change without changing the
        # authoritative topology or geometry.
        icon_override = mapping[label].get("icon", entry.get("icon"))
        if icon_override:
            icon = icon_override
        elif not unlocks:
            failures.append(f"No verified icon candidate/unlock mapping for {label}")
            icon = "minecraft:barrier"
        else:
            icon = unlocks[0]

        parent = entry.get("parent")
        requirements = [
            {"type": "minecolonies:research", "research": resource_ids[prerequisite]}
            for prerequisite in sorted(incoming.get(label, set()))
        ]
        research: dict[str, Any] = {
            "branch": tree_resource,
            "costs": cost_nodes.get(label, {}).get("costs", []),
            "icon": icon,
            "name": name_key,
            "no-reset": True,
            "researchLevel": depths[label],
            "sortOrder": int(round(float(node_geometry[label].get("y", 0)))) + 10000,
            "subtitle": subtitle_key,
        }
        if parent:
            research["parentResearch"] = resource_ids[str(parent)]
        if requirements:
            research["requirements"] = requirements

        path = research_root / section_id / f"{node_slug}.json"
        write_json(path, research)
        generated_files.append(str(path.relative_to(output)))

    translation_path = output / "data" / "industrial_colonies" / "generated_research_translations.json"
    write_json(translation_path, translations)
    generated_files.append(str(translation_path.relative_to(output)))

    runtime_layout = generate_client_layout(
        svg_path=svg_path,
        graph=graph,
        resource_ids=resource_ids,
        tree=tree,
        output_path=layout_output,
        failures=failures,
    )
    if runtime_layout is not None:
        generated_files.append(str(layout_output.relative_to(output)))

    report = {
        "drawio_source": graph.get("source"),
        "drawio_source_sha256": graph.get("source_sha256"),
        "rendered_svg": str(svg_path),
        "rendered_svg_sha256": sha256(svg_path) if svg_path.is_file() else None,
        "drawio_nodes": len(graph_labels),
        "drawio_edges": len(graph_edges),
        "logical_roots": logical_roots,
        "minecolonies_branches": 1,
        "minecolonies_branch": tree_resource,
        "minecolonies_branch_name": tree["name"],
        "stable_resource_path_sections": len(section_meta),
        "generated_research_nodes": len(node_layout),
        "generated_costed_nodes": sum(1 for label in node_layout if cost_nodes.get(label, {}).get("costs")),
        "generated_cost_entries": sum(len(cost_nodes.get(label, {}).get("costs", [])) for label in node_layout),
        "max_research_depth": max(depths.values(), default=0),
        "structural_parent_edges": len(structural_edges),
        "explicit_research_requirements": explicit_requirement_count,
        "nonstructural_edges": len(nonstructural_edges),
        "runtime_layout_nodes": len(runtime_layout["nodes"]) if runtime_layout else 0,
        "runtime_layout_edges": len(runtime_layout["edges"]) if runtime_layout else 0,
        "generated_files": generated_files,
        "failures": failures,
    }
    if args.report:
        write_json(args.report.resolve(), report)

    print(
        f"Generated {report['generated_research_nodes']} research nodes in one {tree_resource} branch; "
        f"encoded all {report['drawio_edges']} Draw.io edges at structural depth {report['max_research_depth']}."
    )
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(
        f"PASS: {report['structural_parent_edges']} structural-parent edges, "
        f"{report['explicit_research_requirements']} explicit AND requirements "
        f"({report['nonstructural_edges']} nonstructural edges), and "
        f"{report['runtime_layout_edges']} exact SVG routes in one Tech Tree tab."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
