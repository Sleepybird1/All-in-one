from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def ancestors(node: str, incoming: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    frontier = list(incoming.get(node, set()))
    while frontier:
        parent = frontier.pop()
        if parent in found:
            continue
        found.add(parent)
        frontier.extend(incoming.get(parent, set()))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reject rewritten machine recipes that consume downstream Draw.io unlocks; vanilla inputs remain foundational."
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="industrial-colonies project root",
    )
    parser.add_argument(
        "--drawio-export",
        type=Path,
        required=True,
        help="read-only authoritative Draw.io JSON export",
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    graph = load_json(args.drawio_export.resolve())
    mapping = load_json(project / "progression" / "machine_node_assignments.json")
    manifest = load_json(project / "tools" / "machine_recipe_dependencies.json")
    policies = load_json(project / "tools" / "canonicalization_policies.json")

    id_to_label = {node["id"]: node["label"] for node in graph["nodes"]}
    graph_nodes = set(id_to_label.values())
    incoming: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        source = id_to_label.get(edge["source"])
        target = id_to_label.get(edge["target"])
        if source and target:
            incoming[target].add(source)

    item_owners: dict[str, set[str]] = defaultdict(set)
    for node, definition in mapping["nodes"].items():
        for item in definition.get("unlocks", []):
            item_owners[item].add(node)

    overhaul_by_output = {
        policy["machine"]: policy for policy in policies.get("machine_overhauls", [])
    }
    results: list[dict[str, Any]] = []
    failures: list[str] = []

    manifest_outputs = {entry["output"] for entry in manifest["recipes"]}
    policy_outputs = set(overhaul_by_output)
    for output in sorted(policy_outputs - manifest_outputs):
        failures.append(f"Missing dependency manifest for overhaul: {output}")
    for output in sorted(manifest_outputs - policy_outputs):
        failures.append(f"Dependency manifest has no machine-overhaul policy: {output}")

    for entry in manifest["recipes"]:
        output = entry["output"]
        target = entry["node"]
        policy = overhaul_by_output.get(output)
        row: dict[str, Any] = {
            "output": output,
            "node": target,
            "recipe_id": entry["recipe_id"],
            "script": entry["script"],
            "ingredients": [],
            "foundational_tags": entry.get("foundational_tags", []),
        }

        if target not in graph_nodes:
            failures.append(f"Unknown target node for {output}: {target}")
        allowed_nodes = ancestors(target, incoming) | {target}

        if policy:
            for key in ("node", "script", "replacement_recipe"):
                expected = entry["recipe_id"] if key == "replacement_recipe" else entry[key]
                if policy.get(key) != expected:
                    failures.append(
                        f"Manifest/policy mismatch for {output} {key}: "
                        f"{expected!r} != {policy.get(key)!r}"
                    )

        script_path = project / "pack-scripts" / "server_scripts" / entry["script"]
        script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        if not script_path.exists():
            failures.append(f"Missing recipe script for {output}: {script_path}")
        if entry["recipe_id"] not in script_text:
            failures.append(f"Recipe id is absent from {entry['script']}: {entry['recipe_id']}")

        for ingredient in entry["ingredients"]:
            owners = item_owners.get(ingredient, set())
            valid_owners = owners & allowed_nodes
            status = (
                "valid"
                if valid_owners
                else "vanilla"
                if ingredient.startswith("minecraft:")
                else "unmapped"
                if not owners
                else "downstream"
            )
            row["ingredients"].append(
                {
                    "item": ingredient,
                    "owners": sorted(owners),
                    "valid_owners": sorted(valid_owners),
                    "status": status,
                }
            )
            if ingredient not in script_text:
                failures.append(f"Manifest ingredient is absent from {entry['script']}: {ingredient}")
            if status == "unmapped":
                failures.append(f"Unmapped exact ingredient for {output}: {ingredient}")
            elif status == "downstream":
                failures.append(
                    f"Downstream/sibling ingredient for {output} at {target}: "
                    f"{ingredient} belongs to {' | '.join(sorted(owners))}"
                )
        results.append(row)

    report = {
        "drawio_source": graph.get("source"),
        "drawio_source_sha256": graph.get("source_sha256"),
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph["edges"]),
        "machine_recipes": len(results),
        "exact_ingredients": sum(len(row["ingredients"]) for row in results),
        "foundational_tags": sum(len(row["foundational_tags"]) for row in results),
        "results": results,
        "failures": failures,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"Checked {report['machine_recipes']} rewritten machine recipes, "
        f"{report['exact_ingredients']} exact ingredient references, and "
        f"{report['foundational_tags']} declared foundational tag references "
        f"against {report['graph_nodes']} Draw.io nodes / {report['graph_edges']} edges."
    )
    if failures:
        print(f"FAIL: {len(failures)} progression issue(s)", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("PASS: every exact ingredient is vanilla-foundational or unlocked at the recipe node/ancestor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
