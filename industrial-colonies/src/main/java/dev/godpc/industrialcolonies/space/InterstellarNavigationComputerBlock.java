package dev.godpc.industrialcolonies.space;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/** Physical route authority required aboard a commissioned interstellar ship. */
public final class InterstellarNavigationComputerBlock extends BaseEntityBlock {
    public static final MapCodec<InterstellarNavigationComputerBlock> CODEC =
            simpleCodec(InterstellarNavigationComputerBlock::new);

    public InterstellarNavigationComputerBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new InterstellarNavigationComputerBlockEntity(pos, state);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected ItemInteractionResult useItemOn(
            ItemStack stack,
            BlockState state,
            net.minecraft.world.level.Level level,
            BlockPos pos,
            Player player,
            InteractionHand hand,
            BlockHitResult hit
    ) {
        if (!stack.is(dev.waco0311.cosmowarp.registry.ModItems.WARP_CRYSTAL.get())) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (!level.isClientSide) {
            boolean signed = SignedInterstellarRoute.signForDimension(stack, level.dimension());
            player.displayClientMessage(
                    Component.translatable(signed
                            ? "message.industrial_colonies.interstellar_route.signed"
                            : "message.industrial_colonies.interstellar_route.invalid_dimension"),
                    true);
            if (!signed) {
                return ItemInteractionResult.FAIL;
            }
            player.getInventory().setChanged();
        }
        return ItemInteractionResult.SUCCESS;
    }
}
