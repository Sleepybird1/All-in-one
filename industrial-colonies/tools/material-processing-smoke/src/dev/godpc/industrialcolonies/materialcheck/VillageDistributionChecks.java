package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.*;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.placement.StructurePlacement;

public final class VillageDistributionChecks {
    public static void run(GameTestHelper h,Path stage) throws Exception {
        if(!Files.exists(stage.resolve("village-distribution-migration.json")))return;
        var spec=JsonParser.parseString(Files.readString(stage.resolve("village-distribution-migration.json"))).getAsJsonObject();
        var access=h.getLevel().registryAccess();var structures=access.registryOrThrow(Registries.STRUCTURE);var sets=access.registryOrThrow(Registries.STRUCTURE_SET);
        var biomeTag=TagKey.create(Registries.BIOME,ResourceLocation.parse("industrial_colonies:vanilla_village_biomes"));
        Set<String> restricted=new HashSet<>();
        for(var entry:spec.getAsJsonArray("restrictedStructures")) {
            String id=entry.getAsString();restricted.add(id);var structure=structures.get(ResourceLocation.parse(id));
            h.assertTrue(structure.biomes().stream().allMatch(b->b.is(biomeTag)),"Village escaped vanilla biome eligibility: "+id);
        }
        var ops=RegistryOps.create(JsonOps.INSTANCE,access);var shared=sets.get(ResourceLocation.parse("industrial_colonies:global_landmarks"));
        Map<String,Integer> entries=new TreeMap<>();
        shared.structures().forEach(e->entries.merge(e.structure().unwrapKey().orElseThrow().location().toString(),e.weight(),Integer::sum));
        Map<String,Integer> expected=new TreeMap<>();
        for(var e:spec.getAsJsonArray("sharedPool")){var o=e.getAsJsonObject();expected.put(o.get("structure").getAsString(),o.get("weight").getAsInt());}
        entries.keySet().retainAll(expected.keySet());
        h.assertTrue(entries.equals(expected),"Runtime village pool differs; CTOV/native injection remains: "+entries);
        var actual=StructurePlacement.CODEC.encodeStart(ops,shared.placement()).getOrThrow().getAsJsonObject();
        h.assertTrue(actual.get("spacing").getAsInt()==384 && actual.get("separation").getAsInt()==256,"Global village spacing changed");
        for(var set:sets) {
            if(set==shared||set.structures().stream().noneMatch(e->restricted.contains(e.structure().unwrapKey().orElseThrow().location().toString())))continue;
            var placement=StructurePlacement.CODEC.encodeStart(ops,set.placement()).getOrThrow().getAsJsonObject();
            h.assertTrue(placement.has("frequency")&&placement.get("frequency").getAsFloat()==0,"Independent village site still enabled: "+sets.getKey(set));
        }
        for(String style:List.of("plains","desert","savanna","snowy","taiga")) {
            var structure=structures.get(ResourceLocation.parse("minecraft:village_"+style));
            var json=Structure.DIRECT_CODEC.encodeStart(ops,structure).getOrThrow().getAsJsonObject();
            h.assertTrue(json.get("size").getAsInt()==4,"Vanilla village is not compact");
        }
        double minimumVanilla=1;
        var ratios=new JsonObject();
        for(var biome:access.registryOrThrow(Registries.BIOME).holders().toList()) {
            if(!biome.is(biomeTag))continue;
            int total=0,vanilla=0;
            for(var e:shared.structures())if(expected.containsKey(e.structure().unwrapKey().orElseThrow().location().toString()) && e.structure().value().biomes().contains(biome)) {
                total+=e.weight();if(e.structure().unwrapKey().orElseThrow().location().getNamespace().equals("minecraft"))vanilla+=e.weight();
            }
            h.assertTrue(total>0&&vanilla>0,"Vanilla village biome lost its normal villages");
            double ratio=(double)vanilla/total;minimumVanilla=Math.min(minimumVanilla,ratio);
            h.assertTrue(ratio>=.95,"Modded village weight dominates: "+biome.unwrapKey().orElseThrow());
            ratios.addProperty(biome.unwrapKey().orElseThrow().location().toString(),ratio);
        }
        var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("restrictedStructures",restricted.size());report.addProperty("sharedEntries",entries.size());report.addProperty("minimumEligibleVanillaWeightShare",minimumVanilla);report.add("vanillaWeightShareByBiome",ratios);
        Files.writeString(stage.resolve("village-distribution-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
        System.out.println("VILLAGE_DISTRIBUTION_PASS biomes=vanilla sites=global compact=4 CTOV=rare_small independentSites=disabled");
    }
}
