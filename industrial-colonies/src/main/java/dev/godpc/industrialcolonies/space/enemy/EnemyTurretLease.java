package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import java.util.*;

/** Explicit bounded rotation commands consumed only by the native mount tick.
 * Mechanical inputs remain zero: no kinetic network power is manufactured.
 * Setter writes interrupt immediately; other network changes interrupt on read.
 * No firing authority, automatic reacquisition or native maintenance suppression. */
public final class EnemyTurretLease implements AutoCloseable {
    private static final Map<Object,EnemyTurretLease> OWNERS=new IdentityHashMap<>();
    private static boolean registered;
    private final ServerSubLevel source;
    private final NativeEnemyHull hull;
    private final BlockPos position;
    private final EnemyCannonHold cannon;
    private final EnemyTurretAimPlan planner;
    private final Object mount,yaw,pitch;
    private final long deadline;
    private long refreshed;
    private float expectedYaw,expectedPitch;
    private boolean closed;
    private String reason="ACTIVE";
    private EnemyTurretLease(ServerSubLevel source,NativeEnemyHull hull,BlockPos position,
            EnemyCannonHold cannon,EnemyTurretAimPlan planner,Object mount,Object yaw,Object pitch,int lifetime) {
        this.source=source;this.hull=hull;this.position=position.immutable();this.cannon=cannon;
        this.planner=planner;this.mount=mount;this.yaw=yaw;this.pitch=pitch;
        refreshed=source.getLevel().getGameTime();deadline=Math.addExact(refreshed,lifetime);
    }
    public static Optional<EnemyTurretLease> acquire(ServerSubLevel source,NativeEnemyHull hull,
            BlockPos position,EnemyCannonHold cannon,EnemyTurretAimPlan planner,int lifetime) {
        if(source==null||hull==null||position==null||cannon==null||planner==null||lifetime<1||lifetime>600
                ||!source.getLevel().getServer().isSameThread()||!hull.observes(position)
                ||!cannon.ownsMount(source,hull,position)||OWNERS.size()>=128)return Optional.empty();
        try {
            Object mount=source.getLevel().getBlockEntity(position);
            if(mount==null||OWNERS.containsKey(mount)
                    ||!(mount instanceof EnemyNativeTurretHooks hooks)||!hooks.ic$enemyRotationReadGuard())return Optional.empty();
            Object yaw=mount.getClass().getMethod("getYawInterface").invoke(mount);
            Object pitch=mount.getClass().getMethod("getPitchInterface").invoke(mount);
            if(!(yaw instanceof EnemyNativeTurretHooks yh)||!yh.ic$enemyRotationWriteGuard()
                    ||!(pitch instanceof EnemyNativeTurretHooks ph)||!ph.ic$enemyRotationWriteGuard()
                    ||speed(yaw)!=0||speed(pitch)!=0)return Optional.empty();
            var lease=new EnemyTurretLease(source,hull,position,cannon,planner,mount,yaw,pitch,lifetime);
            if(!registered){registered=true;
                NeoForge.EVENT_BUS.addListener((ServerTickEvent.Pre e)->{
                    for(var owner:List.copyOf(OWNERS.values()))if(owner.source.getLevel().getServer()==e.getServer())owner.validate();
                });
                NeoForge.EVENT_BUS.addListener((ServerStoppingEvent e)->{
                    for(var owner:List.copyOf(OWNERS.values()))if(owner.source.getLevel().getServer()==e.getServer())owner.close("SERVER_STOP");
                });
            }
            OWNERS.put(mount,lease);return Optional.of(lease);
        }catch(ReflectiveOperationException|RuntimeException unavailable){return Optional.empty();}
    }
    public boolean apply(EnemyTurretAimPlan.Plan plan) {
        if(!validate())return false;
        if(plan==null||!plan.observation().weapon().body().equals(source.getUniqueId())||!planner.current(plan)
                ||!Float.isFinite(plan.yawRpm())||!Float.isFinite(plan.pitchRpm())
                ||Math.abs(plan.yawRpm())>16||Math.abs(plan.pitchRpm())>16)return close("STALE_OR_UNSAFE_PLAN");
        return write(plan.yawRpm(),plan.pitchRpm());
    }
    public boolean idle(){return validate()&&write(0,0);}
    private boolean write(float y,float p) {
        expectedYaw=y;expectedPitch=p;
        refreshed=source.getLevel().getGameTime();return true;
    }
    private boolean validate() {
        if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread turret ownership required");
        if(closed)return false;
        try {
            long now=source.getLevel().getGameTime();
            if(now<refreshed||now-refreshed>2||now>=deadline)return close("TURRET_LEASE_EXPIRED");
            if(!cannon.owns(source,hull))return close("CANNON_AUTHORITY_LOST");
            if(source.getLevel().getBlockEntity(position)!=mount
                    ||mount.getClass().getMethod("getYawInterface").invoke(mount)!=yaw
                    ||mount.getClass().getMethod("getPitchInterface").invoke(mount)!=pitch)return close("MOUNT_CHANGED");
            if(speed(yaw)!=0||speed(pitch)!=0)return close("EXTERNAL_ROTATION_INPUT");
            return true;
        }catch(ReflectiveOperationException|RuntimeException unavailable){return close("NATIVE_UNAVAILABLE");}
    }
    private static float speed(Object input)throws ReflectiveOperationException {
        return ((Number)input.getClass().getMethod("getSpeed").invoke(input)).floatValue();
    }
    /** Called only at the native mount tick's two getSpeed invocation sites. */
    public static float rotationInput(Object mount,Object input,float nativeRpm) {
        var owner=OWNERS.get(mount);if(owner==null)return nativeRpm;
        if(!owner.validate())return 0;
        if(input==owner.yaw)return owner.expectedYaw;
        if(input==owner.pitch)return owner.expectedPitch;
        owner.close("ROTATION_READER_CHANGED");return 0;
    }
    /** Native setSpeed is still performed after autonomous ownership is released. */
    public static void beforeInputWrite(Object input) {
        for(var owner:List.copyOf(OWNERS.values()))if(input==owner.yaw||input==owner.pitch){
            if(!owner.source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread turret override required");
            owner.close("EXTERNAL_ROTATION_WRITE");
        }
    }
    public boolean active(){return !closed;}
    public String reason(){return reason;}
    private boolean close(String why) {
        if(closed)return false;closed=true;reason=why;
        expectedYaw=0;expectedPitch=0;OWNERS.remove(mount,this);
        return false;
    }
    @Override public void close(){
        if(!source.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread turret stop required");
        close("EXPLICIT_STOP");
    }
}
