package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.api.RegisterRecipeTypesEvent;
import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.codegen.handlers.CreateSequencedAssemblyCodegen;
import com.zizazr.kjsgen.core.CreateSpecialModel;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;

import java.util.Optional;

/** Adds exact per-operation machine routing to KJSGen's native Sequenced Assembly editor. */
public final class KjsGenSequencedAssemblyIntegration {
    private static final String NATIVE_CODEGEN = "kjsgen:create_sequenced_assembly";

    private KjsGenSequencedAssemblyIntegration() {
    }

    /** Adapt older compiler-produced fluid slots without rewriting the saved card. */
    static RecipeInstance withCanonicalFillingSlots(RecipeInstance recipe, RecipeTypeDefinition type) {
        RecipeInstance exportRecipe = recipe;
        int steps = CreateSpecialModel.seqLen(recipe, type);
        for (int index = 0; index < steps; index++) {
            if (!"filling".equals(CreateSpecialModel.stepTypeId(recipe, type, index))) {
                continue;
            }
            var canonical = CreateSpecialModel.stepItem(recipe, index);
            if (canonical != null && !canonical.isEmpty()) {
                continue; // A newer card's intentional canonical value always wins.
            }
            var legacy = recipe.slot("seqFluid" + index);
            if (legacy == null || legacy.isEmpty()) {
                continue;
            }
            if (legacy.kind() != ContentKind.FLUID && legacy.kind() != ContentKind.FLUID_TAG) {
                throw new IllegalArgumentException("Legacy filling slot is not a fluid: "
                        + recipe.uid() + " seqFluid" + index);
            }
            if (exportRecipe == recipe) {
                exportRecipe = RecipeInstance.fromJson(recipe.toJson().deepCopy());
            }
            // KJSGen 2.0.5 uses seqItemN for both deploying and filling, despite the name.
            CreateSpecialModel.setStepItem(exportRecipe, index, legacy);
        }
        return exportRecipe;
    }

    public static void register() {
        RegisterRecipeTypesEvent.register(event -> {
            RecipeCodegen codegen = new ExactMachineSequenceCodegen();
            // KJSGen's registry is intentionally last-writer-wins. Replace the
            // native handler and the hidden legacy-layout handler after the
            // normal Industrial Colonies registration listener has run.
            event.registerCodegen(NATIVE_CODEGEN, codegen);
            event.registerCodegen(KjsGenIntegration.LEGACY_SEQUENCE_CODEGEN, codegen);
        });
    }

    static final class ExactMachineSequenceCodegen implements RecipeCodegen {
        private static final String NATIVE_DEPLOYING_CALL = "event.recipes.create.deploying(";
        private static final String NATIVE_PRESSING_CALL = "event.recipes.create.pressing(";
        private static final String NATIVE_CUTTING_CALL = "event.recipes.create.cutting(";
        private static final String NATIVE_FILLING_CALL = "event.recipes.create.filling(";
        private static final String NATIVE_OUTER_CALL = "event.recipes.create.sequenced_assembly";

        private final CreateSequencedAssemblyCodegen delegate = new CreateSequencedAssemblyCodegen();

        @Override
        public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
            KjsGenSequenceSupport.requireSupported(recipe, type);
            RecipeInstance exportRecipe = withCanonicalFillingSlots(recipe, type);
            String generated = KjsGenCodegenSafety.forceItemTagIngredients(
                    AssemblyWorkpieceCodegen.generate(exportRecipe, type));

            int steps = CreateSpecialModel.seqLen(recipe, type);
            for (int index = 0; index < steps; index++) {
                String familyId = CreateSpecialModel.stepTypeId(recipe, type, index);
                String nativeCall = nativeStepCall(familyId);
                if (nativeCall == null) {
                    continue;
                }

                TieredRecipeCatalog.RecipeFamily family = MachineRecipeRouting.family(familyId)
                        .filter(TieredRecipeCatalog.RecipeFamily::supportsMachineSelection)
                        .orElseThrow(() -> new IllegalStateException(
                                "Missing selectable " + familyId + " recipe family"));
                TieredRecipeCatalog.Machine machine =
                        MachineRecipeRouting.selectedStepMachine(recipe, index, family);
                String routedCall = "event.recipes."
                        + MachineRecipeRouting.runtimeTypeId(family, machine).replace(':', '.')
                        + "(";
                generated = replaceNextLiteral(generated, nativeCall, routedCall, familyId);
            }

            if (isLegacyOuterType(type.id())) {
                generated = generated.replace(
                        NATIVE_OUTER_CALL,
                        "event.recipes." + type.id().replace(':', '.'));
            }
            return generated;
        }

        @Override
        public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
            return isLegacyOuterType(type.id())
                    ? Optional.of(type.id())
                    : delegate.removeTypeId(recipe, type);
        }

        private static String nativeStepCall(String familyId) {
            return switch (familyId) {
                case "deploying" -> NATIVE_DEPLOYING_CALL;
                case "pressing" -> NATIVE_PRESSING_CALL;
                case "cutting" -> NATIVE_CUTTING_CALL;
                case "filling" -> NATIVE_FILLING_CALL;
                default -> null;
            };
        }

        private static String replaceNextLiteral(
                String source,
                String needle,
                String replacement,
                String familyId
        ) {
            int at = source.indexOf(needle);
            if (at < 0) {
                throw new IllegalStateException(
                        "KJSGen did not emit the expected Sequenced Assembly " + familyId + " call");
            }
            return source.substring(0, at) + replacement + source.substring(at + needle.length());
        }

        private static boolean isLegacyOuterType(String typeId) {
            return typeId != null
                    && typeId.startsWith(IndustrialColonies.MOD_ID + ":")
                    && typeId.endsWith("_sequenced_assembly");
        }
    }
}
