package dev.godpc.industrialcolonies.geology;

import java.util.Comparator;

/** A mine connects to a finite vein; its tunnels need not fit inside the ore body.
 * Translation preserves every native piece and never changes the reserve geometry. */
public final class VeinMineSiting {
 public record Placement(int dx,int dy,int dz,int nodeX,int nodeY,int nodeZ){}
 private VeinMineSiting(){}
 public static Placement site(MiningScanScope scope,MassiveDepositGeometry.Bounds room){
  if(!scope.isContinent())throw new IllegalArgumentException("Finite mine scope required");
  var candidate=scope.reservedCandidate();int x=candidate.x(),y=candidate.y(),z=candidate.z();
  if(!scope.contains(x,y,z)){
   var offset=GeologyMath.shape(candidate.geometrySeed(),candidate.cells(),scope.isCoal()).stream()
       .min(Comparator.comparingLong((GeologyMath.Voxel p)->(long)p.x()*p.x()+(long)p.y()*p.y()+(long)p.z()*p.z())
           .thenComparingInt(GeologyMath.Voxel::x).thenComparingInt(GeologyMath.Voxel::y).thenComparingInt(GeologyMath.Voxel::z)).orElseThrow();
   x=Math.addExact(x,offset.x());y=Math.addExact(y,offset.y());z=Math.addExact(z,offset.z());
  }
  if(!scope.contains(x,y,z)||y<=scope.minBuildY()||y>=scope.maxBuildYExclusive()-1)
   throw new IllegalStateException("No valid mine node connection in original reserve");
  // MassiveMinePiece uses this exact room-center/minY+1 location for its node.
  // Exact installed BoundingBox.getCenter: min + inclusive span/2 (upper midpoint for even spans).
  int centerX=Math.toIntExact((long)room.minX()+((long)room.maxX()-room.minX()+1)/2);
  int centerZ=Math.toIntExact((long)room.minZ()+((long)room.maxZ()-room.minZ()+1)/2);
  return new Placement(Math.subtractExact(x,centerX),Math.subtractExact(y,Math.addExact(room.minY(),1)),Math.subtractExact(z,centerZ),x,y,z);
 }
}
