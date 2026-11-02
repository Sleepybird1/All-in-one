package dev.godpc.industrialcolonies.mixin;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Preserve the native missing-controller fallback for nullable physics views. */
@Mixin(targets="earth.terrarium.adastra.common.blocks.SlidingDoorBlock",remap=false)
public abstract class SlidingDoorSparseViewMixin {
    @ModifyVariable(method="<init>",at=@At("HEAD"),argsOnly=true,remap=false)
    private static BlockBehaviour.Properties industrialColonies$dynamicControllerShape(BlockBehaviour.Properties properties) {
        // The shape depends on the controller in the supplied world view.
        // It cannot be cached from an empty world once per block state.
        return properties.dynamicShape();
    }
    @Redirect(method="getCollisionShape",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/BlockGetter;getBlockState(Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/state/BlockState;"),remap=false)
    private BlockState industrialColonies$missingControllerState(BlockGetter view, BlockPos pos) {
        BlockState state=view.getBlockState(pos);
        // AIR has no door PART, so the original method takes its existing
        // non-controller fallback. This does not return an empty collision.
        return state==null ? Blocks.AIR.defaultBlockState() : state;
    }
}
