package dev.godpc.industrialcolonies.space.enemy;

import java.util.Objects;
import java.util.function.Function;

/** Single-thread, non-persistent assembly bracket. Successful observation
 * updates custody only; it never renews invalidated combat leases. */
public final class EnemyBossAssemblySession {
    public enum State { READY, PENDING, RECORDED_HELD, FAILED_HELD, CLOSED }
    public static final class Token {
        private final EnemyBossAssemblySession owner;
        private final long tick;
        private Token(EnemyBossAssemblySession owner,long tick){this.owner=owner;this.tick=tick;}
    }
    private final Thread thread=Thread.currentThread();
    private EnemyBossModules modules;
    private State state=State.READY;
    private Token pending;
    public EnemyBossAssemblySession(EnemyBossModules modules){this.modules=Objects.requireNonNull(modules);}
    public Token begin(long tick,Runnable releaseCombat){
        thread();
        if(state!=State.READY || tick<0){fail();throw new IllegalStateException("Fresh assembly session required");}
        state=State.PENDING;pending=new Token(this,tick);
        try {
            Objects.requireNonNull(releaseCombat).run();
            if(state!=State.PENDING)throw new IllegalStateException("Session revoked during release");
            return pending;
        }catch(RuntimeException|Error failure){if(state!=State.CLOSED)state=State.FAILED_HELD;pending=null;throw failure;}
    }
    public void complete(Token token,long tick,Function<EnemyBossModules,EnemyBossModules> observe){
        thread();
        if(state!=State.PENDING || token==null || token!=pending || token.owner!=this || tick!=token.tick){
            fail();throw new IllegalStateException("Invalid assembly completion");
        }
        // Consume before external observation: nested/replayed completion cannot publish.
        pending=null;
        try {
            var next=Objects.requireNonNull(observe.apply(modules));
            if(state!=State.PENDING || !next.isDirectSuccessorOf(modules))
                throw new IllegalStateException("Revoked or non-successor custody");
            modules=next;state=State.RECORDED_HELD;
        }catch(RuntimeException|Error failure){fail();throw failure;}
    }
    public void fail(){thread();pending=null;if(state!=State.CLOSED)state=State.FAILED_HELD;}
    public void close(){thread();pending=null;state=State.CLOSED;}
    public State state(){thread();return state;}
    public EnemyBossModules modules(){thread();return modules;}
    private void thread(){if(Thread.currentThread()!=thread)throw new IllegalStateException("Assembly owner thread required");}
}
