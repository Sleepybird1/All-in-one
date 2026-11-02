package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Lazy full-radius grid traversal with an exact resumable in-flight column. No terrain access. */
public final class CinnabarSearchCursor {
 public record Column(int x,int z) {}
 public record Checkpoint(long nextGrid,long activeGrid,int column,long checked,long pockets) {}
 private final long seed,total;private final int x,z,radius,spacing,gx,gz;private final double chance,coverage;
 private long nextGrid,activeGrid=-1,checked,pockets;private int column;private List<LocalCinnabarPattern.Point> current=List.of();
 public CinnabarSearchCursor(long seed,int x,int z,int radius,int spacing,double chance,double coverage){
  if(radius<1||radius>131072||spacing<64||spacing>4096||!Double.isFinite(chance)||chance<0||chance>1||!Double.isFinite(coverage)||coverage<0||coverage>1||Math.abs((long)x)+radius+32>=16777216||Math.abs((long)z)+radius+32>=16777216)throw new IllegalArgumentException("Unsupported cinnabar search bounds/policy");
  this.seed=seed;this.x=x;this.z=z;this.radius=radius;this.spacing=spacing;this.chance=chance;this.coverage=coverage;gx=Math.floorDiv(x,spacing);gz=Math.floorDiv(z,spacing);
  long rings=(radius+spacing-1L)/spacing+2;total=(2*rings+1)*(2*rings+1);
 }
 private LocalCinnabarPattern.Candidate candidate(long index){
  int dx=0,dz=0;if(index>0){int ring=(int)Math.ceil((Math.sqrt(index+1)-1)/2),side=2*ring;long start=(2L*ring-1)*(2L*ring-1);int o=(int)(index-start);switch(o/side){case 0->{dx=-ring+o;dz=-ring;}case 1->{dx=ring;dz=-ring+o-side;}case 2->{dx=ring-(o-2*side);dz=ring;}default->{dx=-ring;dz=ring-(o-3*side);}}}
  var c=LocalCinnabarPattern.at(seed,gx+dx,gz+dz,spacing,chance);return c!=null&&Math.hypot((double)c.x()-x,(double)c.z()-z)<=radius+LocalCinnabarPattern.MAX_RADIUS?c:null;
 }
 /** Null means this pure-work page ended or traversal exhausted; inspect exhausted(). */
 public synchronized Column peek(int gridBudget){
  if(gridBudget<1||gridBudget>4096)throw new IllegalArgumentException("Grid budget1..4096");
  while(true){
   while(column<current.size()){var p=current.get(column);if(Math.hypot((double)p.x()-x,(double)p.z()-z)<=radius)return new Column(p.x(),p.z());column++;}
   current=List.of();column=0;activeGrid=-1;if(nextGrid==total||gridBudget--==0)return null;
   long index=nextGrid++;var candidate=candidate(index);if(candidate==null)continue;
   pockets++;activeGrid=index;current=LocalCinnabarPattern.columns(candidate,coverage);
  }
 }
 public synchronized void commit(){if(activeGrid<0||column>=current.size())throw new IllegalStateException("No selected query column");column++;checked++;}
 public synchronized boolean exhausted(){return nextGrid==total&&column>=current.size();}
 public synchronized long checked(){return checked;}public synchronized long grids(){return nextGrid;}public synchronized long pockets(){return pockets;}
 public synchronized Checkpoint checkpoint(){return new Checkpoint(nextGrid,activeGrid,column,checked,pockets);}
 public synchronized void restore(Checkpoint saved){
  if(saved.nextGrid()<0||saved.nextGrid()>total||saved.activeGrid()<-1||saved.activeGrid()>=saved.nextGrid()||saved.column()<0||saved.checked()<0||saved.pockets()<0||saved.pockets()>saved.nextGrid())throw new IllegalArgumentException("Invalid cinnabar cursor");
  List<LocalCinnabarPattern.Point> points=List.of();if(saved.activeGrid()>=0){if(saved.activeGrid()!=saved.nextGrid()-1)throw new IllegalArgumentException("Non-current cinnabar pocket");var c=candidate(saved.activeGrid());if(c==null)throw new IllegalArgumentException("Changed cinnabar candidate");points=LocalCinnabarPattern.columns(c,coverage);}
  if(saved.column()>points.size())throw new IllegalArgumentException("Cinnabar column cursor");nextGrid=saved.nextGrid();activeGrid=saved.activeGrid();column=saved.column();checked=saved.checked();pockets=saved.pockets();current=points;
 }
}
