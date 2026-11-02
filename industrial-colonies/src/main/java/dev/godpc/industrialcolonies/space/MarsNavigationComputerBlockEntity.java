package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Marker actor whose installed presence authorizes the Mars descent route. */
public final class MarsNavigationComputerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public MarsNavigationComputerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.MARS_NAVIGATION_COMPUTER.get(), pos, state);
    }
}
