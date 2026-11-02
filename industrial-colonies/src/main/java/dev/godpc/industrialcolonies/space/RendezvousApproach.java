package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import org.joml.Vector3d;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.*;

/** Non-persistent local approach session. Its caller must tick it on the server
 * thread and act on the capture-admission result through a separately verified
 * docking controller. This class never powers ports or edits world blocks.
 */
public final class RendezvousApproach implements AutoCloseable {
    public record Endpoint(ServerSubLevel body,BlockPos port,Direction outward,Direction up){
        public Endpoint{Objects.requireNonNull(body);port=Objects.requireNonNull(port).immutable();Objects.requireNonNull(outward);Objects.requireNonNull(up);}
    }
    public record Status(String phase,String reason,boolean captureAdmitted,double distance,double relativeSpeed,double angle){}
    private final Endpoint ship,target;
    private final Limits limits;
    private final RendezvousGuidance guidance;
    private final RcsWrenchDrive drive;
    private Status status=new Status("APPROACH","STARTED",false,Double.NaN,Double.NaN,Double.NaN);
    private boolean ended;
    private int ready;
    private long lastTick=Long.MIN_VALUE;
    private boolean captureClaimed;
    record CaptureTicket(Endpoint ship,Endpoint target,long tick){}
    Optional<CaptureTicket> claimCapture(){
        if(!ship.body().getLevel().getServer().isSameThread()||captureClaimed||!status.captureAdmitted()
                ||lastTick!=ship.body().getLevel().getGameTime())return Optional.empty();
        captureClaimed=true;return Optional.of(new CaptureTicket(ship,target,lastTick));
    }
    private RendezvousApproach(Endpoint ship,Endpoint target,Limits limits,RcsWrenchDrive drive){this.ship=ship;this.target=target;this.limits=limits;this.guidance=new RendezvousGuidance(limits);this.drive=drive;}
    public static Optional<RendezvousApproach> start(Endpoint ship,Endpoint target,List<BlockPos> engines,Limits limits){
        Objects.requireNonNull(limits);
        if(ship==null||target==null||ship.body()==target.body()||ship.body().getLevel()!=target.body().getLevel()
                ||!ship.body().getLevel().getServer().isSameThread()
                ||SpaceflightAuthorization.automationDisabled(ship.body())||SpaceflightAuthorization.automationDisabled(target.body()))return Optional.empty();
        var from=sample(ship);var to=sample(target);
        if(from.isEmpty()||to.isEmpty()||!from.get().frame().equals(to.get().frame()))return Optional.empty();
        return RcsWrenchDrive.acquire(ship.body(),engines).map(drive->new RendezvousApproach(ship,target,limits,drive));
    }
    public Status status(){return status;}
    public Status tick(){
        if(!ship.body().getLevel().getServer().isSameThread())throw new IllegalStateException("Approach requires server thread");
        if(ended){
            if(status.captureAdmitted()&&ship.body().getLevel().getGameTime()!=lastTick)
                status=new Status(status.phase(),"ADMISSION_EXPIRED",false,status.distance(),status.relativeSpeed(),status.angle());
            return status;
        }
        try{
            long tick=ship.body().getLevel().getGameTime();
            if(tick==lastTick)return status;
            if(lastTick!=Long.MIN_VALUE&&(tick<lastTick||tick-lastTick>2))return abort("MISSED_UPDATE");
            lastTick=tick;
            if(!drive.active())return abort(drive.reason());
            if(SpaceflightAuthorization.automationDisabled(ship.body())||SpaceflightAuthorization.automationDisabled(target.body()))return abort("CONTROL_DISABLED");
            var from=sample(ship);var to=sample(target);
            if(from.isEmpty()||to.isEmpty())return abort("PORT_UNAVAILABLE");
            var a=from.get();var b=to.get();
            double relative=a.velocity().sub(b.velocity()).length();
            double horizon=.25+relative/limits.acceleration();
            V finalTravel=b.position().add(b.outward().mul(limits.separation())).sub(a.position());
            var finalClearance=RendezvousClearance.check(ship.body(),finalTravel,horizon,limits.acceleration());
            // A blocked final sweep postpones entry while staging remains clear;
            // losing it after entering final approach is still a latched abort.
            var command=guidance.update(tick/20.0,a,b,new Conditions(true,true,true,true,true,false,finalClearance.clear()));
            if(command.phase()==Phase.ABORT)return abort(command.reason());
            boolean finalApproach=command.phase()==Phase.CAPTURE||command.phase()==Phase.READY;
            double aimDistance=limits.separation()+(finalApproach?0:limits.stagingDistance());
            V travel=b.position().add(b.outward().mul(aimDistance)).sub(a.position());
            var clearance=finalApproach?finalClearance:RendezvousClearance.check(ship.body(),travel,horizon,limits.acceleration());
            if(!clearance.clear())return abort(clearance.reason());
            var attitude=RendezvousAttitude.demand(a.outward(),a.up(),a.angularVelocity(),b.outward().mul(-1),b.up(),b.angularVelocity(),.25,.1);
            var center=ship.body().logicalPose().transformPosition(new Vector3d(ship.body().getMassTracker().getCenterOfMass()));
            V lever=a.position().sub(new V(center.x,center.y,center.z));V omega=a.angularVelocity(),alpha=attitude.angularAcceleration();
            V acceleration=command.acceleration().sub(alpha.cross(lever)).sub(omega.cross(omega.cross(lever)));
            if(drive.apply(acceleration,alpha).isEmpty())return abort(drive.reason());
            ready=command.allowCapture()?ready+1:0;
            boolean admit=ready>=5;
            status=new Status(command.phase().name(),command.reason(),admit,command.distance(),command.relativeSpeed(),attitude.angle());
            if(admit){ended=true;drive.close();}
            return status;
        }catch(RuntimeException error){return abort("NATIVE_ERROR_"+error.getClass().getSimpleName());}
    }
    private static Optional<Port> sample(Endpoint e){return RendezvousTelemetry.sample(e.body(),e.port(),e.outward(),e.up());}
    private Status abort(String why){ended=true;drive.close();status=new Status("ABORT",why,false,Double.NaN,Double.NaN,Double.NaN);return status;}
    @Override public void close(){abort("CANCELLED");}
}
