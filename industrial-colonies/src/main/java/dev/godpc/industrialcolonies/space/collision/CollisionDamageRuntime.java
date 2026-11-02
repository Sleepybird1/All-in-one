package dev.godpc.industrialcolonies.space.collision;

import dev.ryanhcode.sable.api.physics.PhysicsPipeline;
import dev.ryanhcode.sable.companion.math.Pose3d;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.joml.Vector3d;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.*;
import java.util.function.BooleanSupplier;

/** Explicitly armed staged runtime. Physics callbacks only copy bounded native
 * data. Block writes run on the normal server thread, never on the physics worker.
 * Nothing arms from a saved file, startup, re-enabled switch or nearby collision. */
public final class CollisionDamageRuntime {
    private CollisionDamageRuntime() {}
    private static final Map<MinecraftServer,ServerState> SERVERS=new IdentityHashMap<>();
    private static boolean listeners;
    private static final int MAX_BODIES=128,MAX_STEPS=64,MAX_BATCHES=4,MAX_SESSIONS=64;
    private static final class ServerState {
        final CollisionEpisodeBudget budget=new CollisionEpisodeBudget(1024);
        final Map<ServerLevel,Scope> scopes=new IdentityHashMap<>();
    }
    private static final class Scope {
        final ServerLevel level;
        final UUID worldIdentity;
        final Map<UUID,Session> sessions=new LinkedHashMap<>();
        final List<Map<Integer,CollisionContactMotion.Body>> frames=new ArrayList<>();
        final ArrayDeque<Captured> pending=new ArrayDeque<>();
        long tick=-1;String fault;
        Scope(ServerLevel level){this.level=level;worldIdentity=UUID.nameUUIDFromBytes(("ic-collision-world:"+level.dimension().location()).getBytes(StandardCharsets.UTF_8));}
    }
    private record Captured(long tick,List<CollisionObservationBuffer.Contact> contacts,
                            List<Map<Integer,CollisionContactMotion.Body>> frames) {}
    public record Status(boolean held,int contacts,int removed,long dispatchTicks,Map<String,Integer> outcomes) {
        public Status {outcomes=Map.copyOf(outcomes);}
    }
    public static final class Session implements AutoCloseable {
        private final Scope scope;private final ServerSubLevel body;private final CollisionHullDamage damage;
        private final Map<String,Integer> outcomes=new LinkedHashMap<>();
        private int contacts,removed;private long dispatchTicks;private boolean closed;
        private Session(Scope scope,ServerSubLevel body,CollisionHullDamage damage){this.scope=scope;this.body=body;this.damage=damage;}
        private void record(CollisionHullDamage.Outcome outcome){removed+=outcome.removed();outcomes.merge(outcome.reason(),1,Integer::sum);}
        public Status status(){synchronized(CollisionDamageRuntime.class){return new Status(closed||damage.held(),contacts,removed,dispatchTicks,outcomes);}}
        @Override public void close(){synchronized(CollisionDamageRuntime.class){
            requireThread(scope.level);if(closed)return;closed=true;damage.close();scope.sessions.remove(body.getUniqueId(),this);
            if(scope.sessions.isEmpty()){
                var state=SERVERS.get(scope.level.getServer());if(state!=null)state.scopes.remove(scope.level);
                scope.pending.clear();scope.frames.clear();
            }
        }}
    }
    /** Trusted server admission only. The supplied sets are explicit owner approval,
     * not data read from a client packet. Collider hooks stay inert without this call. */
    public static synchronized Optional<Session> arm(ServerSubLevel body,Set<UUID> players,Set<UUID> npcs,
            BooleanSupplier featureEnabled,Path journalDirectory) {
        if(body==null)return Optional.empty();ServerLevel level=body.getLevel();requireThread(level);
        var state=SERVERS.computeIfAbsent(level.getServer(),unused->new ServerState());
        if(state.scopes.values().stream().mapToInt(s->s.sessions.size()).sum()>=MAX_SESSIONS)return Optional.empty();
        var writer=CollisionHullDamage.open(body,players,npcs,featureEnabled,journalDirectory,state.budget);
        if(writer.isEmpty())return Optional.empty();
        var scope=state.scopes.computeIfAbsent(level,Scope::new);
        var session=new Session(scope,body,writer.get());scope.sessions.put(body.getUniqueId(),session);
        // Discard any earlier partial capture: a newly armed body starts next full tick.
        scope.frames.clear();scope.pending.clear();scope.fault="ARMED_MID_TICK";
        if(!listeners){
            NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post event)->dispatch(event.getServer()));
            NeoForge.EVENT_BUS.addListener((ServerStoppedEvent event)->stop(event.getServer()));listeners=true;
        }
        return Optional.of(session);
    }
    public static synchronized void beforeStep(ServerLevel level,PhysicsPipeline pipeline,
            Collection<ServerSubLevel> nativeBodies) {
        Scope scope=scope(level);if(scope==null)return;
        long now=level.getGameTime();if(scope.tick!=now){scope.tick=now;scope.frames.clear();scope.fault=null;}
        try {
            if(scope.fault!=null)return;
            if(scope.frames.size()>=MAX_STEPS||nativeBodies.size()>MAX_BODIES)throw new IllegalStateException("CAPTURE_LIMIT");
            Map<Integer,CollisionContactMotion.Body> frame=new HashMap<>();
            var zero=new CollisionObservationBuffer.Vector(0,0,0);
            frame.put(-1,new CollisionContactMotion.Body(-1,scope.worldIdentity,zero,new CollisionContactMotion.Rotation(0,0,0,1),zero,zero,0));
            for(ServerSubLevel body:nativeBodies){
                if(body==null||body.isRemoved()||body.getLevel()!=level)throw new IllegalStateException("BODY_UNAVAILABLE");
                var pose=pipeline.readPose(body,new Pose3d());var q=pose.orientation();
                var snapshot=new CollisionContactMotion.Body(body.getRuntimeId(),body.getUniqueId(),vector(pose.position()),
                        new CollisionContactMotion.Rotation(q.x,q.y,q.z,q.w),vector(pipeline.getLinearVelocity(body,new Vector3d())),
                        vector(pipeline.getAngularVelocity(body,new Vector3d())),body.getMassTracker().getMass());
                if(frame.put(body.getRuntimeId(),snapshot)!=null)throw new IllegalStateException("DUPLICATE_RUNTIME_BODY");
            }
            scope.frames.add(Map.copyOf(frame));
        }catch(RuntimeException failure){scope.fault=failure.toString();scope.frames.clear();}
    }
    /** Called with the array already returned by the game's sole clearCollisions.
     * Never clears, retains or modifies that native array. */
    public static synchronized void observe(ServerLevel level,long tick,double[] original){
        Scope scope=scope(level);if(scope==null||original==null||original.length==0)return;
        if(scope.fault!=null||scope.tick!=tick||scope.frames.isEmpty()){scope.fault="MISSING_COMPLETE_PRESTEP_CAPTURE";return;}
        var buffer=new CollisionObservationBuffer(1,256);
        if(!buffer.capture(tick,original)){scope.fault="REFUSED_NATIVE_BATCH_"+buffer.snapshot().lastRefusal();return;}
        if(scope.pending.size()>=MAX_BATCHES){scope.fault="PENDING_BATCH_LIMIT";return;}
        scope.pending.add(new Captured(tick,buffer.snapshot().batches().getFirst().contacts(),List.copyOf(scope.frames)));
    }
    private static Scope scope(ServerLevel level){
        var state=SERVERS.get(level.getServer());var scope=state==null?null:state.scopes.get(level);
        return scope==null||scope.sessions.values().stream().noneMatch(s->!s.closed&&!s.damage.held())?null:scope;
    }
    private static synchronized void dispatch(MinecraftServer server){
        var state=SERVERS.get(server);if(state==null)return;
        for(Scope scope:List.copyOf(state.scopes.values())){
            requireThread(scope.level);
            for(Session session:scope.sessions.values()){
                session.dispatchTicks++;if(session.damage.held())continue;
                var poll=session.damage.poll();if(session.damage.held())session.record(poll);
            }
            if(scope.fault!=null){
                scope.pending.clear();for(Session session:scope.sessions.values())session.outcomes.merge("CAPTURE_REFUSED: "+scope.fault,1,Integer::sum);continue;
            }
            while(!scope.pending.isEmpty()){
                Captured captured=scope.pending.removeFirst();
                for(var contact:captured.contacts()){
                    List<CollisionContactMotion.Step> steps=new ArrayList<>();boolean complete=true;int ordinal=0;
                    for(var frame:captured.frames()){
                        var a=frame.get(contact.bodyA());var b=frame.get(contact.bodyB());
                        if(a==null||b==null||a.runtimeId()==b.runtimeId()||a.identity().equals(b.identity())){complete=false;break;}
                        steps.add(new CollisionContactMotion.Step(captured.tick(),ordinal++,a,b));
                    }
                    if(!complete)continue;
                    // Both sides share the same episode budget; only explicitly armed owners can lose blocks.
                    for(UUID id:List.of(steps.getFirst().first().identity(),steps.getFirst().second().identity())){
                        var session=scope.sessions.get(id);if(session==null||session.closed||session.damage.held())continue;
                        session.contacts++;session.record(session.damage.impact(captured.tick(),contact,steps));
                    }
                }
            }
        }
    }
    private static synchronized void stop(MinecraftServer server){
        var state=SERVERS.get(server);if(state==null)return;
        for(var scope:List.copyOf(state.scopes.values()))for(var session:List.copyOf(scope.sessions.values()))session.close();
        SERVERS.remove(server);
    }
    private static void requireThread(ServerLevel level){if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread collision admission/dispatch required");}
    private static CollisionObservationBuffer.Vector vector(org.joml.Vector3dc v){return new CollisionObservationBuffer.Vector(v.x(),v.y(),v.z());}
}
