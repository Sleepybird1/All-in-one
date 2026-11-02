package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.levelgen.Heightmap;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Sparse prospecting sites: the linked branch requires surviving material in this very chunk. */
public final class SurfaceRockClues {
    public record Site(int x,int z,boolean linked,long seed) {}
    private static final class Settings {
        static final JsonObject DATA=externalOrBundled("surface_rocks.json");
        static final double LINKED=validate(number(DATA,"linkedSiteChance",.95));
        private static double validate(double v){if(!Double.isFinite(v)||v<0||v>1)throw new IllegalArgumentException("Invalid surface rock linkedSiteChance");return v;}
    }
    private SurfaceRockClues() {}
    /** Clues belong in exposed stone, never soil, turf, sand, gravel or snow. */
    public static boolean stoneSurface(net.minecraft.world.level.block.state.BlockState state){
        if(state.is(BlockTags.DIRT)||state.is(BlockTags.SAND)||state.is(Blocks.GRAVEL)||state.is(Blocks.SNOW_BLOCK))return false;
        return GeologyFeature.replaceable(state)||state.is(BlockTags.BASE_STONE_OVERWORLD)
                ||state.is(Blocks.COBBLESTONE)||state.is(Blocks.MOSSY_COBBLESTONE)
                ||state.is(Blocks.COBBLED_DEEPSLATE)||state.is(Blocks.CALCITE)||state.is(Blocks.TUFF);
    }
    /** Same raw candidate coordinates as the geology planner, computed without loading terrain or selecting minerals. */
    public static Site site(long worldSeed,int rx,int rz,int region,double linkedChance){
        long candidate=seed(worldSeed,rx,rz,0x494347454f4c4f47L),roll=mix(candidate^0x53555246414345L);
        int x=rx*region+bounded(candidate+1,region),z=rz*region+bounded(candidate+2,region);
        boolean linked=unit(roll)<linkedChance;
        if(!linked){int distance=160+bounded(roll+1,65);switch(bounded(roll+2,4)){
            case 0 -> x+=distance;case 1 -> x-=distance;case 2 -> z+=distance;default -> z-=distance;
        }}
        return new Site(x,z,linked,roll);
    }
    public static boolean generate(WorldGenLevel level,ChunkPos chunk,GeologyWorld world){
        if(NearbyVeinClues.enabled())return linkedOwnerIndicators(level,chunk);
        if(!bool(Settings.DATA,"enabled",true))return false;
        int size=world.planner.regionSize(),rx=Math.floorDiv(chunk.getMiddleBlockX(),size),rz=Math.floorDiv(chunk.getMiddleBlockZ(),size);
        boolean changed=false;
        int reach=(int)Math.ceil(224.0/size)+1;
        for(int a=rx-reach;a<=rx+reach;a++)for(int b=rz-reach;b<=rz+reach;b++){
            Site site=site(level.getSeed(),a,b,size,Settings.LINKED);
            if((site.x>>4)!=chunk.x||(site.z>>4)!=chunk.z)continue;
            var decision=world.planner.decide(a,b);var plan=decision.plan();if(plan==null)continue;
            if(plan.id().equals("cinnabar")&&WorldStartCinnabarRuntime.find(level.getLevel()).isPresent())continue;
            String host=string(plan.definition(),"hostRock","");
            String material=SurfaceRocks.materialForHost(host);if(material==null)continue;
            if(NearbyVeinClues.enabled()){
                if(!NearbyVeinClues.allows(level.getLevel(),plan.id(),site.x,site.z))continue;
            }else if(site.linked){
                // Final carver-stage material exists before FEATURES. No assumed/noise-only deposits qualify.
                var hostBlock=GeologyFeature.state(host).getBlock();
                var cursor=new BlockPos.MutableBlockPos();
                boolean present=world.anyMatchChunk(plan,chunk,level.getMinBuildHeight()+1,level.getMaxBuildHeight(),
                        (x,y,z)->level.getBlockState(cursor.set(x,y,z)).is(hostBlock));
                if(!present)continue;
            }
            // Identical-looking false leads carry the same material but have no required deposit at their location.
            List<Integer> spots=new ArrayList<>();for(int i=0;i<196;i++)spots.add(i);
            spots.sort(Comparator.comparingLong(i->mix(site.seed+i)));
            int wanted=2+bounded(site.seed+3,3),placed=0;Set<BlockPos> used=new HashSet<>();
            for(int index:spots){
                int x=chunk.getMinBlockX()+1+index%14,z=chunk.getMinBlockZ()+1+index/14;
                int y=level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,x,z);
                BlockPos p=new BlockPos(x,y,z);var ground=level.getBlockState(p.below());
                if(!(stoneSurface(ground)))continue;
                if(!level.getBlockState(p).isAir()||!level.getFluidState(p).isEmpty()||!ground.isFaceSturdy(level,p.below(),Direction.UP))continue;
                if(used.stream().anyMatch(q->q.distManhattan(p)<3))continue;
                if(!NearbyVeinClues.allows(level.getLevel(),plan.id(),x,z))continue;
                if(level.setBlock(p,SurfaceRocks.block(material).defaultBlockState(),2)){placed++;used.add(p);changed=true;}
                if(placed>=wanted)break;
            }
        }
        return changed;
    }
    /** Exactly one isolated host block for each source family in this generated owner.
     * No chance roll, old planner, new mineral selection or foreign chunk/terrain query. */
    private static boolean linkedOwnerIndicators(WorldGenLevel level,ChunkPos chunk){
        var direct=NearbyVeinClues.familiesInChunk(level.getLevel(),chunk.x,chunk.z);
        var families=new TreeSet<>(NearbyVeinClues.familiesNearChunk(level.getLevel(),chunk.x,chunk.z));
        boolean changed=false;var used=new ArrayList<BlockPos>();
        for(String family:families){
            // One deterministic scattered destination per64x64 area, plus the source
            // owner fallback. No independent ore roll and no radius enlargement.
            long scatter=seed(level.getSeed()^family.hashCode(),Math.floorDiv(chunk.x,4),Math.floorDiv(chunk.z,4),0x434c554553L);
            if(!direct.contains(family)&&(Math.floorMod(chunk.x,4)!=bounded(scatter,4)||Math.floorMod(chunk.z,4)!=bounded(scatter+1,4)))continue;
            if(!direct.contains(family)&&!NearbyVeinClues.scatteredSite(level.getLevel(),family,chunk.x,chunk.z,scatter))continue;
            var definition=array(GeologyConfig.get().deposits(),"deposits").asList().stream().map(e->e.getAsJsonObject())
                    .filter(d->string(d,"id","").equals(family)).findFirst().orElseThrow();
            var host=GeologyFeature.state(definition.get("hostRock").getAsString());boolean placed=false;
            for(var point:SurfaceVeinClueSites.columns(level.getSeed(),family,chunk.x,chunk.z)){
                // Ocean floor fallback gives an exposed seabed clue without replacing water.
                for(var heightmap:new Heightmap.Types[]{Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,Heightmap.Types.OCEAN_FLOOR_WG}){
                    int y=level.getHeight(heightmap,point.x(),point.z())-1;
                    if(y<=level.getMinBuildHeight()||y>=level.getMaxBuildHeight()-1)continue;
                    var p=new BlockPos(point.x(),y,point.z());var ground=level.getBlockState(p);
                    if(used.stream().anyMatch(q->Math.abs(q.getX()-p.getX())<=1&&Math.abs(q.getZ()-p.getZ())<=1))continue;
                    if(!NearbyVeinClues.allows(level.getLevel(),family,p.getX(),p.getZ())||!level.getFluidState(p).isEmpty()||level.getBlockEntity(p)!=null)continue;
                    if(ground.is(host.getBlock())){placed=true;used.add(p);break;}
                    if(!(stoneSurface(ground)))continue;
                    if(!ground.isFaceSturdy(level,p,Direction.UP))continue;
                    if(level.setBlock(p,host,2)){changed=true;placed=true;used.add(p);break;}
                }
                if(placed)break;
            }
            if(!placed)org.slf4j.LoggerFactory.getLogger("IndustrialColonies/VeinClues").warn("No safe exposed ground for {} clue in owner {}; source retained, no remote generation or protected-block replacement",family,chunk);
        }
        return changed;
    }
}
