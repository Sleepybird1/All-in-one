package dev.godpc.industrialcolonies.minecheck;

import dev.godpc.industrialcolonies.geology.*;
import java.lang.reflect.*;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.level.levelgen.structure.structures.*;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.gametest.*;

@Mod("ic_mineshaft_smoke")
@GameTestHolder("ic_mineshaft_smoke")
@PrefixGameTestTemplate(false)
public final class MineshaftSmoke {
    public MineshaftSmoke() {}
    private static Structure.GenerationContext context(ServerLevel level,long seed,ChunkPos chunk){
        var generator=level.getChunkSource().getGenerator();
        return new Structure.GenerationContext(level.registryAccess(),generator,generator.getBiomeSource(),level.getChunkSource().randomState(),
                level.getStructureManager(),seed,chunk,level,b->true);
    }
    private static MineshaftStructure structure(ServerLevel level,boolean mesa){
        return (MineshaftStructure)level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ResourceLocation.withDefaultNamespace(mesa?"mineshaft_mesa":"mineshaft"));
    }
    @GameTest(template="geology_smoke_empty",timeoutTicks=12000)
    public static void unchangedVanillaGeneration(GameTestHelper h) throws Exception {
        var level=h.getLevel();var serialization=StructurePieceSerializationContext.fromLevel(level);
        Method vanilla=MineshaftStructure.class.getDeclaredMethod("generatePiecesAndAdjust",StructurePiecesBuilder.class,Structure.GenerationContext.class);vanilla.setAccessible(true);
        int oldPieces=0;Set<String> hosts=new TreeSet<>();
        for(boolean mesa:List.of(false,true))for(int i=0;i<64;i++){
            var mine=structure(level,mesa);var chunk=new ChunkPos(i-32,17-i);
            var baseline=context(level,i*7919L,chunk);baseline.random().nextDouble();var original=new StructurePiecesBuilder();
            int offset=(int)vanilla.invoke(mine,original,baseline);
            var updated=context(level,i*7919L,chunk);var result=mine.findGenerationPoint(updated).orElseThrow();var pieces=result.getPiecesBuilder().build().pieces();
            h.assertTrue(result.position().equals(new BlockPos(chunk.getMiddleBlockX(),50+offset,chunk.getMinBlockZ())),"Generation/biome-check position changed");
            h.assertTrue(baseline.random().nextLong()==updated.random().nextLong(),"Consumed vanilla random state");
            var before=original.build().pieces();h.assertTrue(pieces.size()==before.size()+1,"Not exactly one working per shaft");
            for(int n=0;n<before.size();n++){h.assertTrue(before.get(n).createTag(serialization).equals(pieces.get(n).createTag(serialization)),"Original piece changed");oldPieces++;}
            h.assertTrue(pieces.getLast() instanceof MineshaftVeinPiece,"Missing appended working");
            var vein=(MineshaftVeinPiece)pieces.getLast();var blocks=vein.plannedBlocks();hosts.add(vein.host());
            h.assertTrue(!blocks.isEmpty()&&blocks.size()<=1080,"Invalid working size");
            for(BlockPos p:blocks.keySet())h.assertTrue(before.stream().noneMatch(piece->piece.getBoundingBox().isInside(p)),"Working overwrites original structure volume");
            var loaded=(MineshaftVeinPiece)MineshaftVeins.WORKING.get().load(serialization,vein.createTag(serialization));
            h.assertTrue(loaded.plannedBlocks().equals(blocks),"Saved working changed geometry/materials");
            loaded.move(256,16,-256);Map<BlockPos,BlockState> moved=new LinkedHashMap<>();blocks.forEach((p,s)->moved.put(p.offset(256,16,-256),s));
            h.assertTrue(loaded.plannedBlocks().equals(moved),"Structure movement broke the working");
            MineshaftVeins.attach(updated,result,mesa?MineshaftStructure.Type.MESA:MineshaftStructure.Type.NORMAL);
            h.assertTrue(result.getPiecesBuilder().build().pieces().size()==pieces.size(),"Duplicate attachment");
        }
        System.out.println("MINESHAFT_VANILLA_PARITY_PASS samples=128 originalPieces="+oldPieces+" materials="+hosts);h.succeed();
    }
    @GameTest(template="geology_smoke_empty",timeoutTicks=12000)
    public static void actualConnectedWorking(GameTestHelper h) throws Exception {
        var level=h.getLevel();var mine=structure(level,false);var chunk=new ChunkPos(150,150);
        var pieces=mine.findGenerationPoint(context(level,47,chunk)).orElseThrow().getPiecesBuilder().build().pieces();
        var vein=(MineshaftVeinPiece)pieces.getLast();var room=pieces.getFirst().getBoundingBox();var box=vein.getBoundingBox();
        var fixture=new BoundingBox(Math.min(room.minX(),box.minX())-1,Math.max(level.getMinBuildHeight()+1,Math.min(room.minY(),box.minY())-1),Math.min(room.minZ(),box.minZ())-1,
                Math.max(room.maxX(),box.maxX())+1,Math.min(level.getMaxBuildHeight()-2,Math.max(room.maxY(),box.maxY())+1),Math.max(room.maxZ(),box.maxZ())+1);
        var serial=StructurePieceSerializationContext.fromLevel(level);var initialTags=pieces.stream().map(p->p.createTag(serial)).toList();
        List<ChunkPos> chunks=new ArrayList<>();for(int x=fixture.minX()>>4;x<=fixture.maxX()>>4;x++)for(int z=fixture.minZ()>>4;z<=fixture.maxZ()>>4;z++)chunks.add(new ChunkPos(x,z));
        h.assertTrue(chunks.size()<=12,"Fixture exceeds chunk bound");
        Map<BlockPos,BlockState> originals=new LinkedHashMap<>();
        for(BlockPos p:BlockPos.betweenClosed(fixture.minX(),fixture.minY(),fixture.minZ(),fixture.maxX(),fixture.maxY(),fixture.maxZ()))originals.put(p.immutable(),level.getBlockState(p));
        h.assertTrue(originals.size()<30000,"Fixture exceeds block bound");
        ChunkPos[] owner={null};boolean[] checking={false};
        WorldGenLevel proxy=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(receiver,method,args)->{
            if(checking[0]&&args!=null&&args.length>0&&args[0] instanceof BlockPos p&&Set.of("getBlockState","setBlock").contains(method.getName()))
                h.assertTrue(new ChunkPos(p).equals(owner[0]),"Working accessed another chunk");
            if(method.getName().equals("getBiome"))return level.registryAccess().registryOrThrow(Registries.BIOME).getHolderOrThrow(net.minecraft.world.level.biome.Biomes.PLAINS);
            try{return level.getClass().getMethod(method.getName(),method.getParameterTypes()).invoke(level,args);}catch(InvocationTargetException e){throw e.getCause();}
        });
        Map<BlockPos,BlockState> forward=null;int reachableFaces=0;
        try{
            for(boolean reverse:List.of(false,true)){
                originals.keySet().forEach(p->level.setBlock(p,Blocks.STONE.defaultBlockState(),2));
                List<StructurePiece> loaded=new ArrayList<>();for(var tag:initialTags)loaded.add(BuiltInRegistries.STRUCTURE_PIECE.get(ResourceLocation.parse(tag.getString("id"))).load(serial,tag));
                var fresh=(MineshaftVeinPiece)loaded.removeLast();var vanillaStart=new StructureStart(mine,chunk,0,new PiecesContainer(loaded));
                var order=new ArrayList<>(chunks);if(reverse)Collections.reverse(order);
                for(var cp:order){var clip=clip(cp,fixture);vanillaStart.placeInChunk(proxy,level.structureManager(),level.getChunkSource().getGenerator(),RandomSource.create(GeologyMath.seed(47,cp.x,cp.z,44)),clip,cp);}
                Map<BlockPos,BlockState> protectedBefore=new LinkedHashMap<>();for(BlockPos p:originals.keySet())if(loaded.stream().anyMatch(piece->piece.getBoundingBox().isInside(p)))protectedBefore.put(p,level.getBlockState(p));
                checking[0]=true;
                for(var cp:order){owner[0]=cp;fresh.postProcess(proxy,level.structureManager(),level.getChunkSource().getGenerator(),RandomSource.create(1),clip(cp,fixture),cp,BlockPos.ZERO);}
                checking[0]=false;
                protectedBefore.forEach((p,s)->h.assertTrue(level.getBlockState(p).equals(s),"Original placed room/corridor changed"));
                Map<BlockPos,BlockState> actual=new LinkedHashMap<>();fresh.plannedBlocks().forEach((p,s)->{var found=level.getBlockState(p);h.assertTrue(found.equals(s),"Working did not place expected block");actual.put(p,found);});
                if(forward==null)forward=actual;else h.assertTrue(forward.equals(actual),"Reversing chunk order changed working");
                Set<BlockPos> reached=new HashSet<>();ArrayDeque<BlockPos> queue=new ArrayDeque<>();queue.add(fresh.door());reached.add(fresh.door());int exposed=0;
                while(!queue.isEmpty()){
                    BlockPos p=queue.removeFirst();h.assertTrue(level.getBlockState(p).isAir()&&level.getBlockState(p.above()).isAir(),"Blocked room-to-working route");
                    for(Direction d:Direction.values()){BlockPos q=p.relative(d);var state=actual.get(q);if(state!=null&&!state.isAir()&&!state.is(Blocks.OAK_PLANKS)&&!state.is(Blocks.DARK_OAK_PLANKS))exposed++;}
                    for(Direction d:Direction.Plane.HORIZONTAL){BlockPos q=p.relative(d);if(fixture.isInside(q)&&fixture.isInside(q.above())&&level.getBlockState(q).isAir()&&level.getBlockState(q.above()).isAir()&&reached.add(q))queue.addLast(q);}
                }
                h.assertTrue(exposed>0,"No ore reachable from mineshaft room");reachableFaces=exposed;
            }
            System.out.println("MINESHAFT_CONNECTION_PASS material="+vein.host()+" placed="+forward.size()+" reachableOreFaces="+reachableFaces+" chunks="+chunks.size()+" reversedOrder=true");
        }finally{originals.forEach((p,s)->level.setBlock(p,s,2));}
        h.succeed();
    }
    private static BoundingBox clip(ChunkPos c,BoundingBox f){return new BoundingBox(Math.max(c.getMinBlockX(),f.minX()),f.minY(),Math.max(c.getMinBlockZ(),f.minZ()),Math.min(c.getMaxBlockX(),f.maxX()),f.maxY(),Math.min(c.getMaxBlockZ(),f.maxZ()));}
}
