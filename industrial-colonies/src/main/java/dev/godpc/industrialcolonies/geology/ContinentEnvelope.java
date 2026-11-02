package dev.godpc.industrialcolonies.geology;

/** Conservative envelope for the inspected AdvancedContinentGenerator geometry.
 * Callers must independently qualify the native frequency/jitter/warp contracts.
 * This bounds identity membership inside the exact integer-to-float domain only;
 * it is not a connected landmass, measured area or a completed district survey. */
public final class ContinentEnvelope {
    public static final int LIMIT=1<<24;
    public record Parameters(float frequency,float jitter,float warpDistance) {
        public Parameters {
            if(!Float.isFinite(frequency)||frequency<1f/(1<<20)||frequency>1f/1024)
                throw new IllegalArgumentException("Unqualified native frequency");
            if(!Float.isFinite(jitter)||Math.abs(jitter)>1)
                throw new IllegalArgumentException("Unqualified cell jitter");
            if(!Float.isFinite(warpDistance)||Math.abs(warpDistance)>(1<<20))
                throw new IllegalArgumentException("Unqualified warp distance");
        }
    }
    public record Window(int minX,int minZ,int maxX,int maxZ,long unclippedRadius) {
        public boolean contains(int x,int z){return x>=minX&&x<=maxX&&z>=minZ&&z<=maxZ;}
        public long columns(){return ((long)maxX-minX+1)*((long)maxZ-minZ+1);}
    }
    /** Native search chooses from floor(warped*frequency)+[-1,1]. Cell jitter is
     * at most one; the corrected center interpolates the chosen cell and the mean
     * of its eight neighbors. Both centers remain within one lattice unit of the
     * chosen grid cell. Thus the exact-real difference is <=3 lattice units.
     * Four units plus256 world blocks conservatively covers all float operations
     * in the qualified parameter/coordinate range, floor's negative-integer quirk
     * and final truncation. Clamped mapped Perlin warp adds at most distance/2. */
    public static Window around(ReTerraForgedGeography.ContinentKey key,Parameters p){
        if(key==null||p==null)throw new NullPointerException();
        long radius=(long)Math.ceil(4.0/p.frequency()+Math.abs((double)p.warpDistance())/2+256);
        long minX=Math.max(-LIMIT,(long)key.centerX()-radius),maxX=Math.min(LIMIT,(long)key.centerX()+radius);
        long minZ=Math.max(-LIMIT,(long)key.centerZ()-radius),maxZ=Math.min(LIMIT,(long)key.centerZ()+radius);
        if(minX>maxX||minZ>maxZ)throw new IllegalArgumentException("Identity outside admitted coordinate domain");
        return new Window((int)minX,(int)minZ,(int)maxX,(int)maxZ,radius);
    }
    private ContinentEnvelope(){}
}
