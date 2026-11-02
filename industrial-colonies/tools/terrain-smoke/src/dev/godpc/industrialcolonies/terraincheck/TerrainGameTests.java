package dev.godpc.industrialcolonies.terraincheck;

import com.google.gson.*;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.geology.*;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Test-addon only: natural generation in a disposable normal Overworld, never production placement. */
@GameTestHolder("ic_terrain_smoke")
@PrefixGameTestTemplate(false)
public final class TerrainGameTests {
    private static final Comparator<BlockPos> POSITION_ORDER = Comparator.comparingInt((BlockPos p) -> p.getX())
            .thenComparingInt(BlockPos::getY).thenComparingInt(BlockPos::getZ);
    private static final TicketType<ChunkPos> TEST_TICKET=TicketType.create("ic_terrain_smoke",Comparator.comparingLong(ChunkPos::toLong));
    private TerrainGameTests() {}

    @GameTest(templateNamespace = "ic_terrain_smoke", template = "geology_smoke_empty", timeoutTicks = 24000)
    public static void naturalDeposits(GameTestHelper helper) {
        new Run(helper).step("initialization", () -> {});
    }

    @FunctionalInterface private interface CheckedAction { void run() throws Exception; }
    private record Selected(GeologyPlanner.Plan plan,List<BlockPos> shape,Map<Long,List<BlockPos>> chunks) {}

    private static final class Run {
        private final GameTestHelper helper;
        private final ServerLevel level;
        private final long started = System.nanoTime();
        private final long wallMillis = Math.min(480000, Math.max(1000, Long.getLong("ic.terrain.wallTimeoutMillis", 480000)));
        private final boolean reverse = Boolean.getBoolean("ic.terrain.reverse");
        private final JsonObject report = new JsonObject();
        private final JsonArray skips = new JsonArray(), results = new JsonArray(), requestOrder = new JsonArray();
        private final List<int[]> regions = new ArrayList<>();
        private final List<Selected> selected = new ArrayList<>();
        private final Set<Long> requested = new HashSet<>();
        private final Set<Long> held = new HashSet<>();
        private final List<Long> generation = new ArrayList<>();
        private final Set<String> noiseBiomes = new TreeSet<>(), actualBiomes = new TreeSet<>();
        private GeologyWorld world;
        private Path output;
        private int regionalIndex, generationIndex, scanIndex;
        private boolean initialized, ended;

        Run(GameTestHelper helper) { this.helper=helper;this.level=helper.getLevel(); }

        private void check(boolean condition,String message) {
            if(!condition) throw new IllegalStateException(message);
        }

        private void step(String phase,CheckedAction action) {
            if(ended)return;
            String failure=null;
            try {
                check(level.getServer().isSameThread(),"Terrain test left the server thread");
                check((System.nanoTime()-started)/1_000_000 < wallMillis,"Terrain test exceeded its bounded wall-time budget");
                report.addProperty("phase",phase);
                if(!initialized){initialize();initialized=true;later("search",this::search);}
                else action.run();
                if(!ended)check((System.nanoTime()-started)/1_000_000 < wallMillis,"Terrain test exceeded its wall-time budget during "+phase);
            } catch(Exception error) {
                ended=true;failure=error.getClass().getSimpleName()+": "+error.getMessage();
                report.addProperty("status","FAIL");report.addProperty("failure",failure);
                release();
                try { save(); } catch(Exception exportError) { LogUtils.getLogger().error("GEOLOGY_TERRAIN failed to export failure report",exportError); }
                LogUtils.getLogger().error("GEOLOGY_TERRAIN FAIL phase={}",phase,error);
            }
            if(failure!=null)helper.fail(failure);
        }

        private void later(String phase,CheckedAction action) { helper.runAfterDelay(1,()->step(phase,action)); }

        private void initialize() throws Exception {
            Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
            String destination=System.getProperty("ic.terrain.report");
            check(destination!=null&&!destination.isBlank(),"ic.terrain.report must name an output within the disposable stage");
            Path proposedOutput=Path.of(destination).toAbsolutePath().normalize();
            check(proposedOutput.startsWith(stage)&&!proposedOutput.equals(stage),"Terrain report output escapes the stage working directory");
            output=proposedOutput;
            check(level.dimension()==Level.OVERWORLD,"Natural terrain checks require the Overworld");
            check(level.getChunkSource().getGenerator() instanceof NoiseBasedChunkGenerator,"Flat/artificial generator is not valid terrain evidence");
            NoiseBasedChunkGenerator noise=(NoiseBasedChunkGenerator)level.getChunkSource().getGenerator();
            check(noise.generatorSettings().is(NoiseGeneratorSettings.OVERWORLD),"Generator does not use minecraft:overworld noise settings");
            var noiseResource=level.getServer().getResourceManager().getResource(ResourceLocation.parse("minecraft:worldgen/noise_settings/overworld.json"));
            check(noiseResource.isPresent(),"Effective Overworld noise-settings resource is missing");
            String noisePack=noiseResource.get().sourcePackId();
            String terrainMod=System.getProperty("ic.terrain.expectedTerrainMod","tectonic");
            String provider=System.getProperty("ic.terrain.expectedProvider","tectonic");
            check(noisePack.toLowerCase(Locale.ROOT).contains(provider.toLowerCase(Locale.ROOT)),"Effective Overworld noise settings are not supplied by "+provider+": "+noisePack);
            int expectedMin=Integer.getInteger("ic.terrain.expectedMinY",-64),expectedHeight=Integer.getInteger("ic.terrain.expectedHeight",384);
            check(level.getMinBuildHeight()==expectedMin&&level.getMaxBuildHeight()==expectedMin+expectedHeight,"Unexpected effective dimension height");
            String actualNoiseHash;
            try(var input=noiseResource.get().open()){
                byte[] bytes=input.readAllBytes();actualNoiseHash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
                JsonObject effective=JsonParser.parseString(new String(bytes,StandardCharsets.UTF_8)).getAsJsonObject();
                check(effective.getAsJsonObject("noise").get("min_y").getAsInt()==expectedMin&&effective.getAsJsonObject("noise").get("height").getAsInt()==expectedHeight,"Noise height differs from required dimension height");
            }
            String expectedNoiseHash=System.getProperty("ic.terrain.expectedNoiseSha256","");
            check(expectedNoiseHash.isBlank()||actualNoiseHash.equalsIgnoreCase(expectedNoiseHash),"Effective noise resource differs from staged installed terrain artifact");
            check(level.getSeed()==Long.getLong("ic.terrain.expectedSeed",0L),"Unexpected natural-world seed");
            check(ModList.get().isLoaded(terrainMod)&&ModList.get().isLoaded("regions_unexplored"),terrainMod+" and Regions Unexplored must be loaded");
            if(terrainMod.equals("mr_lithosphere"))check(!ModList.get().isLoaded("tectonic"),"Lithosphere acceptance must not also load Tectonic");
            check(GeologyConfig.enabled(),"Geological generation is disabled");
            world=GeologyWorld.of(level);validate(get());
            for(int ring=0;ring<=8;ring++)for(int x=-ring;x<=ring;x++)for(int z=-ring;z<=ring;z++)
                if(Math.max(Math.abs(x),Math.abs(z))==ring)regions.add(new int[]{x,z});
            report.addProperty("formatVersion",1);report.addProperty("status","RUNNING");
            report.addProperty("worldSeed",level.getSeed());report.addProperty("reverseRequests",reverse);
            report.addProperty("generator",level.getChunkSource().getGenerator().getClass().getName());
            report.addProperty("noiseSettingsKey","minecraft:overworld");report.addProperty("noiseSettingsSourcePack",noisePack);
            report.addProperty("expectedTerrainMod",terrainMod);report.addProperty("noiseSettingsSha256",actualNoiseHash);
            report.addProperty("minimumBuildHeight",level.getMinBuildHeight());report.addProperty("maximumBuildHeight",level.getMaxBuildHeight());
            report.addProperty("regionSize",world.planner.regionSize());report.addProperty("maxRegions",289);
            report.addProperty("maxRequestedChunksPerPlan",25);report.addProperty("maxRequestedChunksTotal",60);
            report.addProperty("wallTimeoutMillis",wallMillis);
            report.addProperty("limitations","Requested-chunk cap excludes Minecraft's implicit status/dependency halo. Wall guard cannot interrupt a synchronous chunk call. Final shape-state counts may expose later feature overwrites. Only three selected formations are tested; default frequencies and spacing remain unchanged.");
            report.add("skipped",skips);report.add("plans",results);report.add("requestOrder",requestOrder);
            JsonObject configHash=new JsonObject();
            configHash.addProperty("settings",digest(get().settings().toString()));
            configHash.addProperty("biomes",digest(get().biomes().toString()));
            configHash.addProperty("deposits",digest(get().deposits().toString()));report.add("configSha256",configHash);
            save();
            LogUtils.getLogger().info("GEOLOGY_TERRAIN started: normal seed={} reverse={} noiseSource={} minHeight={} report={}",level.getSeed(),reverse,noisePack,level.getMinBuildHeight(),output);
        }

        private void skip(GeologyPlanner.Plan plan,String reason) {
            JsonObject entry=new JsonObject();entry.addProperty("family",plan.id());entry.addProperty("reason",reason);
            entry.addProperty("regionX",plan.candidate().regionX());entry.addProperty("regionZ",plan.candidate().regionZ());skips.add(entry);
            LogUtils.getLogger().info("GEOLOGY_TERRAIN skip {} region={},{}: {}",plan.id(),plan.candidate().regionX(),plan.candidate().regionZ(),reason);
        }

        private void search() throws Exception {
            if(regionalIndex>=regions.size()){finishSearch();return;}
            int[] region=regions.get(regionalIndex++);
            GeologyPlanner.Decision decision=world.planner.decide(region[0],region[1]);
            if(decision.candidate()!=null)noiseBiomes.add(decision.candidate().site().biome());
            report.addProperty("regionsInspected",regionalIndex);
            if(decision.plan()!=null)consider(decision.plan());
            long families=selected.stream().map(s->GeologyPlanner.family(s.plan.definition())).distinct().count();
            if(selected.size()==3&&families>=2){finishSearch();return;}
            if(regionalIndex%16==0){save();LogUtils.getLogger().info("GEOLOGY_TERRAIN planning progress regions={} selected={}",regionalIndex,selected.size());}
            later("search",this::search);
        }

        private void consider(GeologyPlanner.Plan plan) {
            if(!string(plan.definition(),"hostRock","").startsWith("industrial_colonies:")||array(plan.definition(),"richOres").isEmpty()){
                skip(plan,"requires custom low-yield host plus approved rich pool");return;
            }
            List<BlockPos> shape=new ArrayList<>(world.shape(plan));shape.sort(POSITION_ORDER);
            Map<Long,List<BlockPos>> chunks=new TreeMap<>();
            for(BlockPos p:shape)chunks.computeIfAbsent(new ChunkPos(p).toLong(),k->new ArrayList<>()).add(p);
            if(chunks.size()<2||chunks.size()>25){skip(plan,"planned footprint outside 2..25 requested chunks: "+chunks.size());return;}
            ChunkPos arena=new ChunkPos(helper.absolutePos(BlockPos.ZERO));
            if(chunks.keySet().stream().map(ChunkPos::new).anyMatch(c->Math.abs(c.x-arena.x)<=2&&Math.abs(c.z-arena.z)<=2)){
                skip(plan,"too close to GameTest arena");return;
            }
            JsonObject indicators=object(get().settings(),"indicators");
            if(bool(indicators,"enabled",true)){
                double chance=number(indicators,"chancePerDepositChunk",.025)*number(object(object(get().settings(),"terrain"),plan.candidate().site().terrain()),"indicatorExposure",1);
                for(long packed:chunks.keySet()){
                    ChunkPos c=new ChunkPos(packed);long chunkSeed=seed(plan.candidate().seed(),c.x,c.z,0x484f5354);
                    if(unit(chunkSeed+777)<=chance){skip(plan,"seeded indicator gate could confound pre-rich-host counting");return;}
                }
            }
            Selected replacement=null;
            if(selected.size()==3){
                String family=GeologyPlanner.family(plan.definition());
                if(selected.stream().anyMatch(s->GeologyPlanner.family(s.plan.definition()).equals(family))){skip(plan,"already have three candidates; seeking a second family");return;}
                replacement=selected.getLast();
            }
            Set<Long> union=new HashSet<>();
            for(Selected s:selected)if(s!=replacement)union.addAll(s.chunks.keySet());union.addAll(chunks.keySet());
            if(union.size()>60){skip(plan,"would exceed total 60 requested chunks");return;}
            if(replacement!=null){selected.remove(replacement);skip(replacement.plan,"replaced by natural second-family candidate before any chunk requests");}
            selected.add(new Selected(plan,List.copyOf(shape),chunks));
            LogUtils.getLogger().info("GEOLOGY_TERRAIN selected {} @ {},{},{} quality={} intended={} footprint={}",plan.id(),plan.candidate().x(),plan.candidate().y(),plan.candidate().z(),plan.quality(),plan.intendedSize(),chunks.size());
        }

        private void finishSearch() throws Exception {
            check(selected.size()==3,"Found only "+selected.size()+" naturally accepted bounded rich-host candidates in "+regionalIndex+" regions");
            Set<Long> unique=new HashSet<>();for(Selected s:selected)unique.addAll(s.chunks.keySet());
            generation.addAll(unique);generation.sort(Comparator.comparingInt((Long p)->new ChunkPos(p).x).thenComparingInt(p->new ChunkPos(p).z));
            if(reverse)Collections.reverse(generation);
            check(generation.size()<=60,"Requested chunk cap broken");
            report.addProperty("selectedFamilies",selected.stream().map(s->GeologyPlanner.family(s.plan.definition())).distinct().count());
            report.addProperty("selectedRequestedChunks",generation.size());
            JsonArray choices=new JsonArray();
            for(Selected s:selected){JsonObject choice=new JsonObject();choice.addProperty("id",s.plan.id());choice.addProperty("x",s.plan.candidate().x());
                choice.addProperty("y",s.plan.candidate().y());choice.addProperty("z",s.plan.candidate().z());choice.addProperty("intendedSize",s.plan.intendedSize());
                choice.addProperty("footprintChunks",s.chunks.size());choices.add(choice);}
            report.add("selectedPlans",choices);
            report.addProperty("footprintChunksAlreadyLoaded",generation.stream().map(ChunkPos::new).filter(c->level.getChunkSource().getChunkNow(c.x,c.z)!=null).count());
            save();later("generate",this::generate);
        }

        private void generate() throws Exception {
            if(generationIndex>=generation.size()){later("scan",this::scan);return;}
            long packed=generation.get(generationIndex++);ChunkPos chunk=new ChunkPos(packed);long begin=System.nanoTime();
            // Intentionally one requested FULL chunk per server tick. This call can synchronously
            // generate dependencies; neither an off-thread join nor a claimed hard dependency cap.
            level.getChunkSource().addRegionTicket(TEST_TICKET,chunk,0,chunk);held.add(packed);
            level.getChunk(chunk.x,chunk.z);
            requested.add(packed);JsonObject entry=new JsonObject();entry.addProperty("x",chunk.x);entry.addProperty("z",chunk.z);
            entry.addProperty("elapsedMillis",(System.nanoTime()-begin)/1_000_000);requestOrder.add(entry);
            LogUtils.getLogger().info("GEOLOGY_TERRAIN chunk {}/{} {},{} completed in {} ms",generationIndex,generation.size(),chunk.x,chunk.z,(System.nanoTime()-begin)/1_000_000);
            save();later("generate",this::generate);
        }

        private void scan() throws Exception {
            if(scanIndex>=selected.size()){
                check(results.size()==3,"Three actual formation scans required");
                report.addProperty("status","PASS");report.addProperty("phase","complete");save();ended=true;
                release();
                LogUtils.getLogger().info("GEOLOGY_TERRAIN PASS three naturally planned formations; requestedChunks={} report={}",requested.size(),output);
                helper.succeed();return;
            }
            Selected selection=selected.get(scanIndex++);GeologyPlanner.Plan plan=selection.plan;
            Map<Long,GeologyDebug.Counts> observations=observed(plan.candidate().seed());
            String host=string(plan.definition(),"hostRock","");Set<String> richIds=new HashSet<>(),associationIds=new HashSet<>();
            for(JsonElement e:array(plan.definition(),"richOres"))richIds.add(e.getAsJsonObject().get("block").getAsString());
            for(JsonElement e:array(plan.definition(),"associated"))associationIds.add(e.getAsJsonObject().get("block").getAsString());
            Set<String> geologyIds=new HashSet<>(richIds);geologyIds.addAll(associationIds);geologyIds.add(host);
            JsonObject result=new JsonObject();result.addProperty("id",plan.id());result.addProperty("spacingFamily",GeologyPlanner.family(plan.definition()));
            result.addProperty("regionX",plan.candidate().regionX());result.addProperty("regionZ",plan.candidate().regionZ());
            result.addProperty("x",plan.candidate().x());result.addProperty("y",plan.candidate().y());result.addProperty("z",plan.candidate().z());
            result.addProperty("biome",plan.candidate().site().biome());result.addProperty("terrain",plan.candidate().site().terrain());
            BlockPos center=new BlockPos(plan.candidate().x(),plan.candidate().y(),plan.candidate().z());
            String actualCenter=level.getBiome(center).unwrapKey().map(k->k.location().toString()).orElse("unregistered");
            int actualSurface=level.getHeight(Heightmap.Types.OCEAN_FLOOR,center.getX(),center.getZ());
            String actualSurfaceBiome=level.getBiome(new BlockPos(center.getX(),Math.min(level.getMaxBuildHeight()-1,actualSurface+4),center.getZ()))
                    .unwrapKey().map(k->k.location().toString()).orElse("unregistered");
            actualBiomes.add(actualCenter);actualBiomes.add(actualSurfaceBiome);
            result.addProperty("actualCenterBiome",actualCenter);result.addProperty("actualSurfaceBiome",actualSurfaceBiome);result.addProperty("actualSurfaceY",actualSurface);
            LogUtils.getLogger().info("GEOLOGY_TERRAIN biome {} noiseSurface={} actualCenter={} actualSurface={}",plan.id(),plan.candidate().site().biome(),actualCenter,actualSurfaceBiome);
            result.addProperty("surfaceY",plan.candidate().site().surfaceY());result.addProperty("quality",plan.quality());
            result.addProperty("normalSize",plan.normalSize());result.addProperty("intendedSize",plan.intendedSize());result.addProperty("richFraction",plan.richFraction());
            JsonArray chunkResults=new JsonArray();result.add("chunks",chunkResults);results.add(result);
            int totalActual=0,nonempty=0;Set<BlockPos> retained=new HashSet<>();Map<String,Integer> totalBlocks=new TreeMap<>();
            for(var entry:selection.chunks.entrySet()){
                check(requested.contains(entry.getKey()),"Scan attempted an unrequested footprint chunk");ChunkPos chunk=new ChunkPos(entry.getKey());
                check(level.getChunkSource().getChunkNow(chunk.x,chunk.z)!=null,"Requested chunk unloaded before scan; refusing implicit reload");
                Map<String,Integer> found=new TreeMap<>();int scanned=0,richCount=0;
                for(BlockPos p:entry.getValue()){
                    String block=BuiltInRegistries.BLOCK.getKey(level.getBlockState(p).getBlock()).toString();
                    if(geologyIds.contains(block)){found.merge(block,1,Integer::sum);totalBlocks.merge(block,1,Integer::sum);scanned++;retained.add(p);}
                    if(richIds.contains(block))richCount++;
                }
                GeologyDebug.Counts count=observations.get(entry.getKey());
                if(count==null){check(scanned==0,"Material found without placement observation in "+chunk);continue;}
                long chunkSeed=seed(plan.candidate().seed(),chunk.x,chunk.z,0x484f5354);
                check(count.indicators()==0,"Selected no-indicator fixture unexpectedly placed an indicator");
                check(count.host()<=entry.getValue().size(),"Observed host exceeds owning chunk geometry");
                check(scanned==count.host(),"Final host+rich+association differs from recorded pre-rich host at "+chunk+": scan="+scanned+" recorded="+count.host()+" (possible later feature overwrite)");
                int target=quota(count.host(),plan.richFraction(),chunkSeed,false);
                check(count.richTarget()==target,"Rich target quota differs at "+chunk);
                check(count.richPlaced()==target&&richCount==target,"Rich allocation did not reach exact target at "+chunk);
                JsonArray rich=array(plan.definition(),"richOres");double[] weights=new double[rich.size()];
                for(int i=0;i<weights.length;i++)weights[i]=number(rich.get(i).getAsJsonObject(),"weight",1);
                int[] split=GeologyMath.split(target,weights,chunkSeed+0x50474d);
                for(int i=0;i<split.length;i++)check(found.getOrDefault(rich.get(i).getAsJsonObject().get("block").getAsString(),0)==split[i],"Individual rich-pool count differs at "+chunk);
                for(String associated:associationIds)check(found.getOrDefault(associated,0)==count.associated().getOrDefault(associated,0),"Associated block count differs at "+chunk+": "+associated);
                if(count.host()>0)nonempty++;totalActual+=count.host();
                JsonObject c=new JsonObject();c.addProperty("x",chunk.x);c.addProperty("z",chunk.z);c.addProperty("intendedPositions",entry.getValue().size());
                c.addProperty("actualHostBeforeRich",count.host());c.addProperty("richTarget",target);c.addProperty("richPlaced",count.richPlaced());
                c.add("finalGeologyCounts",new Gson().toJsonTree(found));c.add("associationRolls",new Gson().toJsonTree(new TreeMap<>(count.rolls())));chunkResults.add(c);
            }
            result.addProperty("actualHostBeforeRich",totalActual);result.addProperty("nonemptyChunks",nonempty);
            result.add("finalGeologyCounts",new Gson().toJsonTree(totalBlocks));
            check(totalActual>0&&totalActual<=plan.intendedSize(),"No surviving host or host exceeds intended geometry: "+plan.id());
            check(nonempty>=2,"Formation did not actually span at least two chunks: "+plan.id());
            MessageDigest all=MessageDigest.getInstance("SHA-256"),materials=MessageDigest.getInstance("SHA-256");
            for(BlockPos p:selection.shape){
                BlockState state=level.getBlockState(p);String line=p.getX()+","+p.getY()+","+p.getZ()+"="+state+"\n";
                all.update(line.getBytes(StandardCharsets.UTF_8));if(retained.contains(p))materials.update(line.getBytes(StandardCharsets.UTF_8));
            }
            result.addProperty("shapeStateSha256",HexFormat.of().formatHex(all.digest()));
            result.addProperty("retainedGeologySha256",HexFormat.of().formatHex(materials.digest()));
            int boundaryBonds=0;
            for(BlockPos p:retained)for(BlockPos neighbor:List.of(p.east(),p.south()))
                if(retained.contains(neighbor)&&!new ChunkPos(p).equals(new ChunkPos(neighbor)))boundaryBonds++;
            result.addProperty("retainedCrossChunkNeighborBonds",boundaryBonds);
            result.addProperty("status","PASS");save();
            LogUtils.getLogger().info("GEOLOGY_TERRAIN formation PASS {} actual={} intended={} occupiedChunks={} boundaryBonds={}",plan.id(),totalActual,plan.intendedSize(),nonempty,boundaryBonds);
            later("scan",this::scan);
        }

        @SuppressWarnings("unchecked")
        private Map<Long,GeologyDebug.Counts> observed(long seed) throws ReflectiveOperationException {
            Field field=GeologyDebug.class.getDeclaredField("OBSERVED");field.setAccessible(true);
            Map<Long,Map<Long,GeologyDebug.Counts>> all=(Map<Long,Map<Long,GeologyDebug.Counts>>)field.get(null);
            return Map.copyOf(all.getOrDefault(seed,Map.of()));
        }

        private void save() throws Exception {
            if(output==null)return;
            report.addProperty("elapsedMillis",(System.nanoTime()-started)/1_000_000);
            report.add("observedNoiseBiomes",new Gson().toJsonTree(noiseBiomes));report.add("observedActualBiomes",new Gson().toJsonTree(actualBiomes));
            boolean ruNoise=noiseBiomes.stream().anyMatch(b->b.startsWith("regions_unexplored:"));
            boolean ruActual=actualBiomes.stream().anyMatch(b->b.startsWith("regions_unexplored:"));
            report.addProperty("regionsUnexploredNoiseObserved",ruNoise);report.addProperty("regionsUnexploredActualObserved",ruActual);
            report.addProperty("regionsUnexploredEvidence",ruActual?"RU biome observed in generated chunks":ruNoise?"RU biome observed by real noise sampler; not yet in scanned generated chunks":"RU installed, but no RU biome observed within this bounded sample (not treated as a failure)");
            Files.createDirectories(output.getParent());
            Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);
        }

        private void release() {
            for(long packed:held){ChunkPos chunk=new ChunkPos(packed);level.getChunkSource().removeRegionTicket(TEST_TICKET,chunk,0,chunk);}
            held.clear();
        }

        private static String digest(String text) throws Exception {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));
        }
    }
}
