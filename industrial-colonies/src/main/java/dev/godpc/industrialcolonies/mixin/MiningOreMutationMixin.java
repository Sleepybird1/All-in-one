package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.MiningOreOwnership;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Catch manual mining, machines, fluids and later world generation at native chunk mutation. */
@Mixin({LevelChunk.class,ProtoChunk.class})
public abstract class MiningOreMutationMixin {
    @Inject(method="setBlockState",at=@At("RETURN"))
    private void industrialColonies$revokeOreClaim(BlockPos pos,BlockState state,boolean moving,CallbackInfoReturnable<BlockState> result){
        var old=result.getReturnValue();
        if(old!=null&&!old.equals(state))MiningOreOwnership.changed((ChunkAccess)(Object)this,pos,state);
    }
}
