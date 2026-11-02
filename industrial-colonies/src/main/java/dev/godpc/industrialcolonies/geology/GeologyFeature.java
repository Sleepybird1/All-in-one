package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.*;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** All writes are clipped to the owning chunk. Only tagged stone/deepslate is replaced; air, fluids and bedrock are preserved. */
public final class GeologyFeature extends Feature<NoneFeatureConfiguration> {
    public GeologyFeature(){super(NoneFeatureConfiguration.CODEC);}
    @Override public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context){
        if(context.level().getLevel().getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return false;
        WorldGenLevel level=context.level();if(!enabled()||level.getLevel().dimension()!=Level.OVERWORLD)return false;
        ChunkPos chunk=new ChunkPos(context.origin());GeologyWorld world=GeologyWorld.of(level.getLevel());
        // Surface details remain in ordinary decoration. Deposits already exist before any neighboring FEATURES writes.
        boolean changed=traces(level,chunk,world);changed|=placer(level,chunk,world);changed|=LocalBiomeCinnabarFeature.generate(level,chunk);changed|=SurfaceRockClues.generate(level,chunk,world);return changed;
    }
    /** Called after this owner's carvers finish, before CARVERS becomes available to neighboring decoration. */
    public static boolean generateDeposits(WorldGenLevel level,ChunkPos chunk){
        return generateDeposits(level,chunk,Set.of());
    }
    /** Explicit staged replacement ownership; unlisted families and independent traces retain their rules. */
    public static boolean generateDeposits(WorldGenLevel level,ChunkPos chunk,Set<String> excludedFamilies){
        if(level.getLevel().getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return false;
        if(!enabled()||level.getLevel().dimension()!=Level.OVERWORLD)return false;
        var bound=NativeContinentLevels.excludedFamilies(level.getLevel());
        if(WorldStartCinnabarRuntime.localBiomeMode()||WorldStartCinnabarRuntime.find(level.getLevel()).isPresent()){var surfaceBound=new HashSet<>(bound);surfaceBound.add("cinnabar");bound=Set.copyOf(surfaceBound);}
        if(!bound.isEmpty()){var union=new HashSet<>(excludedFamilies);union.addAll(bound);excludedFamilies=Set.copyOf(union);}
        GeologyWorld world=GeologyWorld.of(level.getLevel());
        var known=new HashSet<String>();for(var d:world.planner.definitions())known.add(d.get("id").getAsString());
        if(!known.containsAll(excludedFamilies))throw new IllegalArgumentException("Unknown excluded mineral family");
        int region=world.planner.regionSize(),rx=Math.floorDiv(chunk.getMiddleBlockX(),region),rz=Math.floorDiv(chunk.getMiddleBlockZ(),region);
        boolean changed=false,major=false;
        // CARVERS neighbors need not yet contain terrain. Never consult their mutable/missing heightmaps.
        Map<Long,Integer> noiseHeights=new HashMap<>();
        if(MassiveDeposits.enabled(get())){
            BitSet claimed=new BitSet();
            int bottom=level.getMinBuildHeight()+1;
            for(var deposit:MassiveDeposits.discover(world.planner,MassiveDeposits.settings(get()),chunk.x,chunk.z)){
                if(excludedFamilies.contains(deposit.plan().id()))continue;
                List<BlockPos> geometry=new ArrayList<>();
                MassiveDepositGeometry.visitChunk(deposit.body(),chunk.x,chunk.z,level.getMinBuildHeight()+1,level.getMaxBuildHeight(),(x,y,z)->{
                    // Fixed geometric ownership, independent of generation order or replaceable-block tags.
                    int index=(y-bottom)*256+(z&15)*16+(x&15);
                    if(claimed.get(index))return;
                    claimed.set(index);
                    geometry.add(new BlockPos(x,y,z));
                });
                int placed=major(level,chunk,world,deposit.plan(),geometry,noiseHeights);
                changed|=placed>0;major|=placed>0;
            }
            if(!major)changed|=micro(level,chunk,world,excludedFamilies);
            changed|=CaveTraceFeature.generate(level,chunk,world);
            return changed;
        }
        // The configured maximum intended volume is bounded; search neighboring regions even at negative boundaries.
        int search=integer(object(get().settings(),"geometry"),"regionSearchRadius",1);
        int reach=(int)Math.ceil(6*Math.cbrt(integer(object(get().settings(),"geometry"),"maxIntendedBlocks",50000)));
        search=Math.max(search,(int)Math.ceil((double)reach/region));
        for(int x=rx-search;x<=rx+search;x++)for(int z=rz-search;z<=rz+search;z++){
            if(!world.planner.mayReach(x,z,chunk.getMinBlockX(),chunk.getMinBlockZ(),chunk.getMaxBlockX(),chunk.getMaxBlockZ(),reach))continue;
            GeologyPlanner.Decision decision=world.planner.decide(x,z);if(decision.plan()==null){GeologyDebug.rejected(x,z,decision);continue;}
            GeologyPlanner.Plan plan=decision.plan();if(excludedFamilies.contains(plan.id()))continue;List<BlockPos> geometry=world.shape(plan);
            if(geometry.stream().noneMatch(p->owns(chunk,p)))continue;
            int placed=major(level,chunk,world,plan,geometry,noiseHeights);changed|=placed>0;major|=placed>0;
        }
        if(!major)changed|=micro(level,chunk,world,excludedFamilies);
        changed|=CaveTraceFeature.generate(level,chunk,world);
        return changed;
    }
    /** Staged explicit owner entry; callers must hold native CARVERS completion and
     * supply an admitted continent plan. No discovery, neighbor loads or legacy fallback. */
    public static int placeContinentOwner(net.minecraft.server.level.WorldGenRegion level,
            net.minecraft.world.level.chunk.ChunkAccess owner,NativeContinentDiscovery discovery)throws java.io.IOException{
        return placeContinentOwner(level,owner,discovery,(request,actual)->{});
    }
    public static int placeContinentOwner(net.minecraft.server.level.WorldGenRegion level,
            net.minecraft.world.level.chunk.ChunkAccess owner,NativeContinentDiscovery discovery,
            java.util.function.BiConsumer<ContinentOccurrenceLedger.Request,List<BlockPos>> record)throws java.io.IOException{
        Objects.requireNonNull(record);
        if(!level.getLevel().getServer().isSameThread())throw new IllegalStateException("Server mailbox required");
        if(level.getLevel().dimension()!=Level.OVERWORLD||owner.isUpgrading()
                ||!owner.getPersistedStatus().isBefore(net.minecraft.world.level.chunk.status.ChunkStatus.CARVERS)
                ||!level.getCenter().equals(owner.getPos()))throw new IllegalStateException("Fresh CARVERS owner required");
        // Re-read the durable occurrence and native configuration before any writes.
        NativeContinentDiscovery.Progress admitted=discovery.advance(1);
        if(admitted.status()!=NativeContinentDiscovery.Status.PRESENT||admitted.plan().isEmpty()
                ||admitted.occurrence().isEmpty()||!admitted.occurrence().get().present())
            throw new IllegalArgumentException("Present committed continent admission required: status="+admitted.status()
                    +", observed="+discovery.observedSelection()+", committed="+admitted.occurrence().map(e->e.request().candidate()));
        GeologyWorld world=GeologyWorld.of(level.getLevel());
        GeologyPlanner.Plan plan=ContinentPlanComposition.compose(admitted.plan().get(),world.planner,get().settings());
        var request=admitted.occurrence().get().request();var selected=request.candidate();var c=plan.candidate();
        if(!request.key().family().equals(plan.id())||c.x()!=selected.x()||c.y()!=selected.y()||c.z()!=selected.z()
                ||c.seed()!=selected.geometrySeed()||plan.intendedSize()!=selected.cells())
            throw new IllegalArgumentException("Composition differs from committed selection");
        // Surface clues need their own accounting; never add unbudgeted ore outside this body.
        return major(level,owner.getPos(),world,plan,world.shape(plan),new HashMap<>(),false,actual->record.accept(request,actual));
    }
    /** Coal shares the caller's open owner ledger with optional minerals; it never seals separately. */
    static int placeCoalOwner(net.minecraft.server.level.WorldGenRegion level,
            net.minecraft.world.level.chunk.ChunkAccess owner,NativeCoalCoordinator coordinator,String slot)throws java.io.IOException {
        coordinator.requireLevel(level.getLevel());
        if(level.getLevel().dimension()!=Level.OVERWORLD||owner.isUpgrading()
                ||!owner.getPersistedStatus().isBefore(net.minecraft.world.level.chunk.status.ChunkStatus.CARVERS)
                ||!level.getCenter().equals(owner.getPos())||!owner.hasData(MiningOreOwnership.LEDGER)
                ||owner.getData(MiningOreOwnership.LEDGER).sealed()||owner.getData(MiningOreOwnership.LEDGER).failed())throw new IllegalStateException("Fresh owner with open provenance required");
        var admitted=coordinator.admit(slot);var world=GeologyWorld.of(level.getLevel());
        var plan=ContinentPlanComposition.compose(admitted.plan(),world.planner,get().settings());
        var selected=admitted.reservation().selected();var c=plan.candidate();
        if(!plan.id().equals("coal")||c.x()!=selected.x()||c.y()!=selected.y()||c.z()!=selected.z()
                ||c.seed()!=selected.geometrySeed()||plan.intendedSize()!=selected.cells())throw new IllegalStateException("Coal composition changed saved selection");
        return major(level,owner.getPos(),world,plan,world.shape(plan),new HashMap<>(),false,
                actual->MiningOreOwnership.recordCoal(owner,admitted.reservation(),actual));
    }
    private static int major(WorldGenLevel level,ChunkPos chunk,GeologyWorld world,GeologyPlanner.Plan plan,List<BlockPos> geometry,Map<Long,Integer> noiseHeights){
        return major(level,chunk,world,plan,geometry,noiseHeights,true);
    }
    private static int major(WorldGenLevel level,ChunkPos chunk,GeologyWorld world,GeologyPlanner.Plan plan,List<BlockPos> geometry,Map<Long,Integer> noiseHeights,boolean allowIndicators){
        return major(level,chunk,world,plan,geometry,noiseHeights,allowIndicators,actual->{});
    }
    private static int major(WorldGenLevel level,ChunkPos chunk,GeologyWorld world,GeologyPlanner.Plan plan,List<BlockPos> geometry,Map<Long,Integer> noiseHeights,boolean allowIndicators,java.util.function.Consumer<List<BlockPos>> record){
        BlockState host=state(plan.definition().get("hostRock").getAsString());
        List<BlockPos> actual=new ArrayList<>();
        Map<BlockPos,BlockState> deepOriginals=new HashMap<>();
        int cover=integer(object(get().settings(),"geometry"),"exteriorCover",3);
        Map<Long,GeologyPlanner.Site> placementSites=new HashMap<>();
        for(BlockPos p:geometry)if(owns(chunk,p)&&validY(level,p)&&allowedPlacement(world,plan.definition(),p,placementSites)
                &&covered(world,noiseHeights,p,GeologyPlacement.exteriorCover(plan.definition(),placementSites.get(ChunkPos.asLong(p.getX(),p.getZ())),cover))&&replaceable(level.getBlockState(p))){
            if(GraphitePlacement.enabled(plan.definition())&&!GraphitePlacement.ordinary(plan.definition(),p.getY()))
                deepOriginals.put(p,level.getBlockState(p));
            if(level.setBlock(p,host,2))actual.add(p);
        }
        if(actual.isEmpty())return 0;
        if(WorldStartVeridiumPolicy.isPlan(plan)){
            int ore=WorldStartVeridiumPolicy.placeOre(level,plan,geometry,actual);
            record.accept(List.copyOf(actual));
            NearbyVeinClues.record(level.getLevel(),plan.id(),actual);
            GeologyDebug.record(level.getLevel(),chunk,plan,actual.size(),0,0,Map.of(WorldStartVeridiumPolicy.ORE,ore),Map.of(),0);
            return actual.size();
        }
        long chunkSeed=seed(plan.candidate().seed(),chunk.x,chunk.z,0x484f5354);
        Set<BlockPos> remaining=new HashSet<>(actual);
        int richTarget=quota(actual.size(),plan.richFraction(),chunkSeed,false),richPlaced=0;
        JsonArray rich=array(plan.definition(),"richOres");
        double[] richWeights=new double[rich.size()];
        for(int i=0;i<rich.size();i++)richWeights[i]=number(rich.get(i).getAsJsonObject(),"weight",1);
        int[] richAmounts=split(richTarget,richWeights,chunkSeed+0x50474d);
        var geometryRules=object(get().settings(),"geometry");
        for(int i=0;i<rich.size();i++){
            JsonObject entry=rich.get(i).getAsJsonObject();
            richPlaced+=clusters(level,remaining,richAmounts[i],state(entry.get("block").getAsString()),chunkSeed+100+i,
                    integer(geometryRules,"richClusterMin",3),integer(geometryRules,"richClusterMax",8),0,0);
        }
        Map<String,Integer> associated=new LinkedHashMap<>();Map<String,String> rolls=new LinkedHashMap<>();
        int ruleIndex=0;
        for(JsonElement element:array(plan.definition(),"associated")){
            JsonObject rule=element.getAsJsonObject();String block=rule.get("block").getAsString();long depositRoll=plan.candidate().seed()+1000+ruleIndex++;
            double chance=numbers(rule,"chanceByQuality")[plan.quality()];boolean succeeds=unit(depositRoll)<chance;
            rolls.put(block,"chance="+chance+", roll="+unit(depositRoll)+", success="+succeeds);
            if(!succeeds){associated.put(block,0);continue;}
            int count=0;
            if(string(rule,"type","").equals("depth_percentage")){
                for(JsonElement bandElement:array(rule,"depthBands")){
                    JsonObject band=bandElement.getAsJsonObject();int min=integer(band,"minY",Integer.MIN_VALUE),max=integer(band,"maxY",Integer.MAX_VALUE);
                    List<BlockPos> bandActual=actual.stream().filter(p->p.getY()>=min&&p.getY()<=max).toList();
                    Set<BlockPos> available=new HashSet<>(bandActual);available.retainAll(remaining);
                    int target=quota(bandActual.size(),numbers(band,"byQuality")[plan.quality()],chunkSeed+depositRoll+min,false);
                    count+=associatedClusters(level,remaining,available,target,rule,chunkSeed+depositRoll+min);
                }
            }else{
                JsonArray range=array(rule,"byQuality").get(plan.quality()).getAsJsonArray();
                double fraction=lerp(range.get(0).getAsDouble(),range.get(1).getAsDouble(),unit(depositRoll+44));
                int target=quota(actual.size(),fraction,chunkSeed+depositRoll,bool(rule,"guaranteeWhenPositive",false));
                rolls.put(block,rolls.get(block)+", fraction="+fraction);
                count=associatedClusters(level,remaining,new HashSet<>(remaining),target,rule,chunkSeed+depositRoll);
            }
            associated.put(block,count);
        }
        // A zero-rounded diamond quota must not leave an ordinary deep graphite deposit.
        // Restore exact pre-generation stone/deepslate, never force an extra diamond.
        if(!deepOriginals.isEmpty()&&associated.getOrDefault(GraphitePlacement.DIAMOND,0)==0){
            Set<BlockPos> written=new HashSet<>(actual);
            for(var entry:deepOriginals.entrySet())if(written.contains(entry.getKey())){
                if(!level.setBlock(entry.getKey(),entry.getValue(),2))throw new IllegalStateException("Failed to restore diamond-free graphite host");
            }
            actual.removeAll(deepOriginals.keySet());
        }
        if(actual.isEmpty())return 0;
        int indicators=allowIndicators?indicators(level,chunk,plan,host,geometry,chunkSeed):0;
        if(MassiveDeposits.enabled(get()))MiningOreOwnership.record(level,chunk,plan,actual);
        record.accept(List.copyOf(actual));
        NearbyVeinClues.record(level.getLevel(),plan.id(),actual);
        GeologyDebug.record(level.getLevel(),chunk,plan,actual.size(),richTarget,richPlaced,associated,rolls,indicators);
        return actual.size();
    }
    private static int associatedClusters(WorldGenLevel level,Set<BlockPos> all,Set<BlockPos> available,int target,JsonObject rule,long seed){
        Set<BlockPos> before=new HashSet<>(available);
        int count=clusters(level,available,target,state(rule.get("block").getAsString()),seed,integer(rule,"clusterMin",1),integer(rule,"clusterMax",2),
                number(rule,"jackpotChance",0),integer(rule,"jackpotMax",3));
        before.removeAll(available);all.removeAll(before);return count;
    }
    /** Count-driven randomized connected walks; never a fixed number of rich veins. */
    static int clusters(WorldGenLevel level,Set<BlockPos> available,int target,BlockState state,long seed,int min,int max,double jackpot,int jackpotMax){
        List<BlockPos> starts=new ArrayList<>(available);starts.sort(Comparator.comparingLong(p->mix(p.asLong()^seed)));
        int count=0,sequence=0;
        for(BlockPos start:starts){
            if(count>=target)break;if(!available.contains(start))continue;
            int cluster=min+bounded(seed+sequence++,Math.max(1,max-min+1));
            if(unit(seed+sequence+917)<jackpot)cluster=jackpotMax;
            ArrayDeque<BlockPos> frontier=new ArrayDeque<>();frontier.add(start);
            int budget=Math.min(cluster,target-count),made=0;
            while(!frontier.isEmpty()&&made<budget){
                BlockPos p=frontier.removeFirst();if(!available.remove(p))continue;
                if(level.setBlock(p,state,2)){count++;made++;}
                int first=bounded(seed+p.asLong(),6);
                for(int i=0;i<6;i++){BlockPos neighbor=p.relative(Direction.values()[(first+i)%6]);if(available.contains(neighbor))frontier.addLast(neighbor);}
            }
        }
        return count;
    }
    private static int indicators(WorldGenLevel level,ChunkPos chunk,GeologyPlanner.Plan plan,BlockState host,List<BlockPos> geometry,long seed){
        if(NearbyVeinClues.enabled())return 0;
        JsonObject rules=object(get().settings(),"indicators");if(!bool(rules,"enabled",true))return 0;
        if(!plan.definition().get("hostRock").getAsString().startsWith("industrial_colonies:"))return 0;
        // Approved low-yield hosts only, never new clues or rich/radioactive ore splashed across mountains.
        if(plan.id().equals("uranium")||plan.id().equals("thorium"))return 0;
        JsonObject terrain=object(object(get().settings(),"terrain"),plan.candidate().site().terrain());
        double chance=number(rules,"chancePerDepositChunk",.025)*number(terrain,"indicatorExposure",1);
        if(unit(seed+777)>chance)return 0;
        // Massive geometry is already filtered to its canonical owner; legacy geometry is the full vein.
        var permittedOutcrop=SurfaceOutcropPolicy.permittedPositions(GeologyPlanner.family(plan.definition()),geometry);
        int reach=integer(rules,"maxVerticalDistance",28),max=integer(rules,"maxBlocksPerDepositChunk",2),count=0;
        List<BlockPos> ordered=geometry.stream().filter(p->owns(chunk,p)).sorted(Comparator.comparingLong(p->mix(seed^p.asLong()))).toList();
        Set<Long> columns=new HashSet<>();
        Map<Long,GeologyPlanner.Site> placementSites=new HashMap<>();
        for(BlockPos p:ordered){
            long column=ChunkPos.asLong(p.getX(),p.getZ());if(!columns.add(column))continue;
            int y=level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG,p.getX(),p.getZ())-1;
            if(Math.abs(y-p.getY())>reach)continue;BlockPos outcrop=new BlockPos(p.getX(),y,p.getZ());
            if(!permittedOutcrop.test(outcrop))continue;
            if(allowedPlacement(GeologyWorld.of(level.getLevel()),plan.definition(),outcrop,placementSites)&&replaceable(level.getBlockState(outcrop))&&level.getBlockState(outcrop.above()).isAir()&&level.setBlock(outcrop,host,2))count++;
            if(count>=max)break;
        }
        return count;
    }
    private static boolean micro(WorldGenLevel level,ChunkPos chunk,GeologyWorld world,Set<String> excludedFamilies){
        if(NearbyVeinClues.enabled())return false;
        long seed=seed(level.getSeed(),chunk.x,chunk.z,0x4d4943524fL);JsonObject settings=get().settings(),rules=object(settings,"micro");
        JsonObject diamond=object(rules,"diamond");
        double scale=number(rules,"frequencyMultiplier",1),cap=number(rules,"maxChancePerChunk",1),upper=0;
        for(JsonObject definition:world.planner.definitions()){
            if(excludedFamilies.contains(definition.get("id").getAsString()))continue;
            JsonObject m=object(definition,"micro");if(bool(m,"enabled",false))upper=Math.max(upper,number(m,"chance",0));
        }
        boolean tryMineral=unit(seed+4)<Math.min(cap,upper*scale);
        boolean tryDiamond=bool(diamond,"enabled",true)&&unit(seed+8)<number(diamond,"chancePerChunk",.0002);
        if(!tryMineral&&!tryDiamond)return false;
        int x=chunk.getMinBlockX()+2+bounded(seed+1,12),z=chunk.getMinBlockZ()+2+bounded(seed+2,12);
        GeologyPlanner.Site site=world.sample(x,z);JsonObject depth=object(settings,"depth");
        int min=integer(depth,"minY",-60),max=Math.min(integer(depth,"maxY",64),site.surfaceY()-6);
        if(max<min)return false;int y=min+bounded(seed+3,max-min+1);BlockPos pos=new BlockPos(x,y,z);
        if(tryMineral){
            List<JsonObject> defs=world.planner.definitions();double[] weights=new double[defs.size()];
            for(int i=0;i<defs.size();i++){JsonObject d=defs.get(i),m=object(d,"micro");
                if(excludedFamilies.contains(d.get("id").getAsString()))continue;
                int mineralY=GeologyPlanner.microY(d,site,y,seed);
                if(mineralY!=Integer.MIN_VALUE&&bool(m,"enabled",false)&&number(m,"chance",0)>0)weights[i]=world.planner.weight(d,site,mineralY);}
            int selected=weighted(weights,unit(seed+5));
            if(selected>=0){JsonObject def=defs.get(selected),m=object(def,"micro");JsonArray rich=array(def,"richOres");
                String id=rich.isEmpty()?def.get("hostRock").getAsString():rich.get(0).getAsJsonObject().get("block").getAsString();
                if(unit(seed+4)<Math.min(cap,number(m,"chance",0)*scale)){
                    BlockPos mineralPos=new BlockPos(x,GeologyPlanner.microY(def,site,y,seed),z);
                    Map<Long,GeologyPlanner.Site> placementSites=new HashMap<>();
                    return tiny(level,chunk,mineralPos,state(id),Math.min(integer(rules,"maxBlocks",3),microSize(m,seed+6)),seed+7,
                            level.getMaxBuildHeight()-2,p->allowedPlacement(world,def,p,placementSites)&&NearbyVeinClues.allows(level.getLevel(),def.get("id").getAsString(),p.getX(),p.getZ()))>0;}}
        }
        if(tryDiamond&&y<=integer(diamond,"maxY",-20)){
            JsonObject graphite=world.planner.definitions().stream().filter(d->string(d,"id","").equals("graphite_rock")).findFirst().orElse(null);
            if(graphite!=null&&unit(seed+11)<Math.min(1,world.planner.biomeWeight(graphite,site)*world.planner.depthWeight(graphite,y)/2.5))
                return tiny(level,chunk,pos,state(string(diamond,"block","industrial_colonies:diamond_ore")),Math.min(integer(rules,"maxBlocks",3),microSize(diamond,seed+9)),seed+10,integer(diamond,"maxY",-20),p->NearbyVeinClues.allows(level.getLevel(),"graphite_rock",p.getX(),p.getZ()))>0;
        }
        return false;
    }
    private static int microSize(JsonObject rules,long seed){int min=integer(rules,"min",1),max=integer(rules,"max",2);
        return unit(seed)<number(rules,"jackpotChance",0)?integer(rules,"jackpotMax",3):min+bounded(seed+1,max-min+1);}
    private static int tiny(WorldGenLevel level,ChunkPos chunk,BlockPos pos,BlockState block,int count,long seed){
        return tiny(level,chunk,pos,block,count,seed,level.getMaxBuildHeight()-2);
    }
    /** A depth-limited ore must keep every neighboring cluster voxel below its ceiling, not just its center. */
    private static int tiny(WorldGenLevel level,ChunkPos chunk,BlockPos pos,BlockState block,int count,long seed,int maximumY){
        return tiny(level,chunk,pos,block,count,seed,maximumY,p->true);
    }
    private static int tiny(WorldGenLevel level,ChunkPos chunk,BlockPos pos,BlockState block,int count,long seed,int maximumY,
                            java.util.function.Predicate<BlockPos> permitted){
        Set<BlockPos> candidates=new HashSet<>();candidates.add(pos);
        for(Direction direction:Direction.values())candidates.add(pos.relative(direction));
        candidates.removeIf(p->!owns(chunk,p)||!validY(level,p)||p.getY()>maximumY||!permitted.test(p)||!replaceable(level.getBlockState(p)));
        return clusters(level,candidates,count,block,seed,count,count,0,0);
    }
    private static boolean traces(WorldGenLevel level,ChunkPos chunk,GeologyWorld world){
        if(NearbyVeinClues.enabled())return false;
        JsonObject rules=object(get().settings(),"trace");if(!bool(rules,"enabled",true))return false;
        long seed=seed(level.getSeed(),chunk.x,chunk.z,0x5452414345L);int count=0;JsonArray resources=array(rules,"resources");
        double[] weights=new double[resources.size()];for(int i=0;i<weights.length;i++)weights[i]=number(resources.get(i).getAsJsonObject(),"weight",1);
        for(int attempt=0;attempt<integer(rules,"attemptsPerChunk",4);attempt++){
            long roll=seed+attempt*313L;if(unit(roll)>number(rules,"chancePerAttempt",.35))continue;
            int x=chunk.getMinBlockX()+2+bounded(roll+1,12),z=chunk.getMinBlockZ()+2+bounded(roll+2,12);
            int surface=level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG,x,z)-1;
            int selected=weighted(weights,unit(roll+3));if(selected<0)continue;
            JsonObject resource=resources.get(selected).getAsJsonObject();
            int amount=microSize(resource,roll+4);
            for(int dy=0;dy<=integer(rules,"maxSurfaceDepth",3);dy++){
                BlockPos p=new BlockPos(x,surface-dy,z);if(!replaceable(level.getBlockState(p)))continue;
                count+=tiny(level,chunk,p,state(resource.get("block").getAsString()),amount,roll+5,level.getMaxBuildHeight()-2,q->NearbyVeinClues.allowsBlock(level.getLevel(),resource.get("block").getAsString(),q.getX(),q.getZ()));break;
            }
        }
        return count>0;
    }
    private static boolean placer(WorldGenLevel level,ChunkPos chunk,GeologyWorld world){
        JsonObject rules=object(get().settings(),"placer");if(!bool(rules,"enabled",true))return false;
        long seed=seed(level.getSeed(),chunk.x,chunk.z,0x504c41434552L);int count=0;
        for(int a=0;a<integer(rules,"attemptsPerChunk",3);a++){
            long roll=seed+a*317;if(unit(roll)>number(rules,"chancePerAttempt",.035))continue;
            int x=chunk.getMinBlockX()+bounded(roll+1,16),z=chunk.getMinBlockZ()+bounded(roll+2,16);
            int wanted=microSize(rules,roll+3);
            for(int i=0;i<wanted;i++){
                int fx=x+i;if(fx>chunk.getMaxBlockX())break;
                int y=level.getHeight(Heightmap.Types.OCEAN_FLOOR_WG,fx,z);
                BlockPos flake=new BlockPos(fx,y,z);
                String biome=level.getBiome(flake).unwrapKey().map(k->k.location().toString()).orElse("");
                if(!contains(array(rules,"riverBiomes"),biome))continue;
                if(RiverGoldPlacement.place(level,chunk,flake))count++;
            }
        }
        return count>0;
    }
    public static boolean replaceable(BlockState state){return state.is(BlockTags.STONE_ORE_REPLACEABLES)||state.is(BlockTags.DEEPSLATE_ORE_REPLACEABLES);}
    public static boolean allowedPlacement(GeologyWorld world,JsonObject definition,BlockPos p,Map<Long,GeologyPlanner.Site> sites){
        if(!definition.has("placement"))return true;
        if(p.getY()<integer(object(definition,"placement"),"minY",Integer.MIN_VALUE))return false;
        var site=sites.computeIfAbsent(ChunkPos.asLong(p.getX(),p.getZ()),ignored->world.sample(p.getX(),p.getZ()));
        return GeologyPlanner.placementAllows(definition,site,p.getY());
    }
    private static boolean covered(GeologyWorld world,Map<Long,Integer> heights,BlockPos pos,int cover){
        if(cover<=0)return true;
        for(Direction d:new Direction[]{Direction.NORTH,Direction.SOUTH,Direction.EAST,Direction.WEST}){
            BlockPos neighbor=pos.relative(d);
            if(pos.getY()>noiseHeight(world,heights,neighbor.getX(),neighbor.getZ())-1-cover)return false;
        }
        return pos.getY()<=noiseHeight(world,heights,pos.getX(),pos.getZ())-1-cover;
    }
    private static int noiseHeight(GeologyWorld world,Map<Long,Integer> heights,int x,int z){
        return heights.computeIfAbsent(ChunkPos.asLong(x,z),ignored->world.height(x,z));
    }
    private static boolean owns(ChunkPos chunk,BlockPos p){return (p.getX()>>4)==chunk.x&&(p.getZ()>>4)==chunk.z;}
    private static boolean validY(WorldGenLevel level,BlockPos p){return p.getY()>level.getMinBuildHeight()&&p.getY()<level.getMaxBuildHeight()-1;}
    public static BlockState state(String id){ResourceLocation key=ResourceLocation.parse(id);
        if(!BuiltInRegistries.BLOCK.containsKey(key))throw new IllegalArgumentException("Unregistered geological block: "+id);
        return BuiltInRegistries.BLOCK.get(key).defaultBlockState();}
}
