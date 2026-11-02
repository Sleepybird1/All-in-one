package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Marker actor whose installed presence authorizes the Venus descent route. */
public final class VenusNavigationComputerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public VenusNavigationComputerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.VENUS_NAVIGATION_COMPUTER.get(), pos, state);
    }
}
