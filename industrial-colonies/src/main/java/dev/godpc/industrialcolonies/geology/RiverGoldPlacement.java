package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.material.Fluids;

/** Natural placer writes only in the owner chunk, onto exposed gravel. Never ticks or respawns. */
public final class RiverGoldPlacement {
    private RiverGoldPlacement() {}

    public static boolean place(LevelAccessor level, ChunkPos owner, BlockPos pos) {
        if ((pos.getX() >> 4) != owner.x || (pos.getZ() >> 4) != owner.z
                || pos.getY() <= level.getMinBuildHeight() || pos.getY() >= level.getMaxBuildHeight()) return false;
        if (!level.getBlockState(pos.below()).is(Blocks.GRAVEL)) return false;
        var previous = level.getBlockState(pos);
        boolean water = previous.is(Blocks.WATER) && previous.getFluidState().getType() == Fluids.WATER
                && previous.getFluidState().isSource();
        if (!previous.isAir() && !water) return false;
        var flakes = GeologyBlocks.GOLD_FLAKES.get().defaultBlockState()
                .setValue(BlockStateProperties.WATERLOGGED, water);
        return flakes.canSurvive(level, pos) && level.setBlock(pos, flakes, 2);
    }
}
