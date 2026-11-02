package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Pure math: no world access, registries, chunk loads, or iteration-order-dependent RandomSource. */
public final class GeologyMath {
    private GeologyMath() {}
    public static long mix(long x) { x=(x^(x>>>30))*0xbf58476d1ce4e5b9L; x=(x^(x>>>27))*0x94d049bb133111ebL; return x^(x>>>31); }
    public static long seed(long world,int x,int z,long salt){return mix(world ^ mix(x*341873128712L) ^ mix(z*132897987541L) ^ salt);}
    public static double unit(long seed){return (mix(seed)>>>11)*0x1.0p-53;}
    public static int bounded(long seed,int bound){return (int)Math.floorMod(mix(seed),bound);}
    public static double lerp(double a,double b,double t){return a+(b-a)*Math.max(0,Math.min(1,t));}
    public static double depth(double y,double shallow,double mid,double deep,double[] w){
        if(y>=mid)return lerp(w[1],w[0],(y-mid)/(shallow-mid));
        return lerp(w[2],w[1],(y-deep)/(mid-deep));
    }
    public static int weighted(double[] weights,double roll){
        double total=Arrays.stream(weights).sum();if(total<=0)return -1;
        double remaining=roll*total;
        for(int i=0;i<weights.length;i++){remaining-=weights[i];if(remaining<0)return i;}
        return weights.length-1;
    }
    public static int quota(int actual,double fraction,long seed,boolean guarantee){
        double desired=actual*Math.max(0,fraction);int whole=(int)Math.floor(desired);
        int result=whole+(unit(seed)<desired-whole?1:0);
        return Math.min(actual,guarantee&&fraction>0&&actual>0?Math.max(1,result):result);
    }
    /** Randomized cumulative rounding conserves the pool without biasing its last (rarest) entry. */
    public static int[] split(int target,double[] weights,long seed){
        if(target<0)throw new IllegalArgumentException("Negative pool size");
        double total=0;
        for(double weight:weights){
            if(!Double.isFinite(weight)||weight<0)throw new IllegalArgumentException("Invalid pool weight");
            total+=weight;
        }
        if(!Double.isFinite(total)||(target>0&&total<=0))throw new IllegalArgumentException("Invalid pool total");
        int[] result=new int[weights.length];if(target==0)return result;
        double cumulative=0,offset=unit(seed);int assigned=0;
        for(int i=0;i<weights.length;i++){
            cumulative+=weights[i];
            int boundary=i==weights.length-1?target:Math.min(target,(int)Math.floor(target*(cumulative/total)+offset));
            result[i]=boundary-assigned;assigned=boundary;
        }
        return result;
    }
    public record Voxel(int x,int y,int z) {
        @Override public int hashCode(){
            // Dense3D bodies collide heavily under the record's linear31*x+y hash.
            // Equality, coordinates, seeded priorities and serialized geometry stay unchanged.
            long value=mix(((long)x<<32)^(y&0xffffffffL));
            value=mix(value^((long)z*0x9e3779b97f4a7c15L));
            return (int)(value^(value>>>32));
        }
    }
    private record Node(Voxel position,double score) {}
    private static final int[][] DIRECTIONS={{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
    /** Smooth seeded value noise, shared across chunk boundaries. */
    public static double noise(long salt,double x,double y,double z) {
        int ix=(int)Math.floor(x),iy=(int)Math.floor(y),iz=(int)Math.floor(z);
        double fx=x-ix,fy=y-iy,fz=z-iz;
        fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy);fz=fz*fz*(3-2*fz);
        double sum=0;
        for(int dx=0;dx<2;dx++)for(int dy=0;dy<2;dy++)for(int dz=0;dz<2;dz++)
            sum+=(unit(seed(salt^mix(iy+dy),ix+dx,iz+dz,71))*2-1)*(dx==0?1-fx:fx)*(dy==0?1-fy:fy)*(dz==0?1-fz:fz);
        return sum;
    }
    /** Exact mineralized volume, connected lobes, native-rock pockets and no chunk-local clipping in the plan. */
    public static List<Voxel> shape(long seed,int target,boolean seam) {
        return shape(seed,target,seam,List.of());
    }
    /** Tunnel attractors bend the body without increasing its material budget. */
    public static List<Voxel> shape(long seed,int target,boolean seam,List<Voxel> tunnels) {
        if(target<0)throw new IllegalArgumentException("Negative deposit volume");
        double ax=1.5+unit(seed+1)*1.1,ay=seam?.24:.65+unit(seed+2)*.35,az=1/(ax*ay);
        double angle=unit(seed+13)*Math.PI*2,cos=Math.cos(angle),sin=Math.sin(angle);
        double scale=Math.max(5,Math.cbrt(target)*.8);
        PriorityQueue<Node> frontier=new PriorityQueue<>(Comparator.comparingDouble(Node::score)
                .thenComparingInt(n->n.position.x).thenComparingInt(n->n.position.y).thenComparingInt(n->n.position.z));
        Set<Voxel> queued=new HashSet<>();List<Voxel> result=new ArrayList<>(target);
        Voxel origin=new Voxel(0,0,0);queued.add(origin);frontier.add(new Node(origin,0));
        while(result.size()<target&&!frontier.isEmpty()){
            Voxel p=frontier.remove().position;result.add(p);
            for(int[] dir:DIRECTIONS){Voxel n=new Voxel(p.x+dir[0],p.y+dir[1],p.z+dir[2]);if(!queued.add(n))continue;
                double wx=n.x+scale*.35*noise(seed+101,n.x/scale,n.y/scale,n.z/scale);
                double wz=n.z+scale*.35*noise(seed+102,n.x/scale,n.y/scale,n.z/scale);
                double rx=wx*cos-wz*sin,rz=wx*sin+wz*cos;
                double r=rx*rx/(ax*ax)+n.y*n.y/(ay*ay)+rz*rz/(az*az);
                double lobes=noise(seed+103,n.x/scale,n.y/scale,n.z/scale);
                double detail=noise(seed+104,n.x/3.5,n.y/3.5,n.z/3.5);
                double pocket=noise(seed+105,n.x/2.1,n.y/2.1,n.z/2.1);
                double pull=0;
                for(Voxel t:tunnels){double dx=n.x-t.x,dy=n.y-t.y,dz=n.z-t.z;pull=Math.max(pull,1/(1+(dx*dx+dy*dy+dz*dz)/25));}
                frontier.add(new Node(n,r*(1+.65*lobes+.28*detail)*(pocket>.12?3.5:1)*(1-.35*pull)));
            }
        }
        return List.copyOf(result);
    }
}
