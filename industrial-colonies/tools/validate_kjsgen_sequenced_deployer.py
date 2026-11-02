#!/usr/bin/env python3
"""Static acceptance for exact-machine KJSGen Sequenced Assembly authoring."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/dev/godpc/industrialcolonies"
RESOURCES = ROOT / "src/main/resources"
KJSGEN_JAR = ROOT / "libs/kjsgen-neoforge-2.0.5+mc1.21.1.jar"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    require(KJSGEN_JAR.is_file(), "the pinned KJSGen 2.0.5 jar is missing")
    with zipfile.ZipFile(KJSGEN_JAR) as archive:
        layout = json.loads(
            archive.read(
                "assets/kjsgen/kjsgen_layouts/create_sequenced_assembly.json"
            ).decode("utf-8")
        )
        special_model = archive.read(
            "com/zizazr/kjsgen/core/CreateSpecialModel.class"
        )

    require(layout.get("editorKind") == "sequence", "KJSGen sequence editor kind changed")
    require(layout.get("codegen") == "kjsgen:create_sequenced_assembly",
            "KJSGen native sequence codegen id changed")
    for operation in (b"deploying", b"pressing", b"cutting", b"filling"):
        require(operation in special_model,
                f"pinned KJSGen no longer contains {operation.decode()} as a step type")

    catalog = json.loads(
        (RESOURCES / "data/industrial_colonies/tier_recipe_environments.json")
        .read_text(encoding="utf-8")
    )
    families = {
        family["id"]: family for family in catalog["recipe_families"]
    }
    expected_machines = {
        "pressing": ("create:mechanical_press", "createcasing:copper_press", 9),
        "deploying": ("create:deployer", "createcasing:copper_deployer", 9),
        "cutting": ("create:mechanical_saw", "createcasing:copper_mechanical_saw", 9),
        "filling": ("create:spout", "createcasing:andesite_spout", 4),
    }
    for family_id, (native_item, encased_item, expected_count) in expected_machines.items():
        items = {machine["item"] for machine in families[family_id]["machines"]}
        require(native_item in items, f"native {family_id} machine is missing")
        require(encased_item in items, f"Encased {family_id} machine is missing")
        require(len(items) == expected_count,
                f"unexpected selectable {family_id} machine count: {len(items)}")

    integration = (JAVA / "KjsGenSequencedAssemblyIntegration.java").read_text(
        encoding="utf-8"
    )
    require('event.registerCodegen(NATIVE_CODEGEN, codegen)' in integration,
            "native KJSGen sequence handler is not overridden")
    require("KjsGenIntegration.LEGACY_SEQUENCE_CODEGEN" in integration,
            "legacy sequence cards do not share exact-machine codegen")
    require("MachineRecipeRouting.selectedStepMachine" in integration,
            "codegen does not read each selected per-step machine")
    require("MachineRecipeRouting.runtimeTypeId(family, machine)" in integration,
            "codegen does not emit an exact hidden step serializer")
    for constant in (
        "NATIVE_PRESSING_CALL", "NATIVE_DEPLOYING_CALL",
        "NATIVE_CUTTING_CALL", "NATIVE_FILLING_CALL",
    ):
        require(constant in integration, f"missing codegen route: {constant}")
    require("nativeStepCall(familyId)" in integration and "replaceNextLiteral" in integration,
            "native inner calls are not rewritten one stage at a time")

    routing = (JAVA / "MachineRecipeRouting.java").read_text(encoding="utf-8")
    require("stepMachineSlot(" in routing and "SlotRole.CATALYST" in routing,
            "dynamic sequence machine slot definition is missing")
    require("selectedStepMachine(" in routing and "family.baseMachine()" in routing,
            "empty sequence machine selections do not safely default to native")
    require("removeSequenceStep(" in routing and "moveSequenceStep(" in routing,
            "per-step machine metadata cannot follow sequence edits")

    panel = (JAVA / "mixin/KjsGenSequencePanelMixin.java").read_text(
        encoding="utf-8"
    )
    require("VanillaSequencePanel" in panel, "sequence panel mixin target is missing")
    require("industrialColonies$addVisibleDeployingStep" in panel
            and 'CreateSpecialModel.addStep(recipe, type, "deploying")' in panel,
            "new stages do not visibly start as Deploying")
    require("industrialColonies$drawStepMachineSelector" in panel
            and "industrialColonies$editStepMachineSelector" in panel,
            "per-stage machine selector is not both rendered and clickable")
    require("selectableStepFamily" in panel,
            "sequence selector is not derived from each row's operation family")
    for family_id in expected_machines:
        require(f'"{family_id}".equals(familyId)' in panel,
                f"sequence selector does not cover {family_id}")
    require("industrialColonies$machineSlotHit" in panel and "@Unique" in panel,
            "the selector hit-test is not namespaced away from KJSGen's instance hit method")
    require("private static boolean hit(" not in panel,
            "a static hit helper would collide with VanillaSequencePanel.hit at runtime")
    require("MachineRecipeRouting.stepMachineSlot(index, family)" in panel,
            "selector does not use the compatible-machine-only slot")
    require("industrialColonies$removeStepAndMachine" in panel
            and "industrialColonies$moveStepAndMachine" in panel
            and "industrialColonies$clearChangedStepMachine" in panel,
            "sequence edits can orphan or misalign machine metadata")

    runtime = (JAVA / "mixin/SequencedAssemblyRuntimeMixin.java").read_text(
        encoding="utf-8"
    )
    require(runtime.count(
        "Lcom/simibubi/create/content/processing/recipe/ProcessingRecipe;getType()"
    ) == 2, "both Create sequence lookup paths must redirect the nested type check")
    require("binding.family().baseType().getType()" in runtime,
            "bound operation is not matched back to Create's requested base family")
    require("CreateRecipeStageGate.machineMatches(" in runtime
            and "CreateMachineContext.current()" in runtime,
            "nested steps are not checked against the actual current machine")
    require("if (binding == null || binding.family() == null)" in runtime,
            "native Create sequence steps no longer have an unchanged path")

    validator = (JAVA / "mixin/KjsGenRecipeValidatorMixin.java").read_text(
        encoding="utf-8"
    )
    require('"sequence".equals(type.editorKind())' in validator,
            "dynamic sequence machine slots are not validated")
    require("MachineRecipeRouting.stepSlotKey(index, stepFamily.get())" in validator,
            "validation is not tied to the exact stage index and operation")

    mixins = json.loads(
        (RESOURCES / "industrial_colonies.mixins.json").read_text(encoding="utf-8")
    )
    client_mixins = set(mixins.get("client", []))
    require({"KjsGenEditorScreenAccessor", "KjsGenSequencePanelMixin"}
            <= client_mixins, "sequence editor client mixins are not registered")
    require("SequencedAssemblyRuntimeMixin" in set(mixins.get("mixins", [])),
            "sequence runtime mixin is not registered on both sides")

    jei_mixins = json.loads(
        (RESOURCES / "industrial_colonies.jei.mixins.json").read_text(encoding="utf-8")
    )
    require("SequencedAssemblyMachineContextMixin" in set(jei_mixins.get("client", [])),
            "sequenced-step JEI machine context is not registered")
    sequence_jei = (
        JAVA / "mixin/jei/SequencedAssemblyMachineContextMixin.java"
    ).read_text(encoding="utf-8")
    for subcategory in (
        "AssemblyPressing", "AssemblyDeploying", "AssemblyCutting", "AssemblySpouting"
    ):
        require(subcategory in sequence_jei,
                f"JEI sequence context does not cover {subcategory}")
    animation_jei = (
        JAVA / "mixin/jei/BoundCreateMachineAnimationMixin.java"
    ).read_text(encoding="utf-8")
    for animation in ("AnimatedPress", "AnimatedDeployer", "AnimatedSaw", "AnimatedSpout"):
        require(animation in animation_jei,
                f"JEI animation replacement does not cover {animation}")

    print("PASS: KJSGen exact-machine Sequenced Assembly support")
    print("  pinned editor: Deploying exists but upstream defaults new rows to Pressing")
    print("  authoring: compatible selector on Pressing, Deploying, Cutting, and Filling")
    print("  codegen: each inner step emits its selected hidden machine-bound type")
    print("  runtime: both Create lookups accept the family type only on the exact machine")
    print("  JEI: each routed step renders its selected Press, Deployer, Saw, or Spout")
    for family_id, (_, _, expected_count) in expected_machines.items():
        print(f"  selectable {family_id} machines: {expected_count}")


if __name__ == "__main__":
    main()
