package dev.godpc.industrialcolonies.space;

import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.godpc.industrialcolonies.space.OrbitalCommonMotionProof.Sample;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;
import dev.devce.rocketnautics.shaded.orekit.frames.Frame;
import dev.devce.rocketnautics.shaded.orekit.time.AbsoluteDate;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;

/** Read-only observed distinct coasts with stationary local bodies. Not an
 * encounter permit, receiving precision proof, future clearance or recovery
 * receipt. Existing encounter profiles are deliberately unaffected. */
public final class OrbitalDistinctCoastProof {
 private OrbitalDistinctCoastProof(){}
 public record Qualified(OrbitalEndpoint.Pair latest,V receivingVelocity,int observations,
                         double maximumPositionError,double maximumVelocityError){}
 private static void require(boolean ok,String why){if(!ok)throw new IllegalArgumentException(why);}
 /** Separate slow-motion cache check; callers establish actual history and zero spin. */
 public static void requireCurrentCache(V current,V cached,V bodyPosition,V velocity,long now,long seen){
  require(current!=null&&cached!=null&&bodyPosition!=null&&velocity!=null&&current.finite()&&cached.finite()
   &&velocity.finite()&&velocity.length()<=.08&&seen>=0&&now>=seen&&now-seen<=40,"Invalid slow-motion cache evidence");
  var effective=OrbitalMotionPrecision.requireResolved(bodyPosition,velocity,2,18).representedVelocity();
  require(current.sub(cached).sub(effective.mul((now-seen)*.05)).length()<=1e-3,"Slow-motion transponder cache disagrees with native translation");
 }
 private static Vector3D j(V v){return new Vector3D(v.x(),v.y(),v.z());}
 private static CartesianOrbit orbit(OrbitalEndpoint e){return new CartesianOrbit(new PVCoordinates(j(e.celestialPosition()),j(e.celestialVelocity())),Frame.getRoot(),AbsoluteDate.J2000_EPOCH,e.mu());}
 private static void identity(OrbitalEndpoint a,OrbitalEndpoint b,int i){
  require(a.body().equals(b.body())&&a.instance()==b.instance()&&a.dimension().equals(b.dimension())
   &&a.frame().equals(b.frame())&&a.mu()==b.mu()&&a.planetRadius()==b.planetRadius()
   &&a.sphere()==b.sphere()&&a.transitionHeight()==b.transitionHeight()
   &&b.serverTick()==Math.addExact(a.serverTick(),i)&&b.universeTick()==Math.addExact(a.universeTick(),i),"Coast identity, planet or consecutive clock changed");
  require(b.localVelocity().length()==0&&b.localOffset().equals(a.localOffset()),"Local body must remain stationary");
  require(b.surfaceDistance()>b.transitionHeight()+100,"Planetary transition too close");
 }
 public static Qualified verify(List<Sample> input){
  require(input!=null&&input.size()>=20&&input.size()<=60,"Twenty to sixty consecutive observations required");
  var samples=List.copyOf(input);var first=samples.getFirst();var base=OrbitalEndpoint.pair(first.pair().ship(),first.pair().destination());
  var a=orbit(base.ship());var b=orbit(base.destination());
  for(var o:List.of(a,b))require(Double.isFinite(o.getA())&&o.getA()>0&&o.getE()<1,"Finite elliptic coast required");
  double maxP=0,maxV=0;
  for(int i=0;i<samples.size();i++){
   var s=samples.get(i);var p=OrbitalEndpoint.pair(s.pair().ship(),s.pair().destination());
   require(p.relation()==OrbitalEndpoint.Relation.INDEPENDENT_NATIVE_INSTANCES,"Independent cells required");
   identity(base.ship(),p.ship(),i);identity(base.destination(),p.destination(),i);
   require(s.sourcePosition().equals(first.sourcePosition())&&s.targetPosition().equals(first.targetPosition())
    &&s.sourceHistoryVelocity().length()==0&&s.targetHistoryVelocity().length()==0
    &&s.sourceSpin()==0&&s.targetSpin()==0,"Native local position/history/spin must be quiescent");
   var endpoints=List.of(p.ship(),p.destination());var orbits=List.of(a,b);
   for(int k=0;k<2;k++){
    var predicted=orbits.get(k).shiftedBy(i*.05).getPVCoordinates();var actual=endpoints.get(k);
    double pe=predicted.getPosition().distance(j(actual.celestialPosition())),ve=predicted.getVelocity().distance(j(actual.celestialVelocity()));
    require(Double.isFinite(pe)&&Double.isFinite(ve)&&pe<=1e-3&&ve<=1e-6,"Observed state does not follow initial unforced coast");
    maxP=Math.max(maxP,pe);maxV=Math.max(maxV,ve);
   }
   double speed=p.ship().celestialVelocity().sub(p.destination().celestialVelocity()).length();
   require(speed>1e-3&&speed<=.08,"Resolved distinct coast speed within encounter envelope required");
   require(p.ship().celestialPosition().sub(p.destination().celestialPosition()).add(p.ship().localOffset()).sub(p.destination().localOffset()).length()<=64,"Physical endpoints outside bounded encounter neighborhood");
  }
  var latest=samples.getLast().pair();latest=OrbitalEndpoint.pair(latest.ship(),latest.destination());
  return new Qualified(latest,latest.ship().celestialVelocity().sub(latest.destination().celestialVelocity()),samples.size(),maxP,maxV);
 }
}
