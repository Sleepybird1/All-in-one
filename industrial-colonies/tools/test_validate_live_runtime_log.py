#!/usr/bin/env python3
"""Focused parser tests for validate_live_runtime_log.py."""

from __future__ import annotations

import unittest

import validate_live_runtime_log as validator


class RuntimeLogParserTests(unittest.TestCase):
    def test_actinide_bridge_runtime_marker_is_required(self) -> None:
        marker = "Canonical actinide waste bridge loaded"
        self.assertEqual(
            marker, validator.FOCUSED_POLICY_MESSAGES["actinide_waste_bridge"]
        )
        self.assertTrue(
            validator.focused_policy_evidence(marker)["actinide_waste_bridge"]["pass"]
        )
        self.assertFalse(
            validator.focused_policy_evidence(
                "Legacy actinide script disabled"
            )["actinide_waste_bridge"]["pass"]
        )

    def test_expected_quest_count_includes_guidance_dungeons_endgame_orbital_and_planetary(self) -> None:
        self.assertEqual(124, validator.load_expected_quest_count(validator.PROJECT_ROOT))
        self.assertEqual(
            {"chapters": 10, "quests": 124, "reward_tables": 0},
            validator.load_expected_quest_topology(validator.PROJECT_ROOT),
        )

    def test_latest_script_block_keeps_extra_user_scripts(self) -> None:
        log = """
[KubeJS Server/]: Loaded script server_scripts:industrial_a.js in 0.001 s
[KubeJS Server/]: Loaded script server_scripts:kjsgen_recipes.js in 0.001 s
[KubeJS Server/]: Loaded script server_scripts:main.js in 0.001 s
[KubeJS Server/]: Loaded 3/3 KubeJS server scripts in 0.01 s with 0 errors and 0 warnings
"""
        actual = validator.parse_latest_server_script_load(log)
        self.assertIsNotNone(actual)
        assert actual is not None
        self.assertEqual(actual["total"], 3)
        self.assertEqual(
            actual["script_names"],
            ["industrial_a.js", "kjsgen_recipes.js", "main.js"],
        )

    def test_latest_script_block_does_not_mix_reload_epochs(self) -> None:
        log = """
[KubeJS Server/]: Loaded script server_scripts:old.js in 0.001 s
[KubeJS Server/]: Loaded 1/1 KubeJS server scripts in 0.01 s with 0 errors and 0 warnings
[KubeJS Server/]: Loaded script server_scripts:new.js in 0.001 s
[KubeJS Server/]: Loaded 1/1 KubeJS server scripts in 0.01 s with 0 errors and 0 warnings
"""
        actual = validator.parse_latest_server_script_load(log)
        self.assertIsNotNone(actual)
        assert actual is not None
        self.assertEqual(actual["script_names"], ["new.js"])

    def test_ftb_server_count_is_distinct_from_network_object_count(self) -> None:
        log = """
[Server thread/INFO] [FTB Quests/]: Loaded 1 chapter groups, 1 chapters, 3 quests, 0 reward tables
[Render thread/INFO] [FTB Quests/]: Read 1190 bytes, 8 objects
"""
        evidence = validator.parse_ftb_quest_evidence(log)
        self.assertEqual(evidence["server"]["quests"], 3)
        self.assertEqual(evidence["client_sync"]["objects"], 8)

    def test_critical_owned_mixins_require_exact_target_application(self) -> None:
        log = """
[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from industrial_colonies.mixins.json into com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
[mixin/]: Mixing DungeonCrawlRandomItemsMixin from industrial_colonies.mixins.json into xiroc.dungeoncrawl.dungeon.treasure.RandomItems
[mixin/]: Mixing SpaceTransitionHandlerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.SpaceTransitionHandler
[mixin/]: Mixing DeepSpaceInstanceMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.orbit.DeepSpaceInstance
[mixin/]: Mixing AsteroidSpawnerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.AsteroidSpawner
[mixin/]: Mixing OxygenDistributorBlockEntityMixin from industrial_colonies.mixins.json into earth.terrarium.adastra.common.blockentities.machines.OxygenDistributorBlockEntity
[mixin/]: Mixing GlobalSpacePhysicsHandlerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.GlobalSpacePhysicsHandler
[mixin/]: Mixing SubLevelWarperUserDataMixin from industrial_colonies.mixins.json into dev.egg.SubLevelWarper
[mixin/]: Mixing SableRemovalBoundaryMixin from industrial_colonies.mixins.json into dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer
[mixin/]: Mixing ReactorSolidAccessPortEntityMixin from industrial_colonies.mixins.json into it.zerono.mods.extremereactors.gamecontent.multiblock.reactor.part.ReactorSolidAccessPortEntity
[mixin/]: Mixing CosmowarpWarpDriveMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity
[mixin/]: Mixing CosmowarpNetworkingMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.network.ModNetworking
[mixin/]: Mixing CosmowarpWarpDriveBlockMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.block.WarpDriveBlock
[mixin/]: Mixing CosmowarpWarpDriveMenuMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.menu.WarpDriveMenu
[mixin/]: Mixing CosmowarpWarpDriveClickMixin from industrial_colonies.mixins.json into net.minecraft.world.inventory.AbstractContainerMenu
[mixin/]: Mixing CosmowarpCrystalSlotOwnerMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntity$1
[mixin/]: Mixing CosmowarpCrystalSlotFreezeMixin from industrial_colonies.mixins.json into net.neoforged.neoforge.items.ItemStackHandler
[mixin/]: Mixing CosmowarpCapabilityMixin from industrial_colonies.mixins.json into dev.waco0311.cosmowarp.Cosmonauticswarpdrive
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity
[mixin/]: Mixing WindmillBearingBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertTrue(evidence["finite_tfmg_oil_reservoir"]["applied"])
        self.assertTrue(evidence["dungeon_crawl_worn_equipment"]["applied"])
        self.assertTrue(evidence["orbital_flight_computer_transition"]["applied"])
        self.assertTrue(evidence["mars_navigation_computer_descent"]["applied"])
        self.assertTrue(evidence["deep_space_asteroid_eligibility"]["applied"])
        self.assertTrue(evidence["station_oxygen_distributor_state"]["applied"])
        self.assertTrue(evidence["station_breathing_boundary"]["applied"])
        self.assertTrue(evidence["station_whole_userdata_transfer"]["applied"])
        self.assertTrue(evidence["interstellar_source_removal_boundary"]["applied"])
        self.assertTrue(evidence["reinforced_reactor_plutonium_boundary"]["applied"])
        self.assertTrue(evidence["signed_interstellar_warp_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_packet_sender_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_menu_open_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_menu_validity_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_menu_click_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_crystal_owner_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_crystal_capability_boundary"]["applied"])
        self.assertTrue(evidence["interstellar_capability_wrapper_boundary"]["applied"])
        self.assertTrue(evidence["orbital_ambient_hydro"]["applied"])
        self.assertTrue(evidence["orbital_ambient_wind"]["applied"])
        self.assertTrue(all(row["applied"] for row in evidence.values()))
        self.assertEqual([], validator.find_owned_mixin_failures(log))
        self.assertTrue(validator.evaluate_owned_mixin_runtime(log, log)["pass"])

    def test_interstellar_warp_mixin_requires_exact_target(self) -> None:
        log = (
            "[mixin/]: Mixing CosmowarpWarpDriveMixin from "
            "industrial_colonies.mixins.json into "
            "dev.waco0311.cosmowarp.block.entity.WarpDriveBlockEntityProxy\n"
        )
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(evidence["signed_interstellar_warp_boundary"]["applied"])

    def test_sable_removal_boundary_requires_exact_container_target(self) -> None:
        log = (
            "[mixin/]: Mixing SableRemovalBoundaryMixin from "
            "industrial_colonies.mixins.json into "
            "dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainerProxy\n"
        )
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(
            evidence["interstellar_source_removal_boundary"]["applied"]
        )

    def test_missing_orbital_transition_mixin_is_not_runtime_proof(self) -> None:
        log = """
[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from industrial_colonies.mixins.json into com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
[mixin/]: Mixing DungeonCrawlRandomItemsMixin from industrial_colonies.mixins.json into xiroc.dungeoncrawl.dungeon.treasure.RandomItems
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity
[mixin/]: Mixing WindmillBearingBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(
            evidence["orbital_flight_computer_transition"]["applied"]
        )
        self.assertFalse(all(row["applied"] for row in evidence.values()))
        self.assertFalse(
            validator.evaluate_owned_mixin_runtime(log, log)["pass"]
        )

    def test_missing_mars_descent_mixin_is_not_runtime_proof(self) -> None:
        log = """
[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from industrial_colonies.mixins.json into com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
[mixin/]: Mixing DungeonCrawlRandomItemsMixin from industrial_colonies.mixins.json into xiroc.dungeoncrawl.dungeon.treasure.RandomItems
[mixin/]: Mixing SpaceTransitionHandlerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.SpaceTransitionHandler
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity
[mixin/]: Mixing WindmillBearingBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(evidence["mars_navigation_computer_descent"]["applied"])
        self.assertFalse(validator.evaluate_owned_mixin_runtime(log, log)["pass"])

    def test_missing_asteroid_eligibility_mixin_is_not_runtime_proof(self) -> None:
        log = """
[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from industrial_colonies.mixins.json into com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
[mixin/]: Mixing DungeonCrawlRandomItemsMixin from industrial_colonies.mixins.json into xiroc.dungeoncrawl.dungeon.treasure.RandomItems
[mixin/]: Mixing SpaceTransitionHandlerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.SpaceTransitionHandler
[mixin/]: Mixing DeepSpaceInstanceMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.orbit.DeepSpaceInstance
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity
[mixin/]: Mixing WindmillBearingBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntity
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(evidence["deep_space_asteroid_eligibility"]["applied"])
        self.assertFalse(validator.evaluate_owned_mixin_runtime(log, log)["pass"])

    def test_missing_ambient_kinetic_mixin_is_not_runtime_proof(self) -> None:
        log = """
[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from industrial_colonies.mixins.json into com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.PumpjackBaseBlockEntity
[mixin/]: Mixing DungeonCrawlRandomItemsMixin from industrial_colonies.mixins.json into xiroc.dungeoncrawl.dungeon.treasure.RandomItems
[mixin/]: Mixing SpaceTransitionHandlerMixin from industrial_colonies.mixins.json into dev.devce.rocketnautics.content.physics.SpaceTransitionHandler
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertTrue(evidence["orbital_ambient_hydro"]["applied"])
        self.assertFalse(evidence["orbital_ambient_wind"]["applied"])
        self.assertFalse(validator.evaluate_owned_mixin_runtime(log, log)["pass"])

    def test_ambient_kinetic_mixins_require_exact_create_targets(self) -> None:
        log = """
[mixin/]: Mixing WaterWheelBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntityProxy
[mixin/]: Mixing WindmillBearingBlockEntityMixin from industrial_colonies.mixins.json into com.simibubi.create.content.contraptions.bearing.WindmillBearingBlockEntityProxy
"""
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(evidence["orbital_ambient_hydro"]["applied"])
        self.assertFalse(evidence["orbital_ambient_wind"]["applied"])

    def test_orbital_transition_mixin_requires_exact_target(self) -> None:
        log = (
            "[mixin/]: Mixing SpaceTransitionHandlerMixin from "
            "industrial_colonies.mixins.json into "
            "dev.devce.rocketnautics.content.physics.SpaceTransitionHandlerProxy\n"
        )
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(
            evidence["orbital_flight_computer_transition"]["applied"]
        )

    def test_wrong_mixin_target_is_not_runtime_proof(self) -> None:
        log = (
            "[mixin/]: Mixing TFMGPumpjackFiniteReservoirMixin from "
            "industrial_colonies.mixins.json into example.WrongPumpjack\n"
        )
        evidence = validator.parse_owned_mixin_evidence(log)
        self.assertFalse(evidence["finite_tfmg_oil_reservoir"]["applied"])

    def test_owned_mixin_failure_is_fatal_evidence(self) -> None:
        log = (
            "[mixin/]: Mixin apply failed industrial_colonies.mixins.json:"
            "DungeonCrawlRandomItemsMixin -> xiroc.dungeoncrawl.dungeon.treasure.RandomItems: "
            "org.spongepowered.asm.mixin.injection.throwables.InvalidInjectionException\n"
        )
        failures = validator.find_owned_mixin_failures(log)
        self.assertEqual(1, len(failures))
        self.assertIn("InvalidInjectionException", failures[0]["message"])

    def test_orbital_transition_mixin_failure_is_fatal_evidence(self) -> None:
        log = (
            "[mixin/]: Mixin apply failed industrial_colonies.mixins.json:"
            "SpaceTransitionHandlerMixin -> "
            "dev.devce.rocketnautics.content.physics.SpaceTransitionHandler: "
            "org.spongepowered.asm.mixin.injection.throwables.InvalidInjectionException\n"
        )
        failures = validator.find_owned_mixin_failures(log)
        self.assertEqual(1, len(failures))
        self.assertIn("SpaceTransitionHandlerMixin", failures[0]["message"])
        self.assertFalse(
            validator.evaluate_owned_mixin_runtime(log, log)["pass"]
        )

    def test_ambient_kinetic_mixin_failure_is_fatal_evidence(self) -> None:
        log = (
            "[mixin/]: Mixin apply failed industrial_colonies.mixins.json:"
            "WaterWheelBlockEntityMixin -> "
            "com.simibubi.create.content.kinetics.waterwheel.WaterWheelBlockEntity: "
            "org.spongepowered.asm.mixin.injection.throwables.InvalidInjectionException\n"
        )
        failures = validator.find_owned_mixin_failures(log)
        self.assertEqual(1, len(failures))
        self.assertIn("WaterWheelBlockEntityMixin", failures[0]["message"])
        self.assertFalse(validator.evaluate_owned_mixin_runtime(log, log)["pass"])

    def test_owned_resource_decoder_failure_is_detected_without_stock_noise(self) -> None:
        log = """
[LootDataType/]: Couldn't parse data file industrial_colonies:regional_oil_field
[LootDataType/]: Couldn't parse data file createcasing:copper_slicer
[LootDataType/]: Error parsing betterdungeons:zombie_dungeon/chests/common
"""
        failures = validator.find_owned_resource_reload_errors(log)
        self.assertEqual(
            [
                "industrial_colonies:regional_oil_field",
                "betterdungeons:zombie_dungeon/chests/common",
            ],
            [row["resource"] for row in failures],
        )

    def test_recipe_listener_exception_is_fatal_evidence(self) -> None:
        log = (
            "[Render thread/ERROR] [KubeJS Server/]: UnknownKubeRecipe.java#64: "
            "Error in 'ServerEvents.recipes': java.lang.IllegalStateException: "
            "Cannot get config value before config is loaded.\n"
        )
        errors = validator.parse_kubejs_listener_errors(log)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["event"], "ServerEvents.recipes")
        self.assertIn("Cannot get config value", errors[0]["message"])

    def test_recipe_summary_rejects_failed_recipe_construction(self) -> None:
        log = (
            "[KubeJS Server/]: Added 455 recipes, removed 863 recipes, "
            "modified 3 recipes, with 1 failed recipes taking 1.641 s in total\n"
        )
        evidence = validator.parse_latest_kubejs_recipe_summary(log)
        self.assertEqual(
            evidence,
            {"added": 455, "removed": 863, "modified": 3, "failed": 1},
        )
        self.assertFalse(validator.is_acceptable_kubejs_recipe_summary(evidence))

    def test_recipe_summary_uses_latest_reload_and_accepts_zero_failures(self) -> None:
        log = """
[KubeJS Server/]: Added 455 recipes, removed 863 recipes, modified 3 recipes, with 1 failed recipes taking 1.641 s in total
[KubeJS Server/]: Added 456 recipes, removed 863 recipes, modified 3 recipes, with 0 failed recipes taking 1.612 s in total
"""
        evidence = validator.parse_latest_kubejs_recipe_summary(log)
        self.assertEqual(
            evidence,
            {"added": 456, "removed": 863, "modified": 3, "failed": 0},
        )
        self.assertTrue(validator.is_acceptable_kubejs_recipe_summary(evidence))

    def test_missing_recipe_summary_is_not_accepted(self) -> None:
        self.assertIsNone(validator.parse_latest_kubejs_recipe_summary("no recipe event"))
        self.assertFalse(validator.is_acceptable_kubejs_recipe_summary(None))

    def test_colony4cc_crafter_recipe_rejections_are_detected(self) -> None:
        log = """
[minecolonies/]: Error parsing crafterrecipe colony4cc:rgb_charge1
[minecolonies/]: Error parsing crafterrecipe colony4cc:rgb_charge2
"""
        self.assertEqual(
            validator.find_colony4cc_crafter_recipe_rejections(log),
            ["colony4cc:rgb_charge1", "colony4cc:rgb_charge2"],
        )

    def test_colony4cc_crafter_recipe_compat_accepts_clean_log(self) -> None:
        self.assertEqual(validator.find_colony4cc_crafter_recipe_rejections("clean"), [])

    def test_retired_third_party_recipe_manager_rejections_are_detected(self) -> None:
        log = """
[RecipeManager/]: Error parsing recipe create_factory:caramel_roll: broken fluid
[RecipeManager/]: Parsing error loading recipe cbc_at:cutting/rocket_pod_rail_cast_mould: broken result
"""
        self.assertEqual(
            validator.find_retired_third_party_recipe_rejections(log),
            [
                "cbc_at:cutting/rocket_pod_rail_cast_mould",
                "create_factory:caramel_roll",
            ],
        )

    def test_kubejs_fallback_warning_is_not_a_final_recipe_rejection(self) -> None:
        log = (
            "[KubeJS Server/]: Failed to parse recipe "
            "'create_factory:caramel_roll[create:filling]'! Falling back to vanilla"
        )
        self.assertEqual(validator.find_retired_third_party_recipe_rejections(log), [])

    def test_jei_uses_probe_parses_role_and_focus_counts(self) -> None:
        log = (
            "[Render thread/INFO] IC_JEI_USES_PROBE "
            "machine=createcasing:copper_press status=PASS pre_runtime_bound=1 "
            "bound=1 supplier_input=1 supplier_catalyst=1 focus_input_bound=1 "
            "focus_catalyst_bound=1 categories_input=1 categories_catalyst=1 "
            "focus_input_total=1 focus_input_unbound=0 focus_input_other_machine=0 "
            "bound_outputs=appliedcreate:stress_circuit_board "
            "mechanical_native_expected=48 mechanical_native_focused=48 "
            "mechanical_native_missing=0 mechanical_bound_visible=1 "
            "mechanical_status=PASS\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["bound"], 1)
        self.assertEqual(evidence["focus_input_bound"], 1)
        self.assertEqual(evidence["focus_input_total"], 1)
        self.assertEqual(evidence["focus_input_unbound"], 0)
        self.assertEqual(evidence["mechanical_native_missing"], 0)
        self.assertTrue(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_accepts_dynamic_multi_recipe_binding_parity(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=3 bound=3 supplier_input=3 supplier_catalyst=3 "
            "focus_input_bound=3 focus_catalyst_bound=3 categories_input=2 "
            "categories_catalyst=3 focus_input_total=3 focus_input_unbound=0 "
            "focus_input_other_machine=0 "
            "bound_outputs=appliedcreate:stress_circuit_board,electroenergetics:insulated_wire,tfmg:electric_pump "
            "mechanical_native_expected=92 mechanical_native_focused=92 "
            "mechanical_native_missing=0 mechanical_bound_visible=55 "
            "mechanical_status=PASS\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(evidence["bound"], 3)
        self.assertEqual(len(evidence["bound_outputs"]), 3)
        self.assertTrue(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_rejects_dynamic_binding_index_mismatch(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=2 bound=3 supplier_input=3 supplier_catalyst=3 "
            "focus_input_bound=3 focus_catalyst_bound=3 categories_input=2 "
            "categories_catalyst=3 focus_input_total=3 focus_input_unbound=0 "
            "focus_input_other_machine=0 bound_outputs=a:a,b:b,c:c "
            "mechanical_native_expected=92 mechanical_native_focused=92 "
            "mechanical_native_missing=0 mechanical_bound_visible=55 "
            "mechanical_status=PASS\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        self.assertFalse(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_rejects_dynamic_catalyst_index_miss(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=3 bound=3 supplier_input=3 supplier_catalyst=3 "
            "focus_input_bound=3 focus_catalyst_bound=2 categories_input=2 "
            "categories_catalyst=3 focus_input_total=3 focus_input_unbound=0 "
            "focus_input_other_machine=0 bound_outputs=a:a,b:b,c:c "
            "mechanical_native_expected=92 mechanical_native_focused=92 "
            "mechanical_native_missing=0 mechanical_bound_visible=55 "
            "mechanical_status=PASS\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        self.assertFalse(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_rejects_unbound_input_focus_leak(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=1 bound=1 supplier_input=1 supplier_catalyst=1 "
            "focus_input_bound=1 focus_catalyst_bound=1 categories_input=2 "
            "categories_catalyst=1 focus_input_total=2 focus_input_unbound=1 "
            "focus_input_other_machine=0 "
            "bound_outputs=appliedcreate:stress_circuit_board "
            "mechanical_native_expected=48 mechanical_native_focused=48 "
            "mechanical_native_missing=0 mechanical_bound_visible=1 "
            "mechanical_status=PASS\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        self.assertFalse(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_rejects_mechanical_press_native_regression(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=1 bound=1 supplier_input=1 supplier_catalyst=1 "
            "focus_input_bound=1 focus_catalyst_bound=1 categories_input=1 "
            "categories_catalyst=1 focus_input_total=1 focus_input_unbound=0 "
            "focus_input_other_machine=0 "
            "bound_outputs=appliedcreate:stress_circuit_board "
            "mechanical_native_expected=48 mechanical_native_focused=47 "
            "mechanical_native_missing=1 mechanical_bound_visible=1 "
            "mechanical_status=NATIVE_RECIPES_MISSING\n"
        )
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        self.assertFalse(validator.is_acceptable_jei_uses_probe(evidence))

    def test_jei_uses_probe_rejects_legacy_nonexclusive_marker(self) -> None:
        log = (
            "IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS "
            "pre_runtime_bound=1 bound=1 supplier_input=1 supplier_catalyst=1 "
            "focus_input_bound=1 focus_catalyst_bound=1 "
            "categories_input=1 categories_catalyst=1\n"
        )
        self.assertIsNone(validator.parse_latest_jei_uses_probe(log))

    def test_jei_uses_probe_uses_latest_runtime(self) -> None:
        log = """
IC_JEI_USES_PROBE machine=createcasing:copper_press status=INPUT_INDEX_MISS pre_runtime_bound=1 bound=1 supplier_input=1 supplier_catalyst=1 focus_input_bound=0 focus_catalyst_bound=1 categories_input=0 categories_catalyst=1 focus_input_total=0 focus_input_unbound=0 focus_input_other_machine=0 bound_outputs=appliedcreate:stress_circuit_board mechanical_native_expected=48 mechanical_native_focused=48 mechanical_native_missing=0 mechanical_bound_visible=1 mechanical_status=PASS
IC_JEI_USES_PROBE machine=createcasing:copper_press status=PASS pre_runtime_bound=1 bound=1 supplier_input=1 supplier_catalyst=1 focus_input_bound=1 focus_catalyst_bound=1 categories_input=1 categories_catalyst=1 focus_input_total=1 focus_input_unbound=0 focus_input_other_machine=0 bound_outputs=appliedcreate:stress_circuit_board mechanical_native_expected=48 mechanical_native_focused=48 mechanical_native_missing=0 mechanical_bound_visible=1 mechanical_status=PASS
"""
        evidence = validator.parse_latest_jei_uses_probe(log)
        self.assertIsNotNone(evidence)
        assert evidence is not None
        self.assertEqual(evidence["status"], "PASS")

    def test_jei_exact_u_filter_proves_input_only_ui_path(self) -> None:
        log = (
            "IC_JEI_EXACT_U_FILTER machine=createcasing:copper_press "
            "status=APPLIED roles_before=INPUT,CATALYST roles_after=INPUT\n"
        )
        evidence = validator.parse_latest_jei_exact_u_filter(log)
        self.assertIsNotNone(evidence)
        self.assertTrue(validator.is_acceptable_jei_exact_u_filter(evidence))

    def test_jei_exact_u_filter_rejects_catalyst_role_after_rewrite(self) -> None:
        log = (
            "IC_JEI_EXACT_U_FILTER machine=createcasing:copper_press "
            "status=APPLIED roles_before=INPUT,CATALYST "
            "roles_after=INPUT,CATALYST\n"
        )
        evidence = validator.parse_latest_jei_exact_u_filter(log)
        self.assertIsNotNone(evidence)
        self.assertFalse(validator.is_acceptable_jei_exact_u_filter(evidence))

    def test_interactive_jei_probe_is_optional_for_unattended_acceptance(self) -> None:
        self.assertTrue(validator.gate_optional_runtime_probe(False, required=False))
        self.assertTrue(validator.gate_optional_runtime_probe(True, required=False))
        self.assertFalse(validator.gate_optional_runtime_probe(False, required=True))
        self.assertTrue(validator.gate_optional_runtime_probe(True, required=True))


if __name__ == "__main__":
    unittest.main()
