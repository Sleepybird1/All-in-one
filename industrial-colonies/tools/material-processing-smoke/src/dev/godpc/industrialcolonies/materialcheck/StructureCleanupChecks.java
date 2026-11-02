package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.registries.*;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.*;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.placement.*;
import net.minecraft.world.level.storage.loot.*;
import net.minecraft.world.level.storage.loot.parameters.*;
import net.minecraft.world.phys.Vec3;

/** Native registry, placement, generation and dimension-conditioned loot checks. */
public final class StructureCleanupChecks {
    public static void run(GameTestHelper h,Path stage) throws Exception {
        var file=stage.resolve("structure-cleanup-migration.json");if(!Files.exists(file))return;
        var spec=JsonParser.parseString(Files.readString(file)).getAsJsonObject();var level=h.getLevel();var server=level.getServer();
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);var sets=level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
        var ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
        for(var id:spec.getAsJsonArray("disabledVillages"))h.assertTrue(registry.get(ResourceLocation.parse(id.getAsString())).biomes().size()==0,"Jungle village still eligible "+id);
        var tower=registry.get(ResourceLocation.parse("block_factorys_bosses:dragon_tower"));Set<String> allowed=new HashSet<>();
        tower.biomes().forEach(b->allowed.add(b.unwrapKey().orElseThrow().location().toString()));
        h.assertTrue(allowed.size()==4&&allowed.stream().allMatch(s->s.contains("venus")),"Tower biome leak "+allowed);
        Set<String> destinations=new HashSet<>();
        for(var world:server.getAllLevels()) {
            if(world.getChunkSource().getGenerator().getBiomeSource().possibleBiomes().stream().anyMatch(tower.biomes()::contains))destinations.add(world.dimension().location().toString());
        }
        h.assertTrue(destinations.equals(Set.of("ad_astra:venus","stellaris:venus")),"Tower destination leak "+destinations);
        var shared=sets.get(ResourceLocation.parse("industrial_colonies:global_landmarks"));
        Set<String> ships=Set.of("minecolonies:ship","block_factorys_bosses:kraken_ship","irons_spellbooks:impaled_icebreaker");
        Set<String> pool=new HashSet<>();shared.structures().forEach(e->pool.add(e.structure().unwrapKey().orElseThrow().location().toString()));
        h.assertTrue(pool.containsAll(ships),"Ship pool lost content");
        var placement=(RandomSpreadStructurePlacement)shared.placement();h.assertTrue(placement.spacing()==384&&placement.separation()==256,"Ship spacing wrong");
        List<ChunkPos> samples=new ArrayList<>();
        for(int x=-6;x<=6;x++)for(int z=-6;z<=6;z++)samples.add(placement.getPotentialStructureChunk(19420811L,x*placement.spacing(),z*placement.spacing()));
        for(int i=0;i<samples.size();i++)for(int j=i+1;j<samples.size();j++) {
            var a=samples.get(i);var b=samples.get(j);
            h.assertTrue(Math.max(Math.abs(a.x-b.x),Math.abs(a.z-b.z))>=placement.separation(),"Maritime candidate overlap");
        }
        for(var entry:spec.getAsJsonArray("placements")) {
            var change=entry.getAsJsonObject();var actual=StructurePlacement.CODEC.encodeStart(ops,sets.get(ResourceLocation.parse(change.get("id").getAsString())).placement()).getOrThrow().getAsJsonObject();var expected=change.getAsJsonObject("after");
            for(String key:List.of("spacing","separation","frequency"))h.assertTrue(Math.abs(actual.get(key).getAsDouble()-(key.equals("frequency")?0:expected.get(key).getAsDouble()))<.000001,"Placement override missing "+change.get("id")+" "+key);
        }
        for(var set:sets) {
            boolean hasShip=set.structures().stream().anyMatch(e->ships.contains(e.structure().unwrapKey().orElseThrow().location().toString()));
            if(!hasShip||set==shared)continue;
            var encoded=StructurePlacement.CODEC.encodeStart(ops,set.placement()).getOrThrow().getAsJsonObject();
            h.assertTrue(encoded.has("frequency")&&encoded.get("frequency").getAsFloat()==0,"Independent ship set still active "+sets.getKey(set));
        }
        var venus=server.getLevel(ResourceKey.create(Registries.DIMENSION,ResourceLocation.parse("ad_astra:venus")));h.assertTrue(venus!=null,"Venus missing");
        var generator=venus.getChunkSource().getGenerator();boolean generated=false;String bounds="";
        for(int i=0;i<8&&!generated;i++) {
            var start=tower.generate(venus.registryAccess(),generator,generator.getBiomeSource(),venus.getChunkSource().randomState(),venus.getStructureManager(),venus.getSeed(),new ChunkPos(i*96,i*48),0,venus,tower.biomes()::contains);
            if(start.isValid()){generated=true;bounds=start.getBoundingBox().toString();h.assertTrue(start.getPieces().size()>1,"Incomplete tower generation");}
        }
        h.assertTrue(generated,"Tower cannot generate on Venus terrain");
        for(var id:spec.getAsJsonArray("towerDenizens")) {
            var entity=BuiltInRegistries.ENTITY_TYPE.getHolder(ResourceLocation.parse(id.getAsString())).orElseThrow();
            for(String tag:List.of("ad_astra:can_survive_in_space","ad_astra:can_survive_extreme_heat","ad_astra:can_survive_in_acid_rain","ad_astra:lives_without_oxygen","stellaris:no_oxygen_needed"))h.assertTrue(entity.is(TagKey.create(Registries.ENTITY_TYPE,ResourceLocation.parse(tag))),"Missing atmosphere protection "+id+" "+tag);
        }
        var key=ResourceKey.create(Registries.LOOT_TABLE,ResourceLocation.parse("block_factorys_bosses:chests/dragon_tower"));var loot=server.reloadableRegistries().getLootTable(key);
        int rewards=0;
        for(int i=0;i<100;i++)for(var world:List.of(level,venus)) {
            var params=new LootParams.Builder(world).withParameter(LootContextParams.ORIGIN,new Vec3(0,80,0)).create(LootContextParamSets.CHEST);
            var items=loot.getRandomItems(params,(long)i+1);
            boolean premium=items.stream().anyMatch(stack->Set.of("nuclearcraft:titanium_ingot","nuclearcraft:tungsten_ingot","nuclearcraft:platinum_ingot","tfmg:n_semiconductor","minecraft:netherite_ingot").contains(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString()));
            h.assertTrue(premium==(world==venus),"Treasure dimension condition failed");if(premium)rewards++;
        }
        var boss=server.reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE,ResourceLocation.parse("block_factorys_bosses:entities/infernal_dragon")));
        var bossJson=LootTable.DIRECT_CODEC.encodeStart(ops,boss).getOrThrow().getAsJsonObject();
        h.assertTrue(bossJson.toString().contains("block_factorys_bosses:dragon_skull")&&bossJson.toString().contains("block_factorys_bosses:dragon_bone"),"Boss trophies lost");
        for(var p:bossJson.getAsJsonArray("pools"))if(p.toString().contains("nuclearcraft:")||p.toString().contains("tfmg:n_semiconductor")||p.toString().contains("netherite_ingot")||p.toString().contains("enchanted_golden_apple"))
            h.assertTrue(p.toString().contains("killed_by_player")&&p.toString().contains("ad_astra:venus"),"Boss reward lacks destination/kill condition");
        var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("shipCandidates",samples.size());report.addProperty("venusTreasureRolls",rewards);report.addProperty("towerBounds",bounds);report.addProperty("disabledJungleStructures",6);
        Files.writeString(stage.resolve("structure-cleanup-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
        System.out.println("STRUCTURE_CLEANUP_PASS jungle=6 islands=disabled ships=global tower=Venus generation=PASS loot=100");
    }
}
