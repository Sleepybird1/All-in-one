package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.*;
import net.minecraft.tags.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.levelgen.structure.placement.StructurePlacement;
import net.neoforged.neoforge.gametest.*;

@GameTestHolder("ic_material_smoke")
@PrefixGameTestTemplate(false)
public final class GlacioAnglerTests {
    @GameTest(templateNamespace="ic_material_smoke",template="geology_smoke_empty",timeoutTicks=2400)
    @SuppressWarnings("unchecked")
    public static void habitatAndRelocation(GameTestHelper h) throws Exception {
        Path stage=Path.of(System.getProperty("ic.material.requireStageRoot"));
        if(!Files.exists(stage.resolve("glacio-anglers-migration.json"))){h.succeed();return;}
        var server=h.getLevel().getServer();
        var glacio=server.getLevel(ResourceKey.create(Registries.DIMENSION,ResourceLocation.parse("ad_astra:glacio")));
        h.assertTrue(glacio!=null,"Glacio not loaded");
        server.setDifficulty(Difficulty.NORMAL,true);
        var id=ResourceLocation.parse("cataclysm:deepling_angler");
        var type=(EntityType<Mob>)BuiltInRegistries.ENTITY_TYPE.get(id);
        Set<String> eligible=new HashSet<>();
        var biomes=glacio.registryAccess().registryOrThrow(Registries.BIOME);
        for(var biome:biomes) {
            if(biome.getMobSettings().getMobs(MobCategory.MONSTER).unwrap().stream().anyMatch(s->s.type==type))eligible.add(biomes.getKey(biome).toString());
        }
        h.assertTrue(eligible.equals(Set.of("ad_astra:glacio_ice_peaks","ad_astra:glacio_snowy_barrens")),"Angler biome leak: "+eligible);
        var cold=TagKey.create(Registries.ENTITY_TYPE,ResourceLocation.parse("ad_astra:can_survive_extreme_cold"));
        h.assertTrue(type.is(cold),"Angler lacks cold tolerance");
        h.assertTrue(BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.parse("cataclysm:lionfish")).is(cold),"Companion lacks cold tolerance");
        var migration=JsonParser.parseString(Files.readString(stage.resolve("glacio-anglers-migration.json"))).getAsJsonObject();
        int templates=0;
        for(String path:migration.getAsJsonObject("templates").keySet()) {
            String name=path.substring("data/cataclysm/structure/".length(),path.length()-4);
            var template=glacio.getStructureManager().get(ResourceLocation.parse("cataclysm:"+name)).orElseThrow();
            String nbt=template.save(new CompoundTag()).toString();
            h.assertTrue(!nbt.contains("deepling_angler")&&nbt.contains("deepling"),"City spawn replacement missing: "+name);
            templates++;
        }
        h.assertTrue(glacio.getChunkSource().getGenerator().getSeaLevel()==0,"Underground water table not applied");
        BlockPos site=null;int water=0;int chunks=0;
        Mob probe=type.create(glacio);
        search: for(int c=0;c<16;c++) {
            int cx=(c%4)*3,cz=(c/4)*3;
            var chunk=glacio.getChunk(cx,cz);chunks++;
            for(int y=-48;y<0;y++)for(int x=0;x<16;x++)for(int z=0;z<16;z++) {
                var pos=new BlockPos(cx*16+x,y,cz*16+z);
                if(!chunk.getFluidState(pos).is(FluidTags.WATER))continue;
                water++;
                if(!glacio.getFluidState(pos.above(2)).is(FluidTags.WATER)||glacio.canSeeSky(pos))continue;
                probe.moveTo(pos.getX()+.5,pos.getY(),pos.getZ()+.5,0,0);
                if(!probe.checkSpawnObstruction(glacio))continue;
                site=pos.immutable();
                if(water>=256)break search;
            }
        }
        h.assertTrue(site!=null&&water>=256,"No viable underground aquatic habitat; water="+water);
        var random=RandomSource.create(9122026);
        h.assertTrue(SpawnPlacements.checkSpawnRules(type,glacio,MobSpawnType.NATURAL,site,random),"Native aquatic spawn predicate rejects habitat");
        boolean passes=false;
        for(int i=0;i<300&&!passes;i++)passes=probe.checkSpawnRules(glacio,MobSpawnType.NATURAL);
        h.assertTrue(passes,"Angler's native random spawn rule never passes");
        var dry=site.above(150);
        h.assertTrue(!SpawnPlacements.checkSpawnRules(type,glacio,MobSpawnType.NATURAL,dry,random),"Anglers can spawn in dry surface air");
        probe.moveTo(site.getX()+.5,site.getY(),site.getZ()+.5,0,0);
        probe.setPersistenceRequired();probe.setNoAi(true);
        probe.finalizeSpawn(glacio,glacio.getCurrentDifficultyAt(site),MobSpawnType.NATURAL,null);
        h.assertTrue(glacio.addFreshEntity(probe),"Angler could not enter Glacio");
        final int sampledWater=water,sampledChunks=chunks,checkedTemplates=templates;
        final BlockPos spawn=site;
        float health=probe.getHealth();
        glacio.setChunkForced(site.getX()>>4,site.getZ()>>4,true);
        h.runAfterDelay(120,()->{
            // Entities in a just-generated, unticketed chunk are not visible to
            // spatial queries yet. Inspect the companion after ticket activation.
            var fish=glacio.getEntities(probe,probe.getBoundingBox().inflate(16),e->BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString().equals("cataclysm:lionfish"));
            h.assertTrue(probe.isAlive()&&probe.getHealth()==health,"Glacio damages its Angler resident");
            h.assertTrue(fish.size()==1&&fish.stream().allMatch(Entity::isAlive),"Native companion did not survive Glacio");
            var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("sampledWaterBlocks",sampledWater);report.addProperty("sampledChunks",sampledChunks);report.addProperty("habitatPosition",spawn.toShortString());report.addProperty("cityTemplates",checkedTemplates);report.addProperty("survivalTicks",120);
            try{Files.writeString(stage.resolve("glacio-anglers-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));}catch(Exception e){throw new RuntimeException(e);}
            probe.discard();fish.forEach(Entity::discard);glacio.setChunkForced(spawn.getX()>>4,spawn.getZ()>>4,false);
            System.out.println("GLACIO_ANGLERS_PASS biomes=2 earth=excluded templates=10 habitat=generated nativeSpawn=PASS companion=PASS survival=120");
            h.succeed();
        });
    }
}
