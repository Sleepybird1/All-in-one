from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit generic Mekanism machines before Create-first removal.")
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    recipes = read_csv(args.catalog / "recipes.csv")
    refs = read_csv(args.catalog / "recipe_refs.csv")
    items = {row["item_id"]: row for row in read_csv(args.catalog / "items.csv")}
    type_by_recipe = {row["recipe_id"]: row["recipe_type"] for row in recipes}

    outputs_by_recipe: dict[str, set[str]] = defaultdict(set)
    inputs_by_recipe: dict[str, set[str]] = defaultdict(set)
    producers_by_output: dict[str, set[str]] = defaultdict(set)
    for ref in refs:
        if ref["role"] == "output" and ref["kind"] != "tag":
            outputs_by_recipe[ref["recipe_id"]].add(ref["resource_id"])
            producers_by_output[ref["resource_id"]].add(ref["recipe_id"])
        elif ref["role"] == "input":
            prefix = "#" if ref["kind"] == "tag" else ""
            inputs_by_recipe[ref["recipe_id"]].add(prefix + ref["resource_id"])

    targets = [
        {
            "machine": "mekanism:crusher",
            "recipe_type": "mekanism:crushing",
            "factory_suffix": "crushing_factory",
            "create_replacement": "create:crushing or create:milling",
        },
        {
            "machine": "mekanism:precision_sawmill",
            "recipe_type": "mekanism:sawing",
            "factory_suffix": "sawing_factory",
            "create_replacement": "create:cutting",
        },
        {
            "machine": "mekanism:energized_smelter",
            "recipe_type": None,
            "factory_suffix": "smelting_factory",
            "create_replacement": "Create fan processing or vanilla smelting infrastructure",
        },
        {
            "machine": "mekanism:formulaic_assemblicator",
            "recipe_type": None,
            "factory_suffix": None,
            "create_replacement": "Create mechanical/deployer assembly early; AE2 autocrafting later",
        },
    ]

    report_targets: list[dict[str, object]] = []
    for target in targets:
        machine = target["machine"]
        construction_recipes = sorted(producers_by_output.get(machine, set()))
        processing_recipes = sorted(
            row["recipe_id"] for row in recipes if target["recipe_type"] and row["recipe_type"] == target["recipe_type"]
        )
        processing_set = set(processing_recipes)
        processing_outputs = sorted({output for recipe_id in processing_recipes for output in outputs_by_recipe[recipe_id]})
        output_rows = []
        unique_outputs = []
        for output in processing_outputs:
            alternate_recipes = sorted(producers_by_output[output] - processing_set)
            row = {
                "output": output,
                "display_name": items.get(output, {}).get("display_name", ""),
                "mekanism_recipes": sorted(producers_by_output[output] & processing_set),
                "alternate_recipes": alternate_recipes,
                "alternate_types": sorted({type_by_recipe.get(recipe_id, "") for recipe_id in alternate_recipes} - {""}),
            }
            output_rows.append(row)
            if not alternate_recipes:
                unique_outputs.append(row)

        factories = []
        if target["factory_suffix"]:
            suffix = target["factory_suffix"]
            factories = sorted(
                item_id
                for item_id in items
                if item_id.startswith("mekanism:") and item_id.endswith(str(suffix))
            )

        report_targets.append(
            {
                **target,
                "construction_recipes": construction_recipes,
                "construction_inputs": sorted({value for recipe_id in construction_recipes for value in inputs_by_recipe[recipe_id]}),
                "processing_recipe_count": len(processing_recipes),
                "processing_output_count": len(processing_outputs),
                "unique_output_count": len(unique_outputs),
                "unique_outputs": unique_outputs,
                "outputs": output_rows,
                "factories": factories,
            }
        )

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "duplicate_mekanism_machine_audit.json").write_text(
        json.dumps({"targets": report_targets}, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# Create-First Audit: Generic Mekanism Machines",
        "",
        "This report is evidence only. No machine is disabled by this audit.",
        "",
    ]
    for target in report_targets:
        lines.extend(
            [
                f"## {target['machine']}",
                "",
                f"Current construction recipe(s): {', '.join(f'`{value}`' for value in target['construction_recipes']) or 'none'}",
                "",
                f"Processing recipes: {target['processing_recipe_count']}",
                "",
                f"Distinct outputs: {target['processing_output_count']}",
                "",
                f"Outputs with no alternate recipe: {target['unique_output_count']}",
                "",
                f"Intended replacement family: {target['create_replacement']}",
                "",
            ]
        )
        if target["factories"]:
            lines.append("Related factory blocks:")
            lines.append("")
            for item_id in target["factories"]:
                lines.append(f"- `{item_id}`")
            lines.append("")
        if target["unique_outputs"]:
            lines.append("Outputs that must be ported before removal:")
            lines.append("")
            for row in target["unique_outputs"]:
                lines.append(f"- `{row['output']}` — {row['display_name']}")
            lines.append("")

    (args.output / "DUPLICATE_MEKANISM_MACHINE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")

    for target in report_targets:
        print(
            f"{target['machine']}: {target['processing_recipe_count']} recipes, "
            f"{target['processing_output_count']} outputs, {target['unique_output_count']} require migration"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
