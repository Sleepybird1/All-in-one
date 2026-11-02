package dev.godpc.industrialcolonies;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.piston.MovingPistonBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Position-aware shape queries. Modded shapes may inspect their actual neighbors. */
public final class SableCollisionShapes {
    private SableCollisionShapes() {}

    public static boolean isSolid(BlockGetter level, BlockPos pos, BlockState state) {
        return !state.isAir() && (state.getBlock() instanceof MovingPistonBlock
                || !state.getCollisionShape(level, pos).isEmpty());
    }

    public static boolean isFullBlock(BlockGetter level, BlockPos pos, BlockState state) {
        return !state.isAir() && state.isCollisionShapeFullBlock(level, pos);
    }
}
