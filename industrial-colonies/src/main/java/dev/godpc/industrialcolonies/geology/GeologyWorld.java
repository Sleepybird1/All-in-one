package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.RandomState;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Noise-column sampling, not chunk loading. Surface geology is inherited by underground cave biomes. */
public final class GeologyWorld implements GeologyPlanner.Sampler {
    private static final Map<ServerLevel,GeologyWorld> WORLDS=Collections.synchronizedMap(new WeakHashMap<>());
    private final ServerLevel level;
    private final ChunkGenerator generator;
    private final RandomState initialState;
    private final Map<Long,Integer> processedHeights=new LinkedHashMap<>(256,0.75f,true);
    private Object processedLookup;
    public final GeologyPlanner planner;
    private final Map<Long,List<BlockPos>> shapes=Collections.synchronizedMap(new LinkedHashMap<>());
    private GeologyWorld(ServerLevel level){this.level=level;generator=level.getChunkSource().getGenerator();initialState=level.getChunkSource().randomState();planner=new GeologyPlanner(level.getSeed(),get(),this);}
    public static GeologyWorld of(ServerLevel level){synchronized(WORLDS){return WORLDS.computeIfAbsent(level,GeologyWorld::new);}}
    public static void clear(){WORLDS.clear();}
    public static void forget(ServerLevel level){WORLDS.remove(level);}
    /** Structure.GenerationContext holds a ChunkAccess, not a WorldGenLevel. */
    public static GeologyWorld forGeneration(RandomState state){
        synchronized(WORLDS){
            for(var world:WORLDS.values())if(world.level.getChunkSource().randomState()==state)return world;
        }
        throw new IllegalStateException("Massive mine generation preceded its LevelEvent.Load registration");
    }
    public boolean overworld(){return level.dimension()==Level.OVERWORLD;}
    private int nativeHeight(int x,int z){return NativeAccurateTerrain.query(level,()->generator.getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,level,level.getChunkSource().randomState()));}
    /** Processed noise is immutable for the exact native context; physical block custody is never cached here. */
    public int height(int x,int z){
        if(!overworld()||!NativeAccurateTerrain.enabled())return nativeHeight(x,z);
        if(generator!=level.getChunkSource().getGenerator()||initialState!=level.getChunkSource().randomState())
            throw new IllegalStateException("Native terrain generator/state changed during finite planning");
        Object lookup=NativeAccurateTerrain.lookup(initialState);long key=ChunkPos.asLong(x,z);
        synchronized(processedHeights){
            if(processedLookup==null)processedLookup=lookup;
            else if(processedLookup!=lookup)throw new IllegalStateException("Native terrain lookup changed during finite planning");
            Integer known=processedHeights.get(key);if(known!=null)return known;
        }
        int sampled=nativeHeight(x,z);
        if(generator!=level.getChunkSource().getGenerator()||initialState!=level.getChunkSource().randomState()||lookup!=NativeAccurateTerrain.lookup(initialState))throw new IllegalStateException("Native terrain context changed during sampling");
        synchronized(processedHeights){
            processedHeights.put(key,sampled);
            if(processedHeights.size()>8192)processedHeights.remove(processedHeights.keySet().iterator().next());
        }
        return sampled;
    }
    public int cachedHeightColumns(){synchronized(processedHeights){return processedHeights.size();}}
    public String biome(int x,int y,int z){
        return NativeAccurateTerrain.query(level,()->generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(x),QuartPos.fromBlock(y),QuartPos.fromBlock(z),
                level.getChunkSource().randomState().sampler()).unwrapKey().map(k->k.location().toString()).orElse("minecraft:plains"));
    }
    @Override public GeologyPlanner.Site sample(int x,int z){
        int surface=height(x,z);String biome=biome(x,surface+4,z);Set<String> families=GeologyConfig.families(biome);
        // A cave biome may occupy this quart near a cave mouth. Look upward without assuming a generic plains geology.
        for(int dy=16;families.isEmpty()&&dy<=96;dy+=16){String above=biome(x,surface+dy,z);Set<String> group=GeologyConfig.families(above);if(!group.isEmpty()){families=group;biome=above;}}
        var thresholds=object(get().settings(),"terrainThresholds");
        int mountain=integer(thresholds,"mountainSurfaceY",120),extreme=integer(thresholds,"extremeSurfaceY",190);
        String terrain=surface>=extreme?"extreme":surface>=mountain||families.contains("mountain_highland")?"mountain":"normal";
        if(GeologyConfig.bool(get().settings(),"useNativeTerrainClassification",false)){
            var nativeTerrain=ReTerraForgedGeography.fromRandomState(level.getChunkSource().randomState()).sample(x,z);
            Set<String> corrected=new LinkedHashSet<>(families);corrected.remove("mountain_highland");families=Set.copyOf(corrected);
            terrain=nativeTerrain.mountain()?(surface>=extreme?"extreme":"mountain"):"normal";
        }
        if(!terrain.equals("normal")){Set<String> expanded=new LinkedHashSet<>(families);expanded.add("mountain_highland");families=Set.copyOf(expanded);}
        return new GeologyPlanner.Site(biome,families,terrain,surface);
    }
    @Override public int caveY(int x,int z,int preferred,int min,int max){
        var column=NativeAccurateTerrain.query(level,()->generator.getBaseColumn(x,z,level,level.getChunkSource().randomState()));
        int reach=integer(object(get().settings(),"geometry"),"caveSearchRange",24);
        for(int d=0;d<=reach;d++)for(int sign:new int[]{1,-1}){
            int y=preferred+d*sign;
            if(y<min||y>max-3)continue;
            if(column.getBlock(y).isSolid()&&column.getBlock(y+1).isAir()&&column.getBlock(y+2).isAir())return y-2;
        }
        return preferred;
    }
    public List<BlockPos> shape(GeologyPlanner.Plan plan){
        if(MassiveDeposits.enabled(get()))throw new IllegalStateException("Massive deposits require chunk-local geometry");
        long seed=plan.candidate().seed();List<BlockPos> found=shapes.get(seed);if(found!=null)return found;
        var center=plan.candidate();
        List<BlockPos> positions=GeologyMath.shape(seed,plan.intendedSize(),plan.id().equals("coal")).stream()
                .map(p->new BlockPos(center.x()+p.x(),center.y()+p.y(),center.z()+p.z())).toList();
        synchronized(shapes){if(shapes.size()>=128)shapes.remove(shapes.keySet().iterator().next());shapes.put(seed,positions);}
        return positions;
    }
    @Override public int fitY(GeologyPlanner.Plan plan){
        return fit(plan,null);
    }
    /** Revalidate an admitted center without choosing a new preferred height. */
    int fitAtY(GeologyPlanner.Plan plan,int centerY){return fit(plan,centerY);}
    /** Existing native density cavities only; no chunk requests, carvers or buried fallback.
     * Native physical exposure through FEATURES remains a separate integration check. */
    public int fitExistingCave(GeologyPlanner.Plan plan,Integer committedY){
        if(!level.getServer().isSameThread())throw new IllegalStateException("Native cave planning requires server thread");
        if(generator!=level.getChunkSource().getGenerator()||initialState!=level.getChunkSource().randomState())
            throw new IllegalStateException("Native cave generator/state changed");
        var c=plan.candidate();
        var column=NativeAccurateTerrain.query(level,()->generator.getBaseColumn(c.x(),c.z(),level,initialState));
        var geometry=object(get().settings(),"geometry");
        int min=level.getMinBuildHeight()+integer(geometry,"formationBedrockClearance",6);
        int max=Math.min(level.getMaxBuildHeight()-2,c.site().surfaceY()-8);
        if(max<min)return Integer.MIN_VALUE;
        // A large body need not have its center below the cave floor. Every central-column
        // contact preserves the same complete geometry; select a fitting vertical translation.
        var offsets=GeologyMath.shape(c.seed(),plan.intendedSize(),plan.id().equals("coal"));
        var contacts=offsets.stream().filter(p->p.x()==0&&p.z()==0).map(GeologyMath.Voxel::y).distinct().toList();
        if(contacts.isEmpty())return Integer.MIN_VALUE;
        int low=min-offsets.stream().mapToInt(GeologyMath.Voxel::y).min().orElseThrow();
        int high=max-offsets.stream().mapToInt(GeologyMath.Voxel::y).max().orElseThrow();
        int[] selected={Integer.MIN_VALUE};
        var result=CaveDirectedLocations.fit(new CaveDirectedLocations.Column(){
            public boolean air(int y){return column.getBlock(y).isAir();}
            public boolean solid(int y){return GeologyFeature.replaceable(column.getBlock(y));}
        },min,max,c.y(),nominal->{
            int floorY=nominal+2;
            var centers=contacts.stream().map(dy->floorY-dy).filter(y->y>=low&&y<=high)
                    .filter(y->committedY==null||committedY.intValue()==y.intValue())
                    .sorted(Comparator.<Integer>comparingLong(y->Math.abs((long)y-c.y())).thenComparingInt(Integer::intValue)).toList();
            for(int y:centers)if(fitAtY(plan,y)==y){selected[0]=y;return true;}
            return false;
        });
        return result.isPresent()?selected[0]:Integer.MIN_VALUE;
    }
    private int fit(GeologyPlanner.Plan plan,Integer committedY){
        if(MassiveDeposits.enabled(get()))throw new IllegalStateException("Massive geometry needs its own fitting policy");
        var c=plan.candidate();var definition=plan.definition();var geometry=object(get().settings(),"geometry");
        int floor=level.getMinBuildHeight()+integer(geometry,"formationBedrockClearance",6),ceiling=level.getMaxBuildHeight()-2;
        Map<Long,Integer> heights=new HashMap<>();Map<Long,GeologyPlanner.Site> sites=new HashMap<>();
        sites.put(ChunkPos.asLong(c.x(),c.z()),c.site());
        var band=formationBand(definition,c.site(),c.y(),floor,ceiling);
        var centerBounds=new FormationFitting.Column(band[0],Math.min(band[1],c.site().surfaceY()-GeologyPlacement.centerCover(definition,c.site(),8)));
        var offsets=GeologyMath.shape(c.seed(),plan.intendedSize(),plan.id().equals("coal"));
        java.util.function.BiFunction<Integer,Integer,FormationFitting.Column> terrain=(x,z)->{
            var site=sites.computeIfAbsent(ChunkPos.asLong(x,z),ignored->sample(x,z));
            var rules=object(definition,"placement");var biomes=array(rules,"requiredSurfaceBiomes");
            if(!GeologyPlacement.habitatAllows(definition,site)||!biomes.isEmpty()&&!contains(biomes,site.biome()))return null;
            var limits=formationBand(definition,site,c.y(),floor,ceiling);
            int cover=GeologyPlacement.exteriorCover(definition,site,integer(geometry,"exteriorCover",3));
            int top=site.surfaceY();heights.put(ChunkPos.asLong(x,z),top);
            if(cover>0)for(Direction d:new Direction[]{Direction.NORTH,Direction.SOUTH,Direction.EAST,Direction.WEST}){
                long nx=(long)x+d.getStepX(),nz=(long)z+d.getStepZ();
                if(nx<Integer.MIN_VALUE||nx>Integer.MAX_VALUE||nz<Integer.MIN_VALUE||nz>Integer.MAX_VALUE)return null;
                int px=(int)nx,pz=(int)nz;top=Math.min(top,heights.computeIfAbsent(ChunkPos.asLong(px,pz),ignored->height(px,pz)));
            }
            return new FormationFitting.Column(limits[0],Math.min(limits[1],top-1-cover));
        };
        var result=committedY==null?FormationFitting.fit(c.x(),c.y(),c.z(),offsets,centerBounds,terrain)
                :FormationFitting.at(c.x(),committedY,c.z(),offsets,centerBounds,terrain);
        if(!result.fits())return Integer.MIN_VALUE;
        List<BlockPos> positions=offsets.stream().map(p->new BlockPos(c.x()+p.x(),result.centerY()+p.y(),c.z()+p.z())).toList();
        synchronized(shapes){if(shapes.size()>=128)shapes.remove(shapes.keySet().iterator().next());shapes.put(c.seed(),positions);}
        return result.centerY();
    }
    private static int[] formationBand(com.google.gson.JsonObject definition,GeologyPlanner.Site site,int originalY,int floor,int ceiling){
        var rules=object(definition,"placement");int low=Math.max(floor,integer(rules,"minY",Integer.MIN_VALUE)),high=ceiling;
        if(GraphitePlacement.diamondDepth(definition,originalY)){
            // Select the connected original diamond band; never shift across a forbidden gap.
            var intervals=new ArrayList<int[]>();
            for(var b:array(array(definition,"associated").get(0).getAsJsonObject(),"depthBands")){
                var band=b.getAsJsonObject();intervals.add(new int[]{integer(band,"minY",0),integer(band,"maxY",0)});
            }
            intervals.sort(Comparator.comparingInt(a->a[0]));int start=intervals.get(0)[0],end=intervals.get(0)[1];
            for(int i=1;i<=intervals.size();i++){
                if(i<intervals.size()&&(long)intervals.get(i)[0]<=1L+end){end=Math.max(end,intervals.get(i)[1]);continue;}
                if(originalY>=start&&originalY<=end)return new int[]{Math.max(low,start),Math.min(high,end)};
                if(i<intervals.size()){start=intervals.get(i)[0];end=intervals.get(i)[1];}
            }
            return new int[]{1,0};
        }
        if(rules.has("absoluteY")){var band=GeologyPlacement.absoluteY(definition,site);low=Math.max(low,(int)band[0]);high=Math.min(high,(int)band[1]);}
        return GeologyPlacement.restrictSurfaceDepth(definition,site,low,high);
    }
    /** Boolean host searches do not materialize a massive body's entire chunk slice. */
    public boolean anyMatchChunk(GeologyPlanner.Plan plan,ChunkPos chunk,int minY,int maxY,
            MassiveDepositGeometry.VoxelPredicate predicate) {
        Objects.requireNonNull(predicate,"predicate");
        if(MassiveDeposits.enabled(get()))return MassiveDepositGeometry.anyMatchChunk(
                MassiveDeposits.body(plan,MassiveDeposits.settings(get())),chunk.x,chunk.z,minY,maxY,predicate);
        for(BlockPos p:shape(plan)){
            if((p.getX()>>4)==chunk.x&&(p.getZ()>>4)==chunk.z&&p.getY()>=minY&&p.getY()<maxY
                    &&predicate.test(p.getX(),p.getY(),p.getZ()))return true;
        }
        return false;
    }
    /** Short-lived owner-chunk positions only; never retain a million-block body in the shape cache. */
    public List<BlockPos> chunkShape(GeologyPlanner.Plan plan,ChunkPos chunk,int minY,int maxY) {
        if(!MassiveDeposits.enabled(get()))return shape(plan);
        List<BlockPos> result=new ArrayList<>();
        MassiveDepositGeometry.visitChunk(MassiveDeposits.body(plan,MassiveDeposits.settings(get())),chunk.x,chunk.z,minY,maxY,
                (x,y,z)->result.add(new BlockPos(x,y,z)));
        return result;
    }
}
