#!/usr/bin/env python3
"""Mutation tests for the isolated Stage 14 validator."""

from __future__ import annotations

import json
import csv
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

import validate_interstellar_escape_isolated as validator


class IsolatedInterstellarEscapeMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        for relative in validator.REQUIRED_FILES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(validator.PROJECT / relative, target)
        planets = validator.PROJECT / "src/main/resources/data/rocketnautics/universe_planets"
        target_planets = self.project / "src/main/resources/data/rocketnautics/universe_planets"
        for source in planets.glob("*.json"):
            target = target_planets / source.name
            if not target.exists():
                shutil.copy2(source, target)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def failures(self, **kwargs) -> list[str]:
        return validator.collect_failures(self.project, **kwargs)

    def replace(self, relative: Path, old: str, new: str) -> None:
        path = self.project / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def move_before(self, relative: Path, fragment: str, anchor: str) -> None:
        path = self.project / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(fragment, text)
        self.assertIn(anchor, text)
        text = text.replace(fragment, "", 1)
        text = text.replace(anchor, fragment + anchor, 1)
        path.write_text(text, encoding="utf-8")

    def mutate_json(self, relative: Path, mutate) -> None:
        path = self.project / relative
        value = json.loads(path.read_text(encoding="utf-8"))
        mutate(value)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def quest(self, relative: Path, key: str) -> dict:
        payload = json.loads((self.project / relative).read_text(encoding="utf-8"))
        if relative == validator.QUESTS:
            quests = payload["chapter"]["quests"]
            return next(row for row in quests if row.get("key") == key)
        tag = f"industrial_colonies:planetary_guidance/{key}"
        return next(row for row in payload["quests"] if tag in row.get("tags", []))

    def mutate_quest(self, relative: Path, key: str, mutate) -> None:
        path = self.project / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        if relative == validator.QUESTS:
            quests = payload["chapter"]["quests"]
            quest = next(row for row in quests if row.get("key") == key)
        else:
            tag = f"industrial_colonies:planetary_guidance/{key}"
            quest = next(row for row in payload["quests"] if tag in row.get("tags", []))
        mutate(quest)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_candidate(
        self,
        *,
        missing: str | None = None,
        corrupt_asset: str | None = None,
        shaded: bool = False,
    ) -> Path:
        jar = Path(self.temp.name) / "candidate.jar"
        with zipfile.ZipFile(jar, "w") as archive:
            for entry in sorted(validator.CANDIDATE_ENTRIES):
                if entry == missing:
                    continue
                source = validator.CANDIDATE_RESOURCE_SOURCES.get(entry)
                if entry == "META-INF/neoforge.mods.toml":
                    data = ("\n\n".join(validator.CANDIDATE_SPACE_DEPENDENCIES) + "\n").encode()
                else:
                    data = (self.project / source).read_bytes() if source is not None else b"class"
                    markers = validator.CANDIDATE_CLASS_MARKERS.get(entry, ())
                    if markers:
                        data += b"\x00" + b"\x00".join(markers)
                if entry == corrupt_asset:
                    if entry == "META-INF/neoforge.mods.toml":
                        data = data.replace(b'type="required"', b'type="optional"')
                    elif entry in validator.CANDIDATE_CLASS_MARKERS:
                        marker = validator.CANDIDATE_CLASS_MARKERS[entry][0]
                        data = data.replace(marker, b"removed-bytecode-marker", 1)
                    else:
                        data += b"\ncorrupt"
                archive.writestr(entry, data)
            if shaded:
                archive.writestr("dev/waco0311/cosmowarp/IllegalCopy.class", b"class")
        return jar

    def installed_mods(self) -> Path:
        properties = (validator.PROJECT / "gradle.properties").read_text(encoding="utf-8-sig")
        for line in properties.splitlines():
            if line.startswith("pack_mods_dir="):
                return Path(line.split("=", 1)[1].strip())
        self.fail("gradle.properties is missing pack_mods_dir")

    def write_catalog(self, *, extra_owner: bool = False) -> Path:
        catalog = Path(self.temp.name) / "catalog"
        catalog.mkdir(exist_ok=True)
        fields = [
            "recipe_id", "namespace", "recipe_type", "source_jar", "source_path",
            "industrial", "outputs", "inputs", "tags",
        ]
        rows = []
        for recipe_id, expected in validator.CATALOG_STOCK_RECIPES.items():
            rows.append({
                "recipe_id": recipe_id,
                "namespace": "cosmowarp",
                "industrial": "1" if recipe_id.endswith("moon_crystal_sanding") else "0",
                "tags": "",
                **expected,
            })
        if extra_owner:
            rows.append({
                "recipe_id": "user:forged_warp_drive",
                "namespace": "user",
                "recipe_type": "minecraft:crafting_shapeless",
                "source_jar": "forged.jar",
                "source_path": "data/user/recipe/forged_warp_drive.json",
                "industrial": "0",
                "outputs": "cosmowarp:warp_drive",
                "inputs": "minecraft:dirt",
                "tags": "",
            })
        with (catalog / "recipes.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return catalog

    def test_00_baseline_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_01_proxima_identity_fails(self) -> None:
        self.mutate_json(validator.PROXIMA, lambda value: value.__setitem__("priority", 0))
        self.assertTrue(any("Proxima" in row for row in self.failures()))

    def test_02_prefab_glacio_orbit_fails(self) -> None:
        self.mutate_json(
            validator.GLACIO,
            lambda value: value["dimension_data"].__setitem__("linked_dimension", "ad_astra:glacio_orbit"),
        )
        self.assertTrue(any("canonical" in row or "prefab" in row for row in self.failures()))

    def test_03_second_glacio_owner_fails(self) -> None:
        moon = self.project / "src/main/resources/data/rocketnautics/universe_planets/moon.json"
        value = json.loads(moon.read_text(encoding="utf-8"))
        value.setdefault("dimension_data", {})["linked_dimension"] = "ad_astra:glacio"
        moon.write_text(json.dumps(value), encoding="utf-8")
        self.assertTrue(any("ownership" in row for row in self.failures()))

    def test_04_glacio_physics_fails(self) -> None:
        self.mutate_json(validator.PHYSICS, lambda value: value["base_gravity"].__setitem__(1, -9.81))
        self.assertTrue(any("physics" in row for row in self.failures()))

    def test_05_moon_target_fails(self) -> None:
        self.replace(validator.CONFIGURED_ORE, "ad_astra:moon_stone", "rocketnautics:moon_stone")
        self.assertTrue(any("moon stone" in row for row in self.failures()))

    def test_06_stock_worldgen_override_fails(self) -> None:
        forbidden = self.project / "src/main/resources/data/cosmowarp/worldgen/configured_feature/moon_crystal_ore.json"
        forbidden.parent.mkdir(parents=True)
        forbidden.write_text("{}", encoding="utf-8")
        self.assertTrue(any("overrides Cosmowarp" in row for row in self.failures()))

    def test_07_arrival_reward_fails(self) -> None:
        self.mutate_json(validator.ARRIVAL, lambda value: value.__setitem__("rewards", {"experience": 1}))
        self.assertTrue(any("observation-only" in row for row in self.failures()))

    def test_08_exact_point_set_fails(self) -> None:
        self.replace(validator.SIGNED_ROUTE, "List.of(SOL_POINT, GLACIO_POINT)", "List.of(GLACIO_POINT)")
        self.assertTrue(any("signed route" in row for row in self.failures()))

    def test_09_signature_comparison_fails(self) -> None:
        self.replace(
            validator.SIGNED_ROUTE,
            "expectedCustomData().equals(customData.copyTag())",
            "customData != null",
        )
        self.assertTrue(any("signed route" in row for row in self.failures()))

    def test_10_stale_heartbeat_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "StationServicesControllerBlockEntity.isLiveFor(ship, metadata)",
            "metadata.hasFreshServices(level.getGameTime())",
        )
        self.assertTrue(any("live ship operator" in row or "stale heartbeat" in row for row in self.failures()))

    def test_11_hidden_contraption_drive_fails(self) -> None:
        self.replace(validator.POLICY, "!ship.getPlot().getContraptions().isEmpty()", "false")
        self.assertTrue(any("contraptions" in row.lower() for row in self.failures()))

    def test_12_multiship_chain_fails(self) -> None:
        self.replace(validator.POLICY, "chain.size() != 1", "chain.size() < 1")
        self.assertTrue(any("chain.size" in row for row in self.failures()))

    def test_13_station_role_fails(self) -> None:
        self.replace(validator.POLICY, "metadata.role() != StationRole.SHIP", "metadata.role() == null")
        self.assertTrue(any("live ship operator" in row for row in self.failures()))

    def test_14_second_drive_check_fails(self) -> None:
        self.replace(validator.POLICY, "warpDrives != 1", "warpDrives < 1")
        self.assertTrue(any("warpDrives" in row for row in self.failures()))

    def test_15_physical_computer_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "actor instanceof InterstellarNavigationComputerBlockEntity",
            "actor != null",
        )
        self.assertTrue(any("live ship operator" in row for row in self.failures()))

    def test_16_stock_target_swap_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "expected.targetPoint().equals(stockChargingTarget)",
            "stockChargingTarget != null",
        )
        self.assertTrue(any("stockChargingTarget" in row for row in self.failures()))

    def test_17_candidate_sweep_fails(self) -> None:
        self.replace(validator.POLICY, "AABB candidateBox = stockCandidateBox(origin)", "AABB candidateBox = null")
        self.assertTrue(any("stockCandidateBox" in row for row in self.failures()))

    def test_18_freeze_slot_fails(self) -> None:
        self.replace(validator.POLICY, "stack.canEquip(slot, player)", "true")
        self.assertTrue(any("canEquip" in row for row in self.failures()))

    def test_19_duplicate_snapshot_guard_fails(self) -> None:
        self.replace(validator.POLICY, "hasUniqueValues(occupants)", "true")
        self.assertTrue(any("hasUniqueValues" in row for row in self.failures()))

    def test_20_serialization_preflight_fails(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "blockEntity.saveWithFullMetadata(source.getLevel().registryAccess())",
            "blockEntity.setChanged()",
        )
        self.assertTrue(any("saveWithFullMetadata" in row for row in self.failures()))

    def test_21_destination_rollback_scope_fails(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "destination.removeSubLevel(candidate, SubLevelRemovalReason.REMOVED)",
            "candidate.deleteAllEntities()",
        )
        self.assertTrue(any("removeSubLevel" in row for row in self.failures()))

    def test_22_source_boundary_fails(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "sourceContainer.getSubLevel(source.getUniqueId()) == source",
            "true",
        )
        self.assertTrue(any("getSubLevel" in row for row in self.failures()))

    def test_22b_per_player_cleanup_fails(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "for (PlayerSnapshot snapshot : snapshots)",
            "if (!snapshots.isEmpty())",
        )
        self.assertTrue(any("PlayerSnapshot snapshot" in row for row in self.failures()))

    def test_22c_removal_scope_must_begin_before_copy(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "if (!InterstellarWarpRemovalScope.begin(source))",
            "if (false)",
        )
        self.assertTrue(any("removal scope" in row or "warp transaction" in row for row in self.failures()))

    def test_22d_removal_marker_must_gate_rollback(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "if (!InterstellarWarpRemovalScope.sourceRemovalStarted(source))",
            "if (!source.isRemoved())",
        )
        self.assertTrue(any("removal scope" in row or "sourceRemovalStarted" in row for row in self.failures()))

    def test_22e_removal_scope_must_clear_in_finally(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "InterstellarWarpRemovalScope.clear(source);",
            "// removal scope leak",
        )
        self.assertTrue(any("clear in finally" in row or "warp transaction" in row for row in self.failures()))

    def test_22f_removal_scope_missing_state_must_fail_closed(self) -> None:
        self.replace(
            validator.REMOVAL_SCOPE,
            "return state == null || state.source != source || state.removalStarted;",
            "return state != null && state.source == source && state.removalStarted;",
        )
        self.assertTrue(any("fail-closed interstellar removal scope" in row for row in self.failures()))

    def test_22g_destination_snapshot_must_precede_removal_scope(self) -> None:
        scope = (
            "        if (!InterstellarWarpRemovalScope.begin(source)) {\n"
            "            LOGGER.error(\"Nested interstellar warp removal scope was refused\");\n"
            "            return 0;\n"
            "        }\n"
        )
        self.move_before(
            validator.TRANSACTION,
            scope,
            "        Set<UUID> destinationBefore = new HashSet<>();",
        )
        self.assertTrue(any("snapshotted" in row or "removal scope" in row for row in self.failures()))

    def test_22h_copy_failure_must_be_logged_before_identity_probe(self) -> None:
        log = (
            "                LOGGER.error(\n"
            "                        \"Interstellar warp copy failed; cleanup safety assessment follows\",\n"
            "                        error);\n"
        )
        self.move_before(
            validator.TRANSACTION,
            log,
            "                if (sourcePristine) {",
        )
        self.assertTrue(any("copy failure must be logged first" in row for row in self.failures()))

    def test_22i_identity_probe_failure_must_leave_pristine_false(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "                                probeFailure);\n                    }",
            "                                probeFailure);\n"
            "                        sourcePristine = true;\n"
            "                    }",
        )
        self.assertTrue(any("must leave sourcePristine false" in row for row in self.failures()))

    def test_22j_rollback_must_use_proven_pristine_guard(self) -> None:
        self.replace(
            validator.TRANSACTION,
            "if (sourcePristine) {",
            "if (!source.isRemoved()) {",
        )
        self.assertTrue(any("proven-pristine branch" in row or "warp transaction" in row for row in self.failures()))

    def test_23_execute_target_revalidation_fails(self) -> None:
        self.replace(validator.WARP_MIXIN, "chargingTargetId))", "null))")
        self.assertTrue(any("chargingTargetId" in row for row in self.failures()))

    def test_24_reload_persistence_fails(self) -> None:
        self.replace(validator.WARP_MIXIN, "Authorization.fromTag(", "Optional.empty(")
        self.assertTrue(any("Authorization.fromTag" in row for row in self.failures()))

    def test_25_failed_copy_success_fails(self) -> None:
        self.replace(validator.WARP_MIXIN, "if (!industrialColonies$warpCopySucceeded)", "if (false)")
        self.assertTrue(any("warpCopySucceeded" in row for row in self.failures()))

    def test_26_cleanup_target_fails(self) -> None:
        self.replace(validator.WARP_MIXIN, "chargingTargetId = null", "chargingTargetId = UUID.randomUUID()")
        self.assertTrue(any("chargingTargetId = null" in row for row in self.failures()))

    def test_27_ship_actor_fails(self) -> None:
        self.replace(validator.COMPUTER_BE, "implements BlockEntitySubLevelActor", "")
        self.assertTrue(any("physical Sable actor" in row for row in self.failures()))

    def test_28_schema_type_check_fails(self) -> None:
        self.replace(
            validator.POLICY,
            'tag.contains("schema", Tag.TAG_INT)',
            'tag.contains("schema", Tag.TAG_LONG)',
        )
        self.assertTrue(any("schema" in row for row in self.failures()))

    def test_29_missing_direction_type_check_fails(self) -> None:
        self.replace(
            validator.POLICY,
            'tag.contains("inbound_to_glacio", Tag.TAG_BYTE)',
            'tag.getBoolean("inbound_to_glacio")',
        )
        self.assertTrue(any("inbound_to_glacio" in row for row in self.failures()))

    def test_30_missing_consumed_type_check_fails(self) -> None:
        self.replace(
            validator.POLICY,
            'tag.contains("charge_consumed", Tag.TAG_BYTE)',
            'tag.getBoolean("charge_consumed")',
        )
        self.assertTrue(any("charge_consumed" in row for row in self.failures()))

    def test_31_oversized_crew_bound_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "occupantTags.size() > MAX_PERSISTED_OCCUPANTS",
            "false",
        )
        self.assertTrue(any("occupantTags.size" in row for row in self.failures()))

    def test_32_empty_crew_bound_fails(self) -> None:
        self.replace(validator.POLICY, "occupantTags.isEmpty()", "false")
        self.assertTrue(any("occupantTags.isEmpty" in row for row in self.failures()))

    def test_33_exact_one_vessel_bound_fails(self) -> None:
        self.replace(validator.POLICY, "identityTags.size() != 1", "identityTags.isEmpty()")
        self.assertTrue(any("identityTags.size" in row for row in self.failures()))

    def test_34_malformed_reload_abort_fails(self) -> None:
        self.replace(
            validator.WARP_MIXIN,
            "industrialColonies$activeAuthorization == null",
            "false",
        )
        self.assertTrue(any("activeAuthorization == null" in row for row in self.failures()))

    def test_35_destination_sublevel_collision_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "if (route != null && !destinationIsClear(origin, route, level))",
            "if (false)",
        )
        self.assertTrue(any("destinationIsClear" in row for row in self.failures()))

    def test_36_non_player_candidate_rejection_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "physicalEntities.stream().anyMatch(entity -> !(entity instanceof ServerPlayer))",
            "false",
        )
        self.assertTrue(any("physicalEntities.stream().anyMatch" in row for row in self.failures()))

    def test_37_central_registry_attachment_fails(self) -> None:
        self.replace(
            validator.MAIN_JAVA,
            "IndustrialItems.register(modEventBus);",
            "// Stage14 item registration removed",
        )
        self.assertTrue(any("registry attachment" in row for row in self.failures()))

    def test_38_interstellar_charge_item_registration_fails(self) -> None:
        self.replace(
            validator.ITEMS_JAVA,
            '"interstellar_warp_charge",',
            '"unregistered_warp_charge",',
        )
        self.assertTrue(any("item registry" in row for row in self.failures()))

    def test_39_navigation_block_registration_fails(self) -> None:
        self.replace(
            validator.BLOCKS_JAVA,
            "InterstellarNavigationComputerBlock::new",
            "Block::new",
        )
        self.assertTrue(any("block registry" in row for row in self.failures()))

    def test_40_navigation_block_entity_registration_fails(self) -> None:
        self.replace(
            validator.BLOCK_ENTITIES_JAVA,
            "InterstellarNavigationComputerBlockEntity::new",
            "StationServicesControllerBlockEntity::new",
        )
        self.assertTrue(any("block-entity registry" in row for row in self.failures()))

    def test_41_warp_mixin_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("CosmowarpWarpDriveMixin"),
        )
        self.assertTrue(any("CosmowarpWarpDriveMixin" in row for row in self.failures()))

    def test_41b_deep_space_descent_hook_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("DeepSpaceInstanceMixin"),
        )
        self.assertTrue(any("DeepSpaceInstanceMixin" in row for row in self.failures()))

    def test_41c_deep_space_descent_hook_target_fails(self) -> None:
        self.replace(
            validator.DEEP_SPACE_MIXIN,
            "AllowedTransfer;allowToDimension()Z",
            "AllowedTransfer;allowToPlanet()Z",
        )
        self.assertTrue(any("ordinary descent authorization hook" in row for row in self.failures()))

    def test_41d_network_gate_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("CosmowarpNetworkingMixin"),
        )
        self.assertTrue(any("CosmowarpNetworkingMixin" in row for row in self.failures()))

    def test_41e_network_start_descriptor_fails(self) -> None:
        self.replace(
            validator.NETWORKING_MIXIN,
            "WarpDriveBlockEntity;beginWarp()Ldev/waco0311/cosmowarp/",
            "WarpDriveBlockEntity;beginUnsafeWarp()Ldev/waco0311/cosmowarp/",
        )
        self.assertTrue(any("server-network gate" in row for row in self.failures()))

    def test_41f_initiator_scope_cleanup_fails(self) -> None:
        self.replace(
            validator.INITIATOR_SCOPE,
            "CURRENT.remove();",
            "CURRENT.set(initiator);",
        )
        self.assertTrue(any("initiator scope" in row for row in self.failures()))

    def test_41g_menu_live_authority_fails(self) -> None:
        self.replace(
            validator.WARP_MENU_MIXIN,
            "InterstellarWarpPolicy.mayUseWarpDriveMenu(",
            "InterstellarWarpPolicy.mayMutateRoute(",
        )
        self.assertTrue(any("live Warp Drive menu gate" in row for row in self.failures()))

    def test_41h_required_runtime_dependency_metadata_fails(self) -> None:
        self.replace(
            validator.MODS_TOML,
            'modId="cosmowarp"',
            'modId="cosmowarp_missing"',
        )
        self.assertTrue(any("runtime dependency metadata" in row for row in self.failures()))

    def test_41i_cached_crystal_freeze_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("CosmowarpCrystalSlotFreezeMixin"),
        )
        self.assertTrue(any("CosmowarpCrystalSlotFreezeMixin" in row for row in self.failures()))

    def test_41j_cached_crystal_direct_set_guard_fails(self) -> None:
        self.replace(
            validator.CRYSTAL_FREEZE_MIXIN,
            'method = "setStackInSlot(ILnet/minecraft/world/item/ItemStack;)V"',
            'method = "unsafeSetStackInSlot(ILnet/minecraft/world/item/ItemStack;)V"',
        )
        self.assertTrue(any("cached-capability crystal freeze" in row for row in self.failures()))

    def test_41k_route_independent_live_operator_fails(self) -> None:
        self.replace(
            validator.POLICY,
            "return isLiveShipOperator(drive, initiator);",
            "return SignedInterstellarRoute.resolve(drive).isPresent();",
        )
        self.assertTrue(any("isLiveShipOperator" in row for row in self.failures()))

    def test_41l_dynamic_capability_wrapper_fails(self) -> None:
        self.replace(
            validator.CAPABILITY_MIXIN,
            "return new FrozenWarpCrystalItemHandler(drive, original);",
            "return original;",
        )
        self.assertTrue(any("crystal-capability wrapper" in row for row in self.failures()))

    def test_41m_sable_removal_boundary_registration_fails(self) -> None:
        self.mutate_json(
            validator.MIXINS_JSON,
            lambda value: value["mixins"].remove("SableRemovalBoundaryMixin"),
        )
        self.assertTrue(any("SableRemovalBoundaryMixin" in row for row in self.failures()))

    def test_41n_sable_remove_sublevel_target_fails(self) -> None:
        self.replace(
            validator.SABLE_REMOVAL_MIXIN,
            "removeSubLevel(IILdev/ryanhcode/sable/sublevel/storage/",
            "removeSubLevel(Ldev/ryanhcode/sable/sublevel/storage/",
        )
        self.assertTrue(any("Sable destructive-removal boundary" in row for row in self.failures()))

    def test_42_compile_only_cosmowarp_dependency_fails(self) -> None:
        self.replace(
            validator.BUILD_GRADLE,
            "compileOnly files(cosmowarpJar)",
            "implementation files(cosmowarpJar)",
        )
        failures = self.failures()
        self.assertTrue(any("compile-only" in row for row in failures))
        self.assertTrue(any("bundled or runtime-owned" in row for row in failures))

    def test_43_physical_signer_interaction_fails(self) -> None:
        self.replace(
            validator.COMPUTER_BLOCK,
            "SignedInterstellarRoute.signForDimension(stack, level.dimension())",
            "SignedInterstellarRoute.isExactSignedCrystal(stack)",
        )
        self.assertTrue(any("physical route signer" in row for row in self.failures()))

    def test_44_duplicate_signing_authority_fails(self) -> None:
        path = self.project / validator.COMPUTER_BE
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text + "\n// SignedInterstellarRoute.signForDimension(stack, level.dimension())\n",
            encoding="utf-8",
        )
        self.assertTrue(any("signing authority" in row for row in self.failures()))

    def test_45_unsigned_route_recipe_cannot_embed_components(self) -> None:
        def mutate(value: dict) -> None:
            route = next(row for row in value["recipes"] if row.get("id") == validator.RECIPE_IDS[2])
            route["component_patch"] = {
                "industrial_colonies:interstellar_route": "forged"
            }

        self.mutate_json(validator.SEED, mutate)
        self.assertTrue(any("signing authority" in row for row in self.failures()))

    def test_46_exact_five_recipe_routes_fails(self) -> None:
        self.mutate_json(
            validator.SEED,
            lambda value: value["recipes"].__setitem__(
                slice(None),
                [row for row in value["recipes"] if row.get("id") != validator.RECIPE_IDS[4]],
            ),
        )
        self.assertTrue(any("exactly the five" in row for row in self.failures()))

    def test_47_compiled_mechanical_grid_fails(self) -> None:
        def mutate(value: dict) -> None:
            card = next(row for row in value["recipes"] if row.get("recipeId") == validator.RECIPE_IDS[1])
            card["params"]["gridW"] = "3"

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("exactly 5x5" in row for row in self.failures()))

    def test_48_exact_managed_removal_fails_when_broadened(self) -> None:
        def mutate(value: dict) -> None:
            removal = next(
                row for row in value["removals"]
                if row.get("recipeId") == "cosmowarp:warp_crystal"
            )
            removal["mod"] = "cosmowarp"

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("broader than exact recipe ID" in row for row in self.failures()))

    def test_49_stage14_output_owner_collision_fails(self) -> None:
        def mutate(value: dict) -> None:
            duplicate = json.loads(json.dumps(value["recipes"][0]))
            duplicate["recipeId"] = "user:forged_navigation_computer"
            duplicate["slots"] = {
                "output": {
                    "kind": "ITEM",
                    "id": "industrial_colonies:interstellar_navigation_computer",
                }
            }
            value["recipes"].append(duplicate)

        self.mutate_json(validator.COMPILED, mutate)
        self.assertTrue(any("non-exclusive compiled owners" in row for row in self.failures()))

    def test_50_node_phase_unlock_topology_fails(self) -> None:
        def mutate(value: dict) -> None:
            value["nodes"][validator.INTERSTELLAR_NODE]["unlocks"].pop()

        self.mutate_json(validator.ASSIGNMENTS, mutate)
        self.assertTrue(any("unlock topology drifted" in row for row in self.failures()))

    def test_51_source_final_quest_reward_fails(self) -> None:
        self.mutate_quest(
            validator.QUESTS,
            "escaped_sol",
            lambda quest: quest.__setitem__("rewards", [{"item": "minecraft:diamond"}]),
        )
        self.assertTrue(any("quest contains authority" in row for row in self.failures()))

    def test_52_native_final_quest_reward_fails(self) -> None:
        self.mutate_quest(
            validator.NATIVE_CHAPTER,
            "glacio_arrival",
            lambda quest: quest.__setitem__("rewards", [{"type": "ftbquests:item"}]),
        )
        self.assertTrue(any("native Stage14 quest contains authority" in row for row in self.failures()))

    def test_52b_native_final_quest_identity_fails(self) -> None:
        self.mutate_quest(
            validator.NATIVE_CHAPTER,
            "escaped_sol",
            lambda quest: quest.__setitem__("id", "0000000000000000"),
        )
        self.assertTrue(any("deterministic quest/task identity" in row for row in self.failures()))

    def test_53_ordinary_glacio_descent_denial_fails(self) -> None:
        self.replace(
            validator.SPACEFLIGHT_AUTHORIZATION,
            "if (GLACIO.equals(destinationKey)) {\n            return false;\n        }",
            "if (GLACIO.equals(destinationKey)) {\n            return true;\n        }",
        )
        self.assertTrue(any("ordinary Glacio descent denial" in row for row in self.failures()))

    def test_54_candidate_missing_runtime_class_fails(self) -> None:
        missing = "dev/godpc/industrialcolonies/space/InterstellarWarpPolicy.class"
        candidate = self.write_candidate(missing=missing)
        self.assertTrue(any("lacks Stage14 implementation" in row for row in self.failures(candidate_jar=candidate)))

    def test_55_candidate_resource_byte_drift_fails(self) -> None:
        asset = "data/rocketnautics/universe_planets/glacio.json"
        candidate = self.write_candidate(corrupt_asset=asset)
        self.assertTrue(any("asset differs from source" in row for row in self.failures(candidate_jar=candidate)))

    def test_56_candidate_shaded_dependency_fails(self) -> None:
        candidate = self.write_candidate(shaded=True)
        self.assertTrue(any("improperly bundles" in row for row in self.failures(candidate_jar=candidate)))

    def test_56b_candidate_runtime_dependency_metadata_fails(self) -> None:
        candidate = self.write_candidate(corrupt_asset="META-INF/neoforge.mods.toml")
        self.assertTrue(any("required sable runtime dependency" in row for row in self.failures(candidate_jar=candidate)))

    def test_56c_candidate_runtime_bytecode_marker_fails(self) -> None:
        entry = "dev/godpc/industrialcolonies/mixin/DeepSpaceInstanceMixin.class"
        candidate = self.write_candidate(corrupt_asset=entry)
        self.assertTrue(any("reviewed bytecode markers" in row for row in self.failures(candidate_jar=candidate)))

    def test_56d_candidate_sable_removal_boundary_missing_fails(self) -> None:
        entry = "dev/godpc/industrialcolonies/mixin/SableRemovalBoundaryMixin.class"
        candidate = self.write_candidate(missing=entry)
        self.assertTrue(any("lacks Stage14 implementation" in row for row in self.failures(candidate_jar=candidate)))

    def test_56e_candidate_sable_removal_boundary_marker_fails(self) -> None:
        entry = "dev/godpc/industrialcolonies/mixin/SableRemovalBoundaryMixin.class"
        candidate = self.write_candidate(corrupt_asset=entry)
        self.assertTrue(any("reviewed bytecode markers" in row for row in self.failures(candidate_jar=candidate)))

    def test_56f_candidate_removal_scope_marker_fails(self) -> None:
        entry = "dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope.class"
        candidate = self.write_candidate(corrupt_asset=entry)
        self.assertTrue(any("reviewed bytecode markers" in row for row in self.failures(candidate_jar=candidate)))

    def test_56g_candidate_removal_scope_state_missing_fails(self) -> None:
        entry = "dev/godpc/industrialcolonies/space/InterstellarWarpRemovalScope$State.class"
        candidate = self.write_candidate(missing=entry)
        self.assertTrue(any("lacks Stage14 implementation" in row for row in self.failures(candidate_jar=candidate)))

    def test_57_installed_dependency_hash_drift_fails(self) -> None:
        mods = Path(self.temp.name) / "mods"
        mods.mkdir()
        installed = self.installed_mods()
        for name in validator.DEPENDENCY_PINS:
            shutil.copy2(installed / name, mods / name)
        self.assertEqual([], self.failures(mods=mods))
        with (mods / "cosmowarp-1.0.1.jar").open("ab") as stream:
            stream.write(b"hash drift")
        self.assertTrue(any("dependency hash drifted" in row for row in self.failures(mods=mods)))

    def test_58_catalog_output_owner_collision_fails(self) -> None:
        clean = self.write_catalog()
        self.assertEqual([], self.failures(catalog=clean))
        forged = self.write_catalog(extra_owner=True)
        self.assertTrue(any("unexpected producers" in row for row in self.failures(catalog=forged)))


if __name__ == "__main__":
    unittest.main()
