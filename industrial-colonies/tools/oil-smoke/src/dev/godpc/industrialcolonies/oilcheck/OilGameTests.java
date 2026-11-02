package dev.godpc.industrialcolonies.oilcheck;

import com.drmangotea.tfmg.TFMG;
import com.drmangotea.tfmg.config.TFMGConfigs;
import com.drmangotea.tfmg.content.machinery.oil_processing.pumpjack.base.*;
import com.drmangotea.tfmg.content.machinery.oil_processing.surface_scanner.SurfaceScannerBlockEntity;
import com.google.gson.*;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.geology.GeologyConfig;
import dev.godpc.industrialcolonies.geology.oil.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Controlled native compatibility fixture, not a distribution survey or a powered-machine test. */
@GameTestHolder("ic_oil_smoke")
@PrefixGameTestTemplate(false)
public final class OilGameTests {
    private static final TicketType<ChunkPos> TICKET=TicketType.create("ic_oil_smoke",Comparator.comparingLong(ChunkPos::toLong));
    private static final TagKey<Block> SCANNER_TAG=TagKey.create(Registries.BLOCK,ResourceLocation.parse("tfmg:surface_scanner_findable"));
    private OilGameTests() {}

    @GameTest(templateNamespace="ic_oil_smoke",template="geology_smoke_empty",timeoutTicks=12000)
    public static void nativePlacementScannerAndFiniteExtraction(GameTestHelper helper) {
        new Run(helper).advance();
    }

    private record Surface(int height,Set<String> families) {}
    private static final class Run {
        final GameTestHelper helper;
        final ServerLevel level;
        final long started=System.nanoTime();
        final JsonObject report=new JsonObject();
        final List<int[]> regions=new ArrayList<>();
        final Map<BlockPos,BlockState> originals=new LinkedHashMap<>();
        OilRules rules;
        Path output;
        ChunkPos held;
        FluidReservoir createdReservoir;
        int index,assertions;

        Run(GameTestHelper helper) { this.helper=helper;level=helper.getLevel(); }
        void check(boolean condition,String message) { assertions++;if(!condition)throw new IllegalStateException(message); }
        void advance() {
            try {
                check(level.getServer().isSameThread(),"Oil fixture left the server thread");
                check((System.nanoTime()-started)/1_000_000<240000,"Oil fixture exceeded its 240-second wall budget");
                if(rules==null)initialize();
                check(index<regions.size(),"No eligible bounded oil candidate found within 289 regional cells");
                int[] region=regions.get(index++);
                OilFieldPlanner.Field field=OilFieldPlanner.field(level.getSeed(),rules.salt(),region[0],region[1],
                        rules.regionSize(),rules.regionMargin(),rules.radiusMin(),rules.radiusMax(),rules.wellsMin(),rules.wellsMax());
                Surface center=surface(field.centerX(),field.centerZ());
                if(OilFieldPlanner.accepted(field.roll(),rules.weight(center.families()),rules.fieldChance(),rules.weightNormalizer())
                        && terrainAllowed(field.centerX(),field.centerZ(),center)) {
                    for(OilFieldPlanner.Well well:field.wells())if(eligible(well)) {
                        runFixture(field,well);
                        cleanup();
                        report.addProperty("status","PASS");save();
                        LogUtils.getLogger().info("GEOLOGY_OIL_NATIVE PASS assertions={} report={}",assertions,output);
                        helper.succeed();return;
                    }
                }
                report.addProperty("regionsInspected",index);
                if(index%16==0){save();LogUtils.getLogger().info("GEOLOGY_OIL_NATIVE search regions={}/289",index);}
                helper.runAfterDelay(1,this::advance);
            } catch(Exception failure) {
                try {cleanup();}catch(Exception cleanupFailure){failure.addSuppressed(cleanupFailure);}
                report.addProperty("status","FAIL");report.addProperty("failure",failure.toString());
                try{save();}catch(Exception writeFailure){failure.addSuppressed(writeFailure);}
                LogUtils.getLogger().error("GEOLOGY_OIL_NATIVE FAIL",failure);helper.fail(failure.toString());
            }
        }

        void initialize() throws Exception {
            Path stage=Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
            String path=System.getProperty("ic.oil.report");
            check(path!=null&&!path.isBlank(),"ic.oil.report is required");
            output=Path.of(path).toAbsolutePath().normalize();
            check(output.startsWith(stage)&&!output.equals(stage),"Oil report must stay in the disposable stage");
            check(level.dimension()==Level.OVERWORLD,"Oil test requires the Overworld");
            check(level.getChunkSource().getGenerator() instanceof NoiseBasedChunkGenerator,"Oil fixture requires the existing normal-noise world template");
            check(GeologyConfig.enabled(),"Geology generation is disabled");
            rules=OilRules.get();check(rules.enabled(),"Oil generation disabled");
            check(rules.reservoirY()==-64,"Expected the installed TFMG Y=-64 contract");
            check(level.getMinBuildHeight()<=-64,"World minimum height excludes native oil markers");
            check(TFMGConfigs.common().machines.surfaceScannerScanDepth.get()==rules.reservoirY(),"Native scanner depth differs from reservoir Y");
            check(!TFMGConfigs.common().worldgen.infiniteDeposits.get(),"Finite oil configuration is not enabled; fixture never changes it");
            check(TFMG.DEPOSITS!=null&&TFMG.DEPOSITS.list!=null,"Native reservoir saved-data manager is uninitialized");
            for(int ring=0;ring<=8;ring++)for(int x=-ring;x<=ring;x++)for(int z=-ring;z<=ring;z++)
                if(Math.max(Math.abs(x),Math.abs(z))==ring)regions.add(new int[]{x,z});
            report.addProperty("formatVersion",1);report.addProperty("status","RUNNING");report.addProperty("worldSeed",level.getSeed());
            report.addProperty("maxRegions",289);report.addProperty("maxExplicitlyRequestedChunks",1);
            report.addProperty("configUnmodified",true);report.addProperty("fixtureInvokesActualRegisteredRegionalFeature",true);
            report.addProperty("limitations","Controlled one-well native compatibility only; not natural distribution, long-term depletion balance, full kinetic pumpjack operation, client scanner rendering, or disk restart persistence. Synchronous chunk generation may load dependencies and cannot be interrupted by the wall guard.");
            save();LogUtils.getLogger().info("GEOLOGY_OIL_NATIVE started seed={} report={}",level.getSeed(),output);
        }

        boolean eligible(OilFieldPlanner.Well well) {
            if(RandomSource.create(well.seed()).nextInt(25)==0)return false; // This native seed must produce fluid as well as its marker.
            if(!terrainAllowed(well.x(),well.z(),surface(well.x(),well.z())))return false;
            for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) {
                Surface edge=surface(well.x()+d[0],well.z()+d[1]);
                if(rules.weight(edge.families())<=0||edge.height()>rules.maximumSurfaceY())return false;
            }
            ChunkPos arena=new ChunkPos(helper.absolutePos(BlockPos.ZERO));
            if(Math.abs(well.chunkX()-arena.x)<=2&&Math.abs(well.chunkZ()-arena.z)<=2)return false;
            for(FluidReservoir existing:TFMG.DEPOSITS.list) {
                BlockPos position=BlockPos.of(existing.id);
                if(Math.abs(position.getX()-well.x())<256&&Math.abs(position.getZ()-well.z())<256)return false;
            }
            return true;
        }

        void runFixture(OilFieldPlanner.Field field,OilFieldPlanner.Well well) throws Exception {
            report.addProperty("phase","native_fixture");report.addProperty("regionsInspected",index);
            BlockPos marker=new BlockPos(well.x(),rules.reservoirY(),well.z());
            held=new ChunkPos(marker);level.getChunkSource().addRegionTicket(TICKET,held,0,held);level.getChunk(held.x,held.z);
            report.addProperty("chunkX",held.x);report.addProperty("chunkZ",held.z);
            report.addProperty("wellX",well.x());report.addProperty("wellY",marker.getY());report.addProperty("wellZ",well.z());
            report.addProperty("fieldCenterX",field.centerX());report.addProperty("fieldCenterZ",field.centerZ());
            report.addProperty("fieldRoll",field.roll());
            for(BlockPos p:BlockPos.betweenClosed(held.getMinBlockX(),marker.getY(),held.getMinBlockZ(),
                    held.getMaxBlockX(),marker.getY()+31,held.getMaxBlockZ())) {
                check(level.getBlockEntity(p)==null,"Fixture would overwrite a pre-existing block entity");
                originals.put(p.immutable(),level.getBlockState(p));
            }
            // Establish a negative control without changing generation settings. All edits are restored.
            for(var entry:originals.entrySet())if(entry.getKey().getY()==marker.getY()&&entry.getValue().is(SCANNER_TAG))
                level.setBlock(entry.getKey(),Blocks.BEDROCK.defaultBlockState(),2);
            BlockPos scannerPos=marker.offset(1,30,0);
            level.setBlock(scannerPos,block("tfmg:surface_scanner").defaultBlockState(),2);
            check(level.getBlockEntity(scannerPos) instanceof SurfaceScannerBlockEntity,"Native scanner block entity missing");
            SurfaceScannerBlockEntity scanner=(SurfaceScannerBlockEntity)level.getBlockEntity(scannerPos);
            check(!scanner.hasOil(marker),"Negative-control scanner already detects a marker");
            var configured=level.registryAccess().registryOrThrow(Registries.CONFIGURED_FEATURE)
                    .get(ResourceLocation.parse("industrial_colonies:regional_oil_reservoir"));
            check(configured!=null&&configured.feature() instanceof OilReservoirFeature,"Actual configured oil feature missing/wrong implementation");
            boolean placed=configured.place(level,level.getChunkSource().getGenerator(),RandomSource.create(21),
                    held.getWorldPosition().atY(marker.getY()));
            check(placed,"Registered regional oil feature rejected predicted eligible native well");
            check(level.getBlockState(marker).is(block("tfmg:oil_deposit")),"Regional feature did not place the native oil marker");
            check(scanner.hasOil(marker),"Native scanner does not recognize the regional marker");
            long crude=originals.keySet().stream().filter(p->BuiltInRegistries.FLUID.getKey(level.getFluidState(p).getType()).toString().equals("tfmg:crude_oil")).count();
            check(crude>0,"Native placement did not produce source crude oil");report.addProperty("nativeCrudeSourceBlocks",crude);
            report.addProperty("scannerNegativeBefore",true);report.addProperty("scannerPositiveAfter",true);
            BlockPos pumpPos=marker.above(28);
            for(int y=1;y<28;y++)level.setBlock(marker.above(y),block("tfmg:industrial_pipe").defaultBlockState(),2);
            level.setBlock(pumpPos,block("tfmg:pumpjack_base").defaultBlockState(),2);
            check(level.getBlockEntity(pumpPos) instanceof PumpjackBaseBlockEntity,"Native pumpjack base block entity missing");
            PumpjackBaseBlockEntity pump=(PumpjackBaseBlockEntity)level.getBlockEntity(pumpPos);
            pump.findDeposit();check(marker.equals(pump.deposit),"Native pipe-connected pump cannot discover marker");
            check(TFMG.DEPOSITS.getReservoirFor(marker.asLong())==null,"Fixture well already has a native reservoir record");
            pump.miningRate=0;pump.process(); // Native lazy registration, no oil granted by the fixture.
            createdReservoir=TFMG.DEPOSITS.getReservoirFor(marker.asLong());
            check(createdReservoir!=null&&createdReservoir.id==marker.asLong(),"Native pump did not register an independent finite well");
            check(createdReservoir.oilReserves>=1000,"Native finite reserve is unexpectedly small");
            int initial=createdReservoir.oilReserves;int before=pump.tank.getFluidAmount();
            pump.miningRate=1000;pump.process();
            check(pump.tank.getFluidAmount()-before==1000,"Native process did not extract exactly 1000 mB");
            check(BuiltInRegistries.FLUID.getKey(pump.tank.getFluid().getFluid()).toString().equals("tfmg:crude_oil"),"Pump extracted a non-TFMG fluid");
            check(createdReservoir.oilReserves==initial-1,"Existing finite-reservoir mixin did not debit one bucket-equivalent reserve");
            int after=createdReservoir.oilReserves;
            createdReservoir.oilReserves=0;before=pump.tank.getFluidAmount();pump.miningRate=1000;
            try{pump.process();check(pump.tank.getFluidAmount()==before&&pump.miningRate==0,"Exhausted native well still produces oil");}
            finally{createdReservoir.oilReserves=after;TFMG.DEPOSITS.markDirty();}
            CompoundTag saved=TestSavedData.load(level.getServer()).save(new CompoundTag(),level.registryAccess());
            TestSavedData decoded=TestSavedData.load(saved,level.registryAccess());
            FluidReservoir restored=decoded.getLogisticsNetworks().stream().filter(r->r.id==marker.asLong()).findFirst().orElseThrow();
            check(restored.oilReserves==after&&restored.deposits.contains(marker.asLong()),"Native SavedData serialization lost the fixture reserve/primary well");
            report.addProperty("initialReserves",initial);report.addProperty("reservesAfter1000mB",after);
            report.addProperty("extractedMilliBuckets",1000);report.addProperty("exhaustionStopsExtraction",true);
            report.addProperty("nativeNbtPrimaryWellRoundtrip",true);
            report.addProperty("serializedNbtSha256",HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(saved.toString().getBytes(StandardCharsets.UTF_8))));
        }

        Block block(String id) { Block b=BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id));check(b!=Blocks.AIR,"Missing registered block "+id);return b; }
        int height(int x,int z) { return level.getChunkSource().getGenerator().getBaseHeight(x,z,Heightmap.Types.OCEAN_FLOOR_WG,level,level.getChunkSource().randomState()); }
        Surface surface(int x,int z) {
            var generator=level.getChunkSource().getGenerator();int y=height(x,z);
            var biome=generator.getBiomeSource().getNoiseBiome(Math.floorDiv(x,4),Math.floorDiv(Math.max(y,generator.getSeaLevel()),4),Math.floorDiv(z,4),level.getChunkSource().randomState().sampler());
            return new Surface(y,GeologyConfig.families(biome.unwrapKey().map(k->k.location().toString()).orElse("")));
        }
        boolean terrainAllowed(int x,int z,Surface center) {
            if(center.height()>rules.maximumSurfaceY()||rules.weight(center.families())<=0)return false;
            int low=center.height(),high=low,r=rules.terrainSampleRadius();
            for(int[] d:new int[][]{{r,0},{-r,0},{0,r},{0,-r}}){int h=height(x+d[0],z+d[1]);low=Math.min(low,h);high=Math.max(high,h);}
            return high<=rules.maximumSurfaceY()&&high-low<=rules.maximumRelief();
        }
        void cleanup() {
            if(createdReservoir!=null){TFMG.DEPOSITS.list.remove(createdReservoir);TFMG.DEPOSITS.markDirty();createdReservoir=null;}
            for(var entry:originals.entrySet())level.setBlock(entry.getKey(),entry.getValue(),2);
            if(!originals.isEmpty()){report.addProperty("restoredBlockPositions",originals.size());originals.clear();}
            if(held!=null){level.getChunkSource().removeRegionTicket(TICKET,held,0,held);held=null;}
            report.addProperty("cleanupCompleted",true);
        }
        void save() throws Exception {
            report.addProperty("assertions",assertions);report.addProperty("elapsedMillis",(System.nanoTime()-started)/1_000_000);
            if(output!=null)Files.writeString(output,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n",StandardCharsets.UTF_8);
        }
    }
}
