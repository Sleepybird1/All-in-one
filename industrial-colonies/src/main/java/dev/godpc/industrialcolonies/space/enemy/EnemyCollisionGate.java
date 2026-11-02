package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.RendezvousClearance;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import dev.devce.rocketnautics.content.orbit.DeepSpaceData;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import org.joml.Vector3d;

/** Read-only local gate using the previously qualified swept-hull checker.
 * The forecast remains conditional on the supplied acceleration bound; this
 * is not traffic prediction, a stopping guarantee, or permission to fire. */
public final class EnemyCollisionGate {
    public record Result(boolean clear,String reason,double closingSpeed,int blocks,int bodies) {}
    private EnemyCollisionGate() {}
    public static Result check(ServerSubLevel source,NativeEnemyHull hull,ServerSubLevel target,double closingLimit) {
        if(source==null||target==null||hull==null||!hull.belongsTo(source)||source==target
                ||source.getLevel()!=target.getLevel()||!source.getLevel().getServer().isSameThread()
                ||!Double.isFinite(closingLimit)||closingLimit<=0||closingLimit>.1)return denied("INVALID_REQUEST",0);
        if(!hull.validate())return denied("HULL_"+hull.reason(),0);
        try {
            var own=RigidBodyHandle.of(source);var other=RigidBodyHandle.of(target);
            if(!own.isValid()||!other.isValid())return denied("BODY_UNAVAILABLE",0);
            var p=source.logicalPose().transformPosition(new Vector3d(source.getMassTracker().getCenterOfMass()));
            var q=target.logicalPose().transformPosition(new Vector3d(target.getMassTracker().getCenterOfMass()));
            if(!commonFrame(source,target,p,q))return denied("FRAME_UNAVAILABLE_OR_CHANGED",0);
            var v=new Vector3d(own.getLinearVelocity());var w=new Vector3d(other.getLinearVelocity());
            if(!p.isFinite()||!q.isFinite()||!v.isFinite()||!w.isFinite()||v.length()>.2||w.length()>.1)
                return denied("UNSAFE_MOTION",0);
            var delta=q.sub(p);double distance=delta.length();
            if(distance<10||distance>128)return denied("UNSAFE_RANGE",0);
            double closing=v.sub(w).dot(delta.div(distance));
            if(closing>closingLimit)return denied("UNSAFE_CLOSING_SPEED",closing);
            var assembly=EnemyMountedAssembly.sample(source);
            if(assembly.isEmpty())return denied("ASSEMBLY_UNAVAILABLE",closing);
            if(!EnemyNativeFrame.contains(source,assembly.get().bounds()))return denied("ASSEMBLY_OUTSIDE_NATIVE_FRAME",closing);
            var clearance=assembly.get().attachments()==0?RendezvousClearance.check(source,V.ZERO,1,.05)
                    :RendezvousClearance.checkAssembly(source,V.ZERO,1,.05,assembly.get());
            return new Result(clearance.clear(),clearance.reason(),closing,clearance.checkedBlocks(),clearance.checkedBodies());
        }catch(RuntimeException unavailable){return denied("OBSERVATION_UNAVAILABLE",0);}
    }
    /** Same dimension is insufficient for separate native orbital cells. This
     * only verifies a common current frame; it grants no flight authority. */
    private static boolean commonFrame(ServerSubLevel source,ServerSubLevel target,Vector3d p,Vector3d q) {
        if(source.isRemoved()||target.isRemoved()||!p.isFinite()||!q.isFinite())return false;
        if(!source.getLevel().dimension().location().toString().equals("rocketnautics:deep_space"))return true;
        if(p.x<Integer.MIN_VALUE||p.x>Integer.MAX_VALUE||p.z<Integer.MIN_VALUE||p.z>Integer.MAX_VALUE
                ||q.x<Integer.MIN_VALUE||q.x>Integer.MAX_VALUE||q.z<Integer.MIN_VALUE||q.z>Integer.MAX_VALUE)return false;
        var data=DeepSpaceData.getInstance(source.getLevel().getServer());
        var a=data.getInstanceForPos((int)Math.floor(p.x),(int)Math.floor(p.z));
        var b=data.getInstanceForPos((int)Math.floor(q.x),(int)Math.floor(q.z));
        return a!=null&&b!=null&&a.getId()==b.getId()&&!a.isCorrupted()&&!b.isCorrupted()
                &&a.getPosition()!=null&&b.getPosition()!=null&&!a.getPosition().isCorrupted()&&!b.getPosition().isCorrupted()
                &&a.boundingBox().contains(p.x,p.y,p.z)&&b.boundingBox().contains(q.x,q.y,q.z);
    }
    private static Result denied(String reason,double closing){return new Result(false,reason,closing,0,0);}
}
