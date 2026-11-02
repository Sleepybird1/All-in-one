package dev.godpc.industrialcolonies.geology;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.server.level.ServerLevel;

/** Applies an already selected surface concentration. No automatic occurrence or per-chunk roll. */
public final class CinnabarSurfaceFeature {
    private CinnabarSurfaceFeature() {}
    /** Called only after the range allocator selects this concentration and its frequency roll. */
    public static CinnabarSurfaceGeometry.Plan plan(ServerLevel level,long seed,int x,int z,int width,
            int anchorY,int minimumY,double frequencyRoll,double coverage,int thickness){
        var world=GeologyWorld.of(level);
        var geography=ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState());
        return CinnabarSurfaceGeometry.plan(seed,x,z,width,anchorY,minimumY,frequencyRoll,coverage,thickness,
                new CinnabarSurfaceGeometry.Terrain(){
                    public int topY(int px,int pz){return world.height(px,pz)-1;}
                    public boolean mountain(int px,int pz){return geography.sample(px,pz).mountain();}
                });
    }
    public static int place(WorldGenLevel level,ChunkPos owner,CinnabarSurfaceGeometry.Plan plan){
        if(!plan.admitted())return 0;
        var id=ResourceLocation.parse("industrial_colonies:cinnabar");
        if(!BuiltInRegistries.BLOCK.containsKey(id))throw new IllegalStateException("Missing cinnabar block: "+id);
        var output=BuiltInRegistries.BLOCK.get(id).defaultBlockState();
        Set<BlockPos> written=new HashSet<>();int count=0;
        for(var stroke:plan.strokes()){
            // Only the owner or its immediate neighboring chunks are ever read.
            if(stroke.blocks().stream().noneMatch(v->(v.x()>>4)==owner.x&&(v.z()>>4)==owner.z))continue;
            var f=stroke.face();var v=f.front();var front=new BlockPos(v.x(),v.y(),v.z());var air=front.offset(f.dx(),f.dy(),f.dz());
            // A cave opening below its column's outside surface is not an exposed mountain face.
            if(!level.getBlockState(air).isAir()||air.getY()<level.getHeight(Heightmap.Types.WORLD_SURFACE,air.getX(),air.getZ()))continue;
            var frontState=level.getBlockState(front);
            if(!frontState.equals(output)&&!GeologyFeature.replaceable(frontState))continue;
            for(var p:stroke.blocks()){
                var pos=new BlockPos(p.x(),p.y(),p.z());var state=level.getBlockState(pos);
                // Never tunnel through protected cover, a fluid or a cavity to reach deeper stone.
                if(!state.equals(output)&&!GeologyFeature.replaceable(state))break;
                if((p.x()>>4)!=owner.x||(p.z()>>4)!=owner.z||!written.add(pos)||state.equals(output))continue;
                if(level.setBlock(pos,output,2))count++;
            }
        }
        return count;
    }
}
