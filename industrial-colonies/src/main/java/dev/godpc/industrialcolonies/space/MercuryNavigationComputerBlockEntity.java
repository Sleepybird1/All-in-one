package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Marker actor whose installed presence authorizes the Mercury descent route. */
public final class MercuryNavigationComputerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public MercuryNavigationComputerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.MERCURY_NAVIGATION_COMPUTER.get(), pos, state);
    }
}
