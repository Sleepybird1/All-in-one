package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.blocks.RocketThrusterBlockEntity;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Exclusive, non-resuming autonomous ownership of native rocket-engine computer inputs.
 * Manual calls revoke a live lease. Acquisition requires explicitly disarmed controls. A persisted marker clears orphaned computer
 * activation on load. Rocket native active/throttle setters remain manual control.
 */
public final class RocketActuatorLease implements AutoCloseable {
    public static final String SAVED_MARKER="IndustrialColoniesRocketOwned";
    private static final Map<RocketThrusterBlockEntity,RocketActuatorLease> OWNERS=new ConcurrentHashMap<>();
    private static final ThreadLocal<Boolean> INTERNAL=ThreadLocal.withInitial(()->false);
    private static boolean registered;
    private final ServerSubLevel body;
    private final ServerLevel level;
    private final List<RocketThrusterBlockEntity> engines;
    private final float[] lastThrottle;
    private long refreshedAt;
    private boolean closed;
    private volatile String conflict;
    private String reason="ACTIVE";

    private RocketActuatorLease(ServerSubLevel body,List<RocketThrusterBlockEntity> engines){
        this.body=body;this.level=body.getLevel();this.engines=List.copyOf(engines);
        this.lastThrottle=new float[engines.size()];Arrays.fill(lastThrottle,Float.NaN);
        this.refreshedAt=level.getGameTime();
    }
    public static void register(){
        if(registered)return;registered=true;
        NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post event)->{
            for(var lease:new HashSet<>(OWNERS.values()))if(lease.level.getServer()==event.getServer())lease.validate();
        });
        NeoForge.EVENT_BUS.addListener((ServerStoppingEvent event)->{
            for(var lease:new HashSet<>(OWNERS.values()))if(lease.level.getServer()==event.getServer())lease.close("SERVER_STOP");
        });
    }
    public static Optional<RocketActuatorLease> acquire(ServerSubLevel body,List<BlockPos> positions){
        if(body==null||body.isRemoved()||positions==null||positions.isEmpty()||positions.size()>128
                ||!body.getLevel().getServer().isSameThread()||SpaceflightAuthorization.automationDisabled(body))return Optional.empty();
        var level=body.getLevel();var found=new ArrayList<RocketThrusterBlockEntity>();var unique=new HashSet<BlockPos>();
        for(var p:positions){
            if(p==null||!unique.add(p)||!level.hasChunkAt(p)||Sable.HELPER.getContaining(level,p)!=body
                    ||!(level.getBlockEntity(p) instanceof RocketThrusterBlockEntity engine)||engine.isRemoved()
                    ||OWNERS.containsKey(engine)||engine.isActive()||!controlsOff(engine)
                    ||engine.getPersistentData().contains(SAVED_MARKER))return Optional.empty();
            found.add(engine);
        }
        register();
        var lease=new RocketActuatorLease(body,found);
        for(var engine:found){OWNERS.put(engine,lease);engine.getPersistentData().putBoolean(SAVED_MARKER,true);engine.setChanged();}
        return Optional.of(lease);
    }
    /** Native isActive reports burning, so also reject an armed but unfueled engine. */
    private static boolean controlsOff(RocketThrusterBlockEntity engine){
        var saved=engine.saveWithoutMetadata(engine.getLevel().registryAccess());
        return !saved.getBoolean("TargetActive")&&saved.getFloat("TargetThrottle")==0;
    }
    /** Called every control tick; no renewal means release after two missed ticks. */
    public boolean apply(List<Double> throttles){
        requireServerThread();
        if(!validate())return false;
        if(throttles==null||throttles.size()!=engines.size()) {close("INVALID_COMMAND");return false;}
        for(var value:throttles)if(value==null||!Double.isFinite(value)||value<0||value>1){close("INVALID_COMMAND");return false;}
        // An armed empty engine can restart unexpectedly when a pump supplies fuel.
        // Refuse the whole allocation rather than silently losing one thrust axis.
        for(int i=0;i<engines.size();i++)if(throttles.get(i)>0&&engines.get(i).fuelTank.isEmpty()){
            close("FUEL_UNAVAILABLE");return false;
        }
        try{
            internal(()->{
                for(int i=0;i<engines.size();i++){
                    float value=throttles.get(i).floatValue();
                    if(Float.compare(value,lastThrottle[i])!=0){
                        var engine=engines.get(i);engine.setThrottle(value);engine.setActive(value>0);lastThrottle[i]=value;
                    }
                }
            });
            refreshedAt=level.getGameTime();return true;
        }catch(RuntimeException failure){close("ACTUATOR_ERROR");return false;}
    }
    public boolean active(){return !closed;}
    public String reason(){return reason;}
    private boolean validate(){
        if(closed)return false;
        long now=level.getGameTime();String failure=conflict;
        if(failure==null&&(now<refreshedAt||now-refreshedAt>2))failure="WATCHDOG_EXPIRED";
        if(failure==null&&(body.isRemoved()||body.getLevel()!=level))failure="BODY_UNAVAILABLE";
        if(failure==null&&SpaceflightAuthorization.automationDisabled(body))failure="SERVER_CONTROL_DISABLED";
        if(failure==null)for(var engine:engines){
            var pos=engine.getBlockPos();
            if(engine.isRemoved()||!level.hasChunkAt(pos)||level.getBlockEntity(pos)!=engine
                    ||Sable.HELPER.getContaining(level,pos)!=body||OWNERS.get(engine)!=this
                    ||!engine.getPersistentData().contains(SAVED_MARKER)) {failure="ACTUATOR_CHANGED";break;}
        }
        if(failure==null)for(int i=0;i<engines.size();i++){
            if(lastThrottle[i]>0&&engines.get(i).fuelTank.isEmpty()){failure="FUEL_UNAVAILABLE";break;}
        }
        if(failure!=null){close(failure);return false;}return true;
    }
    @Override public void close(){close("RELEASED");}
    private void close(String why){
        requireServerThread();if(closed)return;closed=true;reason=why;
        for(var engine:engines){
            // Retain the saved marker if stopping throws, so load still clears it.
            try{internal(()->{engine.setThrottle(0);engine.setActive(false);});engine.getPersistentData().remove(SAVED_MARKER);engine.setChanged();}
            catch(RuntimeException failure){reason=why+"_STOP_PENDING_LOAD";}
            finally{OWNERS.remove(engine,this);}
        }
    }
    private void requireServerThread(){if(!level.getServer().isSameThread())throw new IllegalStateException("rocket-engine lease requires server thread");}
    private static void internal(Runnable action){boolean before=INTERNAL.get();INTERNAL.set(true);try{action.run();}finally{INTERNAL.set(before);}}

    /** Mixin boundary: manual native commands take precedence and cancel navigation. */
    public static boolean beforeNativeWrite(Object object){
        if(INTERNAL.get()||!(object instanceof RocketThrusterBlockEntity engine))return true;
        var owner=OWNERS.get(engine);if(owner==null)return true;
        if(!owner.level.getServer().isSameThread()){owner.conflict="OFF_THREAD_OVERRIDE";return false;}
        owner.close("MANUAL_OVERRIDE");return true;
    }
    public static void onNativeLoad(Object object){
        if(!(object instanceof RocketThrusterBlockEntity engine)||!(engine.getLevel() instanceof ServerLevel level)
                ||!level.getServer().isSameThread()||!engine.getPersistentData().contains(SAVED_MARKER))return;
        var owner=OWNERS.get(engine);if(owner!=null)owner.close("RELOADED");
        internal(()->{engine.setThrottle(0);engine.setActive(false);});
        engine.getPersistentData().remove(SAVED_MARKER);engine.setChanged();
    }
    public static void onNativeUnload(Object object){
        if(object instanceof RocketThrusterBlockEntity engine){var owner=OWNERS.get(engine);if(owner!=null){
            if(owner.level.getServer().isSameThread())owner.close("UNLOADED");else owner.conflict="UNLOADED";
        }}
    }
}
