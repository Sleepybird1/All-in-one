package dev.godpc.industrialcolonies.cavecheck;

import dev.godpc.industrialcolonies.geology.*;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.gametest.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import java.lang.reflect.*;
import java.util.*;

@Mod("ic_cave_smoke")
@GameTestHolder("ic_cave_smoke")
@PrefixGameTestTemplate(false)
public final class CaveSmoke {
    public CaveSmoke() {}
    @GameTest(template="geology_smoke_empty",timeoutTicks=400)
    public static void surfaceRockPickup(GameTestHelper h){
        var level=h.getLevel();var player=h.makeMockPlayer(GameType.SURVIVAL);
        BlockPos p=h.absolutePos(new BlockPos(2,3,2));level.setBlock(p.below(),Blocks.STONE.defaultBlockState(),2);
        for(String material:SurfaceRocks.MATERIALS){
            Block block=SurfaceRocks.block(material);BlockState state=block.defaultBlockState();level.setBlock(p,state,2);
            var expected=SurfaceRocks.pickup(block);
            var loot=Block.getDrops(state,level,p,null,player,net.minecraft.world.item.ItemStack.EMPTY);
            h.assertTrue(loot.size()==1&&loot.getFirst().is(expected.getItem())&&loot.getFirst().getCount()==1,"Incorrect hand-break loot: "+material);
            int before=player.getInventory().countItem(expected.getItem());
            state.useWithoutItem(level,player,new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(p),Direction.UP,p,false));
            h.assertTrue(level.isEmptyBlock(p),"Pickup failed to consume rock");
            h.assertTrue(player.getInventory().countItem(expected.getItem())==before+1,"Wrong pickup count");
            state.useWithoutItem(level,player,new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(p),Direction.UP,p,false));
            h.assertTrue(player.getInventory().countItem(expected.getItem())==before+1,"Duplicate pickup");
        }
        int linked=0;
        for(int i=0;i<50000;i++){
            var a=SurfaceRockClues.site(123,i-25000,-i,512,.95);
            h.assertTrue(a.equals(SurfaceRockClues.site(123,i-25000,-i,512,.95)),"Unstable clue site");
            if(a.linked())linked++;
            else{var actual=SurfaceRockClues.site(123,i-25000,-i,512,1);int distance=Math.abs(a.x()-actual.x())+Math.abs(a.z()-actual.z());h.assertTrue(distance>=160&&distance<=224,"False lead not offset");}
        }
        h.assertTrue(linked>47000&&linked<48000,"Incorrect clue weights");
        System.out.println("SURFACE_ROCK_PICKUP_PASS types=21 linked="+linked+"/50000");h.succeed();
    }
    @GameTest(template="geology_smoke_empty",timeoutTicks=12000)
    public static void naturalSurfaceClues(GameTestHelper h){new ClueSurvey(h).step();}
    private static final class ClueSurvey {
        final GameTestHelper h;int index=4;boolean linkedFound,decoyFound;
        ClueSurvey(GameTestHelper h){this.h=h;}
        void step(){
            var level=h.getLevel();var world=GeologyWorld.of(level);int rx=index++,rz=4;
            var site=SurfaceRockClues.site(level.getSeed(),rx,rz,world.planner.regionSize(),.95);
            if((site.linked()&&!linkedFound)||(!site.linked()&&!decoyFound)){
                var plan=world.planner.decide(rx,rz).plan();
                if(plan!=null){
                    String host=plan.definition().get("hostRock").getAsString(),material=SurfaceRocks.materialForHost(host);
                    if(material!=null){
                        ChunkPos chunk=new ChunkPos(site.x()>>4,site.z()>>4);level.getChunk(chunk.x,chunk.z);int found=0;
                        for(int x=chunk.getMinBlockX();x<=chunk.getMaxBlockX();x++)for(int z=chunk.getMinBlockZ();z<=chunk.getMaxBlockZ();z++){
                            int top=level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
                            for(int y=Math.max(-63,top-4);y<=Math.min(511,top+1);y++)if(level.getBlockState(new BlockPos(x,y,z)).is(SurfaceRocks.block(material)))found++;
                        }
                        if(found>0){
                            h.assertTrue(found>=2&&found<=4,"Wrong natural scatter size");
                            if(site.linked()){
                                boolean actual=world.shape(plan).stream().anyMatch(p->new ChunkPos(p).equals(chunk)&&level.getBlockState(p).is(GeologyFeature.state(host).getBlock()));
                                h.assertTrue(actual,"Clue lacks actual matching deposit in owner chunk");linkedFound=true;
                            }else decoyFound=true;
                            System.out.println("SURFACE_ROCK_NATURAL_SITE linked="+site.linked()+" material="+material+" rocks="+found+" chunk="+chunk);
                        }
                    }
                }
            }
            if(linkedFound&&decoyFound){System.out.println("SURFACE_ROCK_NATURAL_PASS verified linked and decoy sites");h.succeed();return;}
            h.assertTrue(index<4096,"Did not find both clue types in bounded search");h.runAfterDelay(1,this::step);
        }
    }
    @GameTest(template="geology_smoke_empty",timeoutTicks=12000)
    public static void nativePlacement(GameTestHelper h) throws Exception {
        var level=h.getLevel();ChunkPos chunk=new ChunkPos(h.absolutePos(BlockPos.ZERO));
        Map<BlockPos,BlockState> before=new LinkedHashMap<>();
        try {
            for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=-26;y<=-18;y++){
                BlockPos p=new BlockPos(chunk.getMinBlockX()+x,y,chunk.getMinBlockZ()+z);
                before.put(p,level.getBlockState(p));
                level.setBlock(p,(y==-22?Blocks.AIR:Blocks.STONE).defaultBlockState(),2);
            }
            WorldGenLevel proxy=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(receiver,method,args)->{
                if(args!=null&&args.length>0&&args[0] instanceof BlockPos p&&Set.of("getBlockState","setBlock").contains(method.getName()))
                    h.assertTrue(new ChunkPos(p).equals(chunk),"Cross-chunk read/write");
                if(method.getName().equals("getBlockState")&&!before.containsKey((BlockPos)args[0]))return Blocks.BEDROCK.defaultBlockState();
                try{return level.getClass().getMethod(method.getName(),method.getParameterTypes()).invoke(level,args);}catch(InvocationTargetException e){throw e.getCause();}
            });
            Class<?> feature=Class.forName("dev.godpc.industrialcolonies.geology.CaveTraceFeature");
            Method generate=feature.getDeclaredMethod("generate",WorldGenLevel.class,ChunkPos.class,GeologyWorld.class);generate.setAccessible(true);
            boolean changed=(boolean)generate.invoke(null,proxy,chunk,GeologyWorld.of(level));
            h.assertTrue(changed,"Native cave fixture placed nothing");int count=0;
            Set<String> allowed=Set.of("minecraft:coal_ore","industrial_colonies:hematite","industrial_colonies:sphalerite","industrial_colonies:cassiterite","industrial_colonies:chalcopyrite");
            for(BlockPos p:before.keySet()){
                BlockState s=level.getBlockState(p);
                if(s.is(Blocks.AIR)){h.assertTrue(p.getY()==-22,"Unexpected air replacement");continue;}
                if(s.is(Blocks.STONE))continue;
                h.assertTrue(allowed.contains(BuiltInRegistries.BLOCK.getKey(s.getBlock()).toString()),"Wrong trace resource");
                h.assertTrue(p.getY()==-21||p.getY()==-23,"Buried fixture trace");count++;
            }
            h.assertTrue(count>0&&count<=18,"Native patch count outside bounds");
            System.out.println("CAVE_NATIVE_PLACEMENT_PASS blocks="+count);
        }finally{before.forEach((p,s)->level.setBlock(p,s,2));}
        h.succeed();
    }
    @GameTest(template="geology_smoke_empty",timeoutTicks=12000)
    public static void naturalCaves(GameTestHelper h){new Survey(h).step();}
    private static final class Survey {
        final GameTestHelper h;int index,exposed;Map<String,Integer> counts=new TreeMap<>();
        Survey(GameTestHelper h){this.h=h;}
        void step(){
            var level=h.getLevel();int cx=64+index,cz=64;
            level.getChunk(cx,cz);
            for(int x=cx*16+1;x<cx*16+15;x++)for(int z=cz*16+1;z<cz*16+15;z++)for(int y=-60;y<120;y++){
                BlockPos p=new BlockPos(x,y,z);String id=BuiltInRegistries.BLOCK.getKey(level.getBlockState(p).getBlock()).toString();
                if(!Set.of("minecraft:coal_ore","industrial_colonies:hematite","industrial_colonies:sphalerite","industrial_colonies:cassiterite","industrial_colonies:chalcopyrite").contains(id))continue;
                for(Direction d:Direction.values())if(level.getBlockState(p.relative(d)).isAir()){exposed++;counts.merge(id,1,Integer::sum);break;}
            }
            if(++index<8){h.runAfterDelay(1,this::step);return;}
            h.assertTrue(level.getMaxBuildHeight()==512,"Lithosphere height missing");
            h.assertTrue(exposed>0,"No exposed starter resources in sampled natural chunks");
            System.out.println("CAVE_NATURAL_SURVEY_PASS chunks=8 exposed="+exposed+" resources="+counts+" (includes existing deposits)");h.succeed();
        }
    }
}
