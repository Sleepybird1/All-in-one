package dev.godpc.industrialcolonies.space.collision;

import java.util.*;

/** Bounded read-only lab capture. Raw scalar/vector semantics require native calibration. */
public final class CollisionObservationBuffer {
    public record Vector(double x,double y,double z) {}
    public record Contact(int bodyA,int bodyB,double unqualifiedScalar,
            Vector rawVectorA,Vector rawVectorB,Vector localPointA,Vector localPointB) {}
    public record Batch(long tick,List<Contact> contacts) {
        public Batch { contacts=List.copyOf(contacts); }
    }
    public record Snapshot(List<Batch> batches,long refused,long overflow,String lastRefusal) {
        public Snapshot { batches=List.copyOf(batches); }
    }
    private final int maxBatches,maxContacts;
    private final ArrayDeque<Batch> batches=new ArrayDeque<>();
    private long refused,overflow,lastTick=-1;
    private String lastRefusal="NONE";
    public CollisionObservationBuffer(int maxBatches,int maxContacts) {
        if(maxBatches<1||maxBatches>1200||maxContacts<1||maxContacts>256)
            throw new IllegalArgumentException("Bounded capture limits required");
        this.maxBatches=maxBatches;this.maxContacts=maxContacts;
    }
    /** Never retains or mutates the native array; malformed batches are refused in full. */
    public synchronized boolean capture(long tick,double[] raw) {
        if(tick<0||tick<lastTick)return refuse("CLOCK_REVERSED");
        if(raw==null||raw.length%15!=0)return refuse("FRAMING");
        if(raw.length/15>maxContacts)return refuse("CONTACT_LIMIT");
        var contacts=new ArrayList<Contact>(raw.length/15);
        for(int i=0;i<raw.length;i+=15) {
            for(int j=0;j<15;j++)if(!Double.isFinite(raw[i+j]))return refuse("NONFINITE");
            if(!integer(raw[i])||!integer(raw[i+1]))return refuse("BODY_ID");
            contacts.add(new Contact((int)raw[i],(int)raw[i+1],raw[i+2],
                    vector(raw,i+3),vector(raw,i+6),vector(raw,i+9),vector(raw,i+12)));
        }
        lastTick=tick;
        if(batches.size()==maxBatches){batches.removeFirst();overflow++;}
        batches.addLast(new Batch(tick,contacts));return true;
    }
    private static boolean integer(double value){return value==Math.rint(value)&&value>=Integer.MIN_VALUE&&value<=Integer.MAX_VALUE;}
    private static Vector vector(double[] raw,int i){return new Vector(raw[i],raw[i+1],raw[i+2]);}
    private boolean refuse(String reason){refused++;lastRefusal=reason;return false;}
    public synchronized Snapshot snapshot(){return new Snapshot(new ArrayList<>(batches),refused,overflow,lastRefusal);}
}
