package dev.godpc.industrialcolonies.terraincheck;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import java.lang.reflect.Proxy;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Development only: effective registry/guard acceptance, without block writes or forced chunks. */
@GameTestHolder("ic_lithosphere_smoke")
@PrefixGameTestTemplate(false)
public final class LithosphereCompatibilityGameTests {
    private static final List<String> ECONOMIC=List.of("ore_coal_windswept","ore_diamond_volcanic",
            "ore_gold_volcanic","ore_iron_windswept","ore_redstone_windswept");
    private LithosphereCompatibilityGameTests() {}

    @GameTest(templateNamespace="ic_lithosphere_smoke",template="geology_smoke_empty",timeoutTicks=400)
    public static void effectiveWwooSuppression(GameTestHelper helper) throws Exception {
        var level=helper.getLevel();
        Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
        String destination=System.getProperty("ic.lithosphere.report");
        helper.assertTrue(destination!=null&&!destination.isBlank(),"ic.lithosphere.report is required");
        Path reportPath=Path.of(destination).toAbsolutePath().normalize();
        helper.assertTrue(reportPath.startsWith(stage)&&!reportPath.equals(stage),"Compatibility report escapes stage");
        JsonObject report=new JsonObject();report.addProperty("status","RUNNING");
        try {
            helper.assertTrue(ModList.get().isLoaded("mr_lithosphere")&&ModList.get().isLoaded("wwoo")
                    &&ModList.get().isLoaded("cristellib")&&!ModList.get().isLoaded("tectonic"),"Wrong terrain compatibility mod set");
            helper.assertTrue(level.getMinBuildHeight()==-64&&level.getMaxBuildHeight()==512,"Lithosphere 576-block dimension not active");
            helper.assertTrue(GeologyConfig.suppressDefaultOres(),"Suppression is disabled");
            helper.assertTrue(GeologyConfig.families("minecraft:pale_garden").equals(Set.of("ordinary_forest")),"Pale Garden mapping differs from ordinary forest");
            var features=level.registryAccess().registryOrThrow(Registries.PLACED_FEATURE);
            var biomes=level.registryAccess().registryOrThrow(Registries.BIOME);
            var forbidden=TagKey.create(Registries.PLACED_FEATURE,ResourceLocation.parse("industrial_colonies:geology/default_ore_features"));
            Set<ResourceLocation> ids=new HashSet<>();
            // A missing/failed guard cannot write anything: only its registry/context reads are permitted.
            WorldGenLevel guarded=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(proxy,method,args)->{
                if(method.getName().equals("getLevel"))return level;
                if(method.getName().equals("registryAccess"))return level.registryAccess();
                if(method.getName().equals("toString"))return "IC WWOO no-write guard probe";
                throw new IllegalStateException("Suppressed WWOO feature attempted world access: "+method.getName());
            });
            for(String name:ECONOMIC){
                var id=ResourceLocation.parse("wythers:ores/"+name);ids.add(id);
                PlacedFeature feature=features.get(id);
                helper.assertTrue(feature!=null,"Missing actual WWOO placed feature "+id);
                var holder=features.getResourceKey(feature).flatMap(features::getHolder).orElseThrow();
                helper.assertTrue(holder.is(forbidden),"WWOO economic source missing from loaded suppression tag: "+id);
                helper.assertFalse(feature.place(guarded,level.getChunkSource().getGenerator(),RandomSource.create(17),BlockPos.ZERO),"Direct placement escaped guard: "+id);
                helper.assertFalse(feature.placeWithBiomeCheck(guarded,level.getChunkSource().getGenerator(),RandomSource.create(17),BlockPos.ZERO),"Biome-checked placement escaped guard: "+id);
            }
            int inspected=0;
            for(var biome:biomes){
                var holder=biomes.getResourceKey(biome).flatMap(biomes::getHolder).orElseThrow();
                if(!holder.is(BiomeTags.IS_OVERWORLD))continue;
                inspected++;
                for(var step:biome.getGenerationSettings().features())for(var feature:step)
                    helper.assertFalse(feature.unwrapKey().map(k->ids.contains(k.location())).orElse(false),"Economic WWOO feature survived Overworld biome removal");
            }
            var lava=features.get(ResourceLocation.parse("wythers:ores/ore_lava_volcanic"));
            helper.assertTrue(lava!=null,"Non-resource volcanic lava feature removed from registry");
            helper.assertFalse(features.getResourceKey(lava).flatMap(features::getHolder).orElseThrow().is(forbidden),"Non-resource volcanic lava was suppressed");
            JsonObject sourceManifest;
            try(var input=GeologyConfig.class.getResourceAsStream("/resourcepacks/ic_wwoo_decorative/source_manifest.json")){
                helper.assertTrue(input!=null,"Candidate lacks the decorative source manifest");
                sourceManifest=JsonParser.parseReader(new InputStreamReader(input,StandardCharsets.UTF_8)).getAsJsonObject();
            }
            JsonArray decorativeEvidence=new JsonArray();
            for(var entry:sourceManifest.getAsJsonArray("resources")){
                var expected=entry.getAsJsonObject();var resourceId=ResourceLocation.parse(expected.get("resource").getAsString());
                var resource=level.getServer().getResourceManager().getResource(resourceId).orElseThrow();
                helper.assertTrue(resource.sourcePackId().contains("ic_wwoo_decorative"),"Decorative compatibility pack lost resource priority: "+resourceId+" -> "+resource.sourcePackId());
                String hash;try(var input=resource.open()){hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(input.readAllBytes()));}
                helper.assertTrue(hash.equalsIgnoreCase(expected.get("sha256").getAsString()),"Effective decorative definition differs from original vanilla bytes: "+resourceId);
                JsonObject evidence=new JsonObject();evidence.addProperty("resource",resourceId.toString());
                evidence.addProperty("sourcePack",resource.sourcePackId());evidence.addProperty("sha256",hash);decorativeEvidence.add(evidence);
            }
            helper.assertTrue(decorativeEvidence.size()==12,"Expected exactly 12 decorative resource overrides");
            // removeOres stays true in this accepted pack; its separate lava-spring policy is preserved.
            for(String name:List.of("spring_lava","spring_lava_frozen")){
                var resource=level.getServer().getResourceManager().getResource(ResourceLocation.parse("minecraft:worldgen/placed_feature/"+name+".json")).orElseThrow();
                helper.assertTrue(resource.sourcePackId().contains("wwoo_remove_ores"),"Lava policy provider changed: "+name);
                try(var reader=new InputStreamReader(resource.open(),StandardCharsets.UTF_8)){
                    var json=JsonParser.parseReader(reader).getAsJsonObject();
                    helper.assertTrue(json.getAsJsonArray("placement").get(0).getAsJsonObject().get("count").getAsInt()==0,"WWOO lava-spring count changed: "+name);
                }
            }
            report.addProperty("status","PASS");report.addProperty("economicFeaturesChecked",5);
            report.addProperty("directGuardCalls",10);report.addProperty("overworldBiomesInspected",inspected);
            report.addProperty("lavaFeatureRetained",true);report.addProperty("paleGardenFamily","ordinary_forest");
            report.add("decorativeResourcePriority",decorativeEvidence);report.addProperty("wwooLavaSpringPolicyPreserved",true);
            report.addProperty("minimumBuildHeight",-64);report.addProperty("maximumBuildHeight",512);
            report.addProperty("scope","Effective registry/tag/biome removal plus actual no-write placement guards. No forced chunk, no block writes, no world distribution certification.");
            LogUtils.getLogger().info("GEOLOGY_LITHOSPHERE_COMPAT PASS features=5 guardCalls=10 overworldBiomes={}",inspected);
        } catch(Exception error){report.addProperty("status","FAIL");report.addProperty("failure",error.toString());throw error;}
        finally {Files.writeString(reportPath,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);}
        helper.succeed();
    }
}
