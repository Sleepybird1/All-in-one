#!/usr/bin/env python3
"""Focused static regressions for the KJSGen review triage UI mixin."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIXIN = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/KjsGenRecipeReviewMixin.java"
STORE = ROOT / "src/main/java/dev/godpc/industrialcolonies/KjsGenRecipeReviewStore.java"
ASSEMBLER = ROOT / "src/main/java/dev/godpc/industrialcolonies/mixin/KjsGenScriptAssemblerMixin.java"
REJECT_SCREEN = ROOT / "src/main/java/dev/godpc/industrialcolonies/KjsGenRejectReasonScreen.java"
LANG = ROOT / "src/main/resources/assets/industrial_colonies/lang/en_us.json"
FOCUSED_JAR_BUILDER = ROOT / "tools/build_approval_only_jar.ps1"


class KjsGenReviewUiTests(unittest.TestCase):
    def test_comments_replace_code_in_place_without_opening_another_screen(self) -> None:
        self.assertIn('@Inject(method = "drawPreview", at = @At("HEAD"), cancellable = true)', self.mixin)
        panel = self.mixin.split('private void industrialColonies$drawCommentPreview(', 1)[1].split('@Inject(', 1)[0]
        self.assertLess(panel.index('ci.cancel();'), panel.index('graphics.fill('))
        self.assertNotIn('new dev.godpc.industrialcolonies.KjsGenRecipeNotesScreen', self.mixin)
        self.assertIn('industrialColonies$commentTabButton.active = !industrialColonies$showCommentTab;', self.mixin)

    @classmethod
    def setUpClass(cls) -> None:
        cls.mixin = MIXIN.read_text(encoding="utf-8")
        cls.store = STORE.read_text(encoding="utf-8")
        cls.assembler = ASSEMBLER.read_text(encoding="utf-8")
        cls.reject_screen = REJECT_SCREEN.read_text(encoding="utf-8")
        cls.lang = json.loads(LANG.read_text(encoding="utf-8"))
        cls.focused_jar_builder = FOCUSED_JAR_BUILDER.read_text(encoding="utf-8")

    def test_focused_jar_includes_the_complete_review_feature_class_closure(self) -> None:
        for class_entry in (
            "KjsGenRecipeReviewStore$ArchiveMutation.class",
            "KjsGenDisabledRecipeFilter.class",
            "KjsGenRecipeReviewMixin$1.class",
        ):
            self.assertIn(class_entry, self.focused_jar_builder)
        self.assertNotIn(
            "KjsGenRecipeReviewStore$ReviewQueueListView.class",
            self.focused_jar_builder,
        )

    def test_deferred_action_is_persisted_and_counted(self) -> None:
        self.assertIn('Component.literal("D")', self.mixin)
        self.assertIn('Component.literal("?")', self.mixin)
        self.assertIn("industrialColonies$reviewStore.defer(recipe)", self.mixin)
        self.assertIn("industrialColonies$reviewStore.maybe(recipe)", self.mixin)
        self.assertIn("counts.deferred()", self.mixin)
        self.assertIn("counts.maybe()", self.mixin)
        self.assertIn("DEFERRED", self.store)
        self.assertIn("MAYBE", self.store)
        self.assertIn("boolean defer(RecipeInstance recipe)", self.store)
        self.assertIn("boolean maybe(RecipeInstance recipe)", self.store)
        self.assertEqual(
            "Defer — revisit after its icon and function are clear",
            self.lang["industrial_colonies.kjsgen.review.defer"],
        )
        self.assertIn(
            "%5$s deferred",
            self.lang["industrial_colonies.kjsgen.review.status.summary"],
        )
        self.assertIn(
            "%6$s maybe",
            self.lang["industrial_colonies.kjsgen.review.status.summary"],
        )
        self.assertEqual(
            "Deferred",
            self.lang["industrial_colonies.kjsgen.review.status.deferred"],
        )
        self.assertEqual(
            "Maybe",
            self.lang["industrial_colonies.kjsgen.review.status.maybe"],
        )

    def test_visible_rows_receive_all_decision_badges_and_tooltips(self) -> None:
        self.assertIn('@Inject(method = "drawRecipeList", at = @At("TAIL"))', self.mixin)
        for marker in (
            'case APPROVED -> "A"',
            'case REJECTED -> "R"',
            'case DEFERRED -> "D"',
            'case MAYBE -> "?"',
            'case DISABLED -> "X"',
        ):
            self.assertIn(marker, self.mixin)
        self.assertIn('case PENDING, STALE -> "!"', self.mixin)
        self.assertIn("graphics.enableScissor", self.mixin)
        self.assertIn("industrialColonies$appendStatusTooltip", self.mixin)
        self.assertEqual(
            "Decision: %1$s",
            self.lang["industrial_colonies.kjsgen.review.list_status"],
        )

    def test_default_uses_a_non_destructive_visible_queue_projection(self) -> None:
        """Reviewed cards disappear from the UI, not from canonical Default."""
        self.assertIn("boolean isVisibleInReviewQueue(", self.store)
        self.assertIn("List<RecipeInstance> visibleRecipes(RecipeProject project)", self.store)
        visible_method = self.store.partition(
            "public synchronized List<RecipeInstance> visibleRecipes(RecipeProject project)"
        )[2].partition("public synchronized Review review(RecipeInstance recipe)")[0]
        self.assertIn("return project.recipes().stream()", visible_method)
        self.assertIn(
            ".filter(recipe -> isVisibleInReviewQueue(project, recipe))",
            visible_method,
        )
        self.assertIn(".toList();", visible_method)
        for mutation in (".remove(", ".removeIf(", ".clear(", ".add(", ".set("):
            self.assertNotIn(mutation, visible_method)

        # Every KJSGen operation which calculates, draws, selects, or scrolls
        # sidebar rows must see the same projection. This keeps a hidden card
        # from remaining clickable at its former row index.
        for method in (
            '"init"',
            '"refreshFromSession"',
            '"setProject"',
            '"drawRecipeList"',
            '"doMouseClicked"',
            '"mouseScrolled"',
        ):
            self.assertIn(method, self.mixin)
        self.assertIn("@Redirect(", self.mixin)
        self.assertIn(
            'target = "Lcom/zizazr/kjsgen/core/RecipeProject;recipes()Ljava/util/List;"',
            self.mixin,
        )
        self.assertIn("require = 10", self.mixin)
        self.assertIn("allow = 10", self.mixin)
        self.assertIn(
            "private List<RecipeInstance> industrialColonies$visibleReviewQueue = List.of();",
            self.mixin,
        )
        self.assertIn("industrialColonies$refreshVisibleReviewQueue(project);", self.mixin)
        self.assertIn(
            ": industrialColonies$reviewStore.visibleRecipes(targetProject);",
            self.mixin,
        )
        self.assertIn("return industrialColonies$visibleReviewQueue;", self.mixin)

        # Reopening/rebuilding may retain the old selected UID. It must be
        # replaced before KJSGen initializes widgets for a hidden card.
        self.assertIn('@Inject(method = "init", at = @At("HEAD"))', self.mixin)
        self.assertIn("boolean selectedIsVisible", self.mixin)
        self.assertIn("if (!selectedIsVisible)", self.mixin)
        self.assertIn("selectedUid = industrialColonies$visibleReviewQueue.isEmpty()", self.mixin)
        self.assertIn(": industrialColonies$visibleReviewQueue.get(0).uid();", self.mixin)

    def test_default_hides_completed_managed_cards_but_keeps_manual_cards(self) -> None:
        # Cards created manually with KJSGen's + button are intentionally not
        # in the managed baseline and must remain available for normal editing.
        self.assertIn("if (!managedUids.contains(recipe.uid()))", self.store)
        self.assertIn("return isPendingForProject(project, review);", self.store)

        # An unchanged decision is complete. A changed Approved/Rejected card
        # becomes STALE and returns for re-review; Maybe/Deferred/Disabled stay
        # parked in their explicit queues until deliberately reclassified.
        self.assertIn("review.currentStatus() != Status.DEFERRED", self.store)
        self.assertIn("review.currentStatus() != Status.MAYBE", self.store)
        self.assertIn("review.currentStatus() != Status.DISABLED", self.store)
        self.assertIn("review.effectiveStatus() == Status.PENDING", self.store)
        self.assertIn("review.effectiveStatus() == Status.STALE", self.store)

        def default_visible(
            managed: bool,
            current: str,
            effective: str,
        ) -> bool:
            if not managed:
                return True
            return current not in {"DEFERRED", "MAYBE", "DISABLED"} and effective in {
                "PENDING",
                "STALE",
            }

        self.assertTrue(default_visible(False, "APPROVED", "APPROVED"))
        self.assertTrue(default_visible(True, "PENDING", "PENDING"))
        self.assertFalse(default_visible(True, "APPROVED", "APPROVED"))
        self.assertFalse(default_visible(True, "REJECTED", "REJECTED"))
        self.assertFalse(default_visible(True, "DEFERRED", "DEFERRED"))
        self.assertFalse(default_visible(True, "MAYBE", "MAYBE"))
        self.assertFalse(default_visible(True, "DISABLED", "DISABLED"))
        self.assertTrue(default_visible(True, "APPROVED", "STALE"))
        self.assertTrue(default_visible(True, "REJECTED", "STALE"))
        self.assertFalse(default_visible(True, "DEFERRED", "STALE"))
        self.assertFalse(default_visible(True, "MAYBE", "STALE"))
        self.assertFalse(default_visible(True, "DISABLED", "STALE"))

    def test_review_buttons_cannot_act_on_a_hidden_default_card(self) -> None:
        self.assertIn("boolean managedSelection = industrialColonies$managedSelection().isPresent();", self.mixin)
        self.assertIn("private Optional<RecipeInstance> industrialColonies$managedSelection()", self.mixin)
        self.assertIn("industrialColonies$reviewStore.isManaged(recipe.uid())", self.mixin)
        self.assertIn(".isVisibleInReviewQueue(project, recipe)", self.mixin)
        for action in ("industrialColonies$rejectButton.active", "industrialColonies$deferButton.active", "industrialColonies$maybeButton.active", "industrialColonies$approveButton.active"):
            self.assertIn(f"{action} = localReview && managedSelection;", self.mixin)

    def test_each_destination_archive_keeps_only_its_matching_decisions(self) -> None:
        expected = {
            "APPROVED_PROJECT": "APPROVED",
            "REJECTED_PROJECT": "REJECTED",
            "DEFERRED_PROJECT": "DEFERRED",
            "MAYBE_PROJECT": "MAYBE",
            "DISABLED_PROJECT": "DISABLED",
        }
        for project, status in expected.items():
            self.assertIn(f"projectNamed(project, {project})", self.store)
            self.assertIn(f"review.currentStatus() == Status.{status}", self.store)

    def test_queue_filter_does_not_remove_approved_cards_from_default_export(self) -> None:
        # The UI projection never reaches ScriptAssembler. Default export is
        # still assembled from KJSGen's canonical recipe batch. Only explicit
        # Disabled decisions are filtered; Approved remains a normal producer.
        self.assertNotIn("visibleRecipes", self.assembler)
        self.assertNotIn("KjsGenRecipeReviewStore", self.assembler)
        self.assertIn("List<RecipeInstance> exportableRecipes = recipes.stream()", self.assembler)
        self.assertIn(
            '? KjsGenDisabledRecipeFilter.loadDisabledRecipeIds()',
            self.assembler,
        )
        self.assertIn(
            "ScriptAssembler.assemble(project, exportableRecipes, removals)",
            self.assembler,
        )
        self.assertIn(
            "ScriptAssembler.assemble(project, List.of(), List.of())",
            self.assembler,
        )

    def test_archive_reclassification_advances_and_rebuilds(self) -> None:
        for project in (
            "approved recipes",
            "rejected recipes",
            "deferred",
            "maybe recipes",
            "disabled recipes",
        ):
            self.assertIn(f'"{project}"', self.mixin)
        self.assertIn("industrialColonies$nextArchiveRecipeUid", self.mixin)
        self.assertIn("archiveStatus.get() != destination", self.mixin)
        self.assertIn("project.recipes().removeIf", self.mixin)
        self.assertIn("rebuildWidgets();", self.mixin)

    def test_restore_default_rejection_has_a_distinct_code_and_label(self) -> None:
        self.assertIn('"restore_default_recipe"', self.reject_screen)
        self.assertIn('"restore_default"', self.reject_screen)
        self.assertIn('"restore_default_recipe"', self.store)
        self.assertEqual(
            "Restore default",
            self.lang[
                "industrial_colonies.kjsgen.review.reject_modal.common.restore_default.label"
            ],
        )
        self.assertEqual(
            "This item doesn’t make anything—restore its default recipe.",
            self.lang[
                "industrial_colonies.kjsgen.review.reject_modal.common.restore_default.note"
            ],
        )

    def test_review_archives_are_symmetric_and_transactional(self) -> None:
        for project in (
            "approved recipes",
            "rejected recipes",
            "Deferred",
            "maybe recipes",
            "disabled recipes",
        ):
            self.assertIn(f'"{project}"', self.store)
        for marker in (
            "moveReviewSnapshot",
            "prepareArchiveMutation",
            "restoreArchiveFiles",
            "synchronizeActiveArchive",
            "atomicWrite(mutation.file()",
        ):
            self.assertIn(marker, self.store)
        self.assertNotIn("upsertApprovedSnapshot", self.store)
        self.assertNotIn("removeApprovedSnapshot", self.store)
        self.assertNotIn("TimeUnit.SECONDS", self.store)

    def test_maybe_and_deferred_have_distinct_second_pass_archives(self) -> None:
        self.assertIn(
            "review.currentStatus() == Status.DEFERRED",
            self.store,
        )
        self.assertIn(
            "review.currentStatus() == Status.MAYBE",
            self.store,
        )
        self.assertIn(
            "review.currentStatus() != Status.DEFERRED",
            self.store,
        )
        self.assertIn(
            "review.currentStatus() != Status.MAYBE",
            self.store,
        )
        self.assertIn("LEGACY_SCHEMA_VERSION = 1", self.store)
        self.assertIn('status = "deferred";', self.store)

    def test_disabled_cards_use_distinct_reasons_and_leave_default_queue(self) -> None:
        for code in (
            "redundant_mechanic",
            "duplicate_machine",
            "progression_bypass",
            "internal_unused",
        ):
            self.assertIn(f'"{code}"', self.store)
        self.assertIn("Status.DISABLED", self.store)
        self.assertIn("review.currentStatus() != Status.DISABLED", self.store)
        self.assertIn("boolean disable(RecipeInstance recipe, String code, String note)", self.store)
        self.assertIn("int disabled", self.store)
        self.assertIn("industrialColonies$reviewStore.disable(", self.mixin)
        self.assertIn("counts.disabled()", self.mixin)
        self.assertIn('case DISABLED -> "X"', self.mixin)
        self.assertEqual(
            "Disabled",
            self.lang["industrial_colonies.kjsgen.review.status.disabled"],
        )

    def test_disable_button_opens_reason_modal_with_editable_note(self) -> None:
        self.assertIn('if ("disable".equals(reason.key()))', self.reject_screen)
        self.assertIn("openDisableReasonChooser();", self.reject_screen)
        self.assertIn("choosingDisableReason", self.reject_screen)
        self.assertIn("EditBox disableNoteBox", self.reject_screen)
        self.assertIn("submitDisableReason();", self.reject_screen)
        self.assertIn("DISABLE_CODE_PREFIX + selectedDisableCode", self.reject_screen)
        for code in (
            "redundant_mechanic",
            "duplicate_machine",
            "progression_bypass",
            "internal_unused",
            "manual",
        ):
            self.assertIn(f'new DisableReason("{code}"', self.reject_screen)
            self.assertIn(
                f"industrial_colonies.kjsgen.review.reject_modal.disable.reason.{code}.label",
                self.lang,
            )
        self.assertIn("closeDisableReasonChooser();", self.reject_screen)
        self.assertIn("redundant_hint", self.reject_screen)

    def test_wrong_machine_uses_two_step_multiselect_catalog_flow(self) -> None:
        self.assertIn("MachineChooserStep.CATEGORY", self.reject_screen)
        self.assertIn("MachineChooserStep.FAMILY", self.reject_screen)
        self.assertIn("MachineChooserStep.RECIPE_TYPE", self.reject_screen)
        self.assertIn("selectedMachineEnvironments", self.reject_screen)
        self.assertIn("loadMachineFamilies()", self.reject_screen)
        self.assertIn("loadRecipeTypes()", self.reject_screen)
        self.assertIn("MACHINE_ENVIRONMENT_RESOURCE", self.reject_screen)
        self.assertIn('!"creative".equals(id)', self.reject_screen)
        for choice in (
            "Default / Create",
            "Sequenced Assembly",
            "TFMG Chemical Vat",
            "TFMG Winding",
            "TFMG Polarizing",
            "TFMG Casting",
            "Mekanism Infusing",
        ):
            self.assertIn(f'"{choice}"', self.reject_screen)
        self.assertIn("submitMachineEnvironment();", self.reject_screen)
        self.assertIn(
            "return super.keyPressed(keyCode, scanCode, modifiers);",
            self.reject_screen,
        )
        self.assertEqual(
            "What is wrong: the machine family or the recipe type?",
            self.lang[
                "industrial_colonies.kjsgen.review.reject_modal.machine.category_prompt"
            ],
        )


if __name__ == "__main__":
    unittest.main()
