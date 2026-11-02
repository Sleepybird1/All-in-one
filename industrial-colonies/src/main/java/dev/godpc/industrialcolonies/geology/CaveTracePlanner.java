package dev.godpc.industrialcolonies.geology;

import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Bounded, chunk-local cave-surface sampling. Plans all writes before any terrain is changed. */
public final class CaveTracePlanner {
    public record Cell(int x,int y,int z) {
        Cell offset(int[] d){return new Cell(x+d[0],y+d[1],z+d[2]);}
    }
    public interface Terrain {
        boolean stone(Cell p);
        boolean air(Cell p);
        int surface(int x,int z);
    }
    public record Resource(String block,double weight) {
        public Resource {
            if(block==null||block.isBlank()||!Double.isFinite(weight)||weight<0)throw new IllegalArgumentException("Invalid cave resource");
        }
    }
    public record Rules(int minY,int maxY,int cover,int columns,int attempts,double chance,int minSize,int maxSize,List<Resource> resources) {
        public Rules {
            resources=List.copyOf(resources);
            double total=resources.stream().mapToDouble(Resource::weight).sum();
            if(minY>maxY||minY< -2048||maxY>2048||cover<1||cover>128||columns<0||columns>196
                    ||attempts<0||attempts>32||!Double.isFinite(chance)||chance<0||chance>1
                    ||minSize<1||maxSize<minSize||maxSize>8||!Double.isFinite(total)||total<=0)
                throw new IllegalArgumentException("Invalid cave trace limits or weights");
        }
    }
    public record Placement(Cell cell,String block,int patch) {}
    private static final int[][] DIRS={{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
    private CaveTracePlanner() {}
    public static List<Placement> plan(long worldSeed,int chunkX,int chunkZ,int buildMin,int buildMax,Rules r,Terrain terrain){
        int min=Math.max(buildMin+1,r.minY),max=Math.min(buildMax-2,r.maxY);
        if(min>max||r.chance==0||r.attempts==0||r.columns==0)return List.of();
        long salt=seed(worldSeed,chunkX,chunkZ,0x434156455452L);
        int baseX=chunkX*16,baseZ=chunkZ*16;
        Map<Long,Integer> heights=new HashMap<>();
        java.util.function.Predicate<Cell> eligible=p->{
            // Includes an inert one-block margin: even adjacency reads stay inside the owner chunk.
            if(p.x<=baseX||p.x>=baseX+15||p.z<=baseZ||p.z>=baseZ+15||p.y<min||p.y>max)return false;
            int surface=heights.computeIfAbsent(((long)p.x<<32)^(p.z&0xffffffffL),k->terrain.surface(p.x,p.z));
            if(p.y>surface-r.cover||!terrain.stone(p))return false;
            for(int[] d:DIRS)if(terrain.air(p.offset(d)))return true;
            return false;
        };
        List<Integer> columns=new ArrayList<>();for(int i=0;i<196;i++)columns.add(i);
        columns.sort(Comparator.comparingLong(i->mix(salt+i)));
        List<Cell> candidates=new ArrayList<>();
        for(int column:columns.subList(0,r.columns)){
            int x=baseX+1+column%14,z=baseZ+1+column/14;
            for(int y=min;y<=max;y++){Cell p=new Cell(x,y,z);if(eligible.test(p))candidates.add(p);}
        }
        candidates.sort(Comparator.comparingLong(p->seed(salt^mix(p.y),p.x,p.z,71)));
        Set<Cell> used=new HashSet<>();List<Placement> result=new ArrayList<>();
        double[] weights=r.resources.stream().mapToDouble(Resource::weight).toArray();
        int attempt=0;
        for(Cell start:candidates){
            if(attempt>=r.attempts)break;if(used.contains(start))continue;
            long roll=mix(salt+10000+attempt++);
            if(unit(roll)>=r.chance)continue;
            String block=r.resources.get(weighted(weights,unit(roll+1))).block;
            int size=r.minSize+bounded(roll+2,r.maxSize-r.minSize+1),made=0;
            ArrayDeque<Cell> frontier=new ArrayDeque<>();frontier.add(start);Set<Cell> queued=new HashSet<>();queued.add(start);
            while(!frontier.isEmpty()&&made<size){
                Cell p=frontier.removeFirst();if(used.contains(p)||!eligible.test(p))continue;
                used.add(p);result.add(new Placement(p,block,attempt));made++;
                int first=bounded(roll+made,6);
                for(int i=0;i<6;i++){Cell n=p.offset(DIRS[(first+i)%6]);if(queued.add(n))frontier.addLast(n);}
            }
        }
        return List.copyOf(result);
    }
}
