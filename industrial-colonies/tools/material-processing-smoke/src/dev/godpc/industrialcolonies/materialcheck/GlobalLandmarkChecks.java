package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.placement.*;

public final class GlobalLandmarkChecks {
    public static void run(GameTestHelper h,Path stage) throws Exception {
        var spec=JsonParser.parseString(Files.readString(stage.resolve("global-landmarks-migration.json"))).getAsJsonObject();
        var access=h.getLevel().registryAccess();var sets=access.registryOrThrow(Registries.STRUCTURE_SET);
        var ops=RegistryOps.create(JsonOps.INSTANCE,access);
        var shared=sets.get(ResourceLocation.parse("industrial_colonies:global_landmarks"));
        Map<String,Integer> actual=new TreeMap<>(),expected=new TreeMap<>();
        shared.structures().forEach(e->actual.put(e.structure().unwrapKey().orElseThrow().location().toString(),e.weight()));
        spec.getAsJsonObject("weights").entrySet().forEach(e->expected.put(e.getKey(),e.getValue().getAsInt()));
        h.assertTrue(actual.equals(expected),"Global pool altered by native injection");
        if(expected.containsKey("industrial_colonies:stellaris_overworld_meteor")) {
            var structures=access.registryOrThrow(Registries.STRUCTURE);
            var nativeMeteor=structures.get(ResourceLocation.parse("stellaris:meteor"));
            var overworldMeteor=structures.get(ResourceLocation.parse("industrial_colonies:stellaris_overworld_meteor"));
            h.assertTrue(nativeMeteor.biomes().size()>0,"Off-world meteor eligibility lost");
            h.assertTrue(nativeMeteor.biomes().stream().noneMatch(b->b.is(net.minecraft.tags.BiomeTags.IS_OVERWORLD)),"Independent Stellaris meteor still allows Overworld");
            h.assertTrue(overworldMeteor.biomes().size()>0&&overworldMeteor.biomes().stream().allMatch(b->b.is(net.minecraft.tags.BiomeTags.IS_OVERWORLD)),"Pooled meteor dimension eligibility incorrect");
        }
        var encoded=StructurePlacement.CODEC.encodeStart(ops,shared.placement()).getOrThrow().getAsJsonObject();
        for(var e:spec.getAsJsonObject("placement").entrySet())h.assertTrue(encoded.get(e.getKey()).equals(e.getValue()),"Global placement mismatch "+e.getKey());
        Set<String> targets=new HashSet<>(expected.keySet());
        spec.getAsJsonArray("disabledIslands").forEach(e->targets.add(e.getAsString()));
        for(var set:sets) {
            if(set==shared||set.structures().stream().noneMatch(e->targets.contains(e.structure().unwrapKey().orElseThrow().location().toString())))continue;
            var p=StructurePlacement.CODEC.encodeStart(ops,set.placement()).getOrThrow().getAsJsonObject();
            h.assertTrue(p.has("frequency")&&p.get("frequency").getAsDouble()==0,"Independent landmark set active: "+sets.getKey(set));
        }
        var placement=(RandomSpreadStructurePlacement)shared.placement();
        int minimum=Integer.MAX_VALUE;
        for(long seed:new long[]{0,19420811L,-183741L}) {
            List<ChunkPos> samples=new ArrayList<>();
            for(int x=-8;x<=8;x++)for(int z=-8;z<=8;z++)samples.add(placement.getPotentialStructureChunk(seed,x*placement.spacing(),z*placement.spacing()));
            for(int i=0;i<samples.size();i++)for(int j=i+1;j<samples.size();j++) {
                var a=samples.get(i);var b=samples.get(j);int distance=Math.max(Math.abs(a.x-b.x),Math.abs(a.z-b.z))*16;
                minimum=Math.min(minimum,distance);h.assertTrue(distance>=4096,"Global sites too close");
            }
        }
        for(String id:List.of("minecraft:mineshaft","minecraft:mineshaft_mesa","minecraft:stronghold","block_factorys_bosses:dragon_tower"))h.assertTrue(!expected.containsKey(id),"Protected placement moved into global pool: "+id);
        var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("entries",actual.size());report.addProperty("minimumSampledOriginDistanceBlocks",minimum);report.addProperty("guaranteedOriginSeparationBlocks",placement.separation()*16);report.addProperty("sampledSeeds",3);
        Files.writeString(stage.resolve("global-landmarks-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
        System.out.println("GLOBAL_LANDMARKS_PASS shared="+actual.size()+" minimum=4096 independent=disabled islands=disabled");
    }
}
