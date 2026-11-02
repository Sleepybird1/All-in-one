package dev.godpc.industrialcolonies.terraincheck;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.geology.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Development-addon fixtures: exercises production placement, NOT natural occurrence or full formation sizes. */
@GameTestHolder("ic_controlled_smoke")
@PrefixGameTestTemplate(false)
public final class ControlledGeologyGameTests {
    private static final TicketType<ChunkPos> TICKET=TicketType.create("ic_controlled_smoke",Comparator.comparingLong(ChunkPos::toLong));
    private static final Comparator<BlockPos> ORDER=Comparator.comparingInt((BlockPos p)->p.getX()).thenComparingInt(BlockPos::getY).thenComparingInt(BlockPos::getZ);
    private ControlledGeologyGameTests() {}

    @GameTest(templateNamespace="ic_controlled_smoke",template="geology_smoke_empty",timeoutTicks=24000)
    public static void allProfilesAndQualities(GameTestHelper helper){new Run(helper).step();}

    private record Case(String label,JsonObject definition,int quality,int minY,boolean success,boolean protectedCells) {}
    private static final class Run {
        final GameTestHelper helper;
        final ServerLevel level;
        final long started=System.nanoTime();
        final JsonObject report=new JsonObject();
        final JsonArray results=new JsonArray();
        final List<Case> cases=new ArrayList<>();
        final Map<BlockPos,BlockState> original=new LinkedHashMap<>();
        final Map<Long,Integer> heights=new HashMap<>();
        GeologyWorld world;
        WorldGenLevel guarded;
        ChunkPos chunk;
        Method major,tiny;
        Field observations;
        Path output;
        String originalConfig;
        int index,assertions,microIndex,restoredPositions;
        boolean initialized,ended,held;

        Run(GameTestHelper helper){this.helper=helper;level=helper.getLevel();}
        void check(boolean condition,String why){assertions++;if(!condition)throw new IllegalStateException(why);}
        void step(){
            if(ended)return;
            try{
                check(level.getServer().isSameThread(),"Fixture execution left server thread");
                check((System.nanoTime()-started)/1_000_000<480000,"Controlled fixture wall budget exceeded");
                if(!initialized){initialize();initialized=true;}
                else if(index<cases.size()){runCase(cases.get(index));index++;}
                else if(microIndex<4){micro(microIndex++);}
                else{finish();return;}
                if(index%12==0){save();LogUtils.getLogger().info("GEOLOGY_CONTROLLED progress {}/{} profile cases",index,cases.size());}
                helper.runAfterDelay(1,this::step);
            }catch(Exception error){
                ended=true;report.addProperty("status","FAIL");report.addProperty("failure",error.toString());
                try{restore();save();}catch(Exception cleanup){error.addSuppressed(cleanup);}
                release();LogUtils.getLogger().error("GEOLOGY_CONTROLLED FAIL",error);helper.fail(error.toString());
            }
        }
        void initialize() throws Exception {
            Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
            String property=System.getProperty("ic.controlled.report");
            check(property!=null&&!property.isBlank(),"ic.controlled.report must point inside the disposable stage");
            Path proposed=Path.of(property).toAbsolutePath().normalize();
            check(proposed.startsWith(stage)&&!proposed.equals(stage),"Controlled report escapes stage");output=proposed;
            check(level.dimension()==Level.OVERWORLD,"Controlled fixtures require disposable Overworld");
            check(level.getChunkSource().getGenerator() instanceof NoiseBasedChunkGenerator,"Use normal noise terrain for real cover heights");
            check(enabled(),"Geology disabled");validate(get());originalConfig=configDigest();
            world=GeologyWorld.of(level);chunk=new ChunkPos(helper.absolutePos(BlockPos.ZERO));
            level.getChunkSource().addRegionTicket(TICKET,chunk,0,chunk);held=true;level.getChunk(chunk.x,chunk.z);
            guarded=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(proxy,method,args)->{
                if(args!=null&&args.length>0&&args[0] instanceof BlockPos p
                        &&Set.of("getBlockState","getFluidState","setBlock","removeBlock","destroyBlock").contains(method.getName()))
                    check(owns(p),"Production placement accessed outside owner chunk: "+method.getName()+" "+p);
                if(method.getName().equals("getHeight")&&args!=null&&args.length==3){
                    int x=(Integer)args[1],z=(Integer)args[2];check((x>>4)==chunk.x&&(z>>4)==chunk.z,"Mutable neighboring heightmap accessed");}
                // ServerLevel implements WorldGenLevel in this mapped version; resolve on the concrete receiver
                // as well so inherited/default-interface declarations cannot confuse reflective dispatch.
                Method receiver=level.getClass().getMethod(method.getName(),method.getParameterTypes());
                try{return receiver.invoke(level,args);}catch(InvocationTargetException error){throw error.getCause();}
            });
            major=GeologyFeature.class.getDeclaredMethod("major",WorldGenLevel.class,ChunkPos.class,GeologyWorld.class,GeologyPlanner.Plan.class,List.class,Map.class);major.setAccessible(true);
            tiny=GeologyFeature.class.getDeclaredMethod("tiny",WorldGenLevel.class,ChunkPos.class,BlockPos.class,BlockState.class,int.class,long.class);tiny.setAccessible(true);
            observations=GeologyDebug.class.getDeclaredField("OBSERVED");observations.setAccessible(true);
            List<JsonObject> definitions=world.planner.definitions();check(definitions.size()==24,"Expected 24 approved profiles");
            for(JsonObject d:definitions)for(int q=0;q<4;q++)cases.add(new Case("profile",d,q,-48,true,false));
            for(String id:List.of("pentlandite","thorium"))for(int q=0;q<4;q++){
                JsonObject d=find(id);double chance=numbers(array(d,"associated").get(0).getAsJsonObject(),"chanceByQuality")[q];
                if(chance>0&&chance<1)cases.add(new Case("association-failed-roll",d,q,-48,false,false));
            }
            for(int y: new int[]{-63,-53,-39,-18})for(int q=0;q<4;q++)cases.add(new Case("graphite-depth-"+y,find("graphite_rock"),q,y,true,false));
            cases.add(new Case("preserved-cells-and-owner-clip",find("chalcopyrite"),3,-48,true,true));
            report.addProperty("formatVersion",1);report.addProperty("status","RUNNING");report.addProperty("worldSeed",level.getSeed());
            report.addProperty("profileCount",definitions.size());report.addProperty("qualitiesPerProfile",4);report.addProperty("placementCases",cases.size());
            report.addProperty("fixtureVolume",512);report.addProperty("explicitFixtureChunks",1);report.addProperty("fixtureChunkX",chunk.x);report.addProperty("fixtureChunkZ",chunk.z);
            report.addProperty("configSha256Before",originalConfig);report.add("cases",results);
            report.addProperty("scope","Controlled fixed-volume 8x8x8 placement fixtures. Plans/qualities and rare-event seeds are selected, not naturally admitted. Real production major/tiny and real noise cover heights; no global config, registry, rate, or biome mutation. Fixture contents restored at completion.");
            report.addProperty("limits","Does not test natural frequency/biome admission, full configured formation sizes, the CARVERS injection, oil, GPU rendering, recipes, or gameplay balance. Pure planner and fresh-world A/B tests are separate evidence. Micro tests exercise bounded placement, not event frequency.");
            save();
        }
        JsonObject find(String id){return world.planner.definitions().stream().filter(d->string(d,"id","").equals(id)).findFirst().orElseThrow();}
        boolean owns(BlockPos p){return (p.getX()>>4)==chunk.x&&(p.getZ()>>4)==chunk.z;}
        void write(BlockPos p,BlockState state){check(owns(p),"Fixture attempted another chunk");original.putIfAbsent(p,level.getBlockState(p));level.setBlock(p,state,2);}
        List<BlockPos> geometry(int minY){
            List<BlockPos> shape=new ArrayList<>();
            for(int x=4;x<12;x++)for(int y=minY;y<minY+8;y++)for(int z=4;z<12;z++)shape.add(new BlockPos(chunk.getMinBlockX()+x,y,chunk.getMinBlockZ()+z));
            return shape;
        }
        Map<BlockPos,BlockState> protectedStates(List<BlockPos> shape){
            Map<BlockPos,BlockState> denied=new LinkedHashMap<>();
            BlockState[] blocks={Blocks.AIR.defaultBlockState(),Blocks.WATER.defaultBlockState(),Blocks.LAVA.defaultBlockState(),Blocks.BEDROCK.defaultBlockState(),Blocks.DIRT.defaultBlockState(),Blocks.GRAVEL.defaultBlockState()};
            for(int i=0;i<blocks.length;i++)denied.put(shape.get(i*17),blocks[i]);return denied;
        }
        void prepare(List<BlockPos> shape,Map<BlockPos,BlockState> denied,int q){
            for(BlockPos p:shape){check(p.getY()>level.getMinBuildHeight()&&p.getY()<level.getMaxBuildHeight()-1,"Fixture depth out of range");
                write(p,denied.getOrDefault(p,(q%2==0?Blocks.STONE:Blocks.DEEPSLATE).defaultBlockState()));
                for(BlockPos column:List.of(p,p.north(),p.south(),p.east(),p.west())){
                    int height=heights.computeIfAbsent(ChunkPos.asLong(column.getX(),column.getZ()),k->world.height(column.getX(),column.getZ()));
                    check(p.getY()<=height-1-integer(object(get().settings(),"geometry"),"exteriorCover",3),"Selected disposable arena lacks real noise cover for fixture "+p);}
            }
        }
        void runCase(Case c) throws Exception {
            List<BlockPos> shape=geometry(c.minY());Map<BlockPos,BlockState> denied=c.protectedCells()?protectedStates(shape):Map.of();
            List<BlockPos> actual=shape.stream().filter(p->!denied.containsKey(p)).toList();
            double fraction=Math.min(1,number(c.definition(),"normalRichOrePercent",0)*numbers(object(get().settings(),"quality"),"richMultipliers")[c.quality()]);
            long chosen=chooseSeed(c,actual,fraction);
            var site=new GeologyPlanner.Site("minecraft:plains",Set.of("ordinary_plains"),"normal",world.height(chunk.getMiddleBlockX(),chunk.getMiddleBlockZ()));
            BlockPos center=shape.get(shape.size()/2);
            var candidate=new GeologyPlanner.Candidate(0,0,center.getX(),center.getY(),center.getZ(),chosen,site);
            var plan=new GeologyPlanner.Plan(candidate,c.definition(),c.quality(),512,512,1,fraction,List.of(string(c.definition(),"id","")));
            List<BlockPos> requested=new ArrayList<>(shape);
            // Out-of-owner geometry is passed without reading or editing that neighboring chunk. The proxy catches any access.
            if(c.protectedCells())requested.add(new BlockPos(chunk.getMaxBlockX()+1,c.minY(),chunk.getMiddleBlockZ()));
            JsonObject result=new JsonObject();result.addProperty("label",c.label());result.addProperty("profile",plan.id());result.addProperty("quality",c.quality());
            result.addProperty("minY",c.minY());result.addProperty("maxY",c.minY()+7);result.addProperty("conditionedSeed",chosen);result.addProperty("richFraction",fraction);
            String firstHash=null;
            for(int repeat=0;repeat<2;repeat++){
                prepare(shape,denied,c.quality());
                int made=(Integer)invoke(major,guarded,chunk,world,plan,requested,new HashMap<>(heights));
                check(made==actual.size(),"Wrong actual host size for "+plan.id());
                GeologyDebug.Counts observed=observed(chosen);check(observed!=null,"Missing production placement observation");
                check(observed.host()==actual.size()&&observed.indicators()==0,"Actual/indicator record mismatch");
                Map<String,Integer> counts=new TreeMap<>();
                for(BlockPos p:actual)counts.merge(id(level.getBlockState(p)),1,Integer::sum);
                long chunkSeed=seed(chosen,chunk.x,chunk.z,0x484f5354);int target=quota(actual.size(),fraction,chunkSeed,false);
                check(observed.richTarget()==target&&observed.richPlaced()==target,"Rich target or placement mismatch");
                JsonArray ores=array(c.definition(),"richOres");double[] weights=new double[ores.size()];for(int i=0;i<weights.length;i++)weights[i]=number(ores.get(i).getAsJsonObject(),"weight",1);
                int[] allocation=split(target,weights,chunkSeed+0x50474d);int assigned=0;
                for(int i=0;i<allocation.length;i++){String ore=ores.get(i).getAsJsonObject().get("block").getAsString();check(counts.getOrDefault(ore,0)==allocation[i],"Actual rich material mismatch "+ore);assigned+=allocation[i];}
                Map<String,Integer> expected=expectedAssociations(c,actual,chosen);
                check(observed.associated().equals(expected),"Associated observations differ from configured expected quota: "+plan.id());
                for(var entry:expected.entrySet()){check(counts.getOrDefault(entry.getKey(),0).equals(entry.getValue()),"Associated actual block count mismatch "+entry.getKey());assigned+=entry.getValue();}
                check(counts.getOrDefault(c.definition().get("hostRock").getAsString(),0)==actual.size()-assigned,"Host/rich/association conservation failed");
                for(var entry:denied.entrySet())check(level.getBlockState(entry.getKey()).equals(entry.getValue()),"Air/fluid/bedrock/dirt/gravel was replaced");
                String hash=shapeHash(shape);if(firstHash==null)firstHash=hash;else check(firstHash.equals(hash),"Repeat with same Plan changed voxel layout");
                result.addProperty("actualBeforeRich",made);result.addProperty("richTarget",target);result.add("counts",new Gson().toJsonTree(counts));result.add("associated",new Gson().toJsonTree(expected));
            }
            result.addProperty("shapeStateSha256",firstHash);result.addProperty("repeatIdentical",true);result.addProperty("preservedCells",denied.size());result.addProperty("status","PASS");results.add(result);
            // In particular, restore water/lava fixtures in this same tick, before scheduled fluid updates can run.
            restore();
        }
        long chooseSeed(Case c,List<BlockPos> actual,double richFraction){
            for(int trial=0;trial<100000;trial++){
                long chosen=mix(0x434f4e54524f4cL+index*100000L+trial),chunkSeed=seed(chosen,chunk.x,chunk.z,0x484f5354);
                double indicatorChance=number(object(get().settings(),"indicators"),"chancePerDepositChunk",.025)*number(object(object(get().settings(),"terrain"),"normal"),"indicatorExposure",1);
                if(unit(chunkSeed+777)<=indicatorChance)continue;
                boolean acceptable=true;int n=0;
                for(JsonElement e:array(c.definition(),"associated")){
                    JsonObject rule=e.getAsJsonObject();double chance=numbers(rule,"chanceByQuality")[c.quality()];boolean rolled=unit(chosen+1000+n++)<chance;
                    if(chance>0&&rolled!=c.success())acceptable=false;
                }
                if(!acceptable)continue;
                Map<String,Integer> expected=expectedAssociations(c,actual,chosen);
                if(c.success()){
                    for(JsonElement e:array(c.definition(),"associated")){
                        JsonObject rule=e.getAsJsonObject();boolean positive=false;
                        if(string(rule,"type","").equals("depth_percentage"))for(JsonElement b:array(rule,"depthBands")){
                            JsonObject band=b.getAsJsonObject();positive|=numbers(band,"byQuality")[c.quality()]>0&&actual.stream().anyMatch(p->p.getY()>=integer(band,"minY",0)&&p.getY()<=integer(band,"maxY",0));}
                        else positive=array(rule,"byQuality").get(c.quality()).getAsJsonArray().get(1).getAsDouble()>0;
                        if(positive&&expected.getOrDefault(rule.get("block").getAsString(),0)==0)acceptable=false;
                    }
                }
                if(string(c.definition(),"id","").equals("ultramafic_rock")){
                    JsonArray ores=array(c.definition(),"richOres");double[] weights=new double[ores.size()];for(int i=0;i<weights.length;i++)weights[i]=number(ores.get(i).getAsJsonObject(),"weight",1);
                    for(int amount:split(quota(actual.size(),richFraction,chunkSeed,false),weights,chunkSeed+0x50474d))if(amount==0)acceptable=false;
                }
                if(acceptable)return chosen;
            }
            throw new IllegalStateException("Could not find bounded deterministic branch-coverage seed for "+c);
        }
        Map<String,Integer> expectedAssociations(Case c,List<BlockPos> actual,long chosen){
            Map<String,Integer> expected=new LinkedHashMap<>();long chunkSeed=seed(chosen,chunk.x,chunk.z,0x484f5354);int n=0;
            for(JsonElement e:array(c.definition(),"associated")){
                JsonObject rule=e.getAsJsonObject();long roll=chosen+1000+n++;int count=0;
                if(unit(roll)<numbers(rule,"chanceByQuality")[c.quality()]){
                    if(string(rule,"type","").equals("depth_percentage"))for(JsonElement b:array(rule,"depthBands")){
                        JsonObject band=b.getAsJsonObject();int min=integer(band,"minY",Integer.MIN_VALUE),max=integer(band,"maxY",Integer.MAX_VALUE);
                        int bandCount=(int)actual.stream().filter(p->p.getY()>=min&&p.getY()<=max).count();
                        count+=quota(bandCount,numbers(band,"byQuality")[c.quality()],chunkSeed+roll+min,false);
                    }else{
                        JsonArray range=array(rule,"byQuality").get(c.quality()).getAsJsonArray();double fraction=lerp(range.get(0).getAsDouble(),range.get(1).getAsDouble(),unit(roll+44));
                        count=quota(actual.size(),fraction,chunkSeed+roll,bool(rule,"guaranteeWhenPositive",false));
                    }
                }
                expected.put(rule.get("block").getAsString(),count);
            }
            return expected;
        }
        void micro(int mode) throws Exception {
            int wanted=mode<3?mode+1:3;
            BlockPos center=new BlockPos(mode==3?chunk.getMinBlockX():chunk.getMinBlockX()+8,-30,chunk.getMinBlockZ()+8);
            List<BlockPos> positions=new ArrayList<>();positions.add(center);for(var direction:net.minecraft.core.Direction.values())positions.add(center.relative(direction));
            List<BlockPos> owned=positions.stream().filter(this::owns).toList();
            for(BlockPos p:owned)write(p,Blocks.STONE.defaultBlockState());
            BlockPos protectedCell=center.above();write(protectedCell,Blocks.DIRT.defaultBlockState());
            BlockState ore=GeologyFeature.state("industrial_colonies:rich_copper_ore");
            int made=(Integer)invoke(tiny,guarded,chunk,center,ore,wanted,0x4d4943524fL+mode);
            check(made==wanted,"Bounded micro placement count mismatch");
            check(owned.stream().filter(p->level.getBlockState(p).equals(ore)).count()==wanted,"Micro actual block count mismatch");
            check(level.getBlockState(protectedCell).is(Blocks.DIRT),"Micro replaced untagged dirt");
            JsonObject result=new JsonObject();result.addProperty("label",mode==3?"micro-owner-boundary":"micro-size-"+wanted);result.addProperty("blocks",made);result.addProperty("status","PASS");results.add(result);restore();
        }
        Object invoke(Method method,Object... args) throws Exception {
            try{return method.invoke(null,args);}catch(InvocationTargetException error){Throwable cause=error.getCause();if(cause instanceof Exception e)throw e;throw error;}
        }
        @SuppressWarnings("unchecked") GeologyDebug.Counts observed(long chosen) throws Exception {
            Map<Long,Map<Long,GeologyDebug.Counts>> all=(Map<Long,Map<Long,GeologyDebug.Counts>>)observations.get(null);return all.getOrDefault(chosen,Map.of()).get(chunk.toLong());
        }
        String shapeHash(List<BlockPos> positions) throws Exception {
            StringBuilder input=new StringBuilder();positions.stream().sorted(ORDER).forEach(p->input.append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append('=').append(level.getBlockState(p)).append('\n'));return digest(input.toString());
        }
        String configDigest() throws Exception{return digest(get().settings().toString()+"\n"+get().biomes()+"\n"+get().deposits());}
        static String digest(String text) throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));}
        static String id(BlockState state){return BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();}
        void restore(){for(var entry:original.entrySet())level.setBlock(entry.getKey(),entry.getValue(),2);
            for(var entry:original.entrySet())check(level.getBlockState(entry.getKey()).equals(entry.getValue()),"Fixture restoration failed at "+entry.getKey());
            restoredPositions+=original.size();original.clear();}
        void release(){if(held){level.getChunkSource().removeRegionTicket(TICKET,chunk,0,chunk);held=false;}}
        void save() throws Exception {if(output==null)return;report.addProperty("elapsedMillis",(System.nanoTime()-started)/1_000_000);report.addProperty("assertions",assertions);report.addProperty("completedCases",results.size());Files.createDirectories(output.getParent());Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);}
        void finish() throws Exception {
            String after=configDigest();check(after.equals(originalConfig),"Global geology configuration was mutated");report.addProperty("configSha256After",after);
            restore();report.addProperty("restoredFixtureWrites",restoredPositions);release();report.addProperty("status","PASS");ended=true;save();
            LogUtils.getLogger().info("GEOLOGY_CONTROLLED PASS profiles=24 qualities=4 placementCases={} microCases=4 assertions={}",cases.size(),assertions);helper.succeed();
        }
    }
}
