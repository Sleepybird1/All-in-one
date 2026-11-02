package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RcsWrenchDrive;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import java.util.*;

/** Explicit finite local flight lease. No autonomous target, spawn, orbit or saved resume.
 * Every demand passes the complete commissioned hull check before native allocation.
 * Wrench feasibility is not stopping distance or collision clearance. */
public final class EnemyFlightAdapter implements AutoCloseable {
    private final ServerSubLevel body;
    private final NativeEnemyHull hull;
    private final RcsWrenchDrive drive;
    private final long deadline;
    private final UUID encounter;
    private final EnemyNativeFrame.Key frame;
    private long lastTick;
    private String reason="ACTIVE";
    private EnemyFlightAdapter(ServerSubLevel body,NativeEnemyHull hull,RcsWrenchDrive drive,int lifetime,EnemyNativeFrame.Key frame) {
        this.body=body;this.hull=hull;this.drive=drive;this.frame=frame;lastTick=body.getLevel().getGameTime();deadline=Math.addExact(lastTick,lifetime);encounter=EnemyHullIdentity.read(body).encounter();
    }
    public static Optional<EnemyFlightAdapter> acquire(ServerSubLevel body,NativeEnemyHull hull,List<BlockPos> engines,int lifetime) {
        if(body==null||hull==null||!hull.belongsTo(body)||engines==null||engines.isEmpty()||engines.size()>128
                ||lifetime<1||lifetime>600
                ||!body.getLevel().getServer().isSameThread()||SpaceflightAuthorization.automationDisabled(body)
                ||engines.stream().anyMatch(p->p==null||!hull.observes(p))||!EnemyTargetSelector.mayControlSource(body,hull)
                ||body.getLevel().getGameTime()>Long.MAX_VALUE-lifetime)return Optional.empty();
        var frame=EnemyNativeFrame.read(body);if(frame.isEmpty())return Optional.empty();
        return RcsWrenchDrive.acquire(body,engines).map(drive->new EnemyFlightAdapter(body,hull,drive,lifetime,frame.get()));
    }
    public boolean apply(V acceleration,V angularAcceleration) {
        if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread flight demand required");
        if(!active())return false;
        long tick=body.getLevel().getGameTime();
        if(tick<lastTick||tick-lastTick>2||tick>=deadline)return hold("FLIGHT_LEASE_EXPIRED");
        if(!hull.validate())return hold("HULL_"+hull.reason());
        if(!EnemyNativeFrame.read(body).filter(frame::equals).isPresent())return hold("NATIVE_FRAME_CHANGED");
        if(!EnemyTargetSelector.mayControlSource(body,hull)||!EnemyHullIdentity.read(body).encounter().equals(encounter))return hold("NPC_AUTHORITY_CHANGED");
        if(!bounded(acceleration,.05)||!bounded(angularAcceleration,.01))return hold("UNSAFE_DEMAND");
        if(drive.apply(acceleration,angularAcceleration).isEmpty())return hold("DRIVE_"+drive.reason());
        lastTick=tick;return true;
    }
    private static boolean bounded(V value,double limit) {
        return value!=null&&Double.isFinite(value.x())&&Double.isFinite(value.y())&&Double.isFinite(value.z())
                &&value.x()*value.x()+value.y()*value.y()+value.z()*value.z()<=limit*limit;
    }
    private boolean hold(String why){reason=why;drive.close();return false;}
    public boolean active(){return reason.equals("ACTIVE")&&drive.active();}
    public String reason(){return reason.equals("ACTIVE")?drive.reason():reason;}
    @Override public void close(){hold("EXPLICIT_STOP");}
}
