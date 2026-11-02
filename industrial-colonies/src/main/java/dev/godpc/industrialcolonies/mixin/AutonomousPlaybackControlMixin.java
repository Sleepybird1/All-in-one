package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.AutonomousShipControl;
import dev.godpc.industrialcolonies.space.ShipHandoffCoordinator;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.sprocketgames.create_aeronautics_automated_logistics.dock.session.DockRequestId;
import net.sprocketgames.create_aeronautics_automated_logistics.route.*;
import net.sprocketgames.create_aeronautics_automated_logistics.service.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=VehicleRoutePlaybackService.class,remap=false)
public abstract class AutonomousPlaybackControlMixin {
 @Inject(method="startPlayback(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/core/BlockPos;Lnet/sprocketgames/create_aeronautics_automated_logistics/route/Route;Lnet/sprocketgames/create_aeronautics_automated_logistics/dock/session/DockRequestId;)Lnet/sprocketgames/create_aeronautics_automated_logistics/service/PlaybackOperationResult;",at=@At("HEAD"),cancellable=true,require=1)
 private void gateStart(ServerLevel level,BlockPos position,Route route,DockRequestId request,CallbackInfoReturnable<PlaybackOperationResult<RouteId>> result){if(AutonomousShipControl.blocksRoute(level.getServer(),route)||ShipHandoffCoordinator.blocksRoute(level.getServer(),route))result.setReturnValue(PlaybackOperationResult.failure(PlaybackFailure.MOVEMENT_FAILURE));}
 @Inject(method="startHeldFaultPlayback(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/core/BlockPos;Lnet/sprocketgames/create_aeronautics_automated_logistics/route/Route;Lnet/sprocketgames/create_aeronautics_automated_logistics/service/PlaybackFailure;Lnet/sprocketgames/create_aeronautics_automated_logistics/dock/session/DockRequestId;)Lnet/sprocketgames/create_aeronautics_automated_logistics/service/PlaybackOperationResult;",at=@At("HEAD"),cancellable=true,require=1)
 private void gateHeld(ServerLevel level,BlockPos position,Route route,PlaybackFailure failure,DockRequestId request,CallbackInfoReturnable<PlaybackOperationResult<RouteId>> result){if(AutonomousShipControl.blocksRoute(level.getServer(),route)||ShipHandoffCoordinator.blocksRoute(level.getServer(),route))result.setReturnValue(PlaybackOperationResult.failure(PlaybackFailure.MOVEMENT_FAILURE));}
 @Inject(method="resumeHeldPlayback",at=@At("HEAD"),cancellable=true,require=1)
 private void gateResume(ServerLevel level,RouteId id,CallbackInfoReturnable<Boolean> result){var data=AutonomousShipControl.get(level.getServer());if(ShipHandoffCoordinator.blocksPlayback(level.getServer(),id)||data.allDisabled()||AutomatedLogisticsServices.PLAYBACK.runtimePlaybackSummaries(level.getServer()).stream().anyMatch(r->r.routeId().equals(id)&&r.transponderId().filter(data::disabled).isPresent()))result.setReturnValue(false);}
}
