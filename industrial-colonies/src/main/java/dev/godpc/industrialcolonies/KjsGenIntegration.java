package dev.godpc.industrialcolonies;

import com.zizazr.kjsgen.api.RegisterRecipeTypesEvent;
import com.zizazr.kjsgen.codegen.JsUtil;
import com.zizazr.kjsgen.codegen.RecipeCodegen;
import com.zizazr.kjsgen.codegen.handlers.CreateMechanicalCraftingCodegen;
import com.zizazr.kjsgen.codegen.handlers.CreateSequencedAssemblyCodegen;
import com.zizazr.kjsgen.codegen.handlers.TemplateRecipeCodegen;
import com.zizazr.kjsgen.core.LayoutDecoration;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.core.SlotDefinition;
import com.zizazr.kjsgen.core.SlotRole;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

/** Installs one process editor per Create operation with an in-canvas machine selector. */
public final class KjsGenIntegration {
    public static final String MACHINE_TEMPLATE_CODEGEN = IndustrialColonies.MOD_ID + ":machine_template";
    public static final String LEGACY_SEQUENCE_CODEGEN = IndustrialColonies.MOD_ID + ":legacy_sequence";
    public static final String LEGACY_MECHANICAL_CODEGEN = IndustrialColonies.MOD_ID + ":legacy_mechanical";
    public static final String MEKANISM_METALLURGIC_INFUSING_CODEGEN =
            IndustrialColonies.MOD_ID + ":mekanism_metallurgic_infusing";
    public static final String TFMG_CHEMICAL_VAT_CODEGEN =
            IndustrialColonies.MOD_ID + ":tfmg_chemical_vat";

    /** Deliberately absent: legacy definitions resolve saved projects but stay out of the type picker. */
    private static final String HIDDEN_LEGACY_MOD = IndustrialColonies.MOD_ID + "_legacy_layout";
    private static final int MACHINE_COLUMN_WIDTH = 24;

    private KjsGenIntegration() {
    }

    public static void register() {
        RegisterRecipeTypesEvent.register(event -> {
            event.registerCodegen(Ae2InscriberCodegen.ID, new Ae2InscriberCodegen());
            event.registerCodegen(CrystalAssemblerCodegen.ID, new CrystalAssemblerCodegen());
            event.registerCodegen(CreateItemApplicationCodegen.ID, new CreateItemApplicationCodegen());
            event.registerCodegen(NuclearCraftManufacturingCodegen.ID, new NuclearCraftManufacturingCodegen());
            event.registerCodegen(MekanismMachineCodegen.ID, new MekanismMachineCodegen());
            event.registerCodegen(TfmgPolarizerCodegen.ID, new TfmgPolarizerCodegen());
            event.registerCodegen(TfmgNativeProcessingCodegen.ID, new TfmgNativeProcessingCodegen());
            event.registerCodegen("industrial_colonies:tool_shaped", new ToolUseOptions.CraftingCodegen(new com.zizazr.kjsgen.codegen.handlers.ShapedRecipeCodegen()));
            event.registerCodegen("industrial_colonies:tool_shapeless", new ToolUseOptions.CraftingCodegen(new com.zizazr.kjsgen.codegen.handlers.ShapelessRecipeCodegen()));
            event.registerCodegen("kjsgen:create_mechanical_crafting", new NativeCraftingCodegen(new CreateMechanicalCraftingCodegen()));
            event.registerCodegen(MACHINE_TEMPLATE_CODEGEN, new MachineTemplateCodegen());
            event.registerCodegen(LEGACY_SEQUENCE_CODEGEN,
                    new LegacyOuterCodegen(new CreateSequencedAssemblyCodegen(),
                            "event.recipes.create.sequenced_assembly"));
            event.registerCodegen(LEGACY_MECHANICAL_CODEGEN,
                    new LegacyOuterCodegen(new CreateMechanicalCraftingCodegen(),
                            "event.recipes.create.mechanical_crafting"));
            event.registerCodegen(MEKANISM_METALLURGIC_INFUSING_CODEGEN,
                    new MekanismMetallurgicInfusingCodegen());
            event.registerCodegen(TFMG_CHEMICAL_VAT_CODEGEN,
                    new TfmgChemicalVatCodegen());
            event.registerCodegen("industrial_colonies:basin_melting", new BasinMeltingCodegen());
            event.registerCodegen("industrial_colonies:metallurgy", new MetallurgyCodegen());
            installMachineCentricDefinitions(event::registerType);
        });
    }

    /** Re-applied after KJSGen's client resource reload replaces bundled layouts. */
    public static void installMachineCentricDefinitions() {
        installMachineCentricDefinitions(RecipeTypeRegistry::register);
    }

    private static void installMachineCentricDefinitions(Consumer<RecipeTypeDefinition> register) {
        for (TieredRecipeCatalog.RecipeFamily family : MachineRecipeRouting.catalog().recipeFamilies()) {
            String nativeEditorId = "kjsgen:create_" + family.id();
            Optional<RecipeTypeDefinition> found = RecipeTypeRegistry.get(nativeEditorId);
            if (found.isEmpty()) {
                continue; // KJSGen has no visual editor for this Create family.
            }

            RecipeTypeDefinition source = found.get();
            if ("deploying".equals(family.id())) source=ToolUseOptions.extend(source,false,source.codegenId());
            if ("mixing".equals(family.id()) || "compacting".equals(family.id())) {
                source = KjsGenBasinOutputs.extend(source);
                source = KjsGenLowHeat.extend(source,
                        net.neoforged.fml.ModList.get().isLoaded("createlowheated"));
            }
            RecipeTypeDefinition processDefinition = source;
            if (family.supportsMachineSelection()
                    && !MACHINE_TEMPLATE_CODEGEN.equals(source.codegenId())) {
                processDefinition = withMachineColumn(source, family);
            }
            register.accept(processDefinition);

            // Old projects used one layout per tier. Keep those identifiers
            // resolvable, but hide them from the recipe-type picker.
            for (TieredRecipeCatalog.Tier tier : MachineRecipeRouting.catalog().tiers()) {
                String legacyId = IndustrialColonies.MOD_ID + ":" + tier.id() + "_" + family.id();
                register.accept(copy(processDefinition, legacyId, IndustrialColonies.MOD_ID,
                        legacyId, HIDDEN_LEGACY_MOD, legacyCodegen(family)));
            }
        }

        // KJSGen 2.0.5 ships a four-argument template for this recipe. KubeJS
        // 2101's codec-backed Mekanism schema has no matching constructor, so
        // keep the visual layout but replace only its exporter.
        RecipeTypeRegistry.get("kjsgen:mekanism_metallurgic_infusing")
                .map(source -> withCodegen(source, MEKANISM_METALLURGIC_INFUSING_CODEGEN))
                .ifPresent(register);
        for(String family:MekanismMachineCodegen.BUNDLED) {
            RecipeTypeRegistry.get("kjsgen:mekanism_"+family)
                    .map(MekanismMachineCodegen::extendBundled).ifPresent(register);
        }
        installKnownUserMachineDefinitions(register);
        for (String crafting : List.of("shaped", "shapeless")) {
            RecipeTypeRegistry.get("kjsgen:"+crafting)
                .map(source->ToolUseOptions.extend(source,true,"industrial_colonies:tool_"+crafting)).ifPresent(register);
        }
    }

    /** User layouts may override bundled definitions after their initial registration. */
    public static void installKnownUserMachineDefinitions() {
        installKnownUserMachineDefinitions(RecipeTypeRegistry::register);
    }

    private static void installKnownUserMachineDefinitions(Consumer<RecipeTypeDefinition> register) {
        for (String family : NuclearCraftManufacturingCodegen.SHAPES.keySet()) {
            RecipeTypeRegistry.get("industrial_colonies:nuclearcraft_" + family)
                    .map(NuclearCraftManufacturingCodegen::extendDefinition).ifPresent(register);
        }
    }

    private static RecipeTypeDefinition withCodegen(RecipeTypeDefinition source, String codegen) {
        return new RecipeTypeDefinition(
                source.id(), source.modId(), source.iconItem(),
                source.canvasWidth(), source.canvasHeight(),
                source.slots(), source.decorations(), source.parameters(), codegen,
                source.requiresMod(), source.editorKind(), source.jeiCategory());
    }

    private static String legacyCodegen(TieredRecipeCatalog.RecipeFamily family) {
        if ("mechanical_crafting".equals(family.id())) {
            return LEGACY_MECHANICAL_CODEGEN;
        }
        if ("sequenced_assembly".equals(family.id())) {
            return LEGACY_SEQUENCE_CODEGEN;
        }
        return MACHINE_TEMPLATE_CODEGEN;
    }

    /** Places the actual machine at x=0 and shifts the recipe diagram right. */
    private static RecipeTypeDefinition withMachineColumn(
            RecipeTypeDefinition source,
            TieredRecipeCatalog.RecipeFamily family
    ) {
        List<SlotDefinition> slots = new ArrayList<>();
        slots.add(new SlotDefinition(
                MachineRecipeRouting.processSlotKey(family), SlotRole.CATALYST,
                0, 0, true, true, false, false, false, false, false, false));
        source.slots().stream().map(KjsGenIntegration::shiftSlot).forEach(slots::add);
        if ("compacting".equals(family.id())) {
            // Some press operations use a durable die. A second, optional
            // output lets the recipe return that mold instead of consuming it.
            slots.add(new SlotDefinition(
                    "returned_tool", SlotRole.OUTPUT,
                    source.canvasWidth() + 2, 33,
                    false, true, false, false,
                    false, true, true, false));
        }

        List<LayoutDecoration> decorations = source.decorations().stream()
                .map(decoration -> new LayoutDecoration(
                        decoration.type(), decoration.x() + MACHINE_COLUMN_WIDTH,
                        decoration.y(), decoration.text()))
                .toList();

        return new RecipeTypeDefinition(
                source.id(), source.modId(), source.iconItem(),
                source.canvasWidth() + MACHINE_COLUMN_WIDTH, source.canvasHeight(),
                slots, decorations, source.parameters(), MACHINE_TEMPLATE_CODEGEN,
                source.requiresMod(), source.editorKind(), source.jeiCategory());
    }

    private static SlotDefinition shiftSlot(SlotDefinition source) {
        return new SlotDefinition(
                source.key(), source.role(), source.x() + MACHINE_COLUMN_WIDTH, source.y(),
                source.required(), source.allowsItem(), source.allowsTag(), source.allowsFluid(),
                source.allowsChemical(), source.allowsCount(), source.allowsChance(), source.list());
    }

    private static RecipeTypeDefinition copy(
            RecipeTypeDefinition source,
            String id,
            String modId,
            String jeiCategory,
            String requiresMod,
            String codegen
    ) {
        return new RecipeTypeDefinition(
                id, modId, source.iconItem(), source.canvasWidth(), source.canvasHeight(),
                source.slots(), source.decorations(), source.parameters(), codegen,
                requiresMod, source.editorKind(), jeiCategory);
    }

    private static final class MachineTemplateCodegen implements RecipeCodegen {
        private final TemplateRecipeCodegen delegate = new TemplateRecipeCodegen();

        @Override
        public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
            Optional<TieredRecipeCatalog.RecipeFamily> found =
                    MachineRecipeRouting.familyForEditorType(type.id());
            if (found.isEmpty()) {
                return delegate.generate(recipe, type);
            }
            TieredRecipeCatalog.RecipeFamily family = found.get();
            if(!recipe.paramRaw(NativeCreateProcessingCodegen.META).isBlank()) {
                SlotContent machine=recipe.slot(MachineRecipeRouting.processSlotKey(family));
                if(!machine.isEmpty()&&MachineRecipeRouting.machineByContent(family,machine)==null)
                    throw new IllegalArgumentException("Unknown machine selection for native process");
                if(family.id().equals("mixing")||family.id().equals("compacting"))KjsGenBasinOutputs.validate(recipe,type);
                return new NativeCreateProcessingCodegen().generate(recipe,type,MachineRecipeRouting.runtimeTypeId(recipe,type,family));
            }
            if(family.id().equals("mixing") || family.id().equals("compacting")) KjsGenBasinOutputs.validate(recipe,type);
            String generated = KjsGenCodegenSafety.forceItemTagIngredients(
                    KjsGenBasinInputCounts.generate(recipe, type, delegate));
            String nativeCall = "event.recipes.create." + family.id();
            String runtimeCall = "event.recipes."
                    + MachineRecipeRouting.runtimeTypeId(recipe, type, family).replace(':', '.');
            String routed=generated.replace(nativeCall, runtimeCall);
            if (family.id().equals("deploying")) routed+=ToolUseOptions.deploySuffix(ToolUseOptions.mode(recipe,type,ToolUseOptions.MODE),recipe.slot("held"),ToolUseOptions.damage(recipe,type,ToolUseOptions.DAMAGE));
            return routed;
        }

        @Override
        public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
            return MachineRecipeRouting.familyForEditorType(type.id())
                    .map(family -> MachineRecipeRouting.runtimeTypeId(recipe, type, family));
        }
    }

    private record LegacyOuterCodegen(RecipeCodegen delegate, String nativeCall) implements RecipeCodegen {
        @Override
        public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
            return delegate.generate(recipe, type).replace(
                    nativeCall, "event.recipes." + type.id().replace(':', '.'));
        }

        @Override
        public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
            return Optional.of(type.id());
        }
    }

    /**
     * Emits the exact 1.21.1 Mekanism codec shape through event.custom.
     *
     * <p>The bundled KJSGen template calls the codec-backed recipe function
     * with four positional arguments. KubeJS only exposes the three mapped
     * stack arguments there, while Mekanism still requires the JSON
     * {@code per_tick_usage} field. Writing the authoritative JSON form avoids
     * that incompatible constructor without changing the editor layout.</p>
     */
    private static final class MekanismMetallurgicInfusingCodegen implements RecipeCodegen {
        @Override
        public String generate(RecipeInstance recipe, RecipeTypeDefinition type) {
            SlotContent input = requireSlot(recipe, "input");
            SlotContent chemical = requireSlot(recipe, "infusion");
            SlotContent output = requireSlot(recipe, "output");
            requireNoComponents(input, "input");
            requireNoComponents(chemical, "infusion");
            requireNoComponents(output, "output");

            String recipeId = KjsGenIntegration.requireRecipeId(recipe, "Mekanism metallurgic infusing");
            return "event.custom({ type: 'mekanism:metallurgic_infusing', item_input: "
                    + itemIngredient(input)
                    + ", chemical_input: " + chemicalIngredient(chemical)
                    + ", output: " + itemOutput(output)
                    + ", per_tick_usage: " + recipe.paramBool(type, "perTickUsage", false)
                    + " }).id(" + JsUtil.quote(recipeId) + ")";
        }

        @Override
        public Optional<String> removeTypeId(RecipeInstance recipe, RecipeTypeDefinition type) {
            return Optional.of("mekanism:metallurgic_infusing");
        }

        private static SlotContent requireSlot(RecipeInstance recipe, String key) {
            SlotContent content = recipe.slot(key);
            if (content == null || content.isEmpty()) {
                throw new IllegalArgumentException("Missing required Mekanism slot: " + key);
            }
            return content;
        }

        private static void requireNoComponents(SlotContent content, String key) {
            if (content.components() != null && !content.components().isBlank()) {
                throw new IllegalArgumentException(
                        "Mekanism metallurgic infusing slot does not support item components: " + key);
            }
        }

        private static String itemIngredient(SlotContent content) {
            String key = switch (content.kind()) {
                case ITEM -> "item";
                case ITEM_TAG -> "tag";
                default -> throw wrongKind("item ingredient", content.kind());
            };
            return "{ count: " + Math.max(1, content.count())
                    + ", " + key + ": " + JsUtil.quote(content.id()) + " }";
        }

        private static String chemicalIngredient(SlotContent content) {
            String key = switch (content.kind()) {
                case CHEMICAL -> "chemical";
                case CHEMICAL_TAG -> "tag";
                default -> throw wrongKind("chemical ingredient", content.kind());
            };
            return "{ amount: " + Math.max(1, content.amount())
                    + ", " + key + ": " + JsUtil.quote(content.id()) + " }";
        }

        private static String itemOutput(SlotContent content) {
            if (content.kind() != ContentKind.ITEM) {
                throw wrongKind("item output", content.kind());
            }
            return "{ count: " + Math.max(1, content.count())
                    + ", id: " + JsUtil.quote(content.id()) + " }";
        }

        private static IllegalArgumentException wrongKind(String expected, ContentKind actual) {
            return new IllegalArgumentException(
                    "Expected Mekanism " + expected + " but found " + actual);
        }
    }

    static String requireRecipeId(RecipeInstance recipe, String recipeFamily) {
        String recipeId = recipe.recipeId();
        if (recipeId == null || recipeId.isBlank()) {
            throw new IllegalArgumentException(recipeFamily + " requires an explicit recipe ID");
        }
        return recipeId;
    }
}
