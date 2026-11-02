package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.RecipeValidator;
import com.zizazr.kjsgen.core.SlotContent;
import dev.godpc.industrialcolonies.MachineRecipeRouting;
import dev.godpc.industrialcolonies.MekanismMachineCodegen;
import dev.godpc.industrialcolonies.KjsGenSequenceSupport;
import dev.godpc.industrialcolonies.TieredRecipeCatalog;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Rejects hand-entered or stale items that are not machines for the selected process. */
@Mixin(value = RecipeValidator.class, remap = false)
public abstract class KjsGenRecipeValidatorMixin {
    @Inject(method = "validate", at = @At("RETURN"), cancellable = true)
    private static void industrialColonies$validateMachineRouting(
            RecipeInstance recipe,
            RecipeTypeDefinition type,
            CallbackInfoReturnable<List<RecipeValidator.Issue>> cir
    ) {
        List<RecipeValidator.Issue> issues = new ArrayList<>(cir.getReturnValue());
        // The preview calls the same generator as export. Surface its exact
        // constraints before preview generation, including temporarily invalid
        // text while editing, instead of letting it close the detached editor.
        if (MekanismMachineCodegen.ID.equals(type.codegenId())) {
            try {
                new MekanismMachineCodegen().generate(recipe, type);
            } catch (IllegalArgumentException invalid) {
                issues.add(new RecipeValidator.Issue(
                        RecipeValidator.Severity.ERROR, "",
                        "industrial_colonies.kjsgen.validation.mekanism_recipe",
                        invalid.getMessage()));
            }
        }
        Optional<TieredRecipeCatalog.RecipeFamily> found =
                MachineRecipeRouting.familyForEditorType(type.id());
        if (found.isPresent() && found.get().supportsMachineSelection()) {
            validateSlot(issues, recipe, MachineRecipeRouting.processSlotKey(found.get()), found.get());
        }

        if ("sequence".equals(type.editorKind())) {
            for (var stage : KjsGenSequenceSupport.unsupported(recipe, type)) {
                issues.add(new RecipeValidator.Issue(
                        RecipeValidator.Severity.ERROR,
                        "seq" + stage.index(),
                        "industrial_colonies.kjsgen.validation.unsupported_sequence_stage",
                        stage.index() + 1, stage.operation()));
            }
            int steps = CreateSpecialModel.seqLen(recipe, type);
            for (int index = 0; index < steps; index++) {
                Optional<TieredRecipeCatalog.RecipeFamily> stepFamily = MachineRecipeRouting.family(
                        CreateSpecialModel.stepTypeId(recipe, type, index));
                if (stepFamily.isPresent() && stepFamily.get().supportsMachineSelection()) {
                    validateSlot(
                            issues,
                            recipe,
                            MachineRecipeRouting.stepSlotKey(index, stepFamily.get()),
                            stepFamily.get());
                }
            }
        }

        cir.setReturnValue(issues);
    }

    private static void validateSlot(
            List<RecipeValidator.Issue> issues,
            RecipeInstance recipe,
            String key,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        SlotContent content = recipe.slot(key);
        if (content.isEmpty()) {
            return; // The normal required-slot validator owns this message.
        }
        boolean valid = content.kind() == ContentKind.ITEM
                && family.machines().stream().anyMatch(machine -> machine.item().equals(content.id()));
        if (!valid) {
            issues.add(new RecipeValidator.Issue(
                    RecipeValidator.Severity.ERROR,
                    key,
                    "industrial_colonies.kjsgen.validation.invalid_machine",
                    family.displayName()));
        }
    }
}
