package dev.godpc.industrialcolonies.geology;

/**
 * Constant-memory, chunk-contiguous scan of a saved deposit envelope. This is not
 * an ore reserve: callers must check actual placed blocks, ownership and drops.
 * Looking at a candidate never advances it. Persist/commit custody before advance.
 */
public final class MiningScanCursor {
    public record Position(int x,int y,int z) {}
    private final MassiveDepositGeometry.Bounds bounds;
    private final int minChunkX,minChunkZ,minY;
    private final long chunksX,perChunk,total;
    private long next;

    public MiningScanCursor(MassiveDepositGeometry.Bounds bounds,int minBuildY,int maxBuildYExclusive,long savedNext) {
        if (minBuildY>=maxBuildYExclusive) throw new IllegalArgumentException("Invalid build interval");
        this.bounds=java.util.Objects.requireNonNull(bounds);
        minChunkX=Math.floorDiv(bounds.minX(),16);minChunkZ=Math.floorDiv(bounds.minZ(),16);
        chunksX=(long)Math.floorDiv(bounds.maxX(),16)-minChunkX+1;
        long chunksZ=(long)Math.floorDiv(bounds.maxZ(),16)-minChunkZ+1;
        minY=Math.max(bounds.minY(),minBuildY);
        long height=Math.max(0L,Math.min((long)bounds.maxY()+1,maxBuildYExclusive)-(long)minY);
        perChunk=Math.multiplyExact(256L,height);
        total=height==0?0:Math.multiplyExact(Math.multiplyExact(chunksX,chunksZ),perChunk);
        if(savedNext<0||savedNext>total)throw new IllegalArgumentException("Invalid saved mining cursor");
        next=savedNext;
    }
    public synchronized long nextIndex(){return next;}
    public long totalCandidates(){return total;}
    public synchronized boolean exhausted(){return next==total;}
    public synchronized Position current(){
        if(exhausted())throw new IllegalStateException("Mining scan exhausted");
        long chunk=next/perChunk,local=next%perChunk;
        int x=Math.toIntExact(((long)minChunkX+chunk%chunksX)*16+(local&15));
        int z=Math.toIntExact(((long)minChunkZ+chunk/chunksX)*16+((local>>>4)&15));
        int y=Math.toIntExact((long)minY+(local>>>8));
        return new Position(x,y,z);
    }
    /** Edge chunks contain padding; those cells must not be mined. */
    public synchronized boolean insideEnvelope(){var p=current();return bounds.contains(p.x,p.y,p.z);}
    /** Reject stale/double commits from a second caller; this does not save to disk. */
    public synchronized void advance(long expectedIndex){
        if(next!=expectedIndex||exhausted())throw new IllegalStateException("Stale or exhausted mining scan commit");
        next++;
    }
}
