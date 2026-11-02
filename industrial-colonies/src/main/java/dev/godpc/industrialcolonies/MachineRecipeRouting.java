package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.core.SlotRole;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Routing metadata shared by the KJSGen editor and its code generators.
 *
 * <p>The machine slots deliberately live outside the generated recipe JSON.
 * They select the runtime serializer used by KubeJS; they are never emitted as
 * an ingredient.</p>
 */
public final class MachineRecipeRouting {
    public static final String PROCESS_SLOT_PREFIX = "__machine_process_";
    public static final String STEP_SLOT_PREFIX = "__machine_step_";

    private static final TieredRecipeCatalog CATALOG = TieredRecipeCatalog.load();

    private MachineRecipeRouting() {
    }

    public static TieredRecipeCatalog catalog() {
        return CATALOG;
    }

    public static Optional<TieredRecipeCatalog.RecipeFamily> family(String id) {
        return CATALOG.recipeFamilies().stream().filter(family -> family.id().equals(id)).findFirst();
    }

    /** Smoking and blasting share the existing fan machine catalog, not washing behavior. */
    public static Optional<TieredRecipeCatalog.RecipeFamily> sequenceFamily(String operation) {
        return family(operation.equals("smoking") || operation.equals("blasting") ? "splashing" : operation);
    }

    public static Optional<TieredRecipeCatalog.RecipeFamily> familyForEditorType(String typeId) {
        if (typeId == null || typeId.isBlank()) {
            return Optional.empty();
        }
        if (typeId.startsWith("kjsgen:create_")) {
            return family(typeId.substring("kjsgen:create_".length()));
        }
        if (!typeId.startsWith(IndustrialColonies.MOD_ID + ":")) {
            return Optional.empty();
        }

        String path = typeId.substring(typeId.indexOf(':') + 1);
        // Dedicated Mekanism editors are not legacy Create tier cards. In
        // particular pigment_mixing must never acquire a Create mixer slot.
        if (path.startsWith("mekanism_")) {
            return Optional.empty();
        }
        return CATALOG.recipeFamilies().stream()
                .filter(family -> path.endsWith("_" + family.id()))
                .findFirst();
    }

    public static String processSlotKey(TieredRecipeCatalog.RecipeFamily family) {
        return PROCESS_SLOT_PREFIX + family.id();
    }

    public static String stepSlotKey(int index, TieredRecipeCatalog.RecipeFamily family) {
        return STEP_SLOT_PREFIX + index + "_" + family.id();
    }

    /** Dynamic catalyst slot shown beside a Sequenced Assembly operation. */
    public static SlotDefinition stepMachineSlot(
            int index,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        return new SlotDefinition(
                stepSlotKey(index, family), SlotRole.CATALYST,
                0, 0, true, true, false, false,
                false, false, false, false);
    }

    public static Optional<TieredRecipeCatalog.RecipeFamily> familyForMachineSlot(SlotDefinition slot) {
        if (slot == null) {
            return Optional.empty();
        }
        return familyForMachineSlot(slot.key());
    }

    public static Optional<TieredRecipeCatalog.RecipeFamily> familyForMachineSlot(String key) {
        if (key == null) {
            return Optional.empty();
        }
        if (key.startsWith(PROCESS_SLOT_PREFIX)) {
            return family(key.substring(PROCESS_SLOT_PREFIX.length()));
        }
        if (!key.startsWith(STEP_SLOT_PREFIX)) {
            return Optional.empty();
        }
        return CATALOG.recipeFamilies().stream()
                .filter(family -> key.endsWith("_" + family.id()))
                .findFirst();
    }

    public static Set<String> allowedMachineItems(SlotDefinition slot) {
        return familyForMachineSlot(slot)
                .map(family -> {
                    Set<String> items = new HashSet<>();
                    family.machines().forEach(machine -> items.add(machine.item()));
                    return items;
                })
                .orElseGet(Set::of);
    }

    public static TieredRecipeCatalog.Machine selectedMachine(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        SlotContent content = recipe.slot(processSlotKey(family));
        TieredRecipeCatalog.Machine explicit = machineByContent(family, content);
        if (explicit != null) {
            return explicit;
        }
        return inferredLegacyMachine(type.id(), family);
    }

    public static TieredRecipeCatalog.Machine selectedStepMachine(
            RecipeInstance recipe,
            int index,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        TieredRecipeCatalog.Machine explicit = machineByContent(family, recipe.slot(stepSlotKey(index, family)));
        return explicit == null ? family.baseMachine() : explicit;
    }

    public static TieredRecipeCatalog.Machine machineByContent(
            TieredRecipeCatalog.RecipeFamily family,
            SlotContent content
    ) {
        if (content == null || content.isEmpty() || content.kind() != ContentKind.ITEM) {
            return null;
        }
        return family.machines().stream()
                .filter(machine -> machine.item().equals(content.id()))
                .findFirst()
                .orElse(null);
    }

    public static String runtimeTypeId(
            TieredRecipeCatalog.RecipeFamily family,
            TieredRecipeCatalog.Machine machine
    ) {
        if (machine == null) {
            return "create:" + family.id();
        }
        String route = machine.isBase() ? "base" : machine.id();
        return IndustrialColonies.MOD_ID + ":" + route + "_" + family.id();
    }

    /** Runtime type for a process editor, including old saved tier layouts. */
    public static String runtimeTypeId(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        if (family.supportsMachineSelection()) {
            return runtimeTypeId(family, selectedMachine(recipe, type, family));
        }
        if (type.id().startsWith(IndustrialColonies.MOD_ID + ":")) {
            return type.id();
        }
        return "create:" + family.id();
    }

    /**
     * Makes the inferred default visible in the editor. This is also the
     * migration path for projects saved with the former tier-per-card model.
     */
    public static boolean ensureEditorDefaults(RecipeInstance recipe, RecipeTypeDefinition type) {
        boolean changed = false;
        Optional<TieredRecipeCatalog.RecipeFamily> outerFamily = familyForEditorType(type.id());
        if (outerFamily.isPresent() && outerFamily.get().supportsMachineSelection()) {
            TieredRecipeCatalog.RecipeFamily family = outerFamily.get();
            String key = processSlotKey(family);
            if (recipe.slot(key).isEmpty()) {
                TieredRecipeCatalog.Machine machine = inferredLegacyMachine(type.id(), family);
                if (machine != null) {
                    recipe.setSlot(key, SlotContent.item(machine.item(), 1));
                    changed = true;
                }
            }
        }

        return changed;
    }

    public static void removeSequenceStep(RecipeInstance recipe, RecipeTypeDefinition type, int removedIndex) {
        List<StepMachine> steps = captureSteps(recipe, type);
        if (removedIndex >= 0 && removedIndex < steps.size()) {
            steps.remove(removedIndex);
            rewriteSteps(recipe, steps);
        }
    }

    public static void moveSequenceStep(RecipeInstance recipe, RecipeTypeDefinition type, int from, int to) {
        List<StepMachine> steps = captureSteps(recipe, type);
        if (from < 0 || from >= steps.size() || to < 0 || to >= steps.size() || from == to) {
            return;
        }
        StepMachine moved = steps.remove(from);
        steps.add(to, moved);
        rewriteSteps(recipe, steps);
    }

    public static void clearSequenceStepMachine(RecipeInstance recipe, int index) {
        List<String> keys = new ArrayList<>(recipe.slots().keySet());
        String prefix = STEP_SLOT_PREFIX + index + "_";
        keys.stream().filter(key -> key.startsWith(prefix)).forEach(key -> recipe.setSlot(key, SlotContent.EMPTY));
    }

    private static List<StepMachine> captureSteps(RecipeInstance recipe, RecipeTypeDefinition type) {
        List<StepMachine> steps = new ArrayList<>();
        int length = CreateSpecialModel.seqLen(recipe, type);
        for (int index = 0; index < length; index++) {
            TieredRecipeCatalog.RecipeFamily family = sequenceFamily(
                    CreateSpecialModel.stepTypeId(recipe, type, index)).orElse(null);
            SlotContent content = family == null ? SlotContent.EMPTY : recipe.slot(stepSlotKey(index, family));
            steps.add(new StepMachine(family, content));
        }
        return steps;
    }

    private static void rewriteSteps(RecipeInstance recipe, List<StepMachine> steps) {
        new ArrayList<>(recipe.slots().keySet()).stream()
                .filter(key -> key.startsWith(STEP_SLOT_PREFIX))
                .forEach(key -> recipe.setSlot(key, SlotContent.EMPTY));
        for (int index = 0; index < steps.size(); index++) {
            StepMachine step = steps.get(index);
            if (step.family() != null && step.content() != null && !step.content().isEmpty()) {
                recipe.setSlot(stepSlotKey(index, step.family()), step.content());
            }
        }
    }

    private static TieredRecipeCatalog.Machine inferredLegacyMachine(
            String typeId,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        if (typeId != null && typeId.startsWith(IndustrialColonies.MOD_ID + ":")) {
            String path = typeId.substring(typeId.indexOf(':') + 1);
            String suffix = "_" + family.id();
            if (path.endsWith(suffix)) {
                String route = path.substring(0, path.length() - suffix.length());
                if ("base".equals(route)) {
                    return family.baseMachine();
                }
                Optional<TieredRecipeCatalog.Tier> tier = CATALOG.tiers().stream()
                        .filter(candidate -> candidate.id().equals(route))
                        .findFirst();
                if (tier.isPresent()) {
                    return family.machineForLegacyTier(tier.get());
                }
            }
        }
        return family.baseMachine();
    }

    private record StepMachine(TieredRecipeCatalog.RecipeFamily family, SlotContent content) {
    }
}
