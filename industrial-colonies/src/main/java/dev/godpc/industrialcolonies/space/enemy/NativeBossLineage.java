package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.api.SubLevelAssemblyHelper.AssemblyTransform;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.*;

/** Unregistered live-only observer owner. Exact native objects, not copied tags,
 * admit descendants. No restart restoration or combat permission is supplied. */
public final class NativeBossLineage implements AutoCloseable {
    private final ServerLevel level;
    private final UUID encounter,root;
    private final Map<UUID,ServerSubLevel> bodies=new HashMap<>();
    private EnemyBossModules modules;
    private EnemyBossAssemblySession session;
    private EnemyBossAssemblySession.Token token;
    private NativeBossAssemblyObservation observation;
    private Destruction pendingDestruction;
    private boolean held;
    public NativeBossLineage(ServerSubLevel original,EnemyBossModules modules){
        level=original.getLevel();thread();
        var identity=EnemyHullIdentity.read(original);
        if(!identity.originalBody()||!modules.belongsTo(identity.encounter(),identity.root())
                ||modules.revision()!=0||modules.modules().values().stream().anyMatch(m->m.destroyed()
                ||!m.location().body().equals(original.getUniqueId())))
            throw new IllegalStateException("Fresh commissioned root required");
        encounter=identity.encounter();root=identity.root();this.modules=modules;bodies.put(root,original);
    }
    public void beforeMove(ServerSubLevel source,AssemblyTransform transform,Set<BlockPos> moving,Runnable releaseCombat){
        thread();
        if(held||session!=null||pendingDestruction!=null||source==null||source.isRemoved()||source.getLevel()!=level
                ||bodies.get(source.getUniqueId())!=source||bodies.size()>=128){
            close();throw new IllegalStateException("Unknown, pending or held lineage");
        }
        session=new EnemyBossAssemblySession(modules);
        try{
            token=session.begin(level.getGameTime(),releaseCombat);
            if(held)throw new IllegalStateException("Lineage revoked during release");
            observation=NativeBossAssemblyObservation.beforeKnown(level,source,modules,transform,moving,encounter,root);
        }catch(RuntimeException|Error failure){close();throw failure;}
    }
    public void afterAssembly(ServerSubLevel destination){
        thread();
        try{
            if(held||session==null||observation==null||destination==null
                    ||bodies.containsKey(destination.getUniqueId()))throw new IllegalStateException("Unexpected fragment completion");
            session.complete(token,level.getGameTime(),baseline->observation.after(destination));
            if(held)throw new IllegalStateException("Lineage revoked during observation");
            modules=session.modules();bodies.put(destination.getUniqueId(),destination);
            session=null;token=null;observation=null;
            // Ready for another read-only mutation bracket; combat stays stopped.
        }catch(RuntimeException|Error failure){close();throw failure;}
    }
    public EnemyBossModules modules(){thread();return modules;}
    /** Exact live post-mutation scope. A later split or close invalidates it.
     * Does not assert destruction, inventory custody or persisted ownership. */
    public final class StructureScope {
        private final EnemyBossModules baseline=modules;
        private final Map<UUID,ServerSubLevel> known=Map.copyOf(bodies);
        private StructureScope(){check();}
        public void check(){
            thread();
            if(!rewardScope(baseline,known)||known.values().stream().anyMatch(b->b.isRemoved()||b.getLevel()!=level))
                throw new IllegalStateException("Lineage structure scope changed or held");
        }
        public EnemyBossModules modules(){check();return baseline;}
        public Map<UUID,ServerSubLevel> bodies(){check();return known;}
        public ServerSubLevel original(){check();return known.get(root);}
        public void revoke(){NativeBossLineage.this.close();}
        /** Only an actual completed assembly in this owner can add an exact
         * body and a direct module successor. This does not commit a journal. */
        public StructureScope afterRelocation(ServerSubLevel destination){
            thread();
            if(held||session!=null||pendingDestruction!=null||destination==null
                    ||!modules.isDirectSuccessorOf(baseline)||known.containsKey(destination.getUniqueId())
                    ||bodies.size()!=known.size()+1||bodies.get(destination.getUniqueId())!=destination
                    ||known.entrySet().stream().anyMatch(e->bodies.get(e.getKey())!=e.getValue()))
                throw new IllegalStateException("Unproven lineage successor");
            for(var entry:baseline.modules().entrySet()){
                var next=modules.modules().get(entry.getKey());
                if(next==null||next.destroyed()!=entry.getValue().destroyed()||next.role()!=entry.getValue().role())
                    throw new IllegalStateException("Relocation changed module membership or defeat state");
            }
            if(!modules.modules().keySet().equals(baseline.modules().keySet()))throw new IllegalStateException("Relocation changed module names");
            return new StructureScope();
        }
        public Destruction beginDestruction(String name,EnemyBossDestructionJournal journal,String before)throws java.io.IOException{
            check();
            try{
                if(journal==null||journal.held()||!journal.belongsTo(encounter,root))throw new IllegalStateException("Live root journal required");
                var mutation=new Destruction(this,name,journal);
                pendingDestruction=mutation;
                mutation.permit=journal.begin(Set.of(name),before);
                return mutation;
            }catch(java.io.IOException|RuntimeException|Error failure){close();throw failure;}
        }
    }
    /** Owns the native witness and actual durable intent. Publication follows
     * a successful journal commit; no supplied destroyed-set can update custody. */
    public final class Destruction implements AutoCloseable {
        private final StructureScope scope;
        private final EnemyBossDestructionJournal journal;
        private final NativeBossDestructionObservation witness;
        private final long tick=level.getGameTime();
        private EnemyBossDestructionJournal.Permit permit;
        private Destruction(StructureScope scope,String name,EnemyBossDestructionJournal journal){
            this.scope=scope;this.journal=journal;
            witness=new NativeBossDestructionObservation(level,scope.known,scope.baseline,encounter,root,name);
        }
        public void check(){
            thread();
            if(held||session!=null||pendingDestruction!=this||modules!=scope.baseline
                    ||!bodies.equals(scope.known)||level.getGameTime()!=tick
                    ||scope.known.values().stream().anyMatch(b->b.isRemoved()||b.getLevel()!=level))
                throw new IllegalStateException("Destruction scope revoked");
        }
        public EnemyBossDestructionJournal.Permit permit(){check();return permit;}
        public StructureScope complete(boolean nativeReturn,boolean sameTick,String after,String evidence)throws java.io.IOException{
            try{
                check();var next=witness.after(nativeReturn,sameTick);
                journal.commit(permit,after,evidence);check();
                modules=next;pendingDestruction=null;return new StructureScope();
            }catch(java.io.IOException|RuntimeException|Error failure){NativeBossLineage.this.close();throw failure;}
        }
        @Override public void close(){NativeBossLineage.this.close();}
    }
    public StructureScope observeStructure(){thread();return new StructureScope();}
    /** No copied tags or caller-supplied body map can issue this observation. */
    public NativeRewardOwnership observeRewardOwnership()throws java.io.IOException{
        thread();if(held||session!=null||pendingDestruction!=null)throw new java.io.IOException("Closed or pending native lineage mutation");
        return new NativeRewardOwnership(this,modules,level,encounter,root,bodies);
    }
    boolean rewardScope(EnemyBossModules expected,Map<UUID,ServerSubLevel> expectedBodies){
        thread();return !held&&session==null&&pendingDestruction==null&&modules==expected&&bodies.equals(expectedBodies);
    }
    public boolean held(){thread();return held||session!=null||pendingDestruction!=null;}
    @Override public void close(){thread();held=true;if(session!=null)session.close();token=null;observation=null;}
    private void thread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");}
}
