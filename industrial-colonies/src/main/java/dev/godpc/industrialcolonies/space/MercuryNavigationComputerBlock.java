package dev.godpc.industrialcolonies.space;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Physical route computer required aboard a player-bearing craft bound for Mercury. */
public final class MercuryNavigationComputerBlock extends BaseEntityBlock {
    public static final MapCodec<MercuryNavigationComputerBlock> CODEC =
            simpleCodec(MercuryNavigationComputerBlock::new);

    public MercuryNavigationComputerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new MercuryNavigationComputerBlockEntity(pos, state);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }
}
