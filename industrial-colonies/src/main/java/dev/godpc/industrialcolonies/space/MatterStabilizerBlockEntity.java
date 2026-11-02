package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.IndustrialBlockEntities;
import dev.ryanhcode.sable.api.block.BlockEntitySubLevelActor;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Marker block entity that Sable indexes as part of a moving sublevel.
 *
 * <p>No ticking logic is needed. Its presence in the sublevel actor index is
 * the fail-closed authorization signal consumed by the transition mixin.</p>
 */
public final class MatterStabilizerBlockEntity extends BlockEntity
        implements BlockEntitySubLevelActor {
    public MatterStabilizerBlockEntity(BlockPos pos, BlockState state) {
        super(IndustrialBlockEntities.MATTER_STABILIZER.get(), pos, state);
    }
}
