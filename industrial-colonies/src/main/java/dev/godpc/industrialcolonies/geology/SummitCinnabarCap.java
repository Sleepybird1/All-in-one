package dev.godpc.industrialcolonies.geology;
import java.util.*;
/** Fit an exact chart reserve to existing eligible rock before any chunk writes. */
public final class SummitCinnabarCap {
 public record Cell(int x,int y,int z,int surfaceY) {}
 private SummitCinnabarCap(){}
 public static List<Cell> fit(List<Cell> eligible,int reserve){
  if(reserve!=1000&&reserve!=5000&&reserve!=15000)throw new IllegalArgumentException("Chart cinnabar tier required");
  if(eligible.size()>32*32*24)throw new IllegalArgumentException("Local cap bound exceeded");
  if(eligible.size()<reserve)return List.of();
  var peak=eligible.stream().max(Comparator.comparingInt(Cell::surfaceY).thenComparingInt(Cell::x).thenComparingInt(Cell::z)).orElseThrow();
  var cells=new ArrayList<>(eligible);
  cells.sort(Comparator.comparingDouble((Cell c)->{
   double dx=c.x()-peak.x(),dz=c.z()-peak.z(),depth=c.surfaceY()-c.y();
   return depth*depth*2+(dx*dx+dz*dz)*.35+(peak.surfaceY()-c.surfaceY())*4;
  }).thenComparingInt(Cell::x).thenComparingInt(Cell::z).thenComparing(Comparator.comparingInt(Cell::y).reversed()));
  if(new HashSet<>(cells).size()!=cells.size())throw new IllegalArgumentException("Duplicate cap cells");
  return List.copyOf(cells.subList(0,reserve));
 }
}
