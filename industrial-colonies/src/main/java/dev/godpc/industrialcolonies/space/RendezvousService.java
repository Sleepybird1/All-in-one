package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.LeverBlock;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.sprocketgames.create_aeronautics_automated_logistics.dock.DockingConnectorDiscovery;
import java.util.*;

/** Server-thread operator-commissioned, non-resuming local docking sessions. */
public final class RendezvousService {
    public record Snapshot(String state,String reason,long captureAt,RendezvousApproach.Status guidance){}
    private static final Map<MinecraftServer,Map<UUID,Run>> RUNS=new WeakHashMap<>();
    private static boolean registered;
    private static final class Run {
        final ServerLevel level;final ServerSubLevel ship,target;final BlockPos shipPort,targetPort,shipLever,targetLever;
        final RendezvousApproach approach;final long started;
        long captureAt=-1;int lockedTicks;String state="APPROACH",reason="STARTED";boolean terminal;
        RendezvousApproach.Status latest;
        Run(ServerLevel level,ServerSubLevel ship,ServerSubLevel target,BlockPos a,BlockPos b,BlockPos x,BlockPos y,RendezvousApproach approach){
            this.level=level;this.ship=ship;this.target=target;shipPort=a.immutable();targetPort=b.immutable();shipLever=x.immutable();targetLever=y.immutable();this.approach=approach;latest=approach.status();started=level.getGameTime();
        }
        void stop(String why){approach.close();terminal=true;state="STOPPED";reason=why;}
    }
    private RendezvousService(){}
    public static void register(){
        if(registered)return;registered=true;RcsActuatorLease.register();
        NeoForge.EVENT_BUS.addListener(RendezvousCommands::commands);
        NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post event)->tick(event.getServer()));
        NeoForge.EVENT_BUS.addListener((ServerStoppingEvent event)->{var runs=RUNS.remove(event.getServer());if(runs!=null)runs.values().forEach(run->run.stop("SERVER_STOP"));});
    }
    public static UUID start(ServerLevel level,BlockPos shipPort,BlockPos targetPort,BlockPos shipLever,BlockPos targetLever){
        var server=level.getServer();if(!server.isSameThread())throw new IllegalStateException("Server thread required");
        if(!(Sable.HELPER.getContaining(level,shipPort) instanceof ServerSubLevel ship)
                ||!(Sable.HELPER.getContaining(level,targetPort) instanceof ServerSubLevel target)||ship==target)throw new IllegalArgumentException("Ports must belong to two loaded ships in this dimension");
        var runs=RUNS.computeIfAbsent(server,k->new LinkedHashMap<>());
        if(runs.values().stream().filter(run->!run.terminal).count()>=8)throw new IllegalStateException("Eight active rendezvous sessions maximum");
        if(runs.values().stream().anyMatch(run->!run.terminal&&(run.ship==ship||run.target==ship||run.ship==target||run.target==target)))throw new IllegalStateException("A ship or target is already reserved by another rendezvous");
        for(var p:List.of(shipPort,targetPort)){
            if(!level.hasChunkAt(p)||!DockingConnectorDiscovery.isDock(level,p)||level.hasNeighborSignal(p))throw new IllegalArgumentException("Both native ports must be loaded and unpowered");
            var be=level.getBlockEntity(p);if(be==null||be.saveWithoutMetadata(level.registryAccess()).contains("OtherConnector"))throw new IllegalStateException("A port already has a native partner");
        }
        validateLever(level,ship,shipLever);validateLever(level,target,targetLever);
        var engines=new ArrayList<BlockPos>();
        for(var holder:ship.getPlot().getLoadedChunks())for(var be:holder.getChunk().getBlockEntities().values())
            if(be instanceof RCSThrusterBlockEntity&&Sable.HELPER.getContaining(be)==ship)engines.add(be.getBlockPos().immutable());
        if(engines.isEmpty()||engines.size()>128)throw new IllegalStateException("Expected 1-128 loaded RCS engines");
        engines.sort(Comparator.comparingLong(BlockPos::asLong));
        var a=endpoint(level,ship,shipPort);var b=endpoint(level,target,targetPort);
        // Larger tilted cargo hulls need a short braking/rotation envelope even
        // when their current attitude is aligned. Keep collision reserves and
        // command a slow local approach instead of repeatedly accelerating into
        // the clearance abort. These are blocks/second, not blocks/game tick.
        // The full receiver footprint leaves only one block between the swept
        // plot boxes at the final three-block port separation. At .08 the
        // speed-dependent stopping/rotation reserve can exceed that gap after
        // entry. Stage below .04 and retain the same collision inflation.
        var limits=new RendezvousGuidance.Limits(3,3,.10,.04,.2,.2,Math.toRadians(2),.02,.15,32,3);
        var approach=RendezvousApproach.start(a,b,engines,limits).orElseThrow(()->new IllegalStateException("Ship controls, native frame or actuator ownership denied start"));
        runs.entrySet().removeIf(e->e.getValue().terminal&&runs.size()>=64);
        runs.put(ship.getUniqueId(),new Run(level,ship,target,shipPort,targetPort,shipLever,targetLever,approach));return ship.getUniqueId();
    }
    private static RendezvousApproach.Endpoint endpoint(ServerLevel level,ServerSubLevel body,BlockPos port){
        var outward=level.getBlockState(port).getValue(BlockStateProperties.FACING);
        return new RendezvousApproach.Endpoint(body,port,outward,outward.getAxis()==Direction.Axis.Y?Direction.NORTH:Direction.UP);
    }
    private static void validateLever(ServerLevel level,ServerSubLevel body,BlockPos p){
        if(!level.hasChunkAt(p)||Sable.HELPER.getContaining(level,p)!=body)throw new IllegalArgumentException("Lever must be loaded on its ship");
        var state=level.getBlockState(p);if(!(state.getBlock() instanceof LeverBlock)||state.getValue(LeverBlock.POWERED))throw new IllegalArgumentException("Configure an existing lever in the off position");
    }
    public static String status(MinecraftServer server,UUID id){var run=RUNS.getOrDefault(server,Map.of()).get(id);return run==null?"No session (sessions do not resume after restart)":run.state+": "+run.reason;}
    public static Optional<Snapshot> snapshot(MinecraftServer server,UUID id){
        if(!server.isSameThread())throw new IllegalStateException("Server thread required");
        var run=RUNS.getOrDefault(server,Map.of()).get(id);return run==null?Optional.empty():Optional.of(new Snapshot(run.state,run.reason,run.captureAt,run.latest));
    }
    public static boolean stop(MinecraftServer server,UUID id){
        if(!server.isSameThread())throw new IllegalStateException("Server thread required");
        var run=RUNS.getOrDefault(server,Map.of()).get(id);if(run==null)return false;run.stop("OPERATOR_STOP; existing dock lever positions retained");return true;
    }
    private static void tick(MinecraftServer server){
        for(var run:RUNS.getOrDefault(server,Map.of()).values()){
            if(run.terminal)continue;
            try{
                long now=run.level.getGameTime();
                if(run.ship.isRemoved()||run.target.isRemoved()||SpaceflightAuthorization.automationDisabled(run.ship)||SpaceflightAuthorization.automationDisabled(run.target)){run.stop("SHIP_UNAVAILABLE_OR_DISABLED");continue;}
                if(now<run.started||now-run.started>6400){run.stop("SESSION_TIMEOUT");continue;}
                if(run.captureAt<0){
                    if(run.level.hasNeighborSignal(run.shipPort)||run.level.hasNeighborSignal(run.targetPort)){run.stop("MANUAL_DOCK_POWER");continue;}
                    var result=run.approach.tick();run.latest=result;run.state=result.phase();run.reason=result.reason();
                    if(result.phase().equals("ABORT")){run.stop(result.reason());continue;}
                    if(result.captureAdmitted()){
                        var capture=RendezvousCapture.activate(run.approach,run.shipLever,run.targetLever);
                        if(!capture.activated()){run.stop(capture.reason());continue;}
                        run.captureAt=now;run.state="CAPTURING";run.reason=capture.reason();
                    }
                }else{
                    if(!run.level.hasChunkAt(run.shipPort)||!run.level.hasChunkAt(run.targetPort)){run.stop("PORT_UNLOADED");continue;}
                    if(DockingConnectorDiscovery.isLockedPair(run.level,run.shipPort,run.targetPort))run.lockedTicks++;else run.lockedTicks=0;
                    if(run.lockedTicks>=10){run.approach.close();run.terminal=true;run.state="DOCKED";run.reason="Native reciprocal lock held ten ticks; physical levers remain on";}
                    else if(now-run.captureAt>100)run.stop("CAPTURE_TIMEOUT; inspect existing dock levers");
                }
            }catch(RuntimeException failure){run.stop("NATIVE_ERROR_"+failure.getClass().getSimpleName());}
        }
    }
}
