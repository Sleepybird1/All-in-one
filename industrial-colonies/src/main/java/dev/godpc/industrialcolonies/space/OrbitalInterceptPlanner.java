package dev.godpc.industrialcolonies.space;

import java.util.Objects;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Read-only fixed-time shooting calculation. The supplied target state must be
 * propagated to the arrival epoch in the same inertial frame as departure.
 * This proposes ideal instantaneous impulses, not a flyable finite burn, fuel
 * budget, collision clearance, encounter admission or minimum-cost trajectory.
 * A native propagator must reject unsupported or unsafe orbital states. */
public final class OrbitalInterceptPlanner {
 private OrbitalInterceptPlanner(){}
 public record State(V position,V velocity){
  public State{finite(position);finite(velocity);}
 }
 @FunctionalInterface public interface Propagator {
  State propagate(State initial,double seconds);
 }
 public record Proposal(V departureImpulse,V arrivalImpulse,State arrival,
                        double seconds,double positionResidual,int iterations){}
 public static Proposal solve(State departure,State targetAtArrival,double seconds,
                              double departureBudget,double arrivalBudget,Propagator propagator){
  Objects.requireNonNull(departure);Objects.requireNonNull(targetAtArrival);Objects.requireNonNull(propagator);
  require(Double.isFinite(seconds)&&seconds>=1&&seconds<=3600,"Qualified flight time is 1..3600 seconds");
  require(Double.isFinite(departureBudget)&&departureBudget>0&&departureBudget<=1000
   &&Double.isFinite(arrivalBudget)&&arrivalBudget>0&&arrivalBudget<=1000,"Finite impulse budgets in (0,1000] required");
  V velocity=departure.velocity();
  for(int iteration=0;iteration<=16;iteration++){
   State arrival=Objects.requireNonNull(propagator.propagate(new State(departure.position(),velocity),seconds));
   V error=targetAtArrival.position().sub(arrival.position());double residual=norm(error);
   if(residual<=.01){
    V start=velocity.sub(departure.velocity()),end=targetAtArrival.velocity().sub(arrival.velocity());
    require(norm(start)<=departureBudget&&norm(end)<=arrivalBudget,"Impulse budget exceeded");
    return new Proposal(start,end,arrival,seconds,residual,iteration);
   }
   require(iteration<16,"Bounded intercept solve did not converge");
   // Central differences reduce first-order truncation. One millimeter/second
   // is well above double rounding for the bounded velocities used here.
   double h=Math.max(.001,Math.ulp(norm(velocity))*128);
   require(Double.isFinite(h)&&h<=.01,"Velocity precision insufficient for shooting solve");
   V[] columns=new V[3];
   for(int axis=0;axis<3;axis++){
    V offset=axis==0?new V(h,0,0):axis==1?new V(0,h,0):new V(0,0,h);
    var plus=propagator.propagate(new State(departure.position(),velocity.add(offset)),seconds);
    var minus=propagator.propagate(new State(departure.position(),velocity.sub(offset)),seconds);
    columns[axis]=plus.position().sub(minus.position()).mul(.5/h);finite(columns[axis]);
   }
   V correction=linear(columns,error);boolean improved=false;
   for(int backtrack=0;backtrack<12;backtrack++){
    V candidate=velocity.add(correction.mul(Math.scalb(1.0,-backtrack)));
    if(norm(candidate.sub(departure.velocity()))>departureBudget)continue;
    State trial;
    try{trial=propagator.propagate(new State(departure.position(),candidate),seconds);}
    catch(IllegalArgumentException unsafe){continue;}
    if(norm(targetAtArrival.position().sub(trial.position()))<residual){velocity=candidate;improved=true;break;}
   }
   require(improved,"No improving bounded intercept step: iteration="+iteration+", residual="+residual+", correction="+correction+", velocity="+velocity);
  }
  throw new AssertionError("Unreachable bounded solve");
 }
 private static V linear(V[] columns,V rhs){
  double[][] a={{columns[0].x(),columns[1].x(),columns[2].x(),rhs.x()},
                {columns[0].y(),columns[1].y(),columns[2].y(),rhs.y()},
                {columns[0].z(),columns[1].z(),columns[2].z(),rhs.z()}};
  double scale=0;for(V c:columns)scale=Math.max(scale,norm(c));
  require(scale>0,"Singular trajectory sensitivity");
  for(int pivot=0;pivot<3;pivot++){
   int best=pivot;for(int row=pivot+1;row<3;row++)if(Math.abs(a[row][pivot])>Math.abs(a[best][pivot]))best=row;
   var swap=a[pivot];a[pivot]=a[best];a[best]=swap;
   require(Math.abs(a[pivot][pivot])>scale*1e-10,"Ill-conditioned trajectory sensitivity");
   double divisor=a[pivot][pivot];for(int col=pivot;col<4;col++)a[pivot][col]/=divisor;
   for(int row=0;row<3;row++)if(row!=pivot){double factor=a[row][pivot];for(int col=pivot;col<4;col++)a[row][col]-=factor*a[pivot][col];}
  }
  V result=new V(a[0][3],a[1][3],a[2][3]);finite(result);return result;
 }
 private static double norm(V v){finite(v);double n=v.length();require(Double.isFinite(n),"Vector magnitude overflow");return n;}
 private static void finite(V v){require(v!=null&&v.finite(),"Finite vector required");}
 private static void require(boolean value,String reason){if(!value)throw new IllegalArgumentException(reason);}
}
