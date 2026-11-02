package dev.godpc.industrialcolonies.geology;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.Heightmap;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Bounded existing CARVERS neighbors only. No noise lookup, range survey or remote load. */
public final class SummitCinnabarFeature {
 private SummitCinnabarFeature(){}
 private static final Set<String> REPORTED=java.util.concurrent.ConcurrentHashMap.newKeySet();
 public static boolean generate(WorldGenLevel level,ChunkPos owner){
  if(!WorldStartCinnabarRuntime.localBiomeMode()||level.getLevel().dimension()!=Level.OVERWORLD)return false;
  var config=object(get().settings(),"worldStartCinnabar");
  int spacing=integer(config,"localSpacing",512),minimum=integer(config,"minimumY",200),maximum=integer(config,"maximumY",300);
  double chance=number(config,"localChance",.25);
  if(spacing<64||spacing>4096||minimum!=200||maximum!=300||!Double.isFinite(chance)||chance<0||chance>1)throw new IllegalArgumentException("Local cinnabar policy");
  var output=BuiltInRegistries.BLOCK.get(ResourceLocation.parse("industrial_colonies:cinnabar")).defaultBlockState();boolean changed=false;
  for(int gx=Math.floorDiv(owner.getMinBlockX()-32,spacing);gx<=Math.floorDiv(owner.getMaxBlockX()+32,spacing);gx++)
   for(int gz=Math.floorDiv(owner.getMinBlockZ()-32,spacing);gz<=Math.floorDiv(owner.getMaxBlockZ()+32,spacing);gz++){
    var candidate=LocalCinnabarPattern.at(level.getSeed(),gx,gz,spacing,chance);if(candidate==null)continue;
    int tx=Math.floorDiv(candidate.x(),32)*2,tz=Math.floorDiv(candidate.z(),32)*2;
    if(owner.x<tx||owner.x>tx+1||owner.z<tz||owner.z>tz+1)continue;
    var chunks=new HashMap<Long,ChunkAccess>();
    for(int cx=tx;cx<=tx+1;cx++)for(int cz=tz;cz<=tz+1;cz++){
     var chunk=level.getChunk(cx,cz,ChunkStatus.CARVERS,false);
     if(chunk==null)throw new IllegalStateException("Required local CARVERS dependency unavailable");
     if(chunk.hasData(MiningOreOwnership.LEDGER)&&(!chunk.getData(MiningOreOwnership.LEDGER).sealed()||chunk.getData(MiningOreOwnership.LEDGER).failed()))throw new IllegalStateException("Unfinished natural ore ownership");
     chunks.put(ChunkPos.asLong(cx,cz),chunk);
    }
    int reserve=LocalCinnabarPattern.reserve(candidate.key());
    List<SummitCinnabarCap.Cell> cap;
    try{cap=CinnabarCapPlans.select(level.getLevel(),new CinnabarCapStore.Request(candidate.key(),tx,tz,reserve),()->{
    var eligible=new ArrayList<SummitCinnabarCap.Cell>();
    for(int x=tx*16;x<(tx+2)*16;x++)for(int z=tz*16;z<(tz+2)*16;z++){
     var chunk=chunks.get(ChunkPos.asLong(x>>4,z>>4));
     // Read existing rock directly: WG heightmaps observed through different feature
     // passes gave different admission sets. No noise calculation or chunk request.
     int y=level.getMaxBuildHeight()-1;
     while(y>=minimum){var state=chunk.getBlockState(new BlockPos(x,y,z));if(GeologyFeature.replaceable(state)||state.is(output.getBlock()))break;y--;}
     if(y<minimum||y>maximum)continue;
     var biome=level.getBiome(new BlockPos(x,y,z));String id=biome.unwrapKey().map(k->k.location().toString()).orElse("");
     if(!biome.is(BiomeTags.IS_MOUNTAIN)&&!families(id).contains("mountain_highland"))continue;
     var top=chunk.getBlockState(new BlockPos(x,y,z));if(!GeologyFeature.replaceable(top)&&!top.is(output.getBlock()))continue;
     for(int depth=0;depth<24&&y-depth>=minimum;depth++){
      var p=new BlockPos(x,y-depth,z);var state=chunk.getBlockState(p);
      if(chunk.getBlockEntity(p)!=null||!state.getFluidState().isEmpty()||!(GeologyFeature.replaceable(state)||state.is(output.getBlock())))continue;
      if(chunk.hasData(MiningOreOwnership.LEDGER)&&chunk.getData(MiningOreOwnership.LEDGER).claimed(x,p.getY(),z))continue;
      eligible.add(new SummitCinnabarCap.Cell(x,p.getY(),z,y));
     }
    }
    return SummitCinnabarCap.fit(eligible,reserve);
    });}catch(java.io.IOException failure){org.slf4j.LoggerFactory.getLogger("IndustrialColonies/CinnabarCap").error("Cinnabar cap held without blocking chunk; saved record retained",failure);continue;}
    int wanted=0,written=0;var observed=new ArrayList<BlockPos>();
    for(var cell:cap)if((cell.x()>>4)==owner.x&&(cell.z()>>4)==owner.z){
     wanted++;var p=new BlockPos(cell.x(),cell.y(),cell.z());var ownerChunk=chunks.get(owner.toLong());var state=ownerChunk.getBlockState(p);
     if(state.is(output.getBlock())){written++;observed.add(p);continue;}
     if(!GeologyFeature.replaceable(state)||ownerChunk.getBlockEntity(p)!=null||ownerChunk.hasData(MiningOreOwnership.LEDGER)&&ownerChunk.getData(MiningOreOwnership.LEDGER).claimed(p.getX(),p.getY(),p.getZ()))continue;
     if(level.setBlock(p,output,2)){written++;observed.add(p);changed=true;}
    }
    NearbyVeinClues.record(level.getLevel(),"cinnabar",observed);
    String key=level.getSeed()+":"+candidate.key()+":"+owner;
    if(REPORTED.size()>4096)REPORTED.clear();
    if(REPORTED.add(key))org.slf4j.LoggerFactory.getLogger("IndustrialColonies/CinnabarCap").info("Cinnabar cap center={},{} reserve={} savedFit={} owner={} wanted={} written={}",candidate.x(),candidate.z(),reserve,cap.size(),owner,wanted,written);
   }
  return changed;
 }
}
