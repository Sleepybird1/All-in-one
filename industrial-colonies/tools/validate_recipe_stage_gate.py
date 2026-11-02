#!/usr/bin/env python3
"""Static regression checks for the shared exact-ID recipe stage gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "industrial_colonies"
TRANSLATION_PREFIX = "com.industrial_colonies.research."
TRANSLATION_SUFFIX = ".name"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_fragment(path: Path, fragment: str) -> None:
    source = path.read_text(encoding="utf-8")
    if fragment not in source:
        raise AssertionError(f"{path.relative_to(ROOT)} is missing required fragment: {fragment}")


def research_ids_by_label() -> dict[str, str]:
    translations = load_json(
        ROOT
        / "src/generated/resources/data/industrial_colonies/generated_research_translations.json"
    )
    resolved: dict[str, str] = {}
    for key, label in translations.items():
        if not (
            isinstance(key, str)
            and isinstance(label, str)
            and key.startswith(TRANSLATION_PREFIX)
            and key.endswith(TRANSLATION_SUFFIX)
        ):
            continue
        body = key[len(TRANSLATION_PREFIX) : -len(TRANSLATION_SUFFIX)]
        branch, separator, research = body.partition(".")
        if not separator or not branch or not research:
            continue
        research_id = f"{MOD_ID}:{branch}/{research}"
        previous = resolved.setdefault(label, research_id)
        if previous != research_id:
            raise AssertionError(f"research label resolves to multiple IDs: {label}")
    return resolved


def expected_manifest() -> dict[str, str]:
    labels = research_ids_by_label()
    dependencies = load_json(ROOT / "tools/machine_recipe_dependencies.json")
    additional = load_json(ROOT / "tools/additional_recipe_stages.json")
    expected: dict[str, str] = {}
    for source in (dependencies, additional):
        for entry in source["recipes"]:
            recipe_id = entry["recipe_id"]
            node = entry["node"]
            try:
                stage = labels[node]
            except KeyError as exception:
                raise AssertionError(f"no generated research ID for node: {node}") from exception
            previous = expected.setdefault(recipe_id, stage)
            if previous != stage:
                raise AssertionError(
                    f"recipe {recipe_id} has conflicting stages: {previous} and {stage}"
                )
    return dict(sorted(expected.items()))


def validate_manifest() -> tuple[int, str]:
    generated_path = (
        ROOT
        / "build/generated/recipeStages/data/industrial_colonies/progression/recipe_stages.json"
    )
    expected = expected_manifest()
    selected_mode: str | None = None
    for label, path in (
        ("generated", generated_path),
        (
            "processed",
            ROOT
            / "build/resources/main/data/industrial_colonies/progression/recipe_stages.json",
        ),
    ):
        manifest = load_json(path)
        mode = manifest.get("mode")
        if mode == "physical_recipe_progression":
            # The current pack deliberately leaves the runtime gate installed
            # but gives it no recipe IDs. Progression is enforced by the
            # physical factory recipes compiled into KJSGen, not by hidden
            # MineColonies/FTB Teams authorization. Keeping the hooks loaded
            # is harmless and preserves compatibility if a future optional
            # module supplies an exact-ID stage manifest.
            if manifest.get("recipes") != {}:
                raise AssertionError(
                    f"{label} physical-progression manifest must have an empty recipe map"
                )
            current_mode = "physical_recipe_progression"
        else:
            if manifest.get("source") != "tools/machine_recipe_dependencies.json":
                raise AssertionError(f"{label} recipe-stage manifest has the wrong source marker")
            if manifest.get("additional_source") != "tools/additional_recipe_stages.json":
                raise AssertionError(f"{label} recipe-stage manifest has the wrong additional source marker")
            if manifest.get("recipes") != expected:
                raise AssertionError(
                    f"{label} exact-ID recipe-stage map differs from dependencies"
                )
            current_mode = "legacy_exact_id_stage_gate"

        if selected_mode is None:
            selected_mode = current_mode
        elif selected_mode != current_mode:
            raise AssertionError(
                "generated and processed recipe-stage manifests use different modes"
            )

    count = 0 if selected_mode == "physical_recipe_progression" else len(expected)
    return count, selected_mode or "unknown"


def validate_mixins(*, check_processed: bool = True) -> None:
    mixins_path = ROOT / "src/main/resources/industrial_colonies.mixins.json"
    mixin_metadata = load_json(mixins_path)
    if check_processed:
        processed_metadata = load_json(ROOT / "build/resources/main/industrial_colonies.mixins.json")
        if processed_metadata != mixin_metadata:
            raise AssertionError("processed mixin metadata differs from source")
    mixins = mixin_metadata["mixins"]
    for required in (
        "AECraftingPatternAccessor",
        "AE2CraftingBlockItemMixin",
        "AE2CraftingUnitBlockMixin",
        "AE2InscriberBlockEntityMixin",
        "AE2MolecularAssemblerBlockEntityMixin",
        "AE2StorageCellItemMixin",
        "AbstractFurnaceBlockEntityMixin",
        "CastingBlockEntityMixin",
        "CraftingMenuMixin",
        "ExtendedAERecipeExecutorMixin",
        "FoundryBasinOperatingBEMixin",
        "FoundryMixerBlockEntityMixin",
        "ModernFoundryCastingBlockEntityMixin",
        "RecipeBookMenuMixin",
        "RecipeCacheLookupMonitorMixin",
        "SawBlockEntityMixin",
        "SmithingMenuMixin",
        "StonecutterMenuMixin",
        "TFMGCastingBasinBlockEntityMixin",
        "TFMGPolarizerBlockEntityMixin",
        "TFMGRecipeTypesMixin",
        "TFMGVatBlockEntityMixin",
        "TFMGWindingMachineBlockEntityMixin",
    ):
        if required not in mixins:
            raise AssertionError(f"mixin metadata is missing {required}")

    crafting = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/CraftingMenuMixin.java"
    require_fragment(
        crafting,
        "slotChangedCraftingGrid(Lnet/minecraft/world/inventory/AbstractContainerMenu;",
    )
    require_fragment(crafting, "Lnet/minecraft/world/inventory/ResultContainer;setRecipeUsed(")
    require_fragment(crafting, "RecipeStageGate.canUse(player, recipe)")
    require_fragment(crafting, "result.setRecipeUsed(level, player, recipe)")

    recipe_book = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/RecipeBookMenuMixin.java"
    require_fragment(
        recipe_book,
        "handlePlacement(ZLnet/minecraft/world/item/crafting/RecipeHolder;",
    )
    require_fragment(recipe_book, "cancellable = true")
    require_fragment(recipe_book, "RecipeStageGate.canUse(player, recipe)")

    smithing = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/SmithingMenuMixin.java"
    require_fragment(smithing, 'method = "createResult"')
    require_fragment(smithing, 'method = "mayPickup"')
    require_fragment(smithing, "RecipeStageGate.canUse(serverPlayer, this.selectedRecipe)")
    require_fragment(smithing, "this.resultSlots.setItem(0, ItemStack.EMPTY)")
    require_fragment(smithing, "callback.setReturnValue(false)")

    shared_gate = ROOT / "src/main/java/dev/godpc/industrialcolonies/RecipeStageGate.java"
    require_fragment(shared_gate, '"progression/recipe_stages.json"')
    require_fragment(shared_gate, "getTeamForPlayerID")
    require_fragment(shared_gate, "TeamStagesHelper.hasTeamStage")

    mekanism_gate = ROOT / "src/main/java/dev/godpc/industrialcolonies/MekanismRecipeStageGate.java"
    require_fragment(mekanism_gate, "RecipeStageGate.requiredStage(recipeId)")

    machine_gate = ROOT / "src/main/java/dev/godpc/industrialcolonies/MachineRecipeStageGate.java"
    require_fragment(machine_gate, "public static boolean canUse(BlockEntity machine, RecipeHolder<?> recipe)")
    require_fragment(machine_gate, "public static boolean canUse(BlockEntity machine, Recipe<?> recipe)")
    require_fragment(machine_gate, "CreateMachineOwner.get(machine)")

    ownership = ROOT / "src/main/java/dev/godpc/industrialcolonies/CreateMachineOwner.java"
    require_fragment(ownership, "if (blockEntity == null)")
    require_fragment(ownership, "blockEntity.setData(OWNER.get(), owner)")

    furnace = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/AbstractFurnaceBlockEntityMixin.java"
    require_fragment(furnace, "canBurn(Lnet/minecraft/core/RegistryAccess;")
    require_fragment(furnace, "MachineRecipeStageGate.canUse(furnace, recipe)")

    stonecutter = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/StonecutterMenuMixin.java"
    require_fragment(stonecutter, 'method = "clickMenuButton"')
    require_fragment(stonecutter, 'method = "setupResultSlot"')
    require_fragment(stonecutter, "RecipeStageGate.canUse(serverPlayer, recipe)")

    saw = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/SawBlockEntityMixin.java"
    require_fragment(saw, 'method = "getRecipes"')
    require_fragment(saw, "CreateRecipeStageGate.canUse(saw.getLevel(), recipe, saw)")

    ae2_gate = ROOT / "src/main/java/dev/godpc/industrialcolonies/AE2RecipeStageGate.java"
    require_fragment(ae2_gate, "AERecipeTypes.CELL_DISASSEMBLY")
    require_fragment(ae2_gate, "AERecipeTypes.CRAFTING_UNIT_TRANSFORM")

    inscriber = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/AE2InscriberBlockEntityMixin.java"
    require_fragment(inscriber, 'method = "getTask"')
    require_fragment(inscriber, "MachineRecipeStageGate.canUse(machine, task)")

    molecular = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/AE2MolecularAssemblerBlockEntityMixin.java"
    require_fragment(molecular, 'method = "pushPattern"')
    require_fragment(molecular, 'method = "tickingRequest"')
    require_fragment(molecular, "MachineRecipeStageGate.canUse((BlockEntity) (Object) this, recipe)")

    ae2_accessor = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/AECraftingPatternAccessor.java"
    require_fragment(ae2_accessor, '@Accessor("recipeHolder")')

    extended_ae = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/ExtendedAERecipeExecutorMixin.java"
    require_fragment(extended_ae, "context.currentRecipe")
    require_fragment(extended_ae, "MachineRecipeStageGate.canUse(blockEntity, recipe)")

    tfmg_find = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/TFMGRecipeTypesMixin.java"
    require_fragment(tfmg_find, 'method = "find"')
    require_fragment(tfmg_find, "CreateRecipeStageGate.canUseCurrent(recipe.get())")

    modern_foundry = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/ModernFoundryCastingBlockEntityMixin.java"
    require_fragment(modern_foundry, "findCastingRecipe()")
    require_fragment(modern_foundry, 'method = "serverTick"')
    require_fragment(modern_foundry, "MachineRecipeStageGate.canUse(machine, this.currentRecipe)")

    foundry_mixer = (
        ROOT
        / "src/main/java/dev/godpc/industrialcolonies/mixin/FoundryMixerBlockEntityMixin.java"
    )
    require_fragment(foundry_mixer, "FoundryMixerBlockEntity")
    require_fragment(foundry_mixer, "matchBasinRecipe(")
    require_fragment(foundry_mixer, "CreateRecipeStageGate.canUse")

    foundry_basin = (
        ROOT
        / "src/main/java/dev/godpc/industrialcolonies/mixin/FoundryBasinOperatingBEMixin.java"
    )
    require_fragment(foundry_basin, "FoundryBasinOperatingBE")
    require_fragment(foundry_basin, "matchBasinRecipe(")
    require_fragment(foundry_basin, "CreateRecipeStageGate.canUse")

    casting = (
        ROOT
        / "src/main/java/dev/godpc/industrialcolonies/mixin/CastingBlockEntityMixin.java"
    )
    require_fragment(casting, "CastingBlockEntity")
    require_fragment(casting, "matchCastingRecipe(")
    require_fragment(casting, "CreateRecipeStageGate.canUse")

    classes = ROOT / "build/classes/java/main/dev/godpc/industrialcolonies"
    for class_file in (
        classes / "MachineRecipeStageGate.class",
        classes / "RecipeStageGate.class",
        classes / "MekanismRecipeStageGate.class",
        classes / "mixin/AECraftingPatternAccessor.class",
        classes / "mixin/AE2CraftingBlockItemMixin.class",
        classes / "mixin/AE2CraftingUnitBlockMixin.class",
        classes / "mixin/AE2InscriberBlockEntityMixin.class",
        classes / "mixin/AE2MolecularAssemblerBlockEntityMixin.class",
        classes / "mixin/AE2StorageCellItemMixin.class",
        classes / "mixin/AbstractFurnaceBlockEntityMixin.class",
        classes / "mixin/CastingBlockEntityMixin.class",
        classes / "mixin/CraftingMenuMixin.class",
        classes / "mixin/ExtendedAERecipeExecutorMixin.class",
        classes / "mixin/FoundryBasinOperatingBEMixin.class",
        classes / "mixin/FoundryMixerBlockEntityMixin.class",
        classes / "mixin/ModernFoundryCastingBlockEntityMixin.class",
        classes / "mixin/RecipeBookMenuMixin.class",
        classes / "mixin/SawBlockEntityMixin.class",
        classes / "mixin/SmithingMenuMixin.class",
        classes / "mixin/StonecutterMenuMixin.class",
        classes / "mixin/TFMGCastingBasinBlockEntityMixin.class",
        classes / "mixin/TFMGPolarizerBlockEntityMixin.class",
        classes / "mixin/TFMGRecipeTypesMixin.class",
        classes / "mixin/TFMGVatBlockEntityMixin.class",
        classes / "mixin/TFMGWindingMachineBlockEntityMixin.class",
    ):
        if not class_file.is_file():
            raise AssertionError(f"compiled class is missing: {class_file.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="check source mixins and emitted classes without requiring regenerated resources",
    )
    arguments = parser.parse_args()

    if arguments.source_only:
        validate_mixins(check_processed=False)
        print(
            "Recipe-stage runtime source validation passed: player crafting/cooking/cutting, "
            "Create, Mekanism, AE2, ExtendedAE, TFMG, Create Metallurgy, and ModernFoundry hooks."
        )
        return

    count, mode = validate_manifest()
    validate_mixins(check_processed=True)
    if mode == "physical_recipe_progression":
        print(
            "Recipe-stage runtime validation passed: physical-recipe mode has zero "
            "MineColonies/FTB Teams recipe gates, while all optional exact-ID hooks "
            "remain structurally valid."
        )
    else:
        print(
            f"Recipe-stage gate validation passed: {count} exact recipe IDs and all covered "
            "player/machine runtime hooks."
        )


if __name__ == "__main__":
    main()
