from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


HTML_TAG = re.compile(r"<[^>]+>")


def clean_label(value: str) -> str:
    value = html.unescape(value or "")
    value = value.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    value = HTML_TAG.sub("", value)
    return " ".join(value.split())


def number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def geometry(cell: ET.Element) -> dict[str, float | None]:
    geo = cell.find("mxGeometry")
    if geo is None:
        return {"x": None, "y": None, "width": None, "height": None}
    return {
        "x": number(geo.get("x")),
        "y": number(geo.get("y")),
        "width": number(geo.get("width")),
        "height": number(geo.get("height")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Draw.io nodes, edges, and coordinates without modifying the source.")
    parser.add_argument("drawio", type=Path)
    parser.add_argument("output", type=Path, help="output directory")
    parser.add_argument("--scale", type=float, default=1.0, help="coordinate scale for the mapping CSV")
    args = parser.parse_args()

    source_bytes = args.drawio.read_bytes()
    root = ET.fromstring(source_bytes)
    diagram = root.find("diagram")
    if diagram is None:
        raise SystemExit("No <diagram> found. Compressed Draw.io pages are not supported by this utility yet.")
    graph = diagram.find("mxGraphModel")
    if graph is None:
        raise SystemExit("The selected Draw.io page is compressed; export/save it as uncompressed XML first.")
    graph_root = graph.find("root")
    if graph_root is None:
        raise SystemExit("No graph root found.")

    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    for wrapper in graph_root.findall("object"):
        cell = wrapper.find("mxCell")
        if cell is None or cell.get("vertex") != "1":
            continue
        node_id = wrapper.get("id") or cell.get("id")
        if not node_id:
            continue
        label = clean_label(wrapper.get("label") or cell.get("value") or "")
        entry = {
            "id": node_id,
            "label": label,
            "style": cell.get("style", ""),
            **geometry(cell),
        }
        nodes.append(entry)
        node_ids.add(node_id)

    for cell in graph_root.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        node_id = cell.get("id")
        if not node_id or node_id in node_ids:
            continue
        nodes.append(
            {
                "id": node_id,
                "label": clean_label(cell.get("value") or ""),
                "style": cell.get("style", ""),
                **geometry(cell),
            }
        )
        node_ids.add(node_id)

    edges: list[dict[str, Any]] = []
    for cell in graph_root.iter("mxCell"):
        if cell.get("edge") != "1":
            continue
        source = cell.get("source")
        target = cell.get("target")
        points: list[dict[str, float | None]] = []
        geo = cell.find("mxGeometry")
        if geo is not None:
            for point in geo.iter("mxPoint"):
                points.append({"x": number(point.get("x")), "y": number(point.get("y"))})
        edges.append(
            {
                "id": cell.get("id"),
                "source": source,
                "target": target,
                "style": cell.get("style", ""),
                "points": points,
            }
        )

    nodes.sort(key=lambda node: ((node["x"] if node["x"] is not None else 10**12), (node["y"] if node["y"] is not None else 10**12), node["label"]))
    label_by_id = {node["id"]: node["label"] for node in nodes}

    args.output.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": str(args.drawio.resolve()),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "diagram_name": diagram.get("name", ""),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
    (args.output / "drawio_tree.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    incoming: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if edge["source"] in outgoing and edge["target"]:
            outgoing[edge["source"]].append(edge["target"])
        if edge["target"] in incoming and edge["source"]:
            incoming[edge["target"]].append(edge["source"])

    with (args.output / "drawio_node_mapping.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "drawio_id",
                "label",
                "drawio_x",
                "drawio_y",
                "drawio_width",
                "drawio_height",
                "scaled_x",
                "scaled_y",
                "prerequisite_labels",
                "dependent_labels",
                "ftb_quest_id",
            ],
        )
        writer.writeheader()
        for node in nodes:
            writer.writerow(
                {
                    "drawio_id": node["id"],
                    "label": node["label"],
                    "drawio_x": node["x"],
                    "drawio_y": node["y"],
                    "drawio_width": node["width"],
                    "drawio_height": node["height"],
                    "scaled_x": None if node["x"] is None else node["x"] * args.scale,
                    "scaled_y": None if node["y"] is None else node["y"] * args.scale,
                    "prerequisite_labels": " | ".join(label_by_id.get(node_id, node_id) for node_id in incoming[node["id"]]),
                    "dependent_labels": " | ".join(label_by_id.get(node_id, node_id) for node_id in outgoing[node["id"]]),
                    "ftb_quest_id": "",
                }
            )

    print(f"Exported {len(nodes)} nodes and {len(edges)} edges from {diagram.get('name', '')!r}.")
    print(f"Source SHA-256: {payload['source_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
