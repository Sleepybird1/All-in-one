from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser(description="Join authoritative Draw.io nodes to audited machine/item unlocks.")
    parser.add_argument("drawio_export", type=Path, help="drawio_tree.json")
    parser.add_argument("assignments", type=Path, help="machine_node_assignments.json")
    parser.add_argument("catalog", type=Path, help="current recipe catalog directory")
    parser.add_argument("output", type=Path, help="output directory")
    args = parser.parse_args()

    drawio = json.loads(args.drawio_export.read_text(encoding="utf-8"))
    assignment_data = json.loads(args.assignments.read_text(encoding="utf-8"))
    assignments: dict[str, dict[str, Any]] = assignment_data["nodes"]
    items = {row["item_id"]: row for row in read_csv(args.catalog / "items.csv")}
    recipes = {row["recipe_id"]: row for row in read_csv(args.catalog / "recipes.csv")}
    refs = read_csv(args.catalog / "recipe_refs.csv")
    active_mod_ids = {row["mod_id"] for row in read_csv(args.catalog / "mods.csv")}
    dependency_data = json.loads(
        (Path(__file__).resolve().parent / "machine_recipe_dependencies.json").read_text(
            encoding="utf-8"
        )
    )
    scripted_producers: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in dependency_data["recipes"]:
        # Recipe type is optional in the dependency manifest. When present it
        # provides authoritative evidence for a KubeJS recipe that the static
        # JAR catalog cannot see.
        if entry.get("recipe_type"):
            scripted_producers[(entry["node"], entry["output"])].append(entry)

    drawio_labels = {node["label"] for node in drawio["nodes"]}
    assignment_labels = set(assignments)
    failures: list[str] = []
    warnings: list[str] = []

    for label in sorted(drawio_labels - assignment_labels):
        failures.append(f"Authoritative node has no assignment: {label}")
    for label in sorted(assignment_labels - drawio_labels):
        failures.append(f"Assignment does not exist in authoritative Draw.io: {label}")

    producers: dict[str, set[str]] = defaultdict(set)
    recipe_inputs: dict[str, set[str]] = defaultdict(set)
    reference_kinds: dict[str, set[str]] = defaultdict(set)
    for ref in refs:
        resource_id = ref["resource_id"]
        reference_kinds[resource_id].add(ref["kind"])
        if ref["role"] == "output" and ref["kind"] != "tag":
            producers[resource_id].add(ref["recipe_id"])
        elif ref["role"] == "input":
            prefix = "#" if ref["kind"] == "tag" else ""
            recipe_inputs[ref["recipe_id"]].add(prefix + resource_id)

    owners: dict[str, list[str]] = defaultdict(list)
    unlock_types: dict[str, str] = {}
    allowed_unlock_types = {"item", "vanilla_item", "fluid", "chemical"}
    for label, assignment in assignments.items():
        unlocks = assignment.get("unlocks", [])
        declared_types = assignment.get("unlock_types", {})
        for declared_id in declared_types:
            if declared_id not in unlocks:
                failures.append(f"Typed unlock {declared_id} is not listed at {label}")
        for resource_id in unlocks:
            owners[resource_id].append(label)
            unlock_type = declared_types.get(resource_id, "item")
            unlock_types[resource_id] = unlock_type
            if unlock_type not in allowed_unlock_types:
                failures.append(
                    f"Unsupported unlock type {unlock_type} for {resource_id} at {label}"
                )
                continue
            if unlock_type == "item":
                registered = resource_id in items
            elif unlock_type == "vanilla_item":
                registered = (
                    resource_id.startswith("minecraft:")
                    and "item" in reference_kinds.get(resource_id, set())
                )
            else:
                namespace = resource_id.split(":", 1)[0]
                registered = (
                    namespace in active_mod_ids
                    and bool(reference_kinds.get(resource_id))
                )
            if not registered:
                failures.append(
                    f"Unregistered {unlock_type} unlock {resource_id} assigned to {label}"
                )
    for item_id, labels in sorted(owners.items()):
        if len(labels) > 1:
            warnings.append(f"Unlock appears in multiple nodes: {item_id} -> {' | '.join(labels)}")

    label_by_id = {node["id"]: node["label"] for node in drawio["nodes"]}
    incoming: dict[str, list[str]] = defaultdict(list)
    for edge in drawio["edges"]:
        source_label = label_by_id.get(edge.get("source"))
        target_label = label_by_id.get(edge.get("target"))
        if source_label and target_label:
            incoming[target_label].append(source_label)

    rows: list[dict[str, Any]] = []
    for node in drawio["nodes"]:
        label = node["label"]
        assignment = assignments.get(label, {})
        unlocks = assignment.get("unlocks", [])
        if not unlocks:
            rows.append(
                {
                    "node": label,
                    "role": assignment.get("role", ""),
                    "prerequisites": " | ".join(incoming[label]),
                    "unlock_id": "",
                    "unlock_type": "",
                    "display_name": "",
                    "registered": "",
                    "current_recipe_count": 0,
                    "current_recipe_types": "",
                    "current_recipe_ids": "",
                    "current_direct_inputs": "",
                    "alternate_recipe_action": "pending",
                    "stage_restricted_processing": "pending runtime architecture",
                    "implementation_status": "audit pending" if assignment.get("audit_note") else "milestone mapped",
                    "notes": assignment.get("audit_note", "No direct item unlock; completion/activation milestone."),
                }
            )
            continue

        for item_id in unlocks:
            unlock_type = unlock_types.get(item_id, "item")
            scripted = scripted_producers.get((label, item_id), [])
            if scripted:
                recipe_ids = sorted({entry["recipe_id"] for entry in scripted})
                recipe_types = sorted({entry["recipe_type"] for entry in scripted})
                inputs = sorted({
                    value
                    for entry in scripted
                    for value in entry.get("ingredients", []) + entry.get("foundational_tags", [])
                })
            else:
                recipe_ids = sorted(producers.get(item_id, set()))
                recipe_types = sorted({recipes.get(recipe_id, {}).get("recipe_type", "") for recipe_id in recipe_ids} - {""})
                inputs = sorted({value for recipe_id in recipe_ids for value in recipe_inputs.get(recipe_id, set())})
            rows.append(
                {
                    "node": label,
                    "role": assignment.get("role", ""),
                    "prerequisites": " | ".join(incoming[label]),
                    "unlock_id": item_id,
                    "unlock_type": unlock_type,
                    "display_name": items.get(item_id, {}).get("display_name", "")
                    or item_id.split(":", 1)[-1].replace("_", " ").title(),
                    "registered": (
                        "yes" if unlock_type in {"item", "vanilla_item"}
                        else f"yes ({unlock_type})"
                    ),
                    "current_recipe_count": len(recipe_ids),
                    "current_recipe_types": " | ".join(recipe_types),
                    "current_recipe_ids": " | ".join(recipe_ids),
                    "current_direct_inputs": " | ".join(inputs),
                    "alternate_recipe_action": "implemented" if scripted else "audit before rewrite",
                    "stage_restricted_processing": (
                        f"{label} exact-ID stage gate" if scripted else "pending runtime architecture"
                    ),
                    "implementation_status": (
                        "implemented and runtime-registered"
                        if scripted else "mapped; construction recipe not yet rewritten"
                    ),
                    "notes": assignment.get("audit_note", ""),
                }
            )

    args.output.mkdir(parents=True, exist_ok=True)
    csv_path = args.output / "machine_progression_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    md_lines = [
        "# Machine Progression Matrix",
        "",
        f"Authoritative Draw.io SHA-256: `{drawio['source_sha256']}`",
        "",
        "This is an implementation map, not a redesign. Node labels, prerequisites, positions, and edges come directly from the attached Draw.io file. Recipes remain marked pending until they are individually rewritten and bypass-tested.",
        "",
        "Ordinary item unlocks require real item-model/language catalog evidence; a recipe-only reference is not enough. Vanilla item forms and non-item fluid/chemical unlocks are explicitly typed in the assignment map and require both an active owning namespace and matching catalog references. This prevents optional compatibility outputs such as absent dust items from being misreported as registered.",
        "",
    ]
    for node in drawio["nodes"]:
        label = node["label"]
        assignment = assignments.get(label, {})
        md_lines.append(f"## {label}")
        md_lines.append("")
        md_lines.append(f"Role: {assignment.get('role', '')}")
        md_lines.append("")
        prereqs = incoming[label]
        md_lines.append(f"Prerequisites: {'; '.join(prereqs) if prereqs else 'none (root)'}")
        md_lines.append("")
        unlocks = assignment.get("unlocks", [])
        if unlocks:
            md_lines.append("Mapped unlocks:")
            md_lines.append("")
            for item_id in unlocks:
                unlock_type = unlock_types.get(item_id, "item")
                item = items.get(item_id, {})
                scripted = scripted_producers.get((label, item_id), [])
                count = len({entry["recipe_id"] for entry in scripted}) if scripted else len(producers.get(item_id, set()))
                display_name = item.get("display_name") or item_id.split(":", 1)[-1].replace("_", " ").title()
                type_note = "" if unlock_type in {"item", "vanilla_item"} else f" [{unlock_type}]"
                md_lines.append(f"- `{item_id}` — {display_name}{type_note} ({count} current recipe(s))")
        else:
            md_lines.append(f"Mapped unlocks: none. {assignment.get('audit_note', 'This is a completion/activation milestone rather than a direct item unlock.')}" )
        md_lines.append("")
    (args.output / "MACHINE_PROGRESSION_MATRIX.md").write_text("\n".join(md_lines), encoding="utf-8")

    report = {
        "drawio_sha256": drawio["source_sha256"],
        "nodes": len(drawio["nodes"]),
        "edges": len(drawio["edges"]),
        "matrix_rows": len(rows),
        "mapped_unlock_ids": sum(len(value.get("unlocks", [])) for value in assignments.values()),
        "failures": failures,
        "warnings": warnings,
    }
    (args.output / "machine_progression_validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Mapped {report['nodes']} nodes to {report['mapped_unlock_ids']} unlock IDs ({report['matrix_rows']} rows).")
    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"  WARN {warning}")
    if failures:
        print(f"FAIL: {len(failures)} issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: every authoritative node is mapped and every listed unlock is registered in the current catalog.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
