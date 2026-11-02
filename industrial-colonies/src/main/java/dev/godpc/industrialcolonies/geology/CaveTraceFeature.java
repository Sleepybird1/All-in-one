package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Separate config file makes this addition available to existing settings.json installations. */
final class CaveTraceFeature {
    private record Config(boolean enabled,CaveTracePlanner.Rules rules) {}
    private static final class Holder { static final Config CONFIG=load(); }
    private static Config load(){
        JsonObject o=externalOrBundled("cave_traces.json");
        List<CaveTracePlanner.Resource> resources=new ArrayList<>();
        for(JsonElement e:array(o,"resources")){
            JsonObject r=e.getAsJsonObject();String block=r.get("block").getAsString();
            GeologyFeature.state(block); // Reject unregistered resource IDs at startup of the feature.
            resources.add(new CaveTracePlanner.Resource(block,number(r,"weight",0)));
        }
        return new Config(bool(o,"enabled",true),new CaveTracePlanner.Rules(
                exact(o,"minY"),exact(o,"maxY"),exact(o,"minimumCover"),exact(o,"columnsPerChunk"),
                exact(o,"patchAttemptsPerChunk"),number(o,"chancePerAttempt",.65),exact(o,"minPatchSize"),exact(o,"maxPatchSize"),resources));
    }
    private static int exact(JsonObject o,String key){
        double value=number(o,key,Double.NaN);
        if(!Double.isFinite(value)||value!=Math.rint(value)||value<Integer.MIN_VALUE||value>Integer.MAX_VALUE)
            throw new IllegalArgumentException("Cave trace setting must be an integer: "+key);
        return (int)value;
    }
    static boolean generate(WorldGenLevel level,ChunkPos chunk,GeologyWorld world){
        if(NearbyVeinClues.enabled())return false;
        Config config=Holder.CONFIG;if(!config.enabled)return false;
        var plan=CaveTracePlanner.plan(level.getSeed(),chunk.x,chunk.z,level.getMinBuildHeight(),level.getMaxBuildHeight(),config.rules,
                new CaveTracePlanner.Terrain(){
                    public boolean stone(CaveTracePlanner.Cell p){return GeologyFeature.replaceable(level.getBlockState(pos(p)));}
                    public boolean air(CaveTracePlanner.Cell p){return level.getBlockState(pos(p)).isAir();}
                    public int surface(int x,int z){return world.height(x,z)-1;}
                });
        boolean changed=false;
        for(var placement:plan)if(NearbyVeinClues.allowsBlock(level.getLevel(),placement.block(),placement.cell().x(),placement.cell().z()))changed|=level.setBlock(pos(placement.cell()),GeologyFeature.state(placement.block()),2);
        return changed;
    }
    private static BlockPos pos(CaveTracePlanner.Cell p){return new BlockPos(p.x(),p.y(),p.z());}
}
