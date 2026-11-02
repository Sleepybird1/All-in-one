package dev.godpc.industrialcolonies.space;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Shipboard authorization computer for the first orbital transition. */
public final class OrbitalFlightComputerBlock extends BaseEntityBlock {
    public static final MapCodec<OrbitalFlightComputerBlock> CODEC = simpleCodec(OrbitalFlightComputerBlock::new);

    public OrbitalFlightComputerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new OrbitalFlightComputerBlockEntity(pos, state);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }
}
