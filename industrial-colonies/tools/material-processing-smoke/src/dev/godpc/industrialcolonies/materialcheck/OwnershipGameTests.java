package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.*;
import net.minecraft.world.item.crafting.*;
import dev.godpc.industrialcolonies.CreateRecipeStageGate;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.EntityBlock;
import net.neoforged.neoforge.gametest.*;

@GameTestHolder("ic_material_smoke")
@PrefixGameTestTemplate(false)
public final class OwnershipGameTests {
    @GameTest(templateNamespace="ic_material_smoke",template="geology_smoke_empty",timeoutTicks=2400)
    public static void ownershipAcceptance(GameTestHelper h) throws Exception {
        Path stage=Path.of(System.getProperty("ic.material.requireStageRoot"));
        Path spec=stage.resolve("ownership-migration.json");
        if(!Files.exists(spec)){h.succeed();return;}
        JsonObject migration=JsonParser.parseString(Files.readString(spec)).getAsJsonObject();
        var level=h.getLevel();var manager=level.getRecipeManager();
        var ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
        JsonObject dump=new JsonObject();
        for(var holder:manager.getRecipes()) {
            try {dump.add(holder.id().toString(),Recipe.CODEC.encodeStart(ops,holder.value()).getOrThrow());}
            catch(Exception ex){JsonObject error=new JsonObject();error.addProperty("encodeError",ex.toString());dump.add(holder.id().toString(),error);}
        }
        Files.writeString(stage.resolve("ownership-effective-recipes.json"),new GsonBuilder().setPrettyPrinting().create().toJson(dump));
        int found=0;
        for(String id:migration.getAsJsonObject("changed").keySet()) {
            var holder=manager.byKey(ResourceLocation.parse(id));
            h.assertTrue(holder.isPresent(),"Owned recipe missing after native export/policy: "+id);
            var recipe=holder.orElseThrow().value();
            h.assertTrue(!recipe.getResultItem(level.registryAccess()).isEmpty(),"Owned result missing: "+id);
            for(var ingredient:recipe.getIngredients())h.assertTrue(ingredient.isEmpty()||ingredient.getItems().length>0,"Unresolved ingredient: "+id);
            found++;
        }
        Set<String> blocked=Set.of("mekanism:crushing","immersiveengineering:crusher","modernfoundry:alloy","createmetallurgy:alloying","createmetallurgy:melting","createmetallurgy:casting_in_table","createmetallurgy:casting_in_basin","tfmg:casting","createmetallurgy:bulk_melting","createmetallurgy:entity_melting","createmetallurgy:grinding","mekanism:washing","createdieselgenerators:casting","immersiveengineering:alloy","nuclearcraft:manufactory","nuclearcraft:rock_crusher");
        Set<String> retired=new HashSet<>();migration.getAsJsonArray("retiredOutputs").forEach(e->retired.add(e.getAsString()));
        for(String tier:List.of("basic","advanced","elite","ultimate"))retired.add("mekanism:"+tier+"_crushing_factory");
        for(var holder:manager.getRecipes()) {
            String type=BuiltInRegistries.RECIPE_SERIALIZER.getKey(holder.value().getSerializer()).toString();
            h.assertTrue(!blocked.contains(type),"Competing processor survives: "+holder.id());
            var result=holder.value().getResultItem(level.registryAccess());
            if(result!=null&&!result.isEmpty())h.assertTrue(!retired.contains(BuiltInRegistries.ITEM.getKey(result.getItem()).toString()),"Retired machine survives: "+holder.id());
        }
        // These endpoints must remain present across both migrations.
        for(String path:List.of("prepared_silicon_wafer","etched_silicon_wafer","n_semiconductor","p_semiconductor"))
            h.assertTrue(manager.byKey(ResourceLocation.parse("industrial_colonies:electronics/"+path)).isPresent(),"Semiconductor endpoint lost: "+path);
        for(String path:List.of("molten_alloy","ingot_casting"))
            h.assertTrue(manager.byKey(ResourceLocation.parse("industrial_colonies:materials/yellorium/"+path)).isPresent(),"Downstream construction-metal endpoint lost: "+path);
        var plate=manager.byKey(ResourceLocation.parse("industrial_colonies:ownership/steel_sheet")).orElseThrow().value();
        for(String machine:List.of("create:mechanical_press","createcasing:weathered_iron_press","createcasing:copper_press")) {
            var block=BuiltInRegistries.BLOCK.get(ResourceLocation.parse(machine));
            var entity=((EntityBlock)block).newBlockEntity(BlockPos.ZERO,block.defaultBlockState());entity.setLevel(level);
            h.assertTrue(CreateRecipeStageGate.machineMatches(plate,entity)==machine.equals("createcasing:weathered_iron_press"),"Steel plate capability leak: "+machine);
        }
        if(Files.exists(stage.resolve("semiconductor-migration.json"))) {
            JsonObject semi=JsonParser.parseString(Files.readString(stage.resolve("semiconductor-migration.json"))).getAsJsonObject();
            for(var id:semi.getAsJsonArray("retired"))h.assertTrue(!dump.has(id.getAsString()),"Retired silicon shortcut survives: "+id);
            var owned=semi.getAsJsonObject("owned");
            for(var entry:dump.entrySet()) {
                var body=entry.getValue().getAsJsonObject();
                for(String key:List.of("result","results","output","outputs","item_output","item_outputs")) {
                    if(!body.has(key))continue;
                    String outputs=body.get(key).toString();
                    for(var owner:owned.entrySet())h.assertTrue(!outputs.contains("\""+owner.getKey()+"\"")||entry.getKey().equals(owner.getValue().getAsString()),"Semiconductor alternate output: "+entry.getKey());
                }
            }
            for(String path:List.of("prepared_silicon_wafer","n_semiconductor","p_semiconductor")) {
                if(path.equals("n_semiconductor")&&Files.exists(stage.resolve("advanced-semiconductor-migration.json")))continue;
                var body=dump.getAsJsonObject("industrial_colonies:electronics/"+path);
                String source=path.equals("prepared_silicon_wafer")?"industrial_colonies:high_purity_silicon":"industrial_colonies:etched_silicon_wafer";
                h.assertTrue(body.getAsJsonObject("ingredient").get("item").getAsString().equals(source),"Wrong wafer grade: "+path);
                h.assertTrue(body.get("loops").getAsInt()==2,"Wrong pass count: "+path);
                h.assertTrue(body.getAsJsonArray("results").get(0).getAsJsonObject().get("count").getAsInt()==2,"Wrong yield: "+path);
                if(!path.equals("prepared_silicon_wafer")) {
                    String dopant=path.startsWith("n_")?"industrial_colonies:phosphoric_acid":"nuclearcraft:boric_acid";
                    var feed=body.getAsJsonArray("sequence").get(0).getAsJsonObject().getAsJsonArray("ingredients").get(1).getAsJsonObject();
                    h.assertTrue(feed.get("fluid").getAsString().equals(dopant)&&feed.get("amount").getAsInt()==100,"Wrong dopant/count: "+path);
                    for(String banned:List.of("tfmg:capacitor_item","tfmg:sulfur_dust","minecraft:redstone"))h.assertTrue(!body.toString().contains(banned),"Old filler/dopant survives: "+path);
                }
                for(var step:body.getAsJsonArray("sequence")) {
                    var stepBody=step.getAsJsonObject();String type=stepBody.get("type").getAsString();
                    if(type.endsWith("filling"))continue;
                    String operation=type.substring(type.lastIndexOf('_')+1);
                    String suffix=switch(operation){case "cutting"->"mechanical_saw";case "pressing"->"press";case "deploying"->"deployer";default->throw new IllegalStateException(type);};
                    var decoded=Recipe.CODEC.parse(ops,stepBody).getOrThrow();
                    for(String tier:List.of("weathered_iron_","copper_","industrial_iron_")) {
                        String machine="createcasing:"+tier+suffix;
                        var block=BuiltInRegistries.BLOCK.get(ResourceLocation.parse(machine));
                        var entity=((EntityBlock)block).newBlockEntity(BlockPos.ZERO,block.defaultBlockState());entity.setLevel(level);
                        h.assertTrue(CreateRecipeStageGate.machineMatches(decoded,entity)==tier.equals("copper_"),"Semiconductor machine gate leak: "+machine);
                    }
                }
            }
            for(String id:List.of("industrial_colonies:electronics/etched_silicon_wafer","industrial_colonies:electronics/bootstrap_hydrogen_chloride")) {
                var body=dump.getAsJsonObject(id);
                h.assertTrue(body.get("type").getAsString().equals("tfmg:vat_machine_recipe")&&body.get("min_size").getAsInt()==3&&body.get("heat_requirement").getAsString().equals("heated")&&body.get("processing_time").getAsInt()==600,"Vat infrastructure lost: "+id);
            }
            System.out.println("SEMICONDUCTOR_ACCEPTANCE_PASS endpoints=4 retired=3 copperGates=PASS");
            if(Files.exists(stage.resolve("advanced-semiconductor-migration.json"))) {
                var advanced=dump.getAsJsonObject("industrial_colonies:electronics/n_semiconductor");
                h.assertTrue(advanced.getAsJsonObject("ingredient").get("item").getAsString().equals("industrial_colonies:annealed_silicon_wafer"),"Advanced wafer prerequisite lost");
                h.assertTrue((advanced.has("loops")?advanced.get("loops").getAsInt():1)==1&&advanced.getAsJsonArray("results").get(0).getAsJsonObject().get("count").getAsInt()==2,"Advanced wafer yield changed");
                for(String component:List.of("gold_bonding_wire","copper_contact_frame"))h.assertTrue(advanced.toString().contains("industrial_colonies:"+component),"Missing precision conductor "+component);
                var pattern=dump.getAsJsonObject("industrial_colonies:electronics/patterned_silicon_wafer");
                h.assertTrue(pattern.get("loops").getAsInt()==2&&pattern.toString().contains("precision_wafer_mask")&&pattern.toString().contains("tfmg:sulfuric_acid"),"Missing fine pattern layers");
                var anneal=dump.getAsJsonObject("industrial_colonies:electronics/annealed_silicon_wafer");
                h.assertTrue(anneal.get("heat_requirement").getAsString().equals("superheated")&&anneal.get("processing_time").getAsInt()==1200&&anneal.toString().contains("industrial_colonies:phosphoric_acid")&&anneal.toString().contains("tfmg:hydrogen"),"Missing annealing infrastructure");
                for(String path:List.of("n_semiconductor","patterned_silicon_wafer","gold_bonding_wire")) {
                    for(var step:dump.getAsJsonObject("industrial_colonies:electronics/"+path).getAsJsonArray("sequence")) {
                        var body=step.getAsJsonObject();String type=body.get("type").getAsString();if(type.endsWith("filling"))continue;
                        String operation=type.substring(type.lastIndexOf('_')+1);
                        String suffix=switch(operation){case "cutting"->"mechanical_saw";case "pressing"->"press";case "deploying"->"deployer";default->throw new IllegalStateException(type);};
                        var decoded=Recipe.CODEC.parse(ops,body).getOrThrow();
                        for(String tier:List.of("copper_","brass_","industrial_iron_")) {
                            var block=BuiltInRegistries.BLOCK.get(ResourceLocation.parse("createcasing:"+tier+suffix));
                            var entity=((EntityBlock)block).newBlockEntity(BlockPos.ZERO,block.defaultBlockState());entity.setLevel(level);
                            h.assertTrue(CreateRecipeStageGate.machineMatches(decoded,entity)==tier.equals("brass_"),"Advanced gate leak "+path+" "+tier+suffix);
                        }
                    }
                }
                var transistor=dump.getAsJsonObject("industrial_colonies:electronics/transistor");
                h.assertTrue(!transistor.toString().contains("tfmg:n_semiconductor")&&transistor.toString().contains("tfmg:p_semiconductor"),"Pink transistor bootstrap cycle");
                for(String path:List.of("precision_wafer_mask","copper_contact_frame","gold_bonding_wire"))h.assertTrue(dump.has("industrial_colonies:electronics/"+path),"Missing contact/mask route "+path);
                System.out.println("ADVANCED_SEMICONDUCTOR_PASS pink=Brass green=Copper bootstrap=PASS components=5");
            }
        }
        System.out.println("OWNERSHIP_ACCEPTANCE_PASS owned="+found+" effectiveRecipes="+manager.getRecipes().size()+" semiconductorEndpoints=4");
        if(Files.exists(stage.resolve("metal-unit-migration.json"))) {
            var unitPolicy=JsonParser.parseString(Files.readString(stage.resolve("closure-policy.json"))).getAsJsonObject();
            int checked=0,blocksChecked=0;
            for(var e:dump.entrySet()) {
                var b=e.getValue().getAsJsonObject();
                if(!b.has("type")||!List.of("modernfoundry:casting_table","modernfoundry:casting_basin").contains(b.get("type").getAsString()))continue;
                var holder=manager.byKey(ResourceLocation.parse(e.getKey())).orElseThrow();
                var result=holder.value().getResultItem(level.registryAccess());
                if(result==null||result.isEmpty()||!b.has("fluid"))continue;
                String item=BuiltInRegistries.ITEM.getKey(result.getItem()).toString();
                // Cast molds and cheese ingots are not metal units. Use the actual
                // supported item/tag inventory rather than matching "ingot" in names.
                int unit=unitPolicy.getAsJsonObject("ingots").has(item)?100:unitPolicy.getAsJsonObject("nuggets").has(item)?10:0;
                var blockValue=unitPolicy.getAsJsonObject("finishedValues").getAsJsonObject(item);
                if(Files.exists(stage.resolve("block-unit-migration.json"))&&blockValue!=null&&blockValue.get("amount").getAsInt()==1000)unit=1000;
                if(unit==0)continue;
                var fluid=b.getAsJsonObject("fluid");
                String fluidRef=fluid.has("fluid")?fluid.get("fluid").getAsString():fluid.has("tag")?"#"+fluid.get("tag").getAsString():"";
                var fluidMetal=unitPolicy.getAsJsonObject("fluidMetals").get(fluidRef);
                var itemValue=unitPolicy.getAsJsonObject("finishedValues").getAsJsonObject(item);
                // Andesite-alloy casting and netherite scrap consume a different
                // material fraction; they are not a same-metal ingot casting.
                if(fluidMetal==null||itemValue==null||!fluidMetal.getAsString().equals(itemValue.get("metal").getAsString()))continue;
                int amount=b.getAsJsonObject("fluid").get("amount").getAsInt();
                h.assertTrue(amount==unit*result.getCount(),"Inconsistent casting units: "+e.getKey()+" amount="+amount+" output="+result);
                checked++;
                if(unit==1000)blocksChecked++;
            }
            for(var pair:Map.of("iron/direct_hematite",3,"iron/reduced",8,"gold/flake",1,"raw/iron",25).entrySet()) {
                var b=dump.getAsJsonObject("industrial_colonies:processing/"+pair.getKey());
                h.assertTrue(b.getAsJsonObject("result").get("amount").getAsInt()==pair.getValue(),"Incorrect rounded ore yield: "+pair.getKey());
            }
            h.assertTrue(checked>60,"Insufficient casting coverage: "+checked);
            h.assertTrue(dump.getAsJsonObject("modernfoundry:smeltery/casting/metal/netherite/scrap_sand_cast").getAsJsonObject("fluid").get("amount").getAsInt()==100,"Molten debris alias retains native 90 mB scrap units");
            System.out.println("METAL_UNIT_ACCEPTANCE_PASS casting="+checked+" ingot=100 nugget=10 hematite=3 reducedIron=8");
            if(Files.exists(stage.resolve("block-unit-migration.json"))) {
                h.assertTrue(blocksChecked>20,"Insufficient bucket-block casting coverage: "+blocksChecked);
                System.out.println("BUCKET_BLOCK_ACCEPTANCE_PASS blocks="+blocksChecked+" block=1000 ingot=100");
            }
        }
        StructureCleanupChecks.run(h,stage);
        VillageDistributionChecks.run(h,stage);
        GlobalLandmarkChecks.run(h,stage);
        IronBlastChecks.run(h);
        OreRecoveryChecks.run(h,stage);
        h.succeed();
    }
}

