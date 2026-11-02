package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** A fixed bounded permutation of interior owner columns. Adjacent owners cannot form clusters. */
public final class SurfaceVeinClueSites {
    public record Point(int x,int z) {}
    private SurfaceVeinClueSites() {}
    public static List<Point> columns(long seed,String family,int chunkX,int chunkZ){
        if(family==null||!family.matches("[a-z0-9_]{1,80}"))throw new IllegalArgumentException("Mineral family required");
        int x=Math.multiplyExact(chunkX,16),z=Math.multiplyExact(chunkZ,16);
        var result=new ArrayList<Point>(196);
        for(int dx=1;dx<=14;dx++)for(int dz=1;dz<=14;dz++)result.add(new Point(Math.addExact(x,dx),Math.addExact(z,dz)));
        Collections.shuffle(result,new Random(seed^((long)chunkX<<32)^(chunkZ&0xffffffffL)^((long)family.hashCode()*0x9e3779b97f4a7c15L)));
        return List.copyOf(result);
    }
}
