package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.nio.file.*;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.Recipe;

public final class OreRecoveryChecks {
    public static void run(GameTestHelper h,Path stage) throws Exception {
        var spec=JsonParser.parseString(Files.readString(stage.resolve("ore-yields-migration.json"))).getAsJsonObject();
        var ops=RegistryOps.create(JsonOps.INSTANCE,h.getLevel().registryAccess());
        var manager=h.getLevel().getRecipeManager();
        for(var e:spec.getAsJsonObject("meltAmounts").entrySet()) {
            var recipe=manager.byKey(ResourceLocation.parse("industrial_colonies:processing/"+e.getKey())).orElseThrow().value();
            var json=Recipe.CODEC.encodeStart(ops,recipe).getOrThrow().getAsJsonObject();
            h.assertTrue(json.getAsJsonObject("result").get("amount").getAsInt()==e.getValue().getAsInt(),"Ore yield policy overwritten: "+e.getKey());
        }
        for(String metal:new String[]{"iron","copper","gold","zinc"}) {
            var raw=manager.byKey(ResourceLocation.parse("industrial_colonies:processing/raw/"+metal)).orElseThrow().value();
            var block=manager.byKey(ResourceLocation.parse("industrial_colonies:processing/raw/"+metal+"_block")).orElseThrow().value();
            var a=Recipe.CODEC.encodeStart(ops,raw).getOrThrow().getAsJsonObject();var b=Recipe.CODEC.encodeStart(ops,block).getOrThrow().getAsJsonObject();
            h.assertTrue(a.getAsJsonObject("result").get("amount").getAsInt()*9==b.getAsJsonObject("result").get("amount").getAsInt(),"Raw block changes metal value: "+metal);
        }
        for(String metal:new String[]{"copper","zinc"}) {
            var crushing=(com.simibubi.create.content.processing.recipe.ProcessingRecipe<?,?>)manager.byKey(ResourceLocation.parse("industrial_colonies:processing/"+metal+"/crush_rich_raw")).orElseThrow().value();
            var melt=manager.byKey(ResourceLocation.parse("industrial_colonies:processing/"+(metal.equals("copper")?"copper/dust":"zinc/melt_recovered_dust"))).orElseThrow().value();
            int portion=Recipe.CODEC.encodeStart(ops,melt).getOrThrow().getAsJsonObject().getAsJsonObject("result").get("amount").getAsInt();
            h.assertTrue(crushing.getRollableResults().size()==1&&crushing.getRollableResults().getFirst().getStack().getCount()*portion==spec.getAsJsonObject("richRawRecovery").get(metal).getAsInt(),"Rich ore recovery mismatch: "+metal);
        }
        var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("changedOreRecipes",spec.getAsJsonArray("changed").size());report.addProperty("newRoutes",spec.getAsJsonArray("added").size());
        Files.writeString(stage.resolve("ore-yields-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
        System.out.println("ORE_RECOVERY_PASS rawBlocks=9x materialSpecific=true changed="+spec.getAsJsonArray("changed").size());
    }
}
