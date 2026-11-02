package dev.godpc.industrialcolonies.geology;

import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Shared exact grid/mask math; no terrain reads, registries, chunks or saved decisions. */
public final class LocalCinnabarPattern {
    public record Candidate(long key,int x,int z,int radius) {}
    public record Point(int x,int z) {}
    public record SurfaceColumn(Point point,int depth) {}
    public static final int MAX_RADIUS=128;
    private record PlanKey(Candidate candidate,double coverage,int thickness) {}
    private static final Map<PlanKey,List<SurfaceColumn>> PLANS=Collections.synchronizedMap(new LinkedHashMap<>(16,.75f,true){
        @Override protected boolean removeEldestEntry(Map.Entry<PlanKey,List<SurfaceColumn>> entry){return size()>32;}
    });
    private LocalCinnabarPattern() {}
    public static Candidate at(long worldSeed,int gx,int gz,int spacing,double chance){
        if(spacing<64||spacing>4096||!Double.isFinite(chance)||chance<0||chance>1)throw new IllegalArgumentException("Local cinnabar policy");
        long key=seed(worldSeed,gx,gz,0x43494e4c4f43414cL);
        if(unit(key)>=chance)return null;
        return new Candidate(key,Math.addExact(Math.multiplyExact(gx,spacing),bounded(key^1,spacing)),
                Math.addExact(Math.multiplyExact(gz,spacing),bounded(key^2,spacing)),
                Math.min(MAX_RADIUS,8+(int)Math.ceil(Math.sqrt(reserve(key)/(.4*Math.PI)))));
    }
    public static int reserve(long candidateKey){return ChartDepositSizes.cinnabar(candidateKey^0x53495a4554494552L);}
    public static boolean covered(Candidate c,int x,int z,double coverage){
        double d=((double)(x-c.x())*(x-c.x())+(double)(z-c.z())*(z-c.z()))/(c.radius()*c.radius());
        return d<=1&&unit(seed(c.key(),x,z,4))<coverage*(1-.35*d);
    }
    /** Bounded nearby candidate sample, sorted by center distance. No exhaustion/absence claim. */
    public static List<Candidate> nearby(long seed,int x,int z,int radius,int spacing,double chance){
        if(spacing<64||spacing>4096||!Double.isFinite(chance)||chance<0||chance>1)throw new IllegalArgumentException("Local cinnabar policy");
        if(radius<1||radius>131072)throw new IllegalArgumentException("Cinnabar radius1..131072");
        int gx=Math.floorDiv(x,spacing),gz=Math.floorDiv(z,spacing),rings=Math.min(64,(radius+spacing-1)/spacing+1),visited=0;
        var result=new ArrayList<Candidate>();
        outer:for(int ring=0;ring<=rings;ring++)for(int dx=-ring;dx<=ring;dx++)for(int dz=-ring;dz<=ring;dz++){
            if(Math.max(Math.abs(dx),Math.abs(dz))!=ring)continue;
            if(++visited>16384)break outer;
            var c=at(seed,gx+dx,gz+dz,spacing,chance);if(c==null)continue;
            if(Math.abs((long)c.x())>=ContinentEnvelope.LIMIT-MAX_RADIUS||Math.abs((long)c.z())>=ContinentEnvelope.LIMIT-MAX_RADIUS)continue;
            double distance=Math.hypot((double)c.x()-x,(double)c.z()-z);
            if(distance<=radius+MAX_RADIUS)result.add(c);
        }
        result.sort(Comparator.comparingDouble((Candidate c)->Math.hypot((double)c.x()-x,(double)c.z()-z)).thenComparingInt(Candidate::x).thenComparingInt(Candidate::z));
        return List.copyOf(result);
    }
    public static List<Point> columns(Candidate c,double coverage){
        int minX=Math.floorDiv(c.x(),32)*32,minZ=Math.floorDiv(c.z(),32)*32;
        var points=new ArrayList<Point>();for(int x=minX;x<minX+32;x++)for(int z=minZ;z<minZ+32;z++)points.add(new Point(x,z));
        points.sort(Comparator.comparingInt((Point p)->(p.x()-c.x())*(p.x()-c.x())+(p.z()-c.z())*(p.z()-c.z())).thenComparingInt(Point::x).thenComparingInt(Point::z));
        return List.copyOf(points);
    }
    /** Exact chart-sized geometric budget. Host/height/biome clipping is still reported separately. */
    public static List<SurfaceColumn> plan(Candidate c,double coverage,int thickness){
        if(!Double.isFinite(coverage)||coverage<=0||coverage>1||thickness<1||thickness>3)throw new IllegalArgumentException("Cinnabar surface policy");
        var key=new PlanKey(c,coverage,thickness);var cached=PLANS.get(key);if(cached!=null)return cached;
        var result=new ArrayList<Point>();
        for(int x=c.x()-c.radius();x<=c.x()+c.radius();x++)for(int z=c.z()-c.radius();z<=c.z()+c.radius();z++)if(covered(c,x,z,coverage))result.add(new Point(x,z));
        // Select separate dense patches throughout the footprint, rather than filling
        // only the circle nearest its center. Stable coarse-cell rank keeps local patches.
        result.sort(Comparator.comparingLong((Point p)->mix(seed(c.key(),Math.floorDiv(p.x(),8),Math.floorDiv(p.z(),8),6)))
                .thenComparingInt(Point::x).thenComparingInt(Point::z));
        var selected=new ArrayList<SurfaceColumn>();int remaining=reserve(c.key());
        for(var p:result){int depth=Math.min(remaining,1+bounded(seed(c.key(),p.x(),p.z(),5),thickness));selected.add(new SurfaceColumn(p,depth));remaining-=depth;if(remaining==0)break;}
        if(remaining!=0)throw new IllegalArgumentException("Local cinnabar footprint cannot hold chart reserve; no truncated plan");
        var plan=List.copyOf(selected);PLANS.put(key,plan);return plan;
    }
    public static List<Point> probes(Candidate c,double coverage){var points=columns(c,coverage);return List.copyOf(points.subList(0,Math.min(4,points.size())));}
}
