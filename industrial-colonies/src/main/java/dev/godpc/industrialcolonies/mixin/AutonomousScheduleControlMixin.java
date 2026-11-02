package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.AutonomousShipControl;
import dev.godpc.industrialcolonies.space.ShipHandoffCoordinator;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.*;
import net.sprocketgames.create_aeronautics_automated_logistics.block.entity.*;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;
import net.sprocketgames.create_aeronautics_automated_logistics.service.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.UUID;
@Mixin(value=AirshipScheduleExecutionService.class,remap=false)
public abstract class AutonomousScheduleControlMixin {
 @Inject(method="start",at=@At("HEAD"),cancellable=true,require=1)
 private void gateStart(ServerPlayer player,AirshipStationBlockEntity station,BlockPos position,ShipTransponderBlockEntity ship,AirshipSchedule schedule,CallbackInfoReturnable<PlaybackOperationResult<RouteId>> result){if(AutonomousShipControl.get(player.server).disabled(ship.transponderId())||ShipHandoffCoordinator.blocks(player.server,ship.transponderId()))result.setReturnValue(PlaybackOperationResult.failure(PlaybackFailure.MOVEMENT_FAILURE));}
 @Inject(method="startFromTransponder",at=@At("HEAD"),cancellable=true,require=1)
 private void gateTransponder(ServerPlayer player,ShipTransponderBlockEntity ship,AirshipSchedule schedule,CallbackInfoReturnable<PlaybackOperationResult<RouteId>> result){if(AutonomousShipControl.get(player.server).disabled(ship.transponderId())||ShipHandoffCoordinator.blocks(player.server,ship.transponderId()))result.setReturnValue(PlaybackOperationResult.failure(PlaybackFailure.MOVEMENT_FAILURE));}
 @Inject(method="resumeHeldPlayback",at=@At("HEAD"),cancellable=true,require=1)
 private void gateResume(ServerLevel level,UUID id,CallbackInfoReturnable<Boolean> result){if(AutonomousShipControl.get(level.getServer()).disabled(id)||ShipHandoffCoordinator.blocks(level.getServer(),id))result.setReturnValue(false);}
}
