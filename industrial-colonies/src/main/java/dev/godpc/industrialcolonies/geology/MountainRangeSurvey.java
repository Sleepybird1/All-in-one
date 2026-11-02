package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.util.*;

/** Exact column connectivity, not a generator-region approximation or ore guarantee.
 * The caller must use one immutable world/preset classifier. No native writes occur. */
public final class MountainRangeSurvey {
    public static final int COORDINATE_LIMIT=1<<24, MAX_OBSERVATIONS=1<<20;
    public record Column(int x,int z) implements Comparable<Column> {
        public Column {
            if(Math.abs((long)x)>COORDINATE_LIMIT||Math.abs((long)z)>COORDINATE_LIMIT)
                throw new IllegalArgumentException("Outside exact native float-coordinate domain");
        }
        public int compareTo(Column other){int c=Integer.compare(x,other.x);return c!=0?c:Integer.compare(z,other.z);}
        @Override public int hashCode(){
            // Record's linear 31*x+z hash clusters dense neighboring columns.
            // Mix both coordinates; insertion order and serialized coordinates
            // still exclusively determine traversal and saved identity.
            long value=((long)x<<32)^(z&0xffffffffL);
            value=(value^(value>>>33))*0xff51afd7ed558ccdL;
            value=(value^(value>>>33))*0xc4ceb9fe1a85ec53L;
            value^=value>>>33;
            return (int)(value^(value>>>32));
        }
    }
    public record Observation(Column column,boolean mountain) {
        public Observation {Objects.requireNonNull(column);}
    }
    public enum Status { SEARCHING, COMPLETE, NOT_MOUNTAIN, HELD_LIMIT, HELD_DOMAIN }
    public record Progress(Status status,int observations,int mountainColumns,int frontierColumns) {}
    /** Transport state only. Restoring it does not revalidate native terrain or grant placement authority. */
    public record Snapshot(Column seed,int maximumObservations,List<Observation> observations,Status status) {
        public Snapshot {Objects.requireNonNull(seed);Objects.requireNonNull(status);observations=List.copyOf(observations);}
    }
    /** Members and their entire non-mountain cardinal boundary, in canonical order. */
    public record Range(List<Column> members,List<Column> boundary) {
        public Range {members=List.copyOf(members);boundary=List.copyOf(boundary);if(members.isEmpty())throw new IllegalArgumentException("Empty range");}
    }
    @FunctionalInterface public interface Terrain {boolean mountain(int x,int z)throws IOException;}
    private final Column seed;
    private int maximumObservations;
    // Dense terrain needs bits per column, not several Java objects per column.
    // Ordered packed coordinates retain the exact existing traversal/serialization.
    private static final class Tile {
        final BitSet seen=new BitSet(4096),mountain=new BitSet(4096);
    }
    private final Map<Long,Tile> tiles=new HashMap<>();
    private long[] order=new long[1024];
    private int observationCount;
    private final LinkedHashSet<Column> frontier=new LinkedHashSet<>();
    private int mountainColumns;
    private Status status=Status.SEARCHING;

    public MountainRangeSurvey(Column seed,int maximumObservations){
        this.seed=Objects.requireNonNull(seed);
        if(maximumObservations<1||maximumObservations>MAX_OBSERVATIONS)throw new IllegalArgumentException("Invalid mountain survey bound");
        this.maximumObservations=maximumObservations;frontier.add(seed);
    }
    public Progress progress(){return new Progress(status,observationCount,mountainColumns,frontier.size());}
    private static long packed(int x,int z){return ((long)x<<32)^(z&0xffffffffL);}
    private static int tileIndex(int x,int z){return (x&63)|((z&63)<<6);}
    private Tile tile(int x,int z){return tiles.get(packed(x>>6,z>>6));}
    private boolean observed(Column p){var t=tile(p.x(),p.z());return t!=null&&t.seen.get(tileIndex(p.x(),p.z()));}
    boolean observedMountain(Column p){var t=tile(p.x(),p.z());return t!=null&&t.mountain.get(tileIndex(p.x(),p.z()));}
    private void record(Column p,boolean mountain){
        var t=tiles.computeIfAbsent(packed(p.x()>>6,p.z()>>6),ignored->new Tile());int bit=tileIndex(p.x(),p.z());
        t.seen.set(bit);if(mountain)t.mountain.set(bit);
        if(observationCount==order.length)order=Arrays.copyOf(order,Math.addExact(order.length,Math.max(1024,order.length/2)));
        order[observationCount++]=packed(p.x(),p.z());
    }
    /** Fixed cardinal order and traversal independent of scheduling budget. A failed read commits nothing for that column. */
    public Progress advance(int budget,Terrain terrain)throws IOException{
        if(budget<1||budget>4096)throw new IllegalArgumentException("Survey budget must be1..4096");
        Objects.requireNonNull(terrain);
        for(int queried=0;queried<budget&&status==Status.SEARCHING;queried++){
            Column column=frontier.iterator().next();
            boolean mountain=terrain.mountain(column.x(),column.z());
            frontier.remove(column);record(column,mountain);
            if(mountain){
                mountainColumns++;
                for(int[] offset:new int[][]{{-1,0},{0,-1},{0,1},{1,0}}){
                    long x=(long)column.x()+offset[0],z=(long)column.z()+offset[1];
                    if(Math.abs(x)>COORDINATE_LIMIT||Math.abs(z)>COORDINATE_LIMIT){status=Status.HELD_DOMAIN;continue;}
                    Column neighbor=new Column((int)x,(int)z);
                    if(!observed(neighbor))frontier.add(neighbor);
                }
            }else if(observationCount==1){status=Status.NOT_MOUNTAIN;}
            if(status==Status.SEARCHING){
                if(frontier.isEmpty())status=Status.COMPLETE;
                else if(observationCount==maximumObservations)status=Status.HELD_LIMIT;
            }
        }
        return progress();
    }
    /** Continue the same validated frontier in a new durable work page. This
     * never completes, truncates, re-seeds, or changes already observed terrain.
     * The paged journal, not caller-supplied topology, owns this transition. */
    void continueWorkPage(int pageSize){
        if(status!=Status.HELD_LIMIT||pageSize<1||pageSize>MAX_OBSERVATIONS)
            throw new IllegalStateException("Only an exhausted work page can continue");
        maximumObservations=Math.addExact(maximumObservations,pageSize);
        status=Status.SEARCHING;
    }
    Observation observation(int index){
        if(index<0||index>=observationCount)throw new IndexOutOfBoundsException(index);
        long p=order[index];var column=new Column((int)(p>>32),(int)p);return new Observation(column,observedMountain(column));
    }
    int snapshotLimit(){return maximumObservations;}
    List<Observation> observationsSince(int index){
        if(index<0||index>observationCount)throw new IllegalArgumentException("Observation cursor");
        var result=new ArrayList<Observation>(observationCount-index);for(int i=index;i<observationCount;i++)result.add(observation(i));return List.copyOf(result);
    }
    public Range completedRange(){
        if(status!=Status.COMPLETE)throw new IllegalStateException("Unfinished or held topology is not a connected range");
        var members=new ArrayList<Column>();var boundary=new ArrayList<Column>();
        for(int i=0;i<observationCount;i++){var row=observation(i);(row.mountain()?members:boundary).add(row.column());}
        Collections.sort(members);Collections.sort(boundary);return new Range(members,boundary);
    }
    public Snapshot snapshot(){
        return new Snapshot(seed,maximumObservations,observationsSince(0),status);
    }
    /** Validate the entire deterministic observation prefix, including all frontier/hold outcomes.
     * Caller separately owns disk durability and unchanged native classifier identity. */
    public static MountainRangeSurvey restore(Snapshot saved){
        Objects.requireNonNull(saved);var result=new MountainRangeSurvey(saved.seed(),saved.maximumObservations());
        if(saved.observations().size()>saved.maximumObservations())throw new IllegalArgumentException("Oversized mountain observation prefix");
        for(var observation:saved.observations()){
            if(result.status!=Status.SEARCHING)throw new IllegalArgumentException("Observations after terminal survey outcome");
            try{result.advance(1,(x,z)->{
                if(observation.column().x()!=x||observation.column().z()!=z)throw new IllegalArgumentException("Noncanonical mountain observation prefix");
                return observation.mountain();
            });}catch(IOException impossible){throw new AssertionError(impossible);}
        }
        if(result.status!=saved.status())throw new IllegalArgumentException("Saved mountain status differs from observed topology");
        return result;
    }
}
