package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Local decoration only: existing chunk heights/biomes, no generator lookup or range survey.
 * Stable grid candidates are clipped to each owner; existing finite claims are never replaced. */
public final class LocalBiomeCinnabarFeature {
 private LocalBiomeCinnabarFeature(){}
 public static boolean generate(WorldGenLevel level,ChunkPos owner){return SummitCinnabarFeature.generate(level,owner);}
 private static boolean legacySurfacePatches(WorldGenLevel level,ChunkPos owner){
  if(!WorldStartCinnabarRuntime.localBiomeMode()||level.getLevel().dimension()!=Level.OVERWORLD)return false;
  var config=object(get().settings(),"worldStartCinnabar");
  int spacing=integer(config,"localSpacing",512),minimum=integer(config,"minimumY",200),maximum=integer(config,"maximumY",300);
  double chance=number(config,"localChance",.25),coverage=number(config,"coverage",.7);
  int thickness=integer(config,"maximumThickness",3);
  if(spacing<64||spacing>4096||minimum!=200||maximum!=300||!Double.isFinite(chance)||chance<0||chance>1
      ||!Double.isFinite(coverage)||coverage<0||coverage>1||thickness<1||thickness>3)
   throw new IllegalArgumentException("Invalid local cinnabar policy");
  var chunk=level.getChunk(owner.x,owner.z);
  if(chunk.hasData(MiningOreOwnership.LEDGER)&&(!chunk.getData(MiningOreOwnership.LEDGER).sealed()||chunk.getData(MiningOreOwnership.LEDGER).failed()))
   throw new IllegalStateException("Local cinnabar cannot discard unfinished finite generation");
  var output=BuiltInRegistries.BLOCK.get(ResourceLocation.parse("industrial_colonies:cinnabar")).defaultBlockState();
  boolean changed=false;
  for(int gx=Math.floorDiv(owner.getMinBlockX()-LocalCinnabarPattern.MAX_RADIUS,spacing);gx<=Math.floorDiv(owner.getMaxBlockX()+LocalCinnabarPattern.MAX_RADIUS,spacing);gx++)
   for(int gz=Math.floorDiv(owner.getMinBlockZ()-LocalCinnabarPattern.MAX_RADIUS,spacing);gz<=Math.floorDiv(owner.getMaxBlockZ()+LocalCinnabarPattern.MAX_RADIUS,spacing);gz++){
    var candidate=LocalCinnabarPattern.at(level.getSeed(),gx,gz,spacing,chance);if(candidate==null)continue;
    long key=candidate.key();int cx=candidate.x(),cz=candidate.z(),radius=candidate.radius();
    if(cx+radius<owner.getMinBlockX()||cx-radius>owner.getMaxBlockX()||cz+radius<owner.getMinBlockZ()||cz-radius>owner.getMaxBlockZ())continue;
    for(var column:LocalCinnabarPattern.plan(candidate,coverage,thickness)){
      int x=column.point().x(),z=column.point().z();if(x<owner.getMinBlockX()||x>owner.getMaxBlockX()||z<owner.getMinBlockZ()||z>owner.getMaxBlockZ())continue;
      int y=level.getHeight(Heightmap.Types.WORLD_SURFACE_WG,x,z)-1;
      // Snow is cover, not an ore host. Never dig through soil, trees, water or a cave.
      for(int snow=0;snow<4&&y>=minimum;snow++){
       var state=level.getBlockState(new BlockPos(x,y,z));
       if(!state.is(Blocks.SNOW)&&!state.is(Blocks.SNOW_BLOCK)&&!state.is(Blocks.POWDER_SNOW))break;
       y--;
      }
      // A peak taller than the band may still have an exposed face within it.
      // Read only this chunk's heightmap, never survey the connected mountain.
      int faceY=-1;
      for(int scan=Math.min(y,maximum);scan>=minimum;scan--){
       var at=new BlockPos(x,scan,z);if(!GeologyFeature.replaceable(level.getBlockState(at)))continue;
       boolean exposed=scan==y;
       for(int[] side:new int[][]{{-1,0},{1,0},{0,-1},{0,1}}){
        int nx=x+side[0],nz=z+side[1];
        if(nx<owner.getMinBlockX()||nx>owner.getMaxBlockX()||nz<owner.getMinBlockZ()||nz>owner.getMaxBlockZ())continue;
        if(level.getHeight(Heightmap.Types.WORLD_SURFACE_WG,nx,nz)<=scan&&level.getBlockState(new BlockPos(nx,scan,nz)).isAir())exposed=true;
       }
       if(exposed){faceY=scan;break;}
      }
      if(faceY<minimum)continue;y=faceY;
      var pos=new BlockPos(x,y,z);var biome=level.getBiome(pos);
      String id=biome.unwrapKey().map(k->k.location().toString()).orElse("");
      if(!biome.is(BiomeTags.IS_MOUNTAIN)&&!families(id).contains("mountain_highland"))continue;
      for(int depth=0;depth<column.depth()&&y-depth>=minimum;depth++){
       var target=pos.below(depth);
       if(!GeologyFeature.replaceable(level.getBlockState(target)))break;
       if(chunk.hasData(MiningOreOwnership.LEDGER)&&chunk.getData(MiningOreOwnership.LEDGER).claimed(x,target.getY(),z))break;
       changed|=level.setBlock(target,output,2);
      }
     }
   }
  return changed;
 }
}
