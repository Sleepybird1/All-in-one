package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Round-robin disjoint bands, each independently permuted. A center-biased proposal,
 * not uniform district sampling. Complete coverage remains finite and restart-stable. */
public final class ContinentLocalTraversal {
    private record Rect(int minX,int minZ,int maxX,int maxZ) {
        long width(){return (long)maxX-minX+1;}
        long size(){return width()*((long)maxZ-minZ+1);}
    }
    private record Band(List<Rect> pieces,long count,long salt) {}
    private final GeographicColumnSurvey.Window window;
    private final List<Band> bands;
    private final long maxCount;

    public ContinentLocalTraversal(GeographicColumnSurvey.Window window,int centerX,int centerZ,long seed) {
        this.window=Objects.requireNonNull(window);
        if(centerX < -ContinentEnvelope.LIMIT || centerX > ContinentEnvelope.LIMIT
                ||centerZ < -ContinentEnvelope.LIMIT || centerZ > ContinentEnvelope.LIMIT)
            throw new IllegalArgumentException("Center outside admitted precision domain");
        var found=new ArrayList<Band>();Rect inner=null;
        for(long radius=2048;;radius*=2){
            long minX=Math.max(window.minX(),(long)centerX-radius),maxX=Math.min(window.maxX(),(long)centerX+radius);
            long minZ=Math.max(window.minZ(),(long)centerZ-radius),maxZ=Math.min(window.maxZ(),(long)centerZ+radius);
            if(minX<=maxX&&minZ<=maxZ){
                var outer=new Rect((int)minX,(int)minZ,(int)maxX,(int)maxZ);var pieces=new ArrayList<Rect>();
                if(inner==null)pieces.add(outer);
                else {
                    add(pieces,outer.minX(),outer.minZ(),outer.maxX(),inner.minZ()-1);
                    add(pieces,outer.minX(),inner.maxZ()+1,outer.maxX(),outer.maxZ());
                    add(pieces,outer.minX(),inner.minZ(),inner.minX()-1,inner.maxZ());
                    add(pieces,inner.maxX()+1,inner.minZ(),outer.maxX(),inner.maxZ());
                }
                long count=pieces.stream().mapToLong(Rect::size).sum();
                if(count>0)found.add(new Band(List.copyOf(pieces),count,seed^(0x632be59bd9b4e019L*radius)));
                inner=outer;
                if(outer.minX()==window.minX()&&outer.maxX()==window.maxX()&&outer.minZ()==window.minZ()&&outer.maxZ()==window.maxZ())break;
            }
            if(radius>2L*ContinentEnvelope.LIMIT)throw new IllegalStateException("Window partition failed");
        }
        bands=List.copyOf(found);maxCount=bands.stream().mapToLong(Band::count).max().orElseThrow();
        if(bands.stream().mapToLong(Band::count).sum()!=window.columns())throw new IllegalStateException("Incomplete window partition");
    }
    private static void add(List<Rect> out,int minX,int minZ,int maxX,int maxZ){if(minX<=maxX&&minZ<=maxZ)out.add(new Rect(minX,minZ,maxX,maxZ));}
    private long beforeRound(long round){long sum=0;for(var b:bands)sum+=Math.min(round,b.count());return sum;}
    /** Rank/select over unequal finite round-robin lanes; O(bands*log(columns)), no area-sized allocation. */
    public long at(long ordinal){
        if(ordinal<0||ordinal>=window.columns())throw new IllegalArgumentException("Ordinal outside window");
        long low=0,high=maxCount;
        while(low+1<high){long mid=low+(high-low)/2;if(beforeRound(mid)<=ordinal)low=mid;else high=mid;}
        long lane=ordinal-beforeRound(low);
        for(var b:bands)if(low<b.count()){
            if(lane-->0)continue;
            long offset=ContinentCandidateSearch.permuted(low,b.count(),b.salt());
            for(var r:b.pieces()){
                if(offset>=r.size()){offset-=r.size();continue;}
                long x=r.minX()+offset%r.width(),z=r.minZ()+offset/r.width();
                return (z-window.minZ())*window.width()+x-window.minX();
            }
            throw new AssertionError("Band position outside rectangles");
        }
        throw new AssertionError("Round-robin rank mismatch");
    }
    public int bandCount(){return bands.size();}
}
