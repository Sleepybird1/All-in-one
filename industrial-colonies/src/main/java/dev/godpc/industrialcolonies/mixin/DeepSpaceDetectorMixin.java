package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.station.StationLifeSupport;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Same-body detector coverage in deep space; does not grant entity breathing. */
@Mixin(targets="earth.terrarium.adastra.common.blockentities.machines.DetectorBlockEntity",remap=false)
public abstract class DeepSpaceDetectorMixin {
    @Inject(method="hasOxygen",at=@At("HEAD"),cancellable=true,remap=false)
    private void industrialColonies$actualDeepSpaceCoverage(ServerLevel level, BlockPos pos,
            boolean inverted, CallbackInfoReturnable<Boolean> result) {
        if (!StationLifeSupport.DEEP_SPACE.equals(level.dimension())) return;
        BlockEntity detector=(BlockEntity)(Object)this;
        boolean oxygen=false;
        if (!detector.isRemoved() && detector.getLevel()==level && detector.getBlockPos().equals(pos)
                && level.getBlockEntity(pos)==detector
                && Sable.HELPER.getContaining(detector) instanceof ServerSubLevel body
                && !body.isRemoved() && body.getLevel()==level) {
            for (Direction side:Direction.values()) {
                if (StationLifeSupport.hasLiveCoverage(body,pos.relative(side))) {
                    oxygen=true;
                    break;
                }
            }
        }
        result.setReturnValue(oxygen != inverted);
    }
}
