package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Marker actor whose live ship-local presence authorizes the signed Glacio route. */
public final class InterstellarNavigationComputerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public InterstellarNavigationComputerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.INTERSTELLAR_NAVIGATION_COMPUTER.get(), pos, state);
    }
}
