package dev.godpc.industrialcolonies.space;
import java.util.*;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.shaded.orekit.orbits.CartesianOrbit;
import dev.devce.rocketnautics.shaded.orekit.utils.PVCoordinates;
import dev.devce.rocketnautics.shaded.hipparchus.geometry.euclidean.threed.Vector3D;

/** Read-only two finite pulses with position and velocity closure. Fixed-hull,
 * prescribed response only; callers must qualify clearance and actual motion.
 * Boundary replanning accepts only an externally verified quiet first crossing.
 * No body, actuator, destination, cargo or journal access is present. */
public final class OrbitalTwoPulseArrivalPlanner {
 private OrbitalTwoPulseArrivalPlanner(){}
 public record Proposal(V firstRadial,V secondRadial,V firstForce,V secondForce,
   V firstStage,V secondStage,V arrivalGoal,V receivingPosition,V receivingVelocity,
   int firstTick,int secondTick,int horizonTicks,int poweredTicks,int maneuverTicks,
   double maximumOverrun,int iterations,List<CartesianOrbit> segments){
  public Proposal{segments=List.copyOf(segments);}
 }
 public static Proposal solve(CartesianOrbit source,CartesianOrbit target,V position,V center,
   double hull,double mass,V receivingCenter,V receivingOffset,V desired){
  return new Calculation(source,target,position,center,hull,mass,receivingCenter,receivingOffset,desired,6000,14000,22000,800,false).solve(null);
 }
 public static Proposal replanAtFirstBoundary(CartesianOrbit source,CartesianOrbit target,V position,V center,
   double hull,double mass,V receivingCenter,V receivingOffset,V desired,Proposal initial,int elapsedTicks){
  Objects.requireNonNull(initial);require(elapsedTicks>=0&&elapsedTicks<=initial.firstTick(),"First pulse epoch has not passed");
  return new Calculation(source,target,position,center,hull,mass,receivingCenter,receivingOffset,desired,
   initial.firstTick()-elapsedTicks,initial.secondTick()-elapsedTicks,initial.horizonTicks()-elapsedTicks,initial.poweredTicks(),true).solve(initial);
 }
 static V v(double[] a){return new V(a[0],a[1],a[2]);}
 static V v(Vector3D a){return new V(a.getX(),a.getY(),a.getZ());}
 static Vector3D j(V a){return new Vector3D(a.x(),a.y(),a.z());}
 static CartesianOrbit orbit(V p,V velocity,CartesianOrbit ref){return new CartesianOrbit(new PVCoordinates(j(p),j(velocity)),ref.getFrame(),ref.getDate(),ref.getMu());}
 static void require(boolean b,String s){if(!b)throw new IllegalArgumentException(s);}
 static V unit(V a){require(a.length()>.001,"Unresolved radial direction");return a.mul(1/a.length());}

 private static final class Calculation {
  final CartesianOrbit source,target;final V position,center,receivingCenter,offset,desired;
  final double hull,mass;final int firstTick,secondTick,endTick,poweredTicks;final boolean boundary;boolean collect;
  Calculation(CartesianOrbit source,CartesianOrbit target,V position,V center,double hull,double mass,
   V receivingCenter,V offset,V desired,int first,int second,int end,int powered,boolean boundary){
   Objects.requireNonNull(source);Objects.requireNonNull(target);
   require(source.getFrame()==target.getFrame()&&source.getFrame().isPseudoInertial()&&source.getDate().equals(target.getDate())&&source.getMu()==target.getMu(),"Synchronized inertial source and target required");
   for(var o:List.of(source,target))require(!o.hasNonKeplerianAcceleration()&&Double.isFinite(o.getA())&&o.getA()>0&&Double.isFinite(o.getE())&&o.getE()>=0&&o.getE()<1&&Double.isFinite(o.getMu())&&o.getMu()>0,"Finite elliptic coast required");
   for(var v:new V[]{position,center,receivingCenter,offset,desired})require(v!=null&&v.finite(),"Finite geometry required");
   require(Double.isFinite(hull)&&hull>0&&hull<128&&Double.isFinite(mass)&&mass>0&&mass<=10000,"Qualified hull and mass required");
   require(desired.length()>.001&&desired.length()<=.08,"Bounded nonzero receiving velocity required");
   require(first>=0&&second>first+powered+400&&end>second+powered+400&&end<=22000&&powered>=20&&powered<=800,"Bounded pulse timetable required");
   double overrun=2*(position.sub(center).length()+hull)-256;
   require(boundary?overrun>0&&overrun<.1:overrun<0,"Initial cell containment required");
   this.source=source;this.target=target;this.position=position;this.center=center;this.hull=hull;this.mass=mass;
   this.receivingCenter=receivingCenter;this.offset=offset;this.desired=desired;firstTick=first;secondTick=second;endTick=end;poweredTicks=powered;this.boundary=boundary;
  }
 class State {
  CartesianOrbit orbit=source;V p=position,velocity=V.ZERO,queued=V.ZERO;int ticks;double maxOverrun;final List<CartesianOrbit> segments=new ArrayList<>();
  double overrun(){return 2*(p.sub(center).length()+hull)-256;}
  void step(V acceleration){
   require(ticks<endTick&&acceleration.finite()&&acceleration.length()<=.10000001,"Bounded finite control");
   var r=OrbitalFiniteBurnStep.predict(p,velocity,queued,V.ZERO,mass,center,256,hull);var pv=orbit.getPVCoordinates();
   var segment=OrbitalTwoPulseArrivalPlanner.orbit(v(pv.getPosition()),v(pv.getVelocity()).add(r.orbitalImpulse()),orbit);
   if(collect)segments.add(segment);
   orbit=segment.shiftedBy(.05);
   p=r.localPosition();velocity=r.localVelocity();queued=acceleration.mul(mass);ticks++;maxOverrun=Math.max(maxOverrun,overrun());
   require(overrun()<.1,"Coupling overrun");
  }
  void coast(int count){for(int i=0;i<count;i++)step(V.ZERO);}
  void move(V goal,double speed,int budget){int stable=0;for(int i=0;i<budget;i++){
   step(LocalCellTrimGuidance.acceleration(p,velocity,goal,.1,speed,.055));
   stable=p.sub(goal).length()<.06&&velocity.length()<1e-6?stable+1:0;
   if(stable>=20){coast(101);require(velocity.length()<1e-5,"Unsettled positioning");return;}
  }throw new IllegalArgumentException("Positioning budget");}
  void pulse(V radial,V force,int epoch){
   require(force.finite()&&force.length()<=mass*.1,"Force budget");
   if(!(boundary&&epoch==firstTick)) {
   move(center.add(radial.mul(128-hull-2)),2,6000);
   boolean crossed=false;for(int n=0;n<2000;n++){
    if(overrun()>0){crossed=true;step(V.ZERO);break;}step(radial.mul(.075).sub(velocity).mul(2).capped(.1));
   }
   require(crossed,"Crossing budget");coast(100);require(velocity.length()<1e-5,"Unsettled crossing");
   } else require(overrun()>0&&overrun()<.1,"Measured settled first boundary required");
   require(ticks<=epoch,"Fixed pulse epoch missed: "+ticks+">"+epoch);coast(epoch-ticks);
   for(int i=0;i<poweredTicks;i++)step(force.mul(1/mass));coast(100);require(velocity.length()<1e-5,"Unsettled pulse");
   move(p.sub(unit(p.sub(center)).mul(2)),.4,2000);require(overrun()<-3,"Retreat not inside cell");
  }
 }
 State run(double[] f,V first,V second){State s=new State();s.pulse(first,new V(f[0],f[1],f[2]),firstTick);s.pulse(second,new V(f[3],f[4],f[5]),secondTick);return s;}
 double[] residual(State s,V desired){var a=s.orbit.shiftedBy((endTick-s.ticks)*.05).getPVCoordinates();var b=target.shiftedBy(endTick*.05).getPVCoordinates();V p=v(a.getPosition().subtract(b.getPosition())),d=v(a.getVelocity().subtract(b.getVelocity())).sub(desired);return new double[]{p.x()/100,p.y()/100,p.z()/100,d.x(),d.y(),d.z()};}
 static double norm(double[] r){double n=0;for(double d:r)n+=d*d;return Math.sqrt(n);}
 static double[] linear(double[][] matrix,double[] residual){double[][] a=new double[6][7];for(int i=0;i<6;i++){System.arraycopy(matrix[i],0,a[i],0,6);a[i][6]=-residual[i];}
  for(int i=0;i<6;i++){int best=i;for(int n=i+1;n<6;n++)if(Math.abs(a[n][i])>Math.abs(a[best][i]))best=n;var swap=a[i];a[i]=a[best];a[best]=swap;require(Math.abs(a[i][i])>1e-9,"Singular sensitivity");double d=a[i][i];for(int c=i;c<7;c++)a[i][c]/=d;for(int n=0;n<6;n++)if(n!=i){double f=a[n][i];for(int c=i;c<7;c++)a[n][c]-=f*a[i][c];}}
  double[] x=new double[6];for(int i=0;i<6;i++)x[i]=a[i][6];return x;
 }

  Proposal solve(Proposal initial){
   V first,second,a,b;
   if(initial==null){
    var dep=source.shiftedBy(firstTick*.05);var dst=target.shiftedBy(secondTick*.05);var dp=dep.getPVCoordinates();var tp=dst.getPVCoordinates();
    var ideal=OrbitalInterceptPlanner.solve(new OrbitalInterceptPlanner.State(v(dp.getPosition()),v(dp.getVelocity())),new OrbitalInterceptPlanner.State(v(tp.getPosition()),v(tp.getVelocity())),(secondTick-firstTick)*.05,4,4,(s,dt)->{var q=orbit(s.position(),s.velocity(),dep).shiftedBy(dt).getPVCoordinates();return new OrbitalInterceptPlanner.State(v(q.getPosition()),v(q.getVelocity()));});
    first=unit(ideal.departureImpulse());second=unit(ideal.arrivalImpulse());
    a=ideal.departureImpulse().sub(first.mul(.075)).mul(mass/(poweredTicks*.05));b=ideal.arrivalImpulse().sub(second.mul(.075)).mul(mass/(poweredTicks*.05));
   }else{first=initial.firstRadial();second=initial.secondRadial();a=initial.firstForce();b=initial.secondForce();}
   double[] f={a.x(),a.y(),a.z(),b.x(),b.y(),b.z()};
   for(int iteration=0;iteration<16;iteration++){
    State s=run(f,first,second);double[] error=residual(s,desired);double n=norm(error);
    if(n<.0001){
     collect=true;s=run(f,first,second);var future=s.orbit.shiftedBy((endTick-s.ticks)*.05).getPVCoordinates();
     V separation=v(future.getPosition().subtract(target.shiftedBy(endTick*.05).getPVCoordinates().getPosition()));
     V goal=center.add(offset.sub(separation));require(goal.sub(center).length()+hull<127.5,"Receiving goal outside source cell");
     s.move(goal,2,6000);require(s.ticks<endTick-200,"Insufficient arrival reserve");int finished=s.ticks;s.coast(endTick-s.ticks);
     var err=residual(s,desired);require(norm(err)<.0001,"Final reposition changed orbit");
     V receivingPosition=receivingCenter.add(s.p.sub(center)).add(new V(err[0]*100,err[1]*100,err[2]*100));
     V receivingVelocity=desired.add(new V(err[3],err[4],err[5]));OrbitalMotionPrecision.requireResolved(receivingPosition,receivingVelocity,2,18);
     require(receivingPosition.sub(receivingCenter.add(offset)).length()<.08&&receivingVelocity.length()<=.08,"Final receiving envelope");
     return new Proposal(first,second,new V(f[0],f[1],f[2]),new V(f[3],f[4],f[5]),center.add(first.mul(128-hull-2)),center.add(second.mul(128-hull-2)),goal,receivingPosition,receivingVelocity,firstTick,secondTick,endTick,poweredTicks,finished,s.maxOverrun,iteration,s.segments);
    }
    double[][] m=new double[6][6];double h=.01;
    for(int axis=0;axis<6;axis++){double[] plus=f.clone(),minus=f.clone();plus[axis]+=h;minus[axis]-=h;var pe=residual(run(plus,first,second),desired);var me=residual(run(minus,first,second),desired);for(int row=0;row<6;row++)m[row][axis]=(pe[row]-me[row])/(2*h);}
    double[] correction=linear(m,error);boolean better=false;
    for(int back=0;back<10;back++){double[] trial=f.clone();for(int i=0;i<6;i++)trial[i]+=correction[i]*Math.scalb(1.,-back);try{if(norm(residual(run(trial,first,second),desired))<n){f=trial;better=true;break;}}catch(IllegalArgumentException refused){}}
    require(better,"No improving bounded two-pulse step");
   }
   throw new IllegalArgumentException("Two-pulse solve budget");
  }
 }
}
