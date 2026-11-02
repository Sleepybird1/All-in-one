package dev.godpc.industrialcolonies.space.collision;

/** Explicit one-scope lab session. There is no production registration or damage authority. */
public final class ShipCollisionProbe {
    private static Session active;
    private ShipCollisionProbe() {}
    public static final class Session implements AutoCloseable {
        private final Object scope;
        private final CollisionObservationBuffer buffer;
        private boolean closed;
        private Session(Object scope,int batches,int contacts){this.scope=scope;buffer=new CollisionObservationBuffer(batches,contacts);}
        public CollisionObservationBuffer.Snapshot snapshot(){return buffer.snapshot();}
        public void close(){synchronized(ShipCollisionProbe.class){closed=true;if(active==this)active=null;}}
    }
    public static synchronized Session open(Object exactScope,int batches,int contacts){
        if(exactScope==null)throw new IllegalArgumentException("Exact scope required");
        if(active!=null)throw new IllegalStateException("Collision probe already active");
        active=new Session(exactScope,batches,contacts);return active;
    }
    /** Identity scope only. Returns the exact original array, including rejected observations. */
    public static synchronized double[] observe(Object exactScope,long tick,double[] original){
        if(active!=null&&!active.closed&&active.scope==exactScope)active.buffer.capture(tick,original);
        return original;
    }
}
