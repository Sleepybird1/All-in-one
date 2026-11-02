from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

from generate_minecolonies_research import (
    EXPECTED_DRAWIO_SHA256,
    append_distinct,
    load,
    parse_line_path,
    point_on_card_perimeter,
    sha256,
    slug,
    snap_to_card_perimeter,
    svg_tag,
    write_json,
)


EXPECTED_NODES = 77
EXPECTED_EDGES = 99
EXPECTED_STRUCTURAL_EDGES = 61
EXPECTED_EXPLICIT_REQUIREMENTS = 99
EXPECTED_NONSTRUCTURAL_EDGES = 38
EXPECTED_DEPTH = 6


def require_source_fragment(
    source: str,
    fragment: str,
    description: str,
    failures: list[str],
) -> int:
    position = source.find(fragment)
    if position < 0:
        failures.append(f"Missing runtime enforcement contract: {description}")
    return position


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the one-tab MineColonies Tech Tree and exact layout asset.")
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--drawio-export", type=Path)
    parser.add_argument("--drawio-svg", type=Path)
    parser.add_argument("--generated-root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    graph_path = (
        args.drawio_export
        or project.parent / "industrial-audit" / "drawio-export" / "drawio_tree.json"
    ).resolve()
    svg_path = (
        args.drawio_svg
        or project.parent / "industrial-audit" / "drawio-export" / "tech_tree_rendered"
    ).resolve()
    generated_root = (args.generated_root or project / "src" / "generated" / "resources").resolve()
    report_path = (
        args.report
        or project.parent / "industrial-audit" / "drawio-export" / "minecolonies_single_tab_validation.json"
    ).resolve()
    failures: list[str] = []

    if not graph_path.is_file():
        failures.append(f"Missing Draw.io graph export: {graph_path}")
    if not svg_path.is_file():
        failures.append(f"Missing rendered Draw.io SVG: {svg_path}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    graph = load(graph_path)
    config = load(project / "progression" / "minecolonies_branch_layout.json")
    costs = load(project / "progression" / "research_costs.json")["nodes"]
    tree = config.get("tree", {})
    if graph.get("source_sha256") != EXPECTED_DRAWIO_SHA256:
        failures.append("Authoritative Draw.io source hash changed")
    if tree.get("id") != "tech_tree" or tree.get("name") != "Tech Tree":
        failures.append(f"Visible branch identity changed: {tree}")

    id_to_label = {str(node["id"]): str(node["label"]) for node in graph["nodes"]}
    label_to_id = {label: node_id for node_id, label in id_to_label.items()}
    incoming: dict[str, set[str]] = defaultdict(set)
    graph_edges: set[tuple[str, str]] = set()
    edge_by_id: dict[str, tuple[str, str]] = {}
    for edge in graph["edges"]:
        source = id_to_label.get(str(edge["source"]))
        target = id_to_label.get(str(edge["target"]))
        if source is None or target is None:
            failures.append(f"Unresolved Draw.io edge: {edge}")
            continue
        pair = (source, target)
        incoming[target].add(source)
        graph_edges.add(pair)
        edge_by_id[str(edge["id"])] = pair
    logical_roots = sorted(set(id_to_label.values()) - set(incoming))
    if len(id_to_label) != EXPECTED_NODES:
        failures.append(f"Draw.io node count mismatch: {len(id_to_label)}")
    if len(graph_edges) != EXPECTED_EDGES:
        failures.append(f"Draw.io edge count mismatch: {len(graph_edges)}")
    if logical_roots != ["CR01 — We Don’t Read Manuals"]:
        failures.append(f"Logical root mismatch: {logical_roots}")

    entries: dict[str, dict[str, Any]] = {}
    for section in config["branches"]:
        for entry in section["nodes"]:
            label = str(entry["label"])
            if label in entries:
                failures.append(f"Duplicate layout entry: {label}")
            entries[label] = {**entry, "section": str(section["id"])}
    labels = set(id_to_label.values())
    if set(entries) != labels:
        failures.append(
            f"Stable resource-path coverage mismatch: missing={sorted(labels-set(entries))}, extra={sorted(set(entries)-labels)}"
        )
    resource_ids = {
        label: f"industrial_colonies:{entry['section']}/{slug(label)}"
        for label, entry in entries.items()
    }
    resource_to_label = {resource: label for label, resource in resource_ids.items()}

    depths: dict[str, int] = {}

    def structural_depth(label: str) -> int:
        if label not in depths:
            parent = entries[label].get("parent")
            depths[label] = 1 if not parent else structural_depth(str(parent)) + 1
        return depths[label]

    for label in labels:
        structural_depth(label)
    expected_structural = {
        (str(entry["parent"]), label)
        for label, entry in entries.items()
        if entry.get("parent")
    }
    expected_nonstructural = graph_edges - expected_structural
    if len(expected_structural) != EXPECTED_STRUCTURAL_EDGES:
        failures.append(f"Structural edge count mismatch: {len(expected_structural)}")
    if len(expected_nonstructural) != EXPECTED_NONSTRUCTURAL_EDGES:
        failures.append(f"Nonstructural edge count mismatch: {len(expected_nonstructural)}")
    if max(depths.values(), default=0) != EXPECTED_DEPTH:
        failures.append(f"Structural depth mismatch: {max(depths.values(), default=0)}")

    research_root = generated_root / "data" / "industrial_colonies" / "researches"
    descriptors = sorted(path.name for path in research_root.glob("*.json") if path.is_file())
    if descriptors != ["tech_tree.json"]:
        failures.append(f"Expected exactly one MineColonies branch descriptor, found {descriptors}")
    branch_path = research_root / "tech_tree.json"
    if branch_path.is_file():
        branch_data = load(branch_path)
        expected_branch = {
            "base-time": 1.0,
            "branch-name": "com.industrial_colonies.research.tech_tree.name",
            "sortOrder": int(tree["sort_order"]),
        }
        if branch_data != expected_branch:
            failures.append(f"Tech Tree branch descriptor mismatch: {branch_data}")

    expected_paths = {
        (research_root / entry["section"] / f"{slug(label)}.json").resolve()
        for label, entry in entries.items()
    }
    actual_paths = {path.resolve() for path in research_root.glob("*/*.json") if path.is_file()}
    if actual_paths != expected_paths:
        failures.append(
            f"Research file coverage mismatch: missing={len(expected_paths-actual_paths)}, extra={len(actual_paths-expected_paths)}"
        )

    generated_edges: set[tuple[str, str]] = set()
    structural_count = 0
    requirement_count = 0
    for label, entry in entries.items():
        path = research_root / entry["section"] / f"{slug(label)}.json"
        if not path.is_file():
            continue
        research = load(path)
        if research.get("branch") != "industrial_colonies:tech_tree":
            failures.append(f"Research is outside the single Tech Tree branch: {label}")
        if research.get("no-reset") is not True:
            failures.append(f"DAG-integrity no-reset flag missing: {label}")
        if research.get("researchLevel") != depths[label]:
            failures.append(f"Structural depth mismatch in generated data: {label}")
        if research.get("costs") != costs[label]["costs"]:
            failures.append(f"Research costs changed during generation: {label}")
        expected_parent = entry.get("parent")
        expected_parent_resource = resource_ids[str(expected_parent)] if expected_parent else None
        if research.get("parentResearch") != expected_parent_resource:
            failures.append(f"Structural parent mismatch: {label}")
        if expected_parent:
            structural_count += 1
            generated_edges.add((str(expected_parent), label))

        actual_requirements: set[str] = set()
        for requirement in research.get("requirements", []):
            if requirement.get("type") != "minecolonies:research":
                failures.append(f"Unexpected non-research requirement on {label}: {requirement}")
                continue
            prerequisite = resource_to_label.get(str(requirement.get("research")))
            if prerequisite is None:
                failures.append(f"Unknown generated research requirement on {label}: {requirement}")
                continue
            if prerequisite in actual_requirements:
                failures.append(f"Duplicate generated requirement on {label}: {prerequisite}")
            actual_requirements.add(prerequisite)
            generated_edges.add((prerequisite, label))
        expected_for_node = incoming[label]
        if actual_requirements != expected_for_node:
            failures.append(
                f"Explicit AND requirement mismatch on {label}: "
                f"actual={sorted(actual_requirements)}, expected={sorted(expected_for_node)}"
            )
        requirement_count += len(actual_requirements)

    if structural_count != EXPECTED_STRUCTURAL_EDGES:
        failures.append(f"Generated structural edge count mismatch: {structural_count}")
    if requirement_count != EXPECTED_EXPLICIT_REQUIREMENTS:
        failures.append(f"Generated explicit requirement count mismatch: {requirement_count}")
    if generated_edges != graph_edges:
        failures.append(
            f"Generated topology mismatch: missing={len(graph_edges-generated_edges)}, extra={len(generated_edges-graph_edges)}"
        )

    # The generated data is only half of the contract. A malicious or stale
    # client may still send TryResearchMessage directly, so normal-player AND
    # enforcement must remain at LocalResearchTree.attemptBeginResearch. At the
    # same time, Creative authors need a deliberate one-click override for any
    # unfinished card, including missing parents/requirements, insufficient
    # University level, and a full research-slot queue.
    server_mixin_path = (
        project
        / "src"
        / "main"
        / "java"
        / "dev"
        / "godpc"
        / "industrialcolonies"
        / "mixin"
        / "LocalResearchTreeMixin.java"
    )
    client_mixin_path = (
        project
        / "src"
        / "main"
        / "java"
        / "dev"
        / "godpc"
        / "industrialcolonies"
        / "mixin"
        / "client"
        / "WindowResearchTreeMixin.java"
    )
    server_source = server_mixin_path.read_text(encoding="utf-8")
    client_source = client_mixin_path.read_text(encoding="utf-8")

    server_contract = {
        "attempt_begin_injection": require_source_fragment(
            server_source,
            '@Inject(method = "attemptBeginResearch", at = @At("HEAD"), cancellable = true',
            "cancellable server injection at attemptBeginResearch HEAD",
            failures,
        ),
        "creative_escape_hatch": require_source_fragment(
            server_source,
            "if (player != null && player.isCreative())",
            "Creative-only server escape hatch",
            failures,
        ),
        "creative_force_complete": require_source_fragment(
            server_source,
            "industrialColonies$forceCompleteCreativeResearch(colony, globalResearch);",
            "Creative server force-completion call",
            failures,
        ),
        "creative_cancel_stock": require_source_fragment(
            server_source,
            "industrialColonies$forceCompleteCreativeResearch(colony, globalResearch);\n            callback.cancel();",
            "Creative server action cancels the stock second execution path",
            failures,
        ),
        "stock_can_research_gate": require_source_fragment(
            server_source,
            "!globalResearch.canResearch(university, localTree)",
            "normal-player MineColonies canResearch gate",
            failures,
        ),
        "structural_parent_gate": require_source_fragment(
            server_source,
            "parent != null && !localTree.hasCompletedResearch(parent)",
            "normal-player structural-parent gate",
            failures,
        ),
        "all_requirements_gate": require_source_fragment(
            server_source,
            "isResearchRequirementsFulfilled(\n                globalResearch.getResearchRequirements(), colony)",
            "normal-player explicit AND-requirements gate",
            failures,
        ),
    }
    ordered_server_gates = [
        server_contract["attempt_begin_injection"],
        server_contract["creative_escape_hatch"],
        server_contract["creative_force_complete"],
        server_contract["creative_cancel_stock"],
        server_contract["stock_can_research_gate"],
        server_contract["structural_parent_gate"],
        server_contract["all_requirements_gate"],
    ]
    if all(position >= 0 for position in ordered_server_gates) and ordered_server_gates != sorted(ordered_server_gates):
        failures.append("Runtime enforcement contract is ordered incorrectly around the Creative escape hatch")

    creative_completion_contract = {
        "start_missing_research": require_source_fragment(
            server_source,
            "globalResearch.startResearch(localTree);",
            "Creative force-completion starts a missing local research",
            failures,
        ),
        "revive_unfinished_state": require_source_fragment(
            server_source,
            "localResearch.setState(ResearchState.IN_PROGRESS);",
            "Creative force-completion handles every unfinished local state",
            failures,
        ),
        "prime_completion_tick": require_source_fragment(
            server_source,
            "localResearch.setProgress(Math.max(0, baseTime - 1));",
            "Creative force-completion primes the canonical completion threshold",
            failures,
        ),
        "canonical_completion": require_source_fragment(
            server_source,
            "localResearch.research(colony.getResearchManager().getResearchEffects(), localTree);",
            "Creative force-completion applies effects and finishes through MineColonies",
            failures,
        ),
        "persist_completion": require_source_fragment(
            server_source,
            "colony.getResearchManager().markDirty();\n        colony.markDirty();",
            "Creative force-completion persists research and colony state",
            failures,
        ),
    }

    client_contract = {
        "draw_item_redirect": require_source_fragment(
            client_source,
            '@Redirect(\n            method = "drawResearchItem"',
            "Creative card-state redirect on drawResearchItem",
            failures,
        ),
        "parent_probe": require_source_fragment(
            client_source,
            "ILocalResearchTree;hasCompletedResearch",
            "structural-parent completion probe redirect",
            failures,
        ),
        "creative_scope": require_source_fragment(
            client_source,
            "IndustrialResearchIds.isTechTree(branch)\n                && player != null\n                && player.isCreative()",
            "Creative override scoped to Industrial Colonies Tech Tree",
            failures,
        ),
        "creative_available": require_source_fragment(
            client_source,
            "player.isCreative()) {\n            return true;",
            "Creative missing-parent probe returns available",
            failures,
        ),
        "normal_parent_result": require_source_fragment(
            client_source,
            "return localTree.hasCompletedResearch(parent);",
            "normal-player parent probe preserves MineColonies result",
            failures,
        ),
        "unlimited_level_redirect": require_source_fragment(
            client_source,
            'method = {"getResearchButtonState", "onButtonClicked"}',
            "Creative University-level redirect covers card state and stock click handler",
            failures,
        ),
        "building_level_probe": require_source_fragment(
            client_source,
            "IBuildingView;getBuildingLevel()I",
            "University level and research-slot probe redirect",
            failures,
        ),
        "unlimited_creative_value": require_source_fragment(
            client_source,
            "player.isCreative()) {\n            return Integer.MAX_VALUE;",
            "Creative Tech Tree receives an unlimited effective University level",
            failures,
        ),
        "normal_building_level": require_source_fragment(
            client_source,
            "return building.getBuildingLevel();",
            "normal players and other branches preserve the real University level",
            failures,
        ),
    }
    if 'method = "getResearchButtonState"' in client_source:
        failures.append("Client mixin still overrides MineColonies' stock Creative AVAILABLE decision")
    if "new TryResearchMessage" in client_source or ".sendToServer()" in client_source:
        failures.append("Client mixin sends a duplicate TryResearchMessage instead of using the stock click handler")

    asset_path = generated_root / "assets" / "industrial_colonies" / "research_layout" / "tech_tree.json"
    if not asset_path.is_file():
        failures.append(f"Missing runtime layout asset: {asset_path}")
        asset: dict[str, Any] = {}
    else:
        asset = load(asset_path)
    scale = float(tree["layout_scale"])
    margin = int(tree["layout_margin"])
    node_width = int(tree["node_width"])
    node_height = int(tree["node_height"])
    if asset.get("schema_version") != 1 or asset.get("branch") != "industrial_colonies:tech_tree":
        failures.append("Runtime layout schema/branch mismatch")
    if asset.get("drawio_source_sha256") != EXPECTED_DRAWIO_SHA256:
        failures.append("Runtime layout Draw.io hash mismatch")
    if asset.get("rendered_svg_sha256") != sha256(svg_path):
        failures.append("Runtime layout rendered SVG hash mismatch")

    svg_root = ET.parse(svg_path).getroot()
    view_box = [float(value) for value in svg_root.attrib["viewBox"].split()]
    expected_canvas = {
        "width": math.ceil(view_box[2] * scale) + margin * 2,
        "height": math.ceil(view_box[3] * scale) + margin * 2,
    }
    if asset.get("canvas") != expected_canvas:
        failures.append(f"Runtime layout canvas mismatch: {asset.get('canvas')} != {expected_canvas}")
    groups: dict[str, ET.Element] = {}
    for element in svg_root.iter(svg_tag("g")):
        cell_id = element.get("data-cell-id")
        if cell_id and cell_id not in groups:
            groups[cell_id] = element

    asset_nodes = {str(node.get("research")): node for node in asset.get("nodes", [])}
    if len(asset_nodes) != EXPECTED_NODES or set(asset_nodes) != set(resource_ids.values()):
        failures.append(f"Runtime layout research-node coverage mismatch: {len(asset_nodes)}")
    expected_centers: dict[str, dict[str, int]] = {}
    for label, research_id in resource_ids.items():
        node_id = label_to_id[label]
        group = groups.get(node_id)
        rect = next(group.iter(svg_tag("rect")), None) if group is not None else None
        if rect is None:
            failures.append(f"SVG node rectangle missing during validation: {node_id}")
            continue
        center = {
            "x": margin + round((float(rect.attrib["x"]) + float(rect.attrib["width"]) / 2.0 - view_box[0]) * scale),
            "y": margin + round((float(rect.attrib["y"]) + float(rect.attrib["height"]) / 2.0 - view_box[1]) * scale),
        }
        expected_centers[node_id] = center
        expected_node = {
            "research": research_id,
            "drawio_id": node_id,
            "label": label,
            "x": center["x"] - node_width // 2,
            "y": center["y"] - node_height // 2,
            "center_x": center["x"],
            "center_y": center["y"],
        }
        if asset_nodes.get(research_id) != expected_node:
            failures.append(f"Runtime node geometry mismatch: {label}")

    asset_edges = {str(edge.get("drawio_id")): edge for edge in asset.get("edges", [])}
    if len(asset_edges) != EXPECTED_EDGES or set(asset_edges) != set(edge_by_id):
        failures.append(f"Runtime layout edge coverage mismatch: {len(asset_edges)}")
    for edge in graph["edges"]:
        edge_id = str(edge["id"])
        source_id = str(edge["source"])
        target_id = str(edge["target"])
        actual = asset_edges.get(edge_id)
        if actual is None or source_id not in expected_centers or target_id not in expected_centers:
            continue
        path = next(groups[edge_id].iter(svg_tag("path")), None)
        if path is None:
            failures.append(f"SVG edge route missing during validation: {edge_id}")
            continue
        expected_drawio_points = [
            {
                "x": margin + round((x - view_box[0]) * scale),
                "y": margin + round((y - view_box[1]) * scale),
            }
            for x, y in parse_line_path(path.attrib["d"])
        ]
        expected_points: list[dict[str, int]] = []
        append_distinct(
            expected_points,
            snap_to_card_perimeter(expected_centers[source_id], expected_drawio_points[0], node_width, node_height),
        )
        for point in expected_drawio_points:
            append_distinct(expected_points, point)
        append_distinct(
            expected_points,
            snap_to_card_perimeter(expected_centers[target_id], expected_drawio_points[-1], node_width, node_height),
        )
        source_label, target_label = edge_by_id[edge_id]
        if actual.get("from") != resource_ids[source_label] or actual.get("to") != resource_ids[target_label]:
            failures.append(f"Runtime edge endpoints mismatch: {edge_id}")
        if actual.get("drawio_points") != expected_drawio_points or actual.get("points") != expected_points:
            failures.append(f"Runtime edge polyline differs from rendered Draw.io SVG: {edge_id}")
        if not point_on_card_perimeter(expected_points[0], asset_nodes[resource_ids[source_label]], node_width, node_height):
            failures.append(f"Runtime source endpoint misses card perimeter: {edge_id}")
        if not point_on_card_perimeter(expected_points[-1], asset_nodes[resource_ids[target_label]], node_width, node_height):
            failures.append(f"Runtime target endpoint misses card perimeter: {edge_id}")

    report = {
        "drawio_source_sha256": graph.get("source_sha256"),
        "rendered_svg_sha256": sha256(svg_path),
        "minecolonies_branches": len(descriptors),
        "branch": "industrial_colonies:tech_tree",
        "branch_name": "Tech Tree",
        "research_nodes": len(expected_paths),
        "logical_roots": logical_roots,
        "structural_parent_edges": structural_count,
        "explicit_research_requirements": requirement_count,
        "nonstructural_edges": len(expected_nonstructural),
        "logical_edges": len(generated_edges),
        "maximum_structural_depth": max(depths.values(), default=0),
        "normal_player_server_enforcement": all(position >= 0 for position in server_contract.values()),
        "creative_server_force_completion": all(
            position >= 0 for position in creative_completion_contract.values()
        ),
        "creative_force_unlock_card": all(position >= 0 for position in client_contract.values()),
        "creative_unlimited_university_and_slots": all(
            client_contract[key] >= 0
            for key in (
                "unlimited_level_redirect",
                "building_level_probe",
                "unlimited_creative_value",
                "normal_building_level",
            )
        ),
        "client_uses_single_stock_try_research_message": (
            "new TryResearchMessage" not in client_source and ".sendToServer()" not in client_source
        ),
        "layout_nodes": len(asset_nodes),
        "layout_edges": len(asset_edges),
        "layout_canvas": asset.get("canvas"),
        "failures": failures,
    }
    write_json(report_path, report)
    print(
        f"Checked one Tech Tree branch / {len(expected_paths)} nodes / {len(generated_edges)} logical edges / "
        f"{len(asset_edges)} exact routed lines."
    )
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(
        "PASS: exact 77/99 Draw.io topology, 61 structural parents, 99 explicit AND requirements "
        "(38 nonstructural edges), "
        "authoritative normal-player prerequisite enforcement, one-click Creative force-completion "
        "across parents/requirements/University level/research slots, "
        "one branch descriptor, and all 99 card-snapped SVG polylines."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
