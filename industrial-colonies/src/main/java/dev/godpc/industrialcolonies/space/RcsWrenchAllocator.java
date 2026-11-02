package dev.godpc.industrialcolonies.space;

import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import java.util.*;

/** Bounded nonnegative force/torque allocation. Residuals are mandatory authority
 * diagnostics: an infeasible demand is never reported as achieved. No actuation.
 */
public final class RcsWrenchAllocator {
    private RcsWrenchAllocator() {}
    public record Jet(String id,V forceAtFullThrottle,V leverFromCenter) {}
    public record Allocation(List<Double> throttles,V achievedForce,V achievedTorque,
                             double forceError,double torqueError) {}

    public static Allocation allocate(List<Jet> jets,V force,V torque,double torqueLengthScale) {
        if(jets==null||jets.isEmpty()||jets.size()>128||force==null||torque==null
                ||!force.finite()||!torque.finite()||!Double.isFinite(torqueLengthScale)||torqueLengthScale<=0)
            throw new IllegalArgumentException("Invalid bounded wrench request");
        Set<String> ids=new HashSet<>();int n=jets.size();double[][] columns=new double[n][6];
        double[] residual={-force.x(),-force.y(),-force.z(),-torque.x()/torqueLengthScale,-torque.y()/torqueLengthScale,-torque.z()/torqueLengthScale};
        double[] throttle=new double[n],norm=new double[n];
        for(int i=0;i<n;i++){
            Jet jet=jets.get(i);
            if(jet==null||jet.id()==null||jet.id().isBlank()||!ids.add(jet.id())
                    ||jet.forceAtFullThrottle()==null||jet.leverFromCenter()==null
                    ||!jet.forceAtFullThrottle().finite()||!jet.leverFromCenter().finite())
                throw new IllegalArgumentException("Invalid or duplicate jet");
            V f=jet.forceAtFullThrottle(),t=jet.leverFromCenter().cross(f).mul(1/torqueLengthScale);
            columns[i]=new double[]{f.x(),f.y(),f.z(),t.x(),t.y(),t.z()};
            for(double v:columns[i])norm[i]+=v*v;
            if(!Double.isFinite(norm[i])||norm[i]<1e-16)throw new IllegalArgumentException("Invalid jet authority");
        }
        for(double v:residual)if(!Double.isFinite(v))throw new IllegalArgumentException("Wrench overflow");
        for(int sweep=0;sweep<256;sweep++){
            double changed=0;
            for(int i=0;i<n;i++){
                double gradient=0;for(int axis=0;axis<6;axis++)gradient+=columns[i][axis]*residual[axis];
                double next=Math.max(0,Math.min(1,throttle[i]-gradient/norm[i]));
                double delta=next-throttle[i];throttle[i]=next;changed=Math.max(changed,Math.abs(delta));
                for(int axis=0;axis<6;axis++)residual[axis]+=columns[i][axis]*delta;
            }
            if(changed<1e-10)break;
        }
        V actualForce=V.ZERO,actualTorque=V.ZERO;List<Double> result=new ArrayList<>(n);
        for(int i=0;i<n;i++){
            if(!Double.isFinite(throttle[i]))throw new IllegalArgumentException("Allocation overflow");
            result.add(throttle[i]);V f=jets.get(i).forceAtFullThrottle().mul(throttle[i]);
            actualForce=actualForce.add(f);actualTorque=actualTorque.add(jets.get(i).leverFromCenter().cross(f));
        }
        double forceError=actualForce.sub(force).length(),torqueError=actualTorque.sub(torque).length();
        if(!Double.isFinite(forceError)||!Double.isFinite(torqueError))throw new IllegalArgumentException("Allocation overflow");
        return new Allocation(List.copyOf(result),actualForce,actualTorque,forceError,torqueError);
    }
}
