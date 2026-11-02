package dev.godpc.industrialcolonies.geology;

import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Geometry for a selected concentration, not its occurrence/range allocator. No climate input. */
public final class CinnabarSurfaceGeometry {
    public interface Terrain { int topY(int x,int z); boolean mountain(int x,int z); }
    public record Face(Voxel front,int dx,int dy,int dz) {
        public Face { Objects.requireNonNull(front);if(Math.abs(dx)+Math.abs(dy)+Math.abs(dz)!=1||dy<0)throw new IllegalArgumentException("Exterior surface normal required"); }
    }
    public record Stroke(Face face,List<Voxel> blocks) { public Stroke { blocks=List.copyOf(blocks); } }
    public record Plan(boolean admitted,String reason,double frequency,int eligibleFronts,List<Stroke> strokes) {
        public Plan { strokes=List.copyOf(strokes); }
        public Set<Voxel> blocks(){Set<Voxel> result=new HashSet<>();for(var stroke:strokes)result.addAll(stroke.blocks());return Set.copyOf(result);}
    }
    private CinnabarSurfaceGeometry() {}
    public static double frequency(int anchorY,int minimumY) {
        if(anchorY<minimumY||anchorY>=400)return 0;
        return anchorY<=300?1:(400-anchorY)/100.0;
    }
    /** One frequency roll for the whole concentration; altitude never changes its coverage or thickness. */
    public static Plan plan(long seed,int minX,int minZ,int width,int anchorY,int minimumY,
                            double frequencyRoll,double coverage,int thickness,Terrain terrain) {
        Objects.requireNonNull(terrain);
        if(width<1||width>128||minimumY<-2048||minimumY>300||thickness<1||thickness>3
                ||!Double.isFinite(coverage)||coverage<.6||coverage>.8
                ||!Double.isFinite(frequencyRoll)||frequencyRoll<0||frequencyRoll>=1)
            throw new IllegalArgumentException("Invalid bounded cinnabar surface proposal");
        if((long)minX-4<Integer.MIN_VALUE||(long)minZ-4<Integer.MIN_VALUE
                ||(long)minX+width+4>Integer.MAX_VALUE||(long)minZ+width+4>Integer.MAX_VALUE)
            throw new IllegalArgumentException("Surface coordinates overflow");
        double frequency=frequency(anchorY,minimumY);
        if(frequencyRoll>=frequency)return new Plan(false,"height frequency",frequency,0,List.of());
        Map<Long,Integer> heights=new HashMap<>();Map<Long,Boolean> mountains=new HashMap<>();
        java.util.function.BiFunction<Integer,Integer,Integer> top=(x,z)->heights.computeIfAbsent(key(x,z),k->terrain.topY(x,z));
        java.util.function.BiPredicate<Integer,Integer> mountain=(x,z)->mountains.computeIfAbsent(key(x,z),k->terrain.mountain(x,z));
        Map<Voxel,Face> faces=new HashMap<>();
        for(int x=minX;x<minX+width;x++)for(int z=minZ;z<minZ+width;z++){
            if(!mountain.test(x,z))continue;
            int y=top.apply(x,z);
            if(y>=minimumY&&y<400)add(faces,new Face(new Voxel(x,y,z),0,1,0),seed);
            for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}){
                int neighbor=top.apply(x+d[0],z+d[1]);
                for(int faceY=Math.max(minimumY,neighbor==Integer.MAX_VALUE?Integer.MAX_VALUE:neighbor+1);faceY<=Math.min(y,399);faceY++)
                    add(faces,new Face(new Voxel(x,faceY,z),d[0],0,d[1]),seed);
            }
        }
        List<Face> ordered=new ArrayList<>(faces.values());
        ordered.sort(Comparator.<Face>comparingLong(f->rank(f.front(),seed)).thenComparingInt(f->f.front().x()).thenComparingInt(f->f.front().y()).thenComparingInt(f->f.front().z()));
        int count=ordered.isEmpty()?0:Math.max(1,(int)Math.round(ordered.size()*coverage));
        Set<Voxel> selectedFronts=new HashSet<>();for(var face:ordered.subList(0,count))selectedFronts.add(face.front());
        var strokes=new ArrayList<Stroke>();var unique=new HashSet<Voxel>();
        for(var face:ordered.subList(0,count)){
            var blocks=new ArrayList<Voxel>();var front=face.front();
            for(int depth=0;depth<thickness;depth++){
                var p=new Voxel(front.x()-face.dx()*depth,front.y()-face.dy()*depth,front.z()-face.dz()*depth);
                if(p.y()<minimumY||p.y()>=400||p.y()>top.apply(p.x(),p.z())||!mountain.test(p.x(),p.z()))break;
                if(depth>0&&!selectedFronts.contains(p)){
                    boolean exposed=p.y()==top.apply(p.x(),p.z());
                    for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}})exposed|=p.y()>top.apply(p.x()+d[0],p.z()+d[1]);
                    if(exposed)break; // Inward thickness must not fill deliberately uncovered surface pixels.
                }
                blocks.add(p);unique.add(p);
                if(unique.size()>100000)throw new IllegalArgumentException("Surface concentration exceeds100000block safety bound; no truncated plan");
            }
            if(!blocks.isEmpty())strokes.add(new Stroke(face,blocks));
        }
        return new Plan(!strokes.isEmpty(),strokes.isEmpty()?"no eligible mountain surface":"selected surface",frequency,ordered.size(),strokes);
    }
    private static long key(int x,int z){return ((long)x<<32)^(z&0xffffffffL);}
    private static long rank(Voxel p,long seed){return GeologyMath.seed(seed,p.x(),p.z(),mix(p.y()));}
    private static void add(Map<Voxel,Face> faces,Face face,long seed){
        Face old=faces.get(face.front());
        // Top faces get inward vertical thickness; other corners pick a stable normal.
        if(old==null||face.dy()>old.dy()||face.dy()==old.dy()&&normalRank(face,seed)<normalRank(old,seed))faces.put(face.front(),face);
        if(faces.size()>200000)throw new IllegalArgumentException("Surface concentration exceeds face-work bound; no truncated plan");
    }
    private static long normalRank(Face face,long seed){return mix(seed+face.dx()*11+face.dz()*37);}
}
