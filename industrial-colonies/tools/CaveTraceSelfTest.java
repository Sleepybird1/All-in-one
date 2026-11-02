package dev.godpc.industrialcolonies.geology;

import java.util.*;
import static dev.godpc.industrialcolonies.geology.CaveTracePlanner.*;

/** Production planner tested against synthetic caves; no Minecraft runtime claim. */
public final class CaveTraceSelfTest {
    private static int checks;
    private static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
    private static final List<Resource> RESOURCES=List.of(new Resource("coal",35),new Resource("hematite",30),
            new Resource("zinc",15),new Resource("tin",15),new Resource("copper",5));
    private static Rules rules(double chance){return new Rules(-60,503,8,32,6,chance,1,3,RESOURCES);}
    private static class Cave implements Terrain {
        final int cx,cz;final boolean open;final int surface;
        Cave(int cx,int cz,boolean open,int surface){this.cx=cx;this.cz=cz;this.open=open;this.surface=surface;}
        void bounds(Cell p){check(Math.floorDiv(p.x(),16)==cx&&Math.floorDiv(p.z(),16)==cz,"Cross-chunk terrain access");check(p.y()>=-64&&p.y()<512,"Out-of-height read");}
        public boolean stone(Cell p){bounds(p);return p.y()!=20&&p.y()!=300;}
        public boolean air(Cell p){bounds(p);return open&&(p.y()==20||p.y()==300);}
        public int surface(int x,int z){bounds(new Cell(x,0,z));return surface;}
    }
    public static void main(String[] args){
        Map<String,Integer> counts=new TreeMap<>();int patches=0,total=0;
        for(int seed=0;seed<2000;seed++){
            int cx=seed%3-1,cz=seed%5-2;Cave cave=new Cave(cx,cz,true,400);
            List<Placement> result=plan(seed,cx,cz,-64,512,rules(.65),cave);
            check(result.equals(plan(seed,cx,cz,-64,512,rules(.65),cave)),"Nondeterministic replay");
            check(result.size()<=18,"Exceeded per-chunk block cap");Set<Cell> unique=new HashSet<>();Map<Integer,List<Cell>> groups=new HashMap<>();
            for(var p:result){
                check(unique.add(p.cell()),"Duplicate placement");check(cave.stone(p.cell()),"Replaced non-stone");
                check(Set.of(19,21,299,301).contains(p.cell().y()),"Unexposed placement");
                groups.computeIfAbsent(p.patch(),k->new ArrayList<>()).add(p.cell());total++;
            }
            for(var cells:groups.values()){
                check(cells.size()>=1&&cells.size()<=3,"Invalid patch size");
                Set<Cell> reached=new HashSet<>();reached.add(cells.getFirst());
                for(int n=0;n<cells.size();n++)for(Cell p:cells)if(reached.stream().anyMatch(q->Math.abs(p.x()-q.x())+Math.abs(p.y()-q.y())+Math.abs(p.z()-q.z())==1))reached.add(p);
                check(reached.size()==cells.size(),"Disconnected patch");
            }
            Set<Integer> seen=new HashSet<>();for(var p:result)if(seen.add(p.patch())){counts.merge(p.block(),1,Integer::sum);patches++;}
        }
        for(Resource r:RESOURCES)check(Math.abs((double)counts.getOrDefault(r.block(),0)/patches-r.weight()/100)<.025,"Resource weighting drift: "+r.block());
        check(plan(7,0,0,-64,512,rules(1),new Cave(0,0,false,400)).isEmpty(),"Buried or flooded cave yielded traces");
        check(plan(7,0,0,-64,512,rules(1),new Cave(0,0,true,22)).isEmpty(),"Insufficient surface cover");
        check(plan(7,0,0,-64,512,rules(0),new Cave(0,0,true,400)).isEmpty(),"Zero chance yielded traces");
        Terrain protectedCave=new Cave(0,0,true,400){public boolean stone(Cell p){bounds(p);return false;}};
        check(plan(7,0,0,-64,512,rules(1),protectedCave).isEmpty(),"Protected blocks replaced");
        try{new Rules(-60,503,0,32,6,.65,1,3,RESOURCES);throw new AssertionError("Accepted no cover");}catch(IllegalArgumentException expected){checks++;}
        try{new Rules(-60,503,8,32,6,.65,1,3,List.of(new Resource("coal",0)));throw new AssertionError("Accepted zero weight pool");}catch(IllegalArgumentException expected){checks++;}
        System.out.println("PASS: "+checks+" assertions, 2000 synthetic cave chunks, "+patches+" patches, "+total+" blocks; patch counts="+counts);
    }
}
