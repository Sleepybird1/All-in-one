package dev.godpc.industrialcolonies.worldgen;

import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.Heightmap;

/** Final natural surface policy for the pack's tall Overworld. */
public final class MountainSurface {
    // THE PACK erosion settings: dirtMin 95 + dirtVariance 40.
    public static final int MAX_PEAT_Y=135;
    private static final Set<String> PEAT=Set.of("peat_grass_block","peat_dirt","peat_coarse_dirt","peat_podzol","peat_mud");
    public static boolean peat(BlockState state) {
        var id=BuiltInRegistries.BLOCK.getKey(state.getBlock());
        return id.getNamespace().equals("regions_unexplored")&&PEAT.contains(id.getPath());
    }
    public static boolean snowAt(int x,int y,int z) {
        if(y<320)return false;
        if(y>=400)return true;
        // Stable patches at the snowline, becoming continuous above Y=400.
        long h=(long)Math.floorDiv(x,4)*341873128712L+(long)Math.floorDiv(z,4)*132897987541L;
        h^=h>>>23;h*=0x2127599bf4325c37L;h^=h>>>47;
        return Math.floorMod(h,80)<y-320;
    }
    public static boolean snowGround(BlockState state) {
        return state.is(BlockTags.BASE_STONE_OVERWORLD)||state.is(BlockTags.DIRT)||state.is(Blocks.GRAVEL)||peat(state);
    }
    public static void finish(ChunkAccess chunk) {
        var pos=new BlockPos.MutableBlockPos();
        int x0=chunk.getPos().getMinBlockX(),z0=chunk.getPos().getMinBlockZ();
        // Use section palettes to skip the overwhelmingly common peat-free sections.
        var sections=chunk.getSections();
        for(int i=0;i<sections.length;i++) {
            int base=chunk.getSectionYFromSectionIndex(i)*16;
            if(base+15<=MAX_PEAT_Y||!sections[i].maybeHas(MountainSurface::peat))continue;
            for(int y=Math.max(base,MAX_PEAT_Y+1);y<base+16;y++)for(int z=0;z<16;z++)for(int x=0;x<16;x++) {
                pos.set(x0+x,y,z0+z);
                if(peat(chunk.getBlockState(pos)))chunk.setBlockState(pos,Blocks.STONE.defaultBlockState(),false);
            }
        }
        for(int z=0;z<16;z++)for(int x=0;x<16;x++) {
            int y=chunk.getHeight(Heightmap.Types.WORLD_SURFACE_WG,x,z);
            pos.set(x0+x,y,z0+z);
            if(!snowAt(pos.getX(),y,pos.getZ())||!snowGround(chunk.getBlockState(pos)))continue;
            // Replace only the exposed natural ground block. This doesn't fill
            // caves, bury foliage, cover roofs, or build floating snow shelves.
            chunk.setBlockState(pos,Blocks.SNOW_BLOCK.defaultBlockState(),false);
        }
    }
}
