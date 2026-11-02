package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.api.SubLevelAssemblyHelper.AssemblyTransform;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.Set;

/** Explicit lab integration point, not registered globally. Caller brackets
 * the actual native assembly; exceptions must call failed(), or close().
 * Missing return leaves PENDING, never an active combat permit. */
public final class NativeBossAssemblySession implements AutoCloseable {
    private final ServerLevel level;
    private final EnemyBossAssemblySession session;
    private EnemyBossAssemblySession.Token token;
    private NativeBossAssemblyObservation observation;
    public NativeBossAssemblySession(ServerLevel level,EnemyBossModules modules){
        if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");
        this.level=level;session=new EnemyBossAssemblySession(modules);
    }
    public void beforeMove(ServerSubLevel source,AssemblyTransform transform,Set<BlockPos> moving,Runnable releaseCombat){
        token=session.begin(level.getGameTime(),releaseCombat);
        try{observation=NativeBossAssemblyObservation.before(level,source,session.modules(),transform,moving);}
        catch(RuntimeException|Error failure){session.fail();throw failure;}
    }
    public void afterAssembly(ServerSubLevel destination){
        session.complete(token,level.getGameTime(),baseline->{
            if(observation==null)throw new IllegalStateException("No pre-move observation");
            return observation.after(destination);
        });
        observation=null;token=null;
    }
    public void failed(){session.fail();observation=null;token=null;}
    public EnemyBossAssemblySession.State state(){return session.state();}
    public EnemyBossModules modules(){return session.modules();}
    @Override public void close(){session.close();observation=null;token=null;}
}
