package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.station.OxygenDistributorAccess;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.gen.Invoker;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Captures the exact active Ad Astra distributor state after each server tick. */
@Pseudo
@Mixin(
        targets = "earth.terrarium.adastra.common.blockentities.machines.OxygenDistributorBlockEntity",
        remap = false)
public abstract class OxygenDistributorBlockEntityMixin implements OxygenDistributorAccess {
    @Shadow
    @Final
    private Set<BlockPos> lastDistributedBlocks;

    @Shadow
    public abstract int distributedBlocksCount();

    @Invoker("calculateFluidPerTick")
    protected abstract long industrialColonies$calculateFluidPerTick();

    @Invoker("canCraftDistribution")
    protected abstract boolean industrialColonies$canCraftDistribution(long fluidAmount);

    @Unique
    private boolean industrialColonies$live;
    @Unique
    private long industrialColonies$verifiedTick = Long.MIN_VALUE;

    @Inject(
            method = "serverTick(Lnet/minecraft/server/level/ServerLevel;JLnet/minecraft/world/level/block/state/BlockState;Lnet/minecraft/core/BlockPos;)V",
            at = @At("TAIL"),
            require = 1)
    private void industrialColonies$captureActiveCoverage(
            ServerLevel level,
            long time,
            BlockState state,
            BlockPos pos,
            CallbackInfo callback
    ) {
        long fluidPerTick = industrialColonies$calculateFluidPerTick();
        industrialColonies$live = isLit()
                && canFunction()
                && distributedBlocksCount() > 0
                && !lastDistributedBlocks.isEmpty()
                && industrialColonies$canCraftDistribution(fluidPerTick);
        industrialColonies$verifiedTick = level.getGameTime();
    }

    @Inject(method = "onRemoved()V", at = @At("HEAD"), require = 1)
    private void industrialColonies$invalidateRemovedDistributor(CallbackInfo callback) {
        industrialColonies$live = false;
        industrialColonies$verifiedTick = Long.MIN_VALUE;
    }

    @Override
    public Set<BlockPos> industrialColonies$getDistributedBlocks() {
        return lastDistributedBlocks;
    }

    @Override
    public boolean industrialColonies$isLive() {
        long fluidPerTick = industrialColonies$calculateFluidPerTick();
        return industrialColonies$live
                && isLit()
                && canFunction()
                && distributedBlocksCount() > 0
                && !lastDistributedBlocks.isEmpty()
                && industrialColonies$canCraftDistribution(fluidPerTick);
    }

    @Override
    public long industrialColonies$lastVerifiedTick() {
        return industrialColonies$verifiedTick;
    }
}
