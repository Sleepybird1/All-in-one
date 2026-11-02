#!/usr/bin/env python3
"""Static contract check for the bounded food-diversity health system."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, token: str, label: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"{label}: missing {token!r}")


def main() -> int:
    failures: list[str] = []
    progression_path = ROOT / "src/main/java/dev/godpc/industrialcolonies/food/FoodDiversityProgression.java"
    data_path = ROOT / "src/main/java/dev/godpc/industrialcolonies/food/FoodDiversityData.java"
    milestone_path = ROOT / "src/main/java/dev/godpc/industrialcolonies/food/FoodDiversityMilestones.java"
    attachment_path = ROOT / "src/main/java/dev/godpc/industrialcolonies/IndustrialAttachments.java"
    entrypoint_path = ROOT / "src/main/java/dev/godpc/industrialcolonies/IndustrialColonies.java"
    language_path = ROOT / "src/main/resources/assets/industrial_colonies/lang/en_us.json"
    documentation_path = ROOT / "FOOD_DIVERSITY_PROGRESSION.md"

    paths = (
        progression_path,
        data_path,
        milestone_path,
        attachment_path,
        entrypoint_path,
        language_path,
        documentation_path,
    )
    for path in paths:
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    progression = progression_path.read_text(encoding="utf-8")
    data = data_path.read_text(encoding="utf-8")
    milestones = milestone_path.read_text(encoding="utf-8")
    attachment = attachment_path.read_text(encoding="utf-8")
    entrypoint = entrypoint_path.read_text(encoding="utf-8")
    documentation = documentation_path.read_text(encoding="utf-8")

    threshold_match = re.search(
        r"UNIQUE_FOOD_MILESTONES\s*=\s*\{([^}]*)\}", milestones
    )
    if threshold_match is None:
        failures.append("milestones: threshold array not found")
        thresholds: list[int] = []
    else:
        thresholds = [int(value) for value in re.findall(r"\d+", threshold_match.group(1))]
        if thresholds != [10, 25, 45, 70, 100]:
            failures.append(f"milestones: unexpected conservative thresholds {thresholds}")
        if thresholds != sorted(set(thresholds)):
            failures.append("milestones: thresholds must be strictly increasing and unique")

    require(milestones, "HEALTH_POINTS_PER_MILESTONE = 2", "milestones", failures)
    require(milestones, "MAX_BONUS_HEALTH", "milestones", failures)
    require(progression, "LivingEntityUseItemEvent.Finish", "consumption hook", failures)
    require(progression, "consumed.getFoodProperties(player)", "generic food detection", failures)
    require(progression, "BuiltInRegistries.ITEM.getKey", "registry identity", failures)
    require(progression, "current.hasEaten(foodId)", "repeat protection", failures)
    require(progression, "player.setData(IndustrialAttachments.FOOD_DIVERSITY", "persistence update", failures)
    require(progression, "Attributes.MAX_HEALTH", "health reward", failures)
    require(progression, "addOrReplacePermanentModifier", "health reconciliation", failures)
    require(progression, "PlayerLoggedInEvent", "login reconciliation", failures)
    require(progression, "PlayerRespawnEvent", "respawn reconciliation", failures)
    require(progression, 'Commands.literal("cuisine")', "progress command", failures)

    require(data, "ResourceLocation.CODEC", "serialized item ids", failures)
    require(data, "Set.copyOf", "immutable food set", failures)
    require(attachment, ".serialize(FoodDiversityData.CODEC)", "attachment serialization", failures)
    require(attachment, ".copyOnDeath()", "death persistence", failures)
    require(entrypoint, "IndustrialAttachments.register(modEventBus)", "attachment registration", failures)
    require(entrypoint, "FoodDiversityProgression.register()", "event registration", failures)

    forbidden_hardcoded_ids = ("pamhc2", "farmersdelight:", "minecraft:apple")
    combined_java = progression + data + milestones + attachment
    for token in forbidden_hardcoded_ids:
        if token in combined_java.lower():
            failures.append(f"generic integration: hard-coded food id or namespace {token!r}")

    translations = json.loads(language_path.read_text(encoding="utf-8"))
    for key in (
        "message.industrial_colonies.food_diversity.new_food",
        "message.industrial_colonies.food_diversity.progress",
        "message.industrial_colonies.food_diversity.milestone",
        "message.industrial_colonies.food_diversity.complete",
    ):
        if key not in translations:
            failures.append(f"translations: missing {key}")

    for token in ("+5 hearts", "FoodProperties", "copyOnDeath()", "/cuisine"):
        require(documentation, token, "documentation", failures)

    if thresholds and len(thresholds) * 2 != 10:
        failures.append("milestones: health cap must remain exactly +10 points (+5 hearts)")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    print(
        "Food diversity progression validated: "
        f"{len(thresholds)} milestones through {thresholds[-1]} foods, "
        "+10 max health cap, generic FoodProperties eligibility, "
        "repeat-safe registry identity, persistent copy-on-death data."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
