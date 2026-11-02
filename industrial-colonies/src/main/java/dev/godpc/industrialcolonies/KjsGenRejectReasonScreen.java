package dev.godpc.industrialcolonies;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.lwjgl.glfw.GLFW;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiFunction;
import java.util.function.Consumer;

/** Blocking modal used when a managed KJSGen card is disapproved. */
public final class KjsGenRejectReasonScreen extends Screen {
    private static final Component TITLE = Component.translatable(
            "industrial_colonies.kjsgen.review.reject_modal.title");
    private static final Component PROMPT = Component.translatable(
            "industrial_colonies.kjsgen.review.reject_modal.prompt");
    private static final String DEFAULT_REASON = "Rejected during manual recipe review.";
    private static final String MACHINE_ENVIRONMENT_RESOURCE =
            "/data/industrial_colonies/tier_recipe_environments.json";
    private static final String DISABLE_CODE_PREFIX = "disable:";

    private static final List<DisableReason> DISABLE_REASONS = List.of(
            new DisableReason("redundant_mechanic", "redundant_mechanic"),
            new DisableReason("duplicate_machine", "duplicate_machine"),
            new DisableReason("progression_bypass", "progression_bypass"),
            new DisableReason("internal_unused", "internal_unused"),
            new DisableReason("manual", "manual")
    );

    /** Frequent feedback condensed from the existing review ledger and user audit. */
    private static final List<CommonReason> COMMON_REASONS = List.of(
            new CommonReason(
                    "manual",
                    "disable",
                    "disable"),
            new CommonReason("manual", "machine", "machine"),
            new CommonReason("manual", "cost", "cost"),
            new CommonReason("manual", "tier", "tier"),
            new CommonReason(
                    "default_recipe",
                    "default",
                    "default"),
            new CommonReason(
                    "restore_default_recipe",
                    "restore_default",
                    "restore_default"),
            new CommonReason(
                    "manual",
                    "shape_materials",
                    "shape_materials")
    );

    private static final int PANEL_MAX_WIDTH = 520;
    private static final int PANEL_MAX_HEIGHT = 224;
    private static final int OUTER_MARGIN = 6;
    private static final int INNER_PADDING = 8;
    private static final int GAP = 3;

    private final Screen parent;
    private final Component recipeLabel;
    private final BiFunction<String, String, Boolean> onSubmit;

    private EditBox reasonBox;
    private boolean choosingCost;
    private boolean choosingDesign;
    private final Set<String> selectedDesigns = new LinkedHashSet<>();
    private String designNote = "";
    private final Set<String> selectedCosts = new LinkedHashSet<>();
    private String costNote = "";
    private static final Map<String, String> COST_CHOICES = new LinkedHashMap<>();
    static {
        COST_CHOICES.put("Electronics", "Add electronics: circuit boards, processors, AE2 circuits, semiconductors, wiring, and related electronic components.");
        COST_CHOICES.put("Alloys / ingots", "Use more expensive, progression-appropriate alloys and ingots.");
        COST_CHOICES.put("Machine components", "Add relevant machines or subassemblies as ingredients in this complex machine.");
        COST_CHOICES.put("Expensive blocks / frames", "Add expensive structural blocks, machine frames, or casings that fit this machine.");
    }
    private int panelX;
    private int panelY;
    private int panelWidth;
    private int panelHeight;
    private int recipeTextY;
    private int promptY;
    private Component failureMessage;
    private MachineChooserStep machineChooserStep = MachineChooserStep.NONE;
    private final Set<String> selectedMachineEnvironments = new LinkedHashSet<>();
    private List<MachineEnvironment> machineEnvironments = List.of();
    private boolean choosingDisableReason;
    private String selectedDisableCode = "";
    private EditBox disableNoteBox;
    private final Map<String, Button> disableReasonButtons = new LinkedHashMap<>();

    public KjsGenRejectReasonScreen(
            Screen parent,
            Component recipeLabel,
            Consumer<String> onSubmit
    ) {
        this(parent, recipeLabel, adapt(onSubmit));
    }

    public KjsGenRejectReasonScreen(
            Screen parent,
            Component recipeLabel,
            BiFunction<String, String, Boolean> onSubmit
    ) {
        super(TITLE);
        this.parent = Objects.requireNonNull(parent, "parent");
        this.recipeLabel = recipeLabel == null ? Component.empty() : recipeLabel;
        this.onSubmit = Objects.requireNonNull(onSubmit, "onSubmit");
    }

    @Override
    protected void init() {
        panelWidth = Math.max(1, Math.min(PANEL_MAX_WIDTH, width - 2 * OUTER_MARGIN));
        panelHeight = Math.max(1, Math.min(PANEL_MAX_HEIGHT, height - 2 * OUTER_MARGIN));
        panelX = (width - panelWidth) / 2;
        panelY = (height - panelHeight) / 2;

        int innerX = panelX + INNER_PADDING;
        int innerWidth = Math.max(1, panelWidth - 2 * INNER_PADDING);
        boolean compact = panelHeight < 196;
        int controlHeight = compact ? 16 : 20;
        int phraseHeight = compact ? 13 : 18;
        int phraseGap = compact ? 1 : GAP;

        recipeTextY = panelY + (compact ? 19 : 23);
        promptY = recipeTextY + (compact ? font.lineHeight + 2 : 2 * font.lineHeight + 3);
        if (choosingDesign) {
            initDesignChooser(innerX, innerWidth, compact, controlHeight);
            return;
        }
        if (choosingCost) {
            initCostChooser(innerX, innerWidth, controlHeight);
            return;
        }
        if (choosingDisableReason) {
            initDisableReasonChooser(innerX, innerWidth, compact, controlHeight);
            return;
        }
        if (machineChooserStep != MachineChooserStep.NONE) {
            initMachineEnvironmentChooser(
                    innerX,
                    innerWidth,
                    compact,
                    controlHeight);
            return;
        }
        int phraseY = promptY + font.lineHeight + (compact ? 2 : 5);

        int columns = 2;
        int rows = (COMMON_REASONS.size() + columns - 1) / columns;
        int columnWidth = Math.max(1, (innerWidth - GAP) / columns);
        for (int index = 0; index < COMMON_REASONS.size(); index++) {
            CommonReason reason = COMMON_REASONS.get(index);
            int column = index % columns;
            int row = index / columns;
            int buttonX = innerX + column * (columnWidth + GAP);
            int buttonWidth = column == columns - 1
                    ? innerX + innerWidth - buttonX
                    : columnWidth;
            Button button = Button.builder(
                            commonComponent(reason.key(), "label"),
                            ignored -> {
                                if ("disable".equals(reason.key())) {
                                    openDisableReasonChooser();
                                } else if ("machine".equals(reason.key())) {
                                    openMachineEnvironmentChooser();
                                } else if ("shape_materials".equals(reason.key())) {
                                    designNote = reasonBox == null ? "" : reasonBox.getValue();
                                    choosingDesign = true;
                                    failureMessage = null;
                                    rebuildWidgets();
                                } else if ("cost".equals(reason.key())) {
                                    costNote = reasonBox == null ? "" : reasonBox.getValue();
                                    choosingCost = true;
                                    selectedCosts.clear();
                                    failureMessage = null;
                                    rebuildWidgets();
                                } else {
                                    prefillReason(commonComponent(
                                            reason.noteKey(),
                                            "note").getString());
                                }
                            })
                    .bounds(
                            buttonX,
                            phraseY + row * (phraseHeight + phraseGap),
                            buttonWidth,
                            phraseHeight)
                    .tooltip(Tooltip.create(commonComponent(reason.noteKey(), "note")))
                    .build();
            addRenderableWidget(button);
        }

        int phraseBottom = phraseY + rows * phraseHeight + (rows - 1) * phraseGap;
        int editY = phraseBottom + (compact ? 3 : 7);
        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        if (editY + controlHeight + GAP > footerY) {
            editY = footerY - GAP - controlHeight;
        }

        reasonBox = new EditBox(
                font,
                innerX,
                editY,
                innerWidth,
                controlHeight,
                Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.custom_reason"));
        reasonBox.setMaxLength(512);
        reasonBox.setHint(Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.custom_hint"));
        addRenderableWidget(reasonBox);
        setInitialFocus(reasonBox);

        int footerGap = GAP;
        int footerButtonWidth = Math.max(1, (innerWidth - footerGap) / 2);
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.submit"),
                        ignored -> submit())
                .bounds(innerX, footerY, footerButtonWidth, controlHeight)
                .build());
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.cancel"),
                        ignored -> onClose())
                .bounds(
                        innerX + footerButtonWidth + footerGap,
                        footerY,
                        innerWidth - footerButtonWidth - footerGap,
                        controlHeight)
                .build());
    }

    private static Component designComponent(String key, String suffix) {
        return Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.design." + key + "." + suffix);
    }

    private void initDesignChooser(int x, int innerWidth, boolean compact, int controlHeight) {
        int y = promptY + font.lineHeight + (compact ? 2 : 5);
        int choiceHeight = compact ? 13 : 18;
        int choiceGap = compact ? 1 : GAP;
        int columnWidth = Math.max(1, (innerWidth - GAP) / 2);
        for (int index = 0; index < KjsGenDesignFeedback.CHOICES.size(); index++) {
            String key = KjsGenDesignFeedback.CHOICES.get(index);
            int column = index % 2;
            int row = index / 2;
            addRenderableWidget(Button.builder(
                    Component.literal(selectedDesigns.contains(key) ? "[x] " : "[ ] ")
                            .append(designComponent(key, "label")),
                    button -> {
                        if (!selectedDesigns.remove(key)) selectedDesigns.add(key);
                        button.setMessage(Component.literal(selectedDesigns.contains(key) ? "[x] " : "[ ] ")
                                .append(designComponent(key, "label")));
                        failureMessage = null;
                    }).bounds(x + column * (columnWidth + GAP), y + row * (choiceHeight + choiceGap),
                            column == 0 ? columnWidth : innerWidth - columnWidth - GAP, choiceHeight)
                    .tooltip(Tooltip.create(designComponent(key, "note"))).build());
        }
        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        reasonBox = new EditBox(font, x, footerY - controlHeight - GAP, innerWidth, controlHeight,
                designComponent("details", "label"));
        reasonBox.setMaxLength(512);
        reasonBox.setValue(designNote);
        reasonBox.setHint(designComponent("details", "hint"));
        reasonBox.setResponder(value -> designNote = value);
        addRenderableWidget(reasonBox);
        setInitialFocus(reasonBox);
        int half = (innerWidth - GAP) / 2;
        addRenderableWidget(Button.builder(designComponent("submit", "label"),
                ignored -> submitDesign()).bounds(x, footerY, half, controlHeight).build());
        addRenderableWidget(Button.builder(Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.machine.back"),
                ignored -> closeDesignChooser())
                .bounds(x + half + GAP, footerY, innerWidth - half - GAP, controlHeight).build());
    }

    private void submitDesign() {
        if (selectedDesigns.isEmpty()) {
            failureMessage = designComponent("select_one", "note");
            return;
        }
        submit(KjsGenDesignFeedback.reasonCode(selectedDesigns),
                KjsGenDesignFeedback.note(selectedDesigns, designNote,
                        key -> designComponent(key, "note").getString()));
    }

    private void closeDesignChooser() {
        choosingDesign = false;
        failureMessage = null;
        rebuildWidgets();
        prefillReason(designNote);
    }

    private void initCostChooser(int x, int innerWidth, int controlHeight) {
        int y = promptY + font.lineHeight + 5;
        int columnWidth = Math.max(1, (innerWidth - GAP) / 2);
        int index = 0;
        for (var choice : COST_CHOICES.entrySet()) {
            String key = choice.getKey();
            int column = index % 2;
            int row = index++ / 2;
            addRenderableWidget(Button.builder(
                    Component.literal((selectedCosts.contains(key) ? "[x] " : "[ ] ") + key),
                    button -> {
                        if (!selectedCosts.remove(key)) selectedCosts.add(key);
                        button.setMessage(Component.literal((selectedCosts.contains(key) ? "[x] " : "[ ] ") + key));
                    }).bounds(x + column * (columnWidth + GAP),
                            y + row * (controlHeight + GAP),
                            column == 0 ? columnWidth : innerWidth - columnWidth - GAP,
                            controlHeight)
                    .tooltip(Tooltip.create(Component.literal(choice.getValue()))).build());
        }
        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        reasonBox = new EditBox(font, x, footerY - controlHeight - GAP, innerWidth,
                controlHeight, Component.literal("Additional cost feedback"));
        reasonBox.setMaxLength(512);
        reasonBox.setValue(costNote);
        reasonBox.setHint(Component.literal("Optional details; Enter submits selected categories"));
        reasonBox.setResponder(value -> costNote = value);
        addRenderableWidget(reasonBox);
        setInitialFocus(reasonBox);
        int half = (innerWidth - GAP) / 2;
        addRenderableWidget(Button.builder(Component.literal("Disapprove: selected costs"),
                ignored -> submitCost()).bounds(x, footerY, half, controlHeight).build());
        addRenderableWidget(Button.builder(Component.literal("Back"), ignored -> closeCostChooser())
                .bounds(x + half + GAP, footerY, innerWidth - half - GAP, controlHeight).build());
    }

    private void submitCost() {
        if (selectedCosts.isEmpty()) {
            failureMessage = Component.literal("Select at least one cost category.");
            return;
        }
        String note = COST_CHOICES.entrySet().stream()
                .filter(entry -> selectedCosts.contains(entry.getKey()))
                .map(Map.Entry::getValue).reduce((a, b) -> a + " " + b).orElse("");
        if (!costNote.isBlank()) note += " Notes: " + costNote.trim();
        submit("manual", "Cost: " + note);
    }

    private void closeCostChooser() {
        choosingCost = false;
        failureMessage = null;
        rebuildWidgets();
        prefillReason(costNote);
    }

    private void initDisableReasonChooser(
            int innerX,
            int innerWidth,
            boolean compact,
            int controlHeight
    ) {
        reasonBox = null;
        disableReasonButtons.clear();

        int columns = 2;
        int choiceGap = compact ? 1 : GAP;
        int choiceHeight = compact ? 15 : 18;
        int choiceY = promptY + font.lineHeight + (compact ? 2 : 5);
        int columnWidth = Math.max(1, (innerWidth - choiceGap) / columns);
        for (int index = 0; index < DISABLE_REASONS.size(); index++) {
            DisableReason reason = DISABLE_REASONS.get(index);
            int column = index % columns;
            int row = index / columns;
            int buttonX = innerX + column * (columnWidth + choiceGap);
            int buttonWidth = column == columns - 1
                    ? innerX + innerWidth - buttonX
                    : columnWidth;
            Button button = Button.builder(
                            disableReasonComponent(reason),
                            pressed -> selectDisableReason(reason.code()))
                    .bounds(
                            buttonX,
                            choiceY + row * (choiceHeight + choiceGap),
                            buttonWidth,
                            choiceHeight)
                    .tooltip(Tooltip.create(disableComponent(reason.key(), "note")))
                    .build();
            disableReasonButtons.put(reason.code(), button);
            addRenderableWidget(button);
        }

        int rows = (DISABLE_REASONS.size() + columns - 1) / columns;
        int choicesBottom = choiceY
                + rows * choiceHeight
                + Math.max(0, rows - 1) * choiceGap;
        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        int editY = Math.min(
                choicesBottom + (compact ? 2 : 5),
                footerY - controlHeight - GAP);
        disableNoteBox = new EditBox(
                font,
                innerX,
                editY,
                innerWidth,
                controlHeight,
                Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.disable.note"));
        disableNoteBox.setMaxLength(512);
        disableNoteBox.setHint(Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.disable.note_hint"));
        addRenderableWidget(disableNoteBox);

        int backWidth = Math.max(1, (innerWidth - GAP) / 3);
        int submitWidth = innerWidth - backWidth - GAP;
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.disable.submit"),
                        ignored -> submitDisableReason())
                .bounds(innerX, footerY, submitWidth, controlHeight)
                .build());
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.disable.back"),
                        ignored -> closeDisableReasonChooser())
                .bounds(
                        innerX + submitWidth + GAP,
                        footerY,
                        backWidth,
                        controlHeight)
                .build());

        if (selectedDisableCode.isBlank()) {
            setInitialFocus(disableReasonButtons.values().iterator().next());
        } else {
            setInitialFocus(disableNoteBox);
        }
    }

    private void openDisableReasonChooser() {
        choosingDisableReason = true;
        selectedDisableCode = "";
        failureMessage = null;
        rebuildWidgets();
    }

    private void closeDisableReasonChooser() {
        choosingDisableReason = false;
        selectedDisableCode = "";
        disableNoteBox = null;
        disableReasonButtons.clear();
        failureMessage = null;
        rebuildWidgets();
    }

    private void selectDisableReason(String code) {
        selectedDisableCode = code;
        disableReasonButtons.forEach((candidate, button) -> button.setMessage(
                disableReasonComponent(new DisableReason(candidate, candidate))));
        failureMessage = null;
        if (disableNoteBox != null) {
            disableNoteBox.setHint(Component.translatable(
                    "redundant_mechanic".equals(code)
                            ? "industrial_colonies.kjsgen.review.reject_modal.disable.redundant_hint"
                            : "industrial_colonies.kjsgen.review.reject_modal.disable.note_hint"));
            setFocused(disableNoteBox);
        }
    }

    private void submitDisableReason() {
        if (selectedDisableCode.isBlank()) {
            failureMessage = Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.disable.select_reason");
            return;
        }
        String note = disableNoteBox == null ? "" : disableNoteBox.getValue().trim();
        if ("manual".equals(selectedDisableCode) && note.isBlank()) {
            failureMessage = Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.disable.custom_required");
            if (disableNoteBox != null) {
                setFocused(disableNoteBox);
            }
            return;
        }
        if (note.isBlank()) {
            note = disableComponent(selectedDisableCode, "note").getString();
        }
        submit(DISABLE_CODE_PREFIX + selectedDisableCode, note);
    }

    private Component disableReasonComponent(DisableReason reason) {
        return Component.literal(
                (reason.code().equals(selectedDisableCode) ? "[x] " : "[ ] ")
                        + disableComponent(reason.key(), "label").getString());
    }

    private void initMachineEnvironmentChooser(
            int innerX,
            int innerWidth,
            boolean compact,
            int controlHeight
    ) {
        reasonBox = null;
        if (machineChooserStep == MachineChooserStep.CATEGORY) {
            initMachineCategoryChooser(innerX, innerWidth, compact, controlHeight);
            return;
        }
        if (machineEnvironments.isEmpty()) {
            machineEnvironments = loadMachineEnvironments(machineChooserStep);
        }

        int columns = 4;
        int rows = (machineEnvironments.size() + columns - 1) / columns;
        int choiceGap = compact ? 1 : 2;
        int choiceHeight = compact ? 13 : 18;
        int choiceY = promptY + font.lineHeight + (compact ? 2 : 5);
        int columnWidth = Math.max(1, (innerWidth - (columns - 1) * choiceGap) / columns);
        for (int index = 0; index < machineEnvironments.size(); index++) {
            MachineEnvironment environment = machineEnvironments.get(index);
            int column = index % columns;
            int row = index / columns;
            int buttonX = innerX + column * (columnWidth + choiceGap);
            int buttonWidth = column == columns - 1
                    ? innerX + innerWidth - buttonX
                    : columnWidth;
            Button button = Button.builder(
                            machineEnvironmentComponent(environment),
                            pressed -> {
                                if (!selectedMachineEnvironments.remove(environment.key())) {
                                    selectedMachineEnvironments.add(environment.key());
                                }
                                pressed.setMessage(machineEnvironmentComponent(environment));
                            })
                    .bounds(
                            buttonX,
                            choiceY + row * (choiceHeight + choiceGap),
                            buttonWidth,
                            choiceHeight)
                    .tooltip(Tooltip.create(Component.literal(
                            environment.kind() + ": " + environment.displayName())))
                    .build();
            addRenderableWidget(button);
        }

        int choicesBottom = choiceY
                + rows * choiceHeight
                + Math.max(0, rows - 1) * choiceGap;
        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        if (choicesBottom > footerY - GAP) {
            footerY = choicesBottom + GAP;
        }
        int backWidth = Math.max(1, (innerWidth - GAP) / 3);
        int submitWidth = innerWidth - backWidth - GAP;
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.machine.submit"),
                        ignored -> submitMachineEnvironment())
                .bounds(innerX, footerY, submitWidth, controlHeight)
                .build());
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.machine.back"),
                        ignored -> closeMachineEnvironmentChooser())
                .bounds(
                        innerX + submitWidth + GAP,
                        footerY,
                        backWidth,
                        controlHeight)
                .build());
    }

    private void initMachineCategoryChooser(
            int innerX,
            int innerWidth,
            boolean compact,
            int controlHeight
    ) {
        int choiceY = promptY + font.lineHeight + (compact ? 5 : 10);
        int choiceHeight = compact ? 20 : 28;
        int choiceWidth = Math.max(1, (innerWidth - GAP) / 2);
        Button family = Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.machine.family"),
                        ignored -> openMachineAlternatives(MachineChooserStep.FAMILY))
                .bounds(innerX, choiceY, choiceWidth, choiceHeight)
                .tooltip(Tooltip.create(Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.machine.family.tooltip")))
                .build();
        Button recipeType = Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.machine.recipe_type"),
                        ignored -> openMachineAlternatives(MachineChooserStep.RECIPE_TYPE))
                .bounds(
                        innerX + choiceWidth + GAP,
                        choiceY,
                        innerWidth - choiceWidth - GAP,
                        choiceHeight)
                .tooltip(Tooltip.create(Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.machine.recipe_type.tooltip")))
                .build();
        addRenderableWidget(family);
        addRenderableWidget(recipeType);
        setInitialFocus(family);

        int footerY = panelY + panelHeight - INNER_PADDING - controlHeight;
        addRenderableWidget(Button.builder(
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.reject_modal.machine.back"),
                        ignored -> closeMachineEnvironmentChooser())
                .bounds(innerX, footerY, innerWidth, controlHeight)
                .build());
    }

    private void openMachineEnvironmentChooser() {
        machineChooserStep = MachineChooserStep.CATEGORY;
        selectedMachineEnvironments.clear();
        machineEnvironments = List.of();
        failureMessage = null;
        rebuildWidgets();
    }

    private void openMachineAlternatives(MachineChooserStep step) {
        machineChooserStep = step;
        selectedMachineEnvironments.clear();
        machineEnvironments = List.of();
        failureMessage = null;
        rebuildWidgets();
    }

    private void closeMachineEnvironmentChooser() {
        if (machineChooserStep == MachineChooserStep.FAMILY
                || machineChooserStep == MachineChooserStep.RECIPE_TYPE) {
            machineChooserStep = MachineChooserStep.CATEGORY;
        } else {
            machineChooserStep = MachineChooserStep.NONE;
            selectedMachineEnvironments.clear();
        }
        machineEnvironments = List.of();
        failureMessage = null;
        rebuildWidgets();
    }

    private void submitMachineEnvironment() {
        if (selectedMachineEnvironments.isEmpty()) {
            failureMessage = Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.machine.select_one");
            return;
        }
        String selected = machineEnvironments.stream()
                .filter(environment -> selectedMachineEnvironments.contains(environment.key()))
                .map(MachineEnvironment::displayName)
                .reduce((left, right) -> left + ", " + right)
                .orElse("");
        Component category = Component.translatable(machineChooserStep == MachineChooserStep.FAMILY
                ? "industrial_colonies.kjsgen.review.reject_modal.machine.family"
                : "industrial_colonies.kjsgen.review.reject_modal.machine.recipe_type");
        String note = Component.translatable(
                        "industrial_colonies.kjsgen.review.reject_modal.machine.note",
                        category,
                        selected)
                .getString();
        submit("manual", note);
    }

    private Component machineEnvironmentComponent(MachineEnvironment environment) {
        return Component.literal(
                (selectedMachineEnvironments.contains(environment.key()) ? "[x] " : "[ ] ")
                        + environment.displayName());
    }

    private static List<MachineEnvironment> loadMachineEnvironments(
            MachineChooserStep step
    ) {
        if (step == MachineChooserStep.FAMILY) {
            return loadMachineFamilies();
        }
        if (step == MachineChooserStep.RECIPE_TYPE) {
            return loadRecipeTypes();
        }
        return List.of();
    }

    private static List<MachineEnvironment> loadMachineFamilies() {
        Map<String, MachineEnvironment> choices = new LinkedHashMap<>();
        addEnvironment(choices, "family", "default_create", "Default / Create");
        readEnvironmentCatalog().map(root -> root.get("tiers")).filter(JsonElement::isJsonArray)
                .ifPresent(tiers -> {
                    for (JsonElement element : tiers.getAsJsonArray()) {
                        if (!element.isJsonObject()) {
                            continue;
                        }
                        JsonObject tier = element.getAsJsonObject();
                        String id = jsonString(tier, "id");
                        String displayName = jsonString(tier, "display_name");
                        if (!id.isBlank()
                                && !displayName.isBlank()
                                && !"creative".equals(id)) {
                            addEnvironment(choices, "family", id, displayName);
                        }
                    }
                });
        if (choices.size() == 1) {
            for (String tier : List.of(
                    "Andesite", "Zinc", "Copper", "Brass", "Railway",
                    "Industrial Iron", "Weathered Iron", "Refined Radiance",
                    "Shadow Steel")) {
                addEnvironment(choices, "family", slug(tier), tier);
            }
        }
        return List.copyOf(choices.values());
    }

    private static List<MachineEnvironment> loadRecipeTypes() {
        List<String> logicalTypes = List.of(
                "Crafting",
                "Mechanical Crafting",
                "Sequenced Assembly",
                "Pressing",
                "Compacting",
                "Deploying",
                "Mixing",
                "Cutting",
                "Milling",
                "Crushing",
                "Filling",
                "Emptying",
                "Washing",
                "Haunting",
                "Sandpaper Polishing",
                "Item Application",
                "TFMG Chemical Vat",
                "TFMG Winding",
                "TFMG Polarizing",
                "TFMG Casting",
                "Mekanism Enriching",
                "Mekanism Infusing",
                "Smelting / Blasting",
                "Other Machine Process"
        );
        List<MachineEnvironment> choices = new ArrayList<>();
        for (String displayName : logicalTypes) {
            choices.add(new MachineEnvironment(
                    "Recipe type",
                    "recipe_type:" + slug(displayName),
                    displayName));
        }
        return List.copyOf(choices);
    }

    private static Optional<JsonObject> readEnvironmentCatalog() {
        try (InputStream stream = KjsGenRejectReasonScreen.class.getResourceAsStream(
                MACHINE_ENVIRONMENT_RESOURCE)) {
            if (stream == null) {
                return Optional.empty();
            }
            try (InputStreamReader reader = new InputStreamReader(
                    stream,
                    StandardCharsets.UTF_8)) {
                JsonElement parsed = JsonParser.parseReader(reader);
                return parsed.isJsonObject()
                        ? Optional.of(parsed.getAsJsonObject())
                        : Optional.empty();
            }
        } catch (Exception ignored) {
            return Optional.empty();
        }
    }

    private static void addEnvironment(
            Map<String, MachineEnvironment> choices,
            String kind,
            String id,
            String displayName
    ) {
        String key = kind + ":" + id;
        choices.putIfAbsent(key, new MachineEnvironment(kind, key, displayName));
    }

    private static String jsonString(JsonObject object, String key) {
        return object.has(key) && object.get(key).isJsonPrimitive()
                ? object.get(key).getAsString()
                : "";
    }

    private static String slug(String value) {
        return value.toLowerCase(java.util.Locale.ROOT)
                .replaceAll("[^a-z0-9]+", "_")
                .replaceAll("^_+|_+$", "");
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        // The editor renders item models with their own depth/buffer state.
        // Do not render it behind this screen: a later dimmer cannot reliably
        // cover those icons. Keep the parent solely for return navigation.
        graphics.fill(0, 0, width, height, 0xFF14161C);

        graphics.fill(panelX - 3, panelY - 3, panelX + panelWidth + 3,
                panelY + panelHeight + 3, 0xB0000000);
        graphics.fill(panelX, panelY, panelX + panelWidth, panelY + panelHeight,
                0xFF14161C);
        graphics.renderOutline(panelX, panelY, panelWidth, panelHeight, 0xFF9EA9BC);

        int innerX = panelX + INNER_PADDING;
        int innerWidth = Math.max(1, panelWidth - 2 * INNER_PADDING);
        graphics.drawCenteredString(font, TITLE, width / 2, panelY + 7, 0xFFFFFFFF);
        drawWrapped(graphics, recipeLabel, innerX, recipeTextY, innerWidth,
                panelHeight < 196 ? 1 : 2, 0xFFB8C7DD);
        Component guidance = failureMessage == null
                ? chooserGuidance()
                : failureMessage;
        int guidanceColor = failureMessage == null ? 0xFFE0E0E0 : 0xFFFF7070;
        drawWrapped(graphics, guidance, innerX, promptY, innerWidth, 1, guidanceColor);

        // Screen renders only this screen's children. The parent never receives
        // mouse or keyboard events while the modal is installed.
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_ENTER || keyCode == GLFW.GLFW_KEY_KP_ENTER) {
            if (choosingDesign) { submitDesign(); return true; }
            if (choosingCost) { submitCost(); return true; }
            if (choosingDisableReason) {
                submitDisableReason();
                return true;
            }
            if (machineChooserStep == MachineChooserStep.FAMILY
                    || machineChooserStep == MachineChooserStep.RECIPE_TYPE) {
                submitMachineEnvironment();
                return true;
            }
            if (machineChooserStep == MachineChooserStep.CATEGORY) {
                return super.keyPressed(keyCode, scanCode, modifiers);
            }
            submit();
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_ESCAPE) {
            if (choosingDesign) { closeDesignChooser(); return true; }
            if (choosingCost) { closeCostChooser(); return true; }
            if (choosingDisableReason) {
                closeDisableReasonChooser();
                return true;
            }
            if (machineChooserStep != MachineChooserStep.NONE) {
                closeMachineEnvironmentChooser();
                return true;
            }
            onClose();
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (mouseX < panelX || mouseX >= panelX + panelWidth
                || mouseY < panelY || mouseY >= panelY + panelHeight) {
            return true;
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    private Component chooserGuidance() {
        if (choosingDesign) return designComponent("prompt", "note");
        if (choosingCost) return Component.literal("Select one or more cost categories; Enter submits.");
        if (choosingDisableReason) {
            return Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.disable.prompt");
        }
        return switch (machineChooserStep) {
            case NONE -> PROMPT;
            case CATEGORY -> Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.machine.category_prompt");
            case FAMILY -> Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.machine.family_prompt");
            case RECIPE_TYPE -> Component.translatable(
                    "industrial_colonies.kjsgen.review.reject_modal.machine.recipe_type_prompt");
        };
    }

    @Override
    public void onClose() {
        minecraft.setScreen(parent);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private void submit() {
        String reason = reasonBox == null ? "" : reasonBox.getValue().trim();
        submit("manual", reason.isEmpty() ? DEFAULT_REASON : reason);
    }

    private void prefillReason(String reasonText) {
        if (reasonBox == null) {
            return;
        }
        reasonBox.setValue(reasonText == null ? "" : reasonText);
        reasonBox.moveCursorToEnd(false);
        setFocused(reasonBox);
    }

    private void submit(String code, String reason) {
        if (Boolean.TRUE.equals(onSubmit.apply(code, reason))) {
            minecraft.setScreen(parent);
            return;
        }
        failureMessage = Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.save_failed");
        if (reasonBox != null) {
            setFocused(reasonBox);
        }
    }

    private void drawWrapped(
            GuiGraphics graphics,
            Component text,
            int x,
            int y,
            int maxWidth,
            int maxLines,
            int color
    ) {
        var lines = font.split(text, maxWidth);
        int count = Math.min(maxLines, lines.size());
        for (int index = 0; index < count; index++) {
            graphics.drawString(
                    font,
                    lines.get(index),
                    x,
                    y + index * font.lineHeight,
                    color,
                    false);
        }
    }

    private static BiFunction<String, String, Boolean> adapt(Consumer<String> callback) {
        Consumer<String> required = Objects.requireNonNull(callback, "onSubmit");
        return (code, note) -> {
            required.accept(note);
            return true;
        };
    }

    private static Component commonComponent(String key, String suffix) {
        return Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.common."
                        + key
                        + "."
                        + suffix);
    }

    private static Component disableComponent(String key, String suffix) {
        return Component.translatable(
                "industrial_colonies.kjsgen.review.reject_modal.disable.reason."
                        + key
                        + "."
                        + suffix);
    }

    private record CommonReason(String code, String key, String noteKey) {
    }

    private record DisableReason(String code, String key) {
    }

    private enum MachineChooserStep {
        NONE,
        CATEGORY,
        FAMILY,
        RECIPE_TYPE
    }

    private record MachineEnvironment(String kind, String key, String displayName) {
    }
}
