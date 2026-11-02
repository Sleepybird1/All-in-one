package dev.godpc.industrialcolonies.materialcheck;

import com.google.gson.*;
import java.nio.file.*;
import java.util.*;
import dev.godpc.industrialcolonies.worldgen.SurfaceStructureTerrain;
import dev.godpc.industrialcolonies.worldgen.SurfaceStructureTerrain.Ground;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.*;
import net.neoforged.neoforge.gametest.*;

@GameTestHolder("ic_material_smoke")
@PrefixGameTestTemplate(false)
public final class SurfaceTerrainTests {
    @GameTest(templateNamespace="ic_material_smoke",template="geology_smoke_empty",timeoutTicks=2400)
    public static void dryLevelFootprints(GameTestHelper h) throws Exception {
        Path stage=Path.of(System.getProperty("ic.material.requireStageRoot"));
        if(!Files.exists(stage.resolve("surface-terrain-migration.json"))){h.succeed();return;}
        var box=new BoundingBox(-20,40,-20,44,80,44);
        h.assertTrue(SurfaceStructureTerrain.fits(box,(x,z)->new Ground(64,false)),"Flat land rejected");
        h.assertTrue(!SurfaceStructureTerrain.fits(box,(x,z)->new Ground(64,x==3&&z==7)),"One-column interior water missed");
        h.assertTrue(!SurfaceStructureTerrain.fits(box,(x,z)->new Ground(x<3?64:70,false)),"Steep ledge accepted");
        h.assertTrue(!SurfaceStructureTerrain.fits(box,(x,z)->new Ground(64+Math.floorDiv(x+21,5),false)),"Sloped hillside accepted");
        h.assertTrue(SurfaceStructureTerrain.fits(box,(x,z)->new Ground(64+Math.floorDiv(x+21,16),false)),"Gentle level site rejected");
        var summitBox=new BoundingBox(-12,400,-12,12,441,12);
        h.assertTrue(SurfaceStructureTerrain.summit(summitBox,(x,z)->new Ground(400-Math.max(0,Math.max(Math.abs(x),Math.abs(z))-20),false),63),"Supported summit rejected");
        h.assertTrue(!SurfaceStructureTerrain.summit(summitBox,(x,z)->new Ground(400,false),63),"High flat plain mistaken for summit");
        h.assertTrue(!SurfaceStructureTerrain.summit(summitBox,(x,z)->new Ground(400+x,false),63),"Mountain shoulder accepted as summit");
        var level=h.getLevel();var access=level.registryAccess();var random=level.getChunkSource().randomState();
        var registry=access.registryOrThrow(Registries.STRUCTURE);
        var surfaceChunk=new net.minecraft.world.level.chunk.ProtoChunk(new ChunkPos(0,0),
                net.minecraft.world.level.chunk.UpgradeData.EMPTY,
                net.minecraft.world.level.LevelHeightAccessor.create(-64,864),access.registryOrThrow(Registries.BIOME),null);
        var peat=net.minecraft.core.registries.BuiltInRegistries.BLOCK.get(ResourceLocation.parse("regions_unexplored:peat_grass_block")).defaultBlockState();
        h.assertTrue(dev.godpc.industrialcolonies.worldgen.MountainSurface.peat(peat),"Missing peat test block");
        var lowPeat=new net.minecraft.core.BlockPos(0,130,0);
        var cavePeat=new net.minecraft.core.BlockPos(1,200,0);
        var peak=new net.minecraft.core.BlockPos(2,450,0);
        var ore=new net.minecraft.core.BlockPos(3,450,0);
        surfaceChunk.setBlockState(lowPeat,peat,false);
        surfaceChunk.setBlockState(cavePeat,peat,false);
        surfaceChunk.setBlockState(cavePeat.above(10),net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(),false);
        surfaceChunk.setBlockState(peak,net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(),false);
        surfaceChunk.setBlockState(ore,net.minecraft.world.level.block.Blocks.IRON_ORE.defaultBlockState(),false);
        dev.godpc.industrialcolonies.worldgen.MountainSurface.finish(surfaceChunk);
        h.assertTrue(surfaceChunk.getBlockState(lowPeat).equals(peat),"Lowland peat changed");
        h.assertTrue(surfaceChunk.getBlockState(cavePeat).is(net.minecraft.world.level.block.Blocks.STONE),"High cave peat survived");
        h.assertTrue(surfaceChunk.getBlockState(peak).is(net.minecraft.world.level.block.Blocks.SNOW_BLOCK),"High exposed ground lacks snow");
        h.assertTrue(surfaceChunk.getBlockState(ore).is(net.minecraft.world.level.block.Blocks.IRON_ORE),"Snow replaced ore");
        h.assertTrue(!dev.godpc.industrialcolonies.worldgen.MountainSurface.snowAt(0,319,0),"Snow extended below snowline");
        for(String id:List.of("stellaris:earth_satellite","stellaris:earth_operation_base","stellaris:mercury_lava_mines"))
            h.assertTrue(SurfaceStructureTerrain.shouldCheck(registry.get(ResourceLocation.parse(id)),access),"Stellaris surface entrance escaped gate: "+id);
        var ops=RegistryOps.create(com.mojang.serialization.JsonOps.INSTANCE,access);
        String flat="{\"type\":\"minecraft:flat\",\"settings\":{\"biome\":\"minecraft:plains\",\"features\":false,\"lakes\":false,\"layers\":[{\"block\":\"minecraft:stone\",\"height\":80},%s]}}";
        var dry=ChunkGenerator.CODEC.parse(ops,JsonParser.parseString(flat.formatted("{\"block\":\"minecraft:grass_block\",\"height\":1}"))).getOrThrow();
        var wet=ChunkGenerator.CODEC.parse(ops,JsonParser.parseString(flat.formatted("{\"block\":\"minecraft:water\",\"height\":8}"))).getOrThrow();
        int checked=0;
        for(String id:List.of("minecraft:village_plains","ctov:small/village_plains","minecraft:ruined_portal")) {
            var structure=registry.get(ResourceLocation.parse(id));
            h.assertTrue(SurfaceStructureTerrain.shouldCheck(structure,access),"Land structure escaped gate: "+id);
            boolean dryPass=false,wetCandidate=false;
            for(int i=0;i<8&&!(dryPass&&wetCandidate);i++) {
                var pos=new ChunkPos(i*16,i*8);
                var dryStart=structure.generate(access,dry,dry.getBiomeSource(),random,level.getStructureManager(),9122026L,pos,0,level,b->true);
                dryPass|=dryStart.isValid();
                var context=new Structure.GenerationContext(access,wet,wet.getBiomeSource(),random,level.getStructureManager(),9122026L,pos,level,b->true);
                var ungated=structure.findValidGenerationPoint(context);
                if(ungated.isPresent()&&!ungated.get().getPiecesBuilder().build().isEmpty()) {
                    wetCandidate=true;
                    var wetStart=structure.generate(access,wet,wet.getBiomeSource(),random,level.getStructureManager(),9122026L,pos,0,level,b->true);
                    h.assertTrue(!wetStart.isValid(),"Production mixin accepted water: "+id);
                }
            }
            h.assertTrue(dryPass&&wetCandidate,"Could not validate both native terrain cases: "+id);checked++;
        }
        for(String id:List.of("minecolonies:ship","block_factorys_bosses:kraken_ship","irons_spellbooks:impaled_icebreaker","minecraft:monument","cataclysm:sunken_city","minecraft:mineshaft"))
            h.assertTrue(!SurfaceStructureTerrain.shouldCheck(registry.get(ResourceLocation.parse(id)),access),"Intended non-land structure blocked: "+id);
        var report=new JsonObject();report.addProperty("status","PASS");report.addProperty("nativeLandTypes",checked);report.addProperty("fullFootprintAndLedgeChecks",true);
        report.addProperty("summitRejectsShouldersAndHighPlains",true);report.addProperty("highPeatRemovedLowPeatPreserved",true);report.addProperty("snowGroundCoveredOrePreserved",true);
        Files.writeString(stage.resolve("surface-terrain-report.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
        System.out.println("SURFACE_TERRAIN_PASS nativeTypes=3 dry=accepted wet=rejected narrowRiver=rejected ledge=rejected ships=exempt");
        h.succeed();
    }
}
