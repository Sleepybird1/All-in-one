package dev.godpc.industrialcolonies;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.zizazr.kjsgen.codegen.handlers.CreateSequencedAssemblyCodegen;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeDefinition;
import java.nio.charset.StandardCharsets;
import java.util.zip.ZipFile;

/** Plain-JVM test using installed KJSGen's actual model and exporter; no game launch. */
public final class KjsGenSequenceFluidCompatibilitySelfTest {
    private static int checks;

    public static void main(String[] args) throws Exception {
        RecipeTypeDefinition layout;
        try (var jar = new ZipFile(args[0])) {
            var entry = jar.getEntry("assets/kjsgen/kjsgen_layouts/create_sequenced_assembly.json");
            try (var stream = jar.getInputStream(entry)) {
                layout = RecipeTypeDefinition.fromJson(JsonParser.parseString(
                        new String(stream.readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject());
            }
        }
        var legacy = card("filling");
        var before = legacy.toJson().deepCopy();
        var adapted = KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(legacy, layout);
        check(adapted != legacy, "Legacy data must be copied, not modified");
        check(legacy.toJson().equals(before), "Original card JSON changed");
        check(adapted.slot("seqItem0").equals(legacy.slot("seqFluid0")), "Fluid content not copied exactly");
        String generated = new CreateSequencedAssemblyCodegen().generate(adapted, layout);
        check(generated.contains("Fluid.of('minecraft:water', 250)"), "Native exporter did not emit original water amount: " + generated);
        check(generated.contains("loops(2)") && generated.contains("2x tfmg:n_semiconductor"), "Loops/output changed");

        JsonObject canonicalJson = card("filling").toJson();
        canonicalJson.getAsJsonObject("slots").add("seqItem0", JsonParser.parseString(
                "{\"kind\":\"FLUID\",\"id\":\"minecraft:lava\",\"amount\":100}"));
        var canonical = RecipeInstance.fromJson(canonicalJson);
        check(KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(canonical, layout) == canonical,
                "Nonempty canonical content must win without copying");
        check(canonical.slot("seqItem0").id().equals("minecraft:lava"), "Canonical fluid overwritten");

        var deploying = card("deploying");
        check(KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(deploying, layout) == deploying,
                "A non-filling operation must not consume the legacy fluid slot");

        JsonObject missingJson = card("filling").toJson();
        missingJson.getAsJsonObject("slots").remove("seqFluid0");
        var missing = RecipeInstance.fromJson(missingJson);
        check(KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(missing, layout) == missing,
                "No fluid may be invented when both slots are empty");

        JsonObject tagJson = card("filling").toJson();
        tagJson.getAsJsonObject("slots").add("seqFluid0", JsonParser.parseString(
                "{\"kind\":\"FLUID_TAG\",\"id\":\"c:water\",\"amount\":500}"));
        var tag = RecipeInstance.fromJson(tagJson);
        var adaptedTag = KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(tag, layout);
        check(adaptedTag.slot("seqItem0").equals(tag.slot("seqFluid0")), "Fluid tag or amount changed");

        JsonObject badJson = card("filling").toJson();
        badJson.getAsJsonObject("slots").add("seqFluid0", JsonParser.parseString(
                "{\"kind\":\"ITEM\",\"id\":\"minecraft:iron_ingot\"}"));
        boolean rejected = false;
        try {
            KjsGenSequencedAssemblyIntegration.withCanonicalFillingSlots(RecipeInstance.fromJson(badJson), layout);
        } catch (IllegalArgumentException expected) {
            rejected = true;
        }
        check(rejected, "Malformed legacy item must not masquerade as fluid");
        System.out.println("KJSGEN_SEQUENCE_FLUID_COMPAT PASS checks=" + checks);
    }

    private static RecipeInstance card(String operation) {
        return RecipeInstance.fromJson(JsonParser.parseString("""
                {"uid":"4e630645-dd56-500d-a7d3-37d180e3abb8","type":"kjsgen:create_sequenced_assembly",
                 "recipeId":"industrial_colonies:electronics/n_semiconductor","replaceRecipe":false,
                 "slots":{"input":{"kind":"ITEM","id":"industrial_colonies:etched_silicon_wafer"},
                          "transitional":{"kind":"ITEM","id":"industrial_colonies:etched_silicon_wafer"},
                          "output0":{"kind":"ITEM","id":"tfmg:n_semiconductor","count":2},
                          "seqFluid0":{"kind":"FLUID","id":"minecraft:water","amount":250}},
                 "params":{"loops":"2","__seqLen":"1","seq0":"OPERATION"}}
                """.replace("OPERATION", operation)).getAsJsonObject());
    }

    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) throw new AssertionError(message);
    }
}
