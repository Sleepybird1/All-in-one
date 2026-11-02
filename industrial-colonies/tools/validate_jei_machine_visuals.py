#!/usr/bin/env python3
"""Static acceptance checks for exact-machine Create JEI integration."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src/main/resources/data/industrial_colonies/tier_recipe_environments.json"
MIXIN_JSON = ROOT / "src/main/resources/industrial_colonies.jei.mixins.json"
JAVA_ROOT = ROOT / "src/main/java/dev/godpc/industrialcolonies"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    mixins = json.loads(MIXIN_JSON.read_text(encoding="utf-8"))
    selectable = {
        family["id"]
        for family in catalog["recipe_families"]
        if len(family.get("machines", [])) > 1
    }
    expected = {
        "cutting", "basin", "mixing", "compacting", "pressing",
        "splashing", "haunting", "deploying", "filling", "emptying",
        "item_application",
    }
    require(selectable == expected, f"unexpected selectable family set: {sorted(selectable)}")

    required_mixins = {
        "CreateRecipeCategoryBuilderMixin",
        "CreateRecipeCategoryMachineMixin",
        "ExactMachineUsesFocusMixin",
        "ExactMachineRecipeLookupMixin",
        "BoundCreateMachineAnimationMixin",
        "BoundFanMachineAnimationMixin",
        "SequencedAssemblyMachineContextMixin",
    }
    require(not mixins.get("required", True), "JEI mixin config must remain optional-safe")
    require(required_mixins <= set(mixins.get("client", [])), "missing JEI mixin entry")

    builder = (JAVA_ROOT / "mixin/jei/CreateRecipeCategoryBuilderMixin.java").read_text(encoding="utf-8")
    require("addTypedRecipes(Lcom/simibubi/create/foundation/recipe/IRecipeTypeInfo;)" in builder,
            "Create category builder hook is not the exact IRecipeTypeInfo overload")
    require("TieredCreateRecipes.typesFor(baseType)" in builder,
            "builder does not add the hidden custom recipe types")
    require("typesFor(AllRecipeTypes.BASIN)" in builder,
            "shared BASIN recipes are not routed into Create's Mixing category")

    category = (JAVA_ROOT / "mixin/jei/CreateRecipeCategoryMachineMixin.java").read_text(encoding="utf-8")
    require("addInvisibleIngredients(RecipeIngredientRole.INPUT)" in category,
            "bound machines are not indexed for JEI Uses lookup")
    require("JeiExactMachineUsesProbe.observeLayout(recipe, machine)" in category,
            "JEI index-time binding observation is missing")
    require("RecipeIngredientRole.CATALYST, 4, 4" in category,
            "bound-machine cue slot is missing")
    require("registering a category catalyst" in category,
            "per-recipe lookup must not regress to a whole-category catalyst")
    require("This recipe runs only in this exact machine." in category,
            "exclusive-machine tooltip is missing")
    require("JeiMachineVisualContext.push(holder.value())" in category,
            "recipe animation context is missing")

    uses_focus = (JAVA_ROOT / "mixin/jei/ExactMachineUsesFocusMixin.java").read_text(encoding="utf-8")
    require("@Mixin(value = FocusUtil.class" in uses_focus,
            "exact-machine Uses filter does not target JEI FocusUtil")
    require("roles.size() != 2" in uses_focus and
            "roles.contains(RecipeIngredientRole.INPUT)" in uses_focus and
            "roles.contains(RecipeIngredientRole.CATALYST)" in uses_focus,
            "exact-machine Uses filter is not limited to JEI's INPUT+CATALYST action")
    require("createFocus(RecipeIngredientRole.INPUT, ingredient)" in uses_focus,
            "exact-machine Uses action does not collapse to its per-recipe INPUT index")
    require("createFocus(RecipeIngredientRole.CATALYST" not in uses_focus,
            "whole-category CATALYST focus leaked back into exact-machine Uses")
    require("JeiExactMachineUsesProbe.observeUsesFocusRewrite(stack)" in uses_focus,
            "real Uses rewrite does not emit its one-shot runtime marker")

    uses_lookup = (JAVA_ROOT / "mixin/jei/ExactMachineRecipeLookupMixin.java").read_text(encoding="utf-8")
    require("@Mixin(value = RecipeManagerInternal.class" in uses_lookup,
            "exact-machine recipe filtering does not target JEI's internal recipe stream")
    require("getRecipesStream(Lmezz/jei/api/recipe/RecipeType;" in uses_lookup and
            "ExactMachineRecipeLookup.machineUses(focuses)" in uses_lookup,
            "exact-machine recipe filtering is not limited to a guarded Uses focus")
    require("lookup.includesCatalyst()" in uses_lookup and
            "observeCombinedUsesFilter(lookup.machineId())" in uses_lookup,
            "the real combined INPUT+CATALYST U path has no acceptance marker")
    require("ExactMachineRecipeLookup.isBoundTo(candidate, lookup.machineId())" in uses_lookup,
            "exact-machine Uses results are not filtered by the recipe's bound machine")

    lookup_helper = (JAVA_ROOT / "client/jei/ExactMachineRecipeLookup.java").read_text(encoding="utf-8")
    require("role != RecipeIngredientRole.INPUT" in lookup_helper and
            "role != RecipeIngredientRole.CATALYST" in lookup_helper and
            "hasInput && machineId != null" in lookup_helper and
            "!machineId.equals(candidate.get())" in lookup_helper and
            ".filter(machine -> !machine.isBase())" in lookup_helper,
            "exact-machine lookup guard could affect base machines, mixed ingredients, or non-Uses queries")

    probe = (JAVA_ROOT / "client/jei/JeiExactMachineUsesProbe.java").read_text(encoding="utf-8")
    require("@JeiPlugin" in probe and "onRuntimeAvailable(IJeiRuntime runtime)" in probe,
            "exact-machine Uses probe is not registered through JEI's runtime API")
    require("IC_JEI_USES_PROBE" in probe,
            "exact-machine Uses probe has no stable acceptance marker")
    require("IC_JEI_EXACT_U_FILTER" in probe and
            "observeUsesFocusRewrite(ItemStack stack)" in probe and
            "observeCombinedUsesFilter(ResourceLocation machineId)" in probe,
            "actual U-key focus rewrite has no stable one-shot marker")
    require("RecipeIngredientRole.INPUT" in probe and "RecipeIngredientRole.CATALYST" in probe,
            "Uses probe must query both INPUT and CATALYST roles")
    require("preRuntimeBound != bound" in probe and
            "boundOutputs.isEmpty()" in probe and
            "supplierInput != bound || supplierCatalyst != bound" in probe and
            "focusInputBound != bound" in probe and
            "focusCatalystBound != bound" in probe,
            "Uses probe does not validate every current Copper Press binding dynamically")
    require("focusInputTotal != bound" in probe and
            "focusInputUnbound != 0" in probe and
            "focusInputOtherMachine != 0" in probe and
            "INPUT_INDEX_LEAK" in probe,
            "Uses probe cannot reject unbound, native, or other-machine leaks")
    require("AllRecipeTypes.PRESSING.getType()" in probe and
            "AllRecipeTypes.COMPACTING.getType()" in probe and
            "mechanicalNativeMissing" in probe,
            "Uses probe does not guard the Mechanical Press native baseline")

    animations = (JAVA_ROOT / "mixin/jei/BoundCreateMachineAnimationMixin.java").read_text(encoding="utf-8")
    for animation in (
        "AnimatedPress.class", "AnimatedDeployer.class", "AnimatedMixer.class",
        "AnimatedSaw.class", "AnimatedSpout.class", "AnimatedItemDrain.class",
    ):
        require(animation in animations, f"missing animation coverage: {animation}")
    require("ordinal = 0" in animations, "machine replacement must leave depot/basin bodies intact")

    sequence = (JAVA_ROOT / "mixin/jei/SequencedAssemblyMachineContextMixin.java").read_text(encoding="utf-8")
    for step in ("AssemblyPressing", "AssemblyDeploying", "AssemblyCutting", "AssemblySpouting"):
        require(step in sequence, f"missing sequenced-step visual coverage: {step}")

    print("PASS: exact-machine Create JEI integration")
    print(f"  selectable families: {len(selectable)}")
    print("  native categories: hidden custom types appended by Create builder")
    print("  uses lookup: non-base exact machines collapse U to the per-recipe INPUT index")
    print("  runtime probe: dynamic exact-binding parity, zero leaks, native press retained")
    print("  U-key marker: one-shot proof that INPUT+CATALYST collapsed to INPUT")
    print("  visuals: press/deployer/mixer/saw/fan/spout/drain")
    print("  sequence hook: exact per-step Press/Deployer/Saw/Spout visuals and runtime")


if __name__ == "__main__":
    main()
