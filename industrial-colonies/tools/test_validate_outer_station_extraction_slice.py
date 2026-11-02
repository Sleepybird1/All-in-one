#!/usr/bin/env python3
"""Mutation tests for commissioned station and gas-giant extraction policy."""

from __future__ import annotations

import csv
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_outer_station_extraction_slice as validator


class OuterStationExtractionMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.source = TOOLS.parent
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source / relative, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self, **kwargs) -> list[str]:
        return validator.validate(self.project, **kwargs)

    def mutate_json(self, relative: Path, mutator) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        mutator(payload)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        source = path.read_text(encoding="utf-8-sig")
        self.assertIn(old, source, f"test mutation token missing: {relative}:{old}")
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

    @staticmethod
    def recipe(payload: dict, recipe_id: str) -> dict:
        return next(row for row in payload["recipes"] if row["id"] == recipe_id)

    @staticmethod
    def quest(payload: dict, key: str) -> dict:
        return next(row for row in payload["chapter"]["quests"] if row["key"] == key)

    def test_01_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_02_missing_recipe_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["recipes"].__setitem__(
                slice(None),
                [row for row in value["recipes"] if row["id"] != validator.RECIPE_IDS[1]],
            ),
        )
        self.assertTrue(any("recipe set/order" in value for value in self.failures()))

    def test_03_recipe_ingredient_drift_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: self.recipe(value, validator.RECIPE_IDS[0])["key"].__setitem__(
                "O", "minecraft:glass"
            ),
        )
        self.assertTrue(any("key drifted" in value for value in self.failures()))

    def test_04_recipe_removal_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: self.recipe(value, validator.RECIPE_IDS[1]).__setitem__(
                "remove", ["minecraft:stick"]
            ),
        )
        self.assertTrue(any("introduced a removal" in value for value in self.failures()))

    def test_05_compiled_grid_fails(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row["recipeId"] == validator.RECIPE_IDS[0])
            card["params"]["gridH"] = "3"
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("not exactly 5x5" in value for value in self.failures()))

    def test_06_compiled_ingredient_fails(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row["recipeId"] == validator.RECIPE_IDS[2])
            card["slots"]["cell_0_0"]["id"] = "minecraft:bucket"
        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("ingredient grid" in value for value in self.failures()))

    def test_07_circular_warp_crystal_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: self.recipe(value, validator.RECIPE_IDS[2])["key"].__setitem__(
                "W", "cosmowarp:warp_crystal"
            ),
        )
        failures = self.failures()
        self.assertTrue(any("circular" in value or "Moon Crystal" in value for value in failures))

    def test_08_node_unlock_fails(self) -> None:
        self.mutate_json(
            validator.ASSIGNMENTS,
            lambda value: value["nodes"][validator.NODE]["unlocks"].pop(),
        )
        self.assertTrue(any("unlock assignment" in value for value in self.failures()))

    def test_09_quest_dependency_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "gas_giant_extraction").__setitem__(
                "dependencies", ["asteroid_bulk_freight"]
            ),
        )
        self.assertTrue(any("quest dependency" in value for value in self.failures()))

    def test_10_quest_reward_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "warp_charge_precursor").__setitem__(
                "rewards", [{"type": "item", "item": "minecraft:diamond"}]
            ),
        )
        self.assertTrue(any("gate, reward" in value for value in self.failures()))

    def test_11_quest_consumption_fails(self) -> None:
        self.mutate_json(
            validator.QUESTS,
            lambda value: self.quest(value, "gas_giant_condensate_return")["tasks"][0].__setitem__(
                "consume_items", True
            ),
        )
        self.assertTrue(any("gate, reward" in value for value in self.failures()))

    def test_12_item_registration_fails(self) -> None:
        self.replace(
            validator.ITEMS_JAVA,
            '"gas_giant_condensate_bucket"',
            '"missing_condensate_bucket"',
        )
        self.assertTrue(any("item registration" in value for value in self.failures()))

    def test_13_capability_registration_fails(self) -> None:
        self.replace(
            validator.BLOCK_ENTITIES_JAVA,
            "Capabilities.EnergyStorage.BLOCK",
            "Capabilities.ItemHandler.BLOCK",
        )
        self.assertTrue(any("capability registration" in value for value in self.failures()))

    def test_14_malformed_metadata_presence_fails(self) -> None:
        self.replace(
            validator.STATION_METADATA,
            "return root != null && root.contains(ROOT_KEY);",
            "return false;",
        )
        self.assertTrue(any("station metadata" in value for value in self.failures()))

    def test_15_whole_root_preservation_fails(self) -> None:
        self.replace(validator.STATION_METADATA, "existing.copy()", "new CompoundTag()")
        self.assertTrue(any("station metadata" in value for value in self.failures()))

    def test_16_ship_commissioning_fails(self) -> None:
        self.replace(
            validator.CONTROLLER_BE,
            "if (metadata == null\n                || !metadata.matchesController",
            "if (metadata == null\n                || metadata.role() != StationRole.STATION\n                || !metadata.matchesController",
        )
        self.assertTrue(any("SHIP role" in value for value in self.failures()))

    def test_17_controller_resource_simulation_fails(self) -> None:
        self.replace(
            validator.CONTROLLER_BE,
            "IFluidHandler.FluidAction.SIMULATE",
            "IFluidHandler.FluidAction.EXECUTE",
        )
        self.assertTrue(any("controller" in value and "SIMULATE" in value for value in self.failures()))

    def test_18_controller_block_removal_decommission_fails(self) -> None:
        self.replace(
            validator.CONTROLLER_BLOCK,
            "!state.is(newState.getBlock())",
            "state.is(newState.getBlock())",
        )
        self.assertTrue(any("block-removal lifecycle" in value for value in self.failures()))

    def test_18b_normal_unload_must_preserve_commissioning(self) -> None:
        self.replace(
            validator.CONTROLLER_BE,
            "public void setRemoved() {\n        // Chunk/sublevel unload",
            "public void setRemoved() {\n        decommissionForBlockRemoval();\n        // Chunk/sublevel unload",
        )
        self.assertTrue(any("normal controller unload" in value for value in self.failures()))

    def test_19_controller_energy_nbt_bound_fails(self) -> None:
        self.replace(
            validator.CONTROLLER_BE,
            "energyTag.getAsInt() <= ENERGY_CAPACITY",
            "true",
        )
        self.assertTrue(any("ENERGY_CAPACITY" in value for value in self.failures()))

    def test_20_controller_progress_nbt_bound_fails(self) -> None:
        self.replace(
            validator.CONTROLLER_BE,
            "progressTag.getAsInt() < COMMISSIONING_TICKS",
            "progressTag.getAsInt() <= Integer.MAX_VALUE",
        )
        self.assertTrue(any("COMMISSIONING_TICKS" in value for value in self.failures()))

    def test_21_controller_fluid_read_bypass_fails(self) -> None:
        path = self.project / validator.CONTROLLER_BE
        path.write_text(path.read_text(encoding="utf-8") + "\n// coolant.readFromNBT(registries, tag);\n", encoding="utf-8")
        self.assertTrue(any("readFromNBT" in value for value in self.failures()))

    def test_22_scoop_station_role_fails(self) -> None:
        self.replace(
            validator.SCOOP_BE,
            "metadata.role() != StationRole.STATION",
            "metadata.role() == null",
        )
        self.assertTrue(any("atmospheric scoop" in value for value in self.failures()))

    def test_23_scoop_live_controller_fails(self) -> None:
        self.replace(
            validator.SCOOP_BE,
            "!StationServicesControllerBlockEntity.isLiveFor(station, metadata)",
            "false",
        )
        self.assertTrue(any("atmospheric scoop" in value for value in self.failures()))

    def test_24_scoop_progress_nbt_bound_fails(self) -> None:
        self.replace(
            validator.SCOOP_BE,
            "progressTag.getAsInt() < CYCLE_TICKS",
            "progressTag.getAsInt() <= Integer.MAX_VALUE",
        )
        self.assertTrue(any("CYCLE_TICKS" in value for value in self.failures()))

    def test_25_surface_ship_coverage_fails(self) -> None:
        self.replace(
            validator.LIFE_SUPPORT,
            "if (subLevel.isRemoved()) {",
            "if (!DEEP_SPACE.equals(subLevel.getLevel().dimension()) || subLevel.isRemoved()) {",
        )
        self.assertTrue(any("surface SHIP" in value for value in self.failures()))

    def test_26_eye_coordinate_fails(self) -> None:
        self.replace(
            validator.LIFE_SUPPORT,
            "entity.getEyePosition()",
            "entity.position()",
        )
        self.assertTrue(any("deep-space breathing" in value for value in self.failures()))

    def test_27_sublevel_identity_fails(self) -> None:
        self.replace(
            validator.LIFE_SUPPORT,
            "Sable.HELPER.getTrackingOrVehicleSubLevel(entity)",
            "null",
        )
        self.assertTrue(any("deep-space breathing" in value for value in self.failures()))

    def test_28_loaded_chunk_scan_fails(self) -> None:
        self.replace(
            validator.LIFE_SUPPORT,
            "subLevel.getPlot().getLoadedChunks()",
            "java.util.List.<PlotChunkHolder>of()",
        )
        self.assertTrue(any("same-sublevel distributor" in value for value in self.failures()))

    def test_29_spherical_gas_math_fails(self) -> None:
        self.replace(
            validator.ORBIT_VERIFIER,
            "Math.sqrt(dx * dx + dy * dy + dz * dz)",
            "bodyPosition.getNorm() - gasGiant.radius()",
        )
        self.assertTrue(any("spherical" in value or "CUBE-shell" in value for value in self.failures()))

    def test_30_negative_coordinate_floor_fails(self) -> None:
        self.replace(validator.ORBIT_VERIFIER, "(int) pose.x()", "(int) Math.floor(pose.x())")
        self.assertTrue(any("cast semantics" in value for value in self.failures()))

    def test_31_live_oxygen_revalidation_fails(self) -> None:
        self.replace(
            validator.OXYGEN_MIXIN,
            "return industrialColonies$live\n                && isLit()",
            "return industrialColonies$live\n                && true",
        )
        self.assertTrue(any("live oxygen revalidation" in value for value in self.failures()))

    def test_32_breath_hook_scope_fails(self) -> None:
        self.replace(validator.BREATH_MIXIN, "@ModifyExpressionValue", "@Inject")
        self.assertTrue(any("breathing" in value for value in self.failures()))

    def test_33_whole_user_data_copy_fails(self) -> None:
        self.replace(
            validator.WARPER_MIXIN,
            "destination.setUserDataTag(sourceData.copy())",
            "destination.setUserDataTag(sourceData.getCompound(\"industrial_colonies:station\"))",
        )
        self.assertTrue(any("whole user-data root" in value or "warp preservation" in value for value in self.failures()))

    def test_34_mixin_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("GlobalSpacePhysicsHandlerMixin"),
        )
        self.assertTrue(any("mixin registration" in value for value in self.failures()))

    def test_35_catalog_bucket_recipe_bypass_fails(self) -> None:
        catalog = Path(self.temp.name) / "catalog"
        catalog.mkdir()
        with (catalog / "recipes.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["recipe_id", "outputs"])
            writer.writeheader()
            writer.writerow({
                "recipe_id": "evil:free_bucket",
                "outputs": "industrial_colonies:gas_giant_condensate_bucket",
            })
        self.assertTrue(any("recipe bypass" in value for value in self.failures(catalog=catalog)))

    def test_36_candidate_jar_requires_stage_entries(self) -> None:
        jar = Path(self.temp.name) / "candidate.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")
        self.assertTrue(any("candidate JAR" in value for value in self.failures(candidate_jar=jar)))


if __name__ == "__main__":
    unittest.main()
