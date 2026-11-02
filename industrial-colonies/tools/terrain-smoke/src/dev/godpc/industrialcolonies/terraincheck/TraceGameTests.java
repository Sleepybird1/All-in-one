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
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Test-only actual trace placement with explicit synthetic seed/flat surface, never natural availability evidence. */
@GameTestHolder("ic_trace_smoke")
@PrefixGameTestTemplate(false)
public final class TraceGameTests {
    private static final TicketType<ChunkPos> TICKET=TicketType.create("ic_trace_smoke",Comparator.comparingLong(ChunkPos::toLong));
    private TraceGameTests() {}
    @GameTest(templateNamespace="ic_trace_smoke",template="geology_smoke_empty",timeoutTicks=12000)
    public static void tracePlacementAndBounds(GameTestHelper helper){new Run(helper).step();}

    private record Attempt(String block,int count,int x,int z) {}
    private record Fixture(String name,long syntheticSeed,int depth,BlockState filler,boolean expectedPlacement) {}
    private static final class Run {
        final GameTestHelper helper;final ServerLevel level;final long started=System.nanoTime();
        final JsonObject report=new JsonObject();final JsonArray results=new JsonArray();
        final List<Fixture> fixtures=new ArrayList<>();final Map<BlockPos,BlockState> originals=new LinkedHashMap<>();
        final int surface=-20;ChunkPos chunk;GeologyWorld world;Method traces;WorldGenLevel proxy;Path output;
        JsonObject rules;Set<String> traceBlocks;String beforeConfig;long fixtureSeed;int maxDepth,budget,index,assertions,restored;boolean ready,ended,held,diamondDone;
        Run(GameTestHelper helper){this.helper=helper;level=helper.getLevel();}
        void check(boolean value,String why){assertions++;if(!value)throw new IllegalStateException(why);}
        void step(){if(ended)return;try{
            check(level.getServer().isSameThread(),"Trace fixture left server thread");
            check((System.nanoTime()-started)/1_000_000<240000,"Trace fixture exceeded four-minute wall guard");
            if(!ready){initialize();ready=true;}else if(index<fixtures.size()){run(fixtures.get(index++));save();}else if(!diamondDone){boundedDiamond();diamondDone=true;save();}else{finish();return;}
            helper.runAfterDelay(1,this::step);
        }catch(Exception error){ended=true;report.addProperty("status","FAIL");report.addProperty("failure",error.toString());
            try{restore();save();}catch(Exception cleanup){error.addSuppressed(cleanup);}release();LogUtils.getLogger().error("GEOLOGY_TRACE FAIL",error);helper.fail(error.toString());}}
        void initialize() throws Exception {
            Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();String destination=System.getProperty("ic.trace.report");
            check(destination!=null&&!destination.isBlank(),"ic.trace.report is required");Path proposed=Path.of(destination).toAbsolutePath().normalize();
            check(proposed.startsWith(stage)&&!proposed.equals(stage),"Trace report escapes isolated stage");output=proposed;
            check(level.dimension()==Level.OVERWORLD&&enabled(),"Trace fixture requires enabled disposable Overworld");
            rules=object(get().settings(),"trace");check(bool(rules,"enabled",false),"Configured traces disabled");maxDepth=integer(rules,"maxSurfaceDepth",3);
            check(maxDepth>=1&&256*(maxDepth+5)<=4096,"Controlled trace fixture exceeds 4096 cells");
            check(surface-maxDepth-2>level.getMinBuildHeight(),"Fixture below legal generation bounds");
            beforeConfig=configHash();chunk=new ChunkPos(helper.absolutePos(BlockPos.ZERO));world=GeologyWorld.of(level);
            level.getChunkSource().addRegionTicket(TICKET,chunk,0,chunk);held=true;level.getChunk(chunk.x,chunk.z);
            traces=GeologyFeature.class.getDeclaredMethod("traces",WorldGenLevel.class,ChunkPos.class,GeologyWorld.class);traces.setAccessible(true);
            traceBlocks=new TreeSet<>();int maximum=0;for(JsonElement e:array(rules,"resources")){
                JsonObject resource=e.getAsJsonObject();traceBlocks.add(resource.get("block").getAsString());maximum=Math.max(maximum,Math.max(integer(resource,"max",2),integer(resource,"jackpotMax",0)));}
            budget=integer(rules,"attemptsPerChunk",4)*maximum;
            check(traceBlocks.equals(Set.of("industrial_colonies:hematite","industrial_colonies:chalcopyrite","minecraft:coal_ore")),"Expected configured Iron/Copper/Coal trace outcomes");
            proxy=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(receiver,method,args)->{
                if(method.getName().equals("getSeed")&&method.getParameterCount()==0)return fixtureSeed;
                if(method.getName().equals("getHeight")&&args!=null&&args.length==3){check(((Integer)args[1]>>4)==chunk.x&&((Integer)args[2]>>4)==chunk.z,"Trace height query escaped owner");return surface+1;}
                if(args!=null&&args.length>0&&args[0] instanceof BlockPos p&&Set.of("getBlockState","getFluidState","setBlock","removeBlock","destroyBlock").contains(method.getName()))check(owns(p),"Trace block access escaped owner: "+p);
                try{return level.getClass().getMethod(method.getName(),method.getParameterTypes()).invoke(level,args);}catch(InvocationTargetException e){throw e.getCause();}
            });
            long iron=choose("industrial_colonies:hematite",false),copper=choose("industrial_colonies:chalcopyrite",false),coal=choose("minecraft:coal_ore",false);
            fixtures.add(new Fixture("iron-surface",iron,0,Blocks.DIRT.defaultBlockState(),true));
            fixtures.add(new Fixture("copper-below-cover",copper,1,Blocks.DIRT.defaultBlockState(),true));
            fixtures.add(new Fixture("coal-at-max-depth",coal,maxDepth,Blocks.DIRT.defaultBlockState(),true));
            fixtures.add(new Fixture("stone-deeper-than-limit",iron,maxDepth+1,Blocks.DIRT.defaultBlockState(),false));
            for(BlockState filler:List.of(Blocks.DIRT.defaultBlockState(),Blocks.AIR.defaultBlockState(),Blocks.WATER.defaultBlockState(),Blocks.LAVA.defaultBlockState()))
                fixtures.add(new Fixture("nonreplaceable-"+id(filler),iron,-1,filler,false));
            fixtures.add(new Fixture("full-attempt-budget",choose(null,true),0,Blocks.DIRT.defaultBlockState(),true));
            report.addProperty("formatVersion",1);report.addProperty("status","RUNNING");report.addProperty("worldSeed",level.getSeed());
            report.addProperty("fixtureChunkX",chunk.x);report.addProperty("fixtureChunkZ",chunk.z);report.addProperty("explicitFixtureChunks",1);
            report.addProperty("maxFixtureCells",256*(maxDepth+5));report.addProperty("interiorCells",196*(maxDepth+3));report.addProperty("inertShell",true);report.addProperty("surfaceY",surface);report.addProperty("maxSurfaceDepth",maxDepth);report.addProperty("perChunkBlockBudget",budget);
            report.addProperty("configSha256Before",beforeConfig);report.addProperty("plannedCases",fixtures.size()+1);report.add("cases",results);
            report.addProperty("scope","Actual private production traces(...) and tiny placement with real block writes. Proxy supplies a synthetic per-fixture seed and flat surface height; this does NOT establish natural trace availability. An inert shell isolates fluid setup; exact prepared layouts are asserted before production calls. Configuration/rates/registries unchanged, one requested fixture chunk, restored within each case/tick.");
            save();
        }
        List<Attempt> attempts(long synthetic){
            List<Attempt> attempts=new ArrayList<>();long chunkSeed=seed(synthetic,chunk.x,chunk.z,0x5452414345L);JsonArray resources=array(rules,"resources");double[] weights=new double[resources.size()];
            for(int i=0;i<weights.length;i++)weights[i]=number(resources.get(i).getAsJsonObject(),"weight",1);
            for(int n=0;n<integer(rules,"attemptsPerChunk",4);n++){
                long roll=chunkSeed+n*313L;if(unit(roll)>number(rules,"chancePerAttempt",.35))continue;int selected=weighted(weights,unit(roll+3));if(selected<0)continue;
                JsonObject r=resources.get(selected).getAsJsonObject();int min=integer(r,"min",1),max=integer(r,"max",2);
                int count=unit(roll+4)<number(r,"jackpotChance",0)?integer(r,"jackpotMax",3):min+bounded(roll+5,max-min+1);
                attempts.add(new Attempt(r.get("block").getAsString(),count,chunk.getMinBlockX()+2+bounded(roll+1,12),chunk.getMinBlockZ()+2+bounded(roll+2,12)));
            }return attempts;
        }
        long choose(String target,boolean full){
            for(int n=0;n<1000000;n++){
                long candidate=mix(0x54524143454349L+n);List<Attempt> chosen=attempts(candidate);
                if(!full){if(chosen.size()==1&&chosen.getFirst().block().equals(target))return candidate;continue;}
                if(chosen.size()!=integer(rules,"attemptsPerChunk",4)||chosen.stream().mapToInt(Attempt::count).sum()!=budget)continue;
                boolean separated=true;for(int a=0;a<chosen.size();a++)for(int b=0;b<a;b++)if(Math.abs(chosen.get(a).x()-chosen.get(b).x())+Math.abs(chosen.get(a).z()-chosen.get(b).z())<=2)separated=false;
                if(separated)return candidate;
            }throw new IllegalStateException("No bounded seed for trace branch "+target+" full="+full);
        }
        List<BlockPos> positions(){List<BlockPos> positions=new ArrayList<>();for(int x=1;x<=14;x++)for(int y=surface-maxDepth-1;y<=surface+1;y++)for(int z=1;z<=14;z++)positions.add(new BlockPos(chunk.getMinBlockX()+x,y,chunk.getMinBlockZ()+z));return positions;}
        List<BlockPos> isolatedPositions(){List<BlockPos> positions=new ArrayList<>();for(int x=0;x<16;x++)for(int y=surface-maxDepth-2;y<=surface+2;y++)for(int z=0;z<16;z++)positions.add(new BlockPos(chunk.getMinBlockX()+x,y,chunk.getMinBlockZ()+z));return positions;}
        boolean owns(BlockPos p){return (p.getX()>>4)==chunk.x&&(p.getZ()>>4)==chunk.z;}
        void write(BlockPos p,BlockState state){check(owns(p),"Fixture write escaped owner");originals.putIfAbsent(p,level.getBlockState(p));level.setBlock(p,state,2);}
        Map<BlockPos,BlockState> snapshot(List<BlockPos> cells){Map<BlockPos,BlockState> states=new LinkedHashMap<>();for(BlockPos p:cells)states.put(p,level.getBlockState(p));return states;}
        String layoutHash(Map<BlockPos,BlockState> states) throws Exception {StringBuilder text=new StringBuilder();for(var e:states.entrySet())text.append(e.getKey()).append('=').append(e.getValue()).append('\n');return digest(text.toString());}
        void requireLayout(Map<BlockPos,BlockState> expected,Map<BlockPos,BlockState> actual,String phase) throws Exception {
            if(!expected.equals(actual)){
                JsonObject diagnostic=new JsonObject();JsonArray differences=new JsonArray();int count=0;
                for(var e:expected.entrySet())if(!Objects.equals(e.getValue(),actual.get(e.getKey()))){count++;if(differences.size()<32){JsonObject difference=new JsonObject();difference.addProperty("position",e.getKey().toString());difference.addProperty("expected",e.getValue().toString());difference.addProperty("actual",String.valueOf(actual.get(e.getKey())));differences.add(difference);}}
                diagnostic.addProperty("phase",phase);diagnostic.addProperty("differentCells",count);diagnostic.addProperty("expectedSha256",layoutHash(expected));diagnostic.addProperty("actualSha256",layoutHash(actual));diagnostic.add("firstDifferences",differences);report.add("layoutMismatch",diagnostic);save();
            }
            check(expected.equals(actual),"Fixture layout mismatch at "+phase+" (diagnostics saved)");
        }
        Map<BlockPos,BlockState> prepare(Fixture fixture,List<BlockPos> cells) throws Exception {
            Map<BlockPos,BlockState> wanted=new LinkedHashMap<>();
            // Clear the entire interior AND install a one-cell shell before introducing
            // fluids. Otherwise native onPlace reactions with natural water/lava can make
            // repeat inputs differ before the trace generator has been invoked at all.
            for(BlockPos p:cells){write(p,Blocks.BARRIER.defaultBlockState());wanted.put(p,Blocks.BARRIER.defaultBlockState());}
            for(BlockPos p:positions()){BlockState target=fixture.depth()>=0&&p.getY()==surface-fixture.depth()?Blocks.STONE.defaultBlockState():fixture.filler();write(p,target);wanted.put(p,target);}
            Map<BlockPos,BlockState> actual=snapshot(cells);requireLayout(wanted,actual,"prepared-"+fixture.name());return actual;
        }
        void run(Fixture fixture) throws Exception {
            fixtureSeed=fixture.syntheticSeed();List<BlockPos> positions=isolatedPositions();Map<String,Integer> expected=new TreeMap<>();
            if(fixture.expectedPlacement())for(Attempt attempt:attempts(fixtureSeed))expected.merge(attempt.block(),attempt.count(),Integer::sum);
            String first=null;Map<BlockPos,BlockState> firstBefore=null,firstAfter=null;JsonObject result=new JsonObject();result.addProperty("name",fixture.name());result.addProperty("syntheticSeed",fixtureSeed);result.addProperty("stoneDepth",fixture.depth());
            for(int repeat=0;repeat<2;repeat++){
                Map<BlockPos,BlockState> before=prepare(fixture,positions);
                if(firstBefore==null)firstBefore=before;else requireLayout(firstBefore,before,"repeat-input-"+fixture.name());
                boolean changed;try{changed=(Boolean)traces.invoke(null,proxy,chunk,world);}catch(InvocationTargetException e){throw new IllegalStateException("Production trace invocation failed",e.getCause());}
                Map<BlockPos,BlockState> afterStates=snapshot(positions);Map<String,Integer> found=new TreeMap<>();int modified=0;
                for(BlockPos p:positions){BlockState after=afterStates.get(p);String id=id(after);if(traceBlocks.contains(id))found.merge(id,1,Integer::sum);
                    if(!after.equals(before.get(p))){modified++;check(before.get(p).is(Blocks.STONE),"Trace replaced protected material");check(p.getY()==surface-fixture.depth(),"Trace escaped selected stone layer");}
                }
                check(found.equals(expected),"Trace resource counts differ: "+fixture.name()+" expected="+expected+" found="+found);
                check(modified==found.values().stream().mapToInt(Integer::intValue).sum()&&modified<=budget,"Trace writes exceeded material/attempt budget");
                check(changed==(modified>0),"Trace return value disagrees with actual writes");
                if(firstAfter==null)firstAfter=afterStates;else requireLayout(firstAfter,afterStates,"repeat-output-"+fixture.name());
                String hash=layoutHash(afterStates);if(first==null)first=hash;else check(first.equals(hash),"Same trace seed changed exact output layout");
                result.add("counts",new Gson().toJsonTree(found));result.addProperty("modifiedCells",modified);
            }
            restore();result.addProperty("repeatInputIdentical",true);result.addProperty("beforeStateSha256",layoutHash(firstBefore));result.addProperty("repeatIdentical",true);result.addProperty("shapeStateSha256",first);result.addProperty("status","PASS");results.add(result);
        }
        void boundedDiamond() throws Exception {
            Method bounded=GeologyFeature.class.getDeclaredMethod("tiny",WorldGenLevel.class,ChunkPos.class,BlockPos.class,BlockState.class,int.class,long.class,int.class);
            Method unbounded=GeologyFeature.class.getDeclaredMethod("tiny",WorldGenLevel.class,ChunkPos.class,BlockPos.class,BlockState.class,int.class,long.class);
            bounded.setAccessible(true);unbounded.setAccessible(true);
            JsonObject diamond=object(object(get().settings(),"micro"),"diamond");int maximumY=integer(diamond,"maxY",-20);
            check(maximumY==-20,"Expected configured independent-diamond ceiling -20");
            BlockPos center=new BlockPos(chunk.getMinBlockX()+8,maximumY,chunk.getMinBlockZ()+8);
            List<BlockPos> cells=new ArrayList<>();cells.add(center);for(net.minecraft.core.Direction direction:net.minecraft.core.Direction.values())cells.add(center.relative(direction));
            BlockState diamondState=GeologyFeature.state(string(diamond,"block","industrial_colonies:diamond_ore"));
            StringBuilder aggregate=new StringBuilder();int unboundedEscapes=0;
            for(int seedIndex=0;seedIndex<64;seedIndex++){
                long clusterSeed=mix(0x4449414d4f4e44L+seedIndex);for(BlockPos p:cells)write(p,Blocks.STONE.defaultBlockState());
                check((Integer)unbounded.invoke(null,proxy,chunk,center,diamondState,3,clusterSeed)==3,"Unbounded control did not fill three cells");
                if(level.getBlockState(center.above()).equals(diamondState))unboundedEscapes++;
                String first=null;
                for(int repeat=0;repeat<2;repeat++){
                    for(BlockPos p:cells)write(p,Blocks.STONE.defaultBlockState());
                    check((Integer)bounded.invoke(null,proxy,chunk,center,diamondState,3,clusterSeed,maximumY)==3,"Bounded diamond cluster lost its three-block quota");
                    int actual=0;StringBuilder states=new StringBuilder();
                    for(BlockPos p:cells){BlockState current=level.getBlockState(p);if(current.equals(diamondState)){actual++;check(p.getY()<=maximumY,"Independent diamond escaped maxY at "+p);}states.append(p).append('=').append(current).append('\n');}
                    check(actual==3,"Bounded diamond return count disagrees with actual blocks");
                    check(level.getBlockState(center.above()).is(Blocks.STONE),"Above-ceiling stone was overwritten");
                    String hash=digest(states.toString());if(first==null)first=hash;else check(first.equals(hash),"Bounded diamond same-seed layout changed");
                }
                aggregate.append(clusterSeed).append('=').append(first).append('\n');
            }
            check(unboundedEscapes>0,"Regression fixture did not expose the old unrestricted-neighbor behavior");restore();
            JsonObject result=new JsonObject();result.addProperty("name","independent-diamond-maximum-y");result.addProperty("status","PASS");result.addProperty("maximumY",maximumY);
            result.addProperty("seeds",64);result.addProperty("boundedCalls",128);result.addProperty("blocksPerCall",3);result.addProperty("aboveCeilingWrites",0);
            result.addProperty("unboundedControlEscapes",unboundedEscapes);result.addProperty("repeatIdentical",true);result.addProperty("shapeStateSha256",digest(aggregate.toString()));
            result.addProperty("scope","Actual bounded tiny helper at the configured maxY, not the natural diamond occurrence gate. The old unrestricted helper is a negative control only.");results.add(result);
        }
        static String id(BlockState state){return BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();}
        static String digest(String input) throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(input.getBytes(StandardCharsets.UTF_8)));}
        String configHash() throws Exception{return digest(get().settings()+"\n"+get().biomes()+"\n"+get().deposits());}
        void restore(){for(BlockPos p:originals.keySet())level.setBlock(p,Blocks.BARRIER.defaultBlockState(),2);for(var e:originals.entrySet())level.setBlock(e.getKey(),e.getValue(),2);for(var e:originals.entrySet())check(level.getBlockState(e.getKey()).equals(e.getValue()),"Trace fixture restoration failed");restored+=originals.size();originals.clear();}
        void release(){if(held){level.getChunkSource().removeRegionTicket(TICKET,chunk,0,chunk);held=false;}}
        void save() throws Exception {if(output==null)return;report.addProperty("completedCases",results.size());report.addProperty("assertions",assertions);report.addProperty("elapsedMillis",(System.nanoTime()-started)/1_000_000);report.addProperty("restoredFixtureWrites",restored);Files.createDirectories(output.getParent());Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);}
        void finish() throws Exception {String after=configHash();check(after.equals(beforeConfig),"Trace test mutated global config");report.addProperty("configSha256After",after);restore();release();report.addProperty("status","PASS");ended=true;save();LogUtils.getLogger().info("GEOLOGY_TRACE PASS cases={} assertions={} maxBudget={}",results.size(),assertions,budget);helper.succeed();}
    }
}
