package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.AABB;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;

/** Bounded conservative physical-space clearance check, not a path planner.
 * Checks the swept hull envelope, including other loaded bodies and static
 * blocks. Unknown chunks/oversized scans deny admission. The destination body
 * is deliberately not exempt: a protruding hull must not be ignored at a dock.
 * Prediction assumes bounded acceleration supplied by the caller; unexpected
 * future obstacles still require repeated checks and an independent abort policy.
 */
public final class RendezvousClearance {
    public record Result(boolean clear,String reason,int checkedBlocks,int checkedBodies) {}
    private RendezvousClearance(){}
    public static Result check(ServerSubLevel ship,V travel,double horizon,double accelerationBound){
        return check(ship,travel,horizon,accelerationBound,null);
    }
    /** Qualified owned attachments enlarge the source envelope. Bare-body
     * separation may not dismiss collisions involving protruding cannon geometry. */
    public static Result checkAssembly(ServerSubLevel ship,V travel,double horizon,double accelerationBound,
            dev.godpc.industrialcolonies.space.enemy.EnemyMountedAssembly assembly){
        if(assembly==null||!assembly.current(ship))return denied("ASSEMBLY_UNAVAILABLE",0,0);
        return check(ship,travel,horizon,accelerationBound,assembly);
    }
    private static Result check(ServerSubLevel ship,V travel,double horizon,double accelerationBound,
            dev.godpc.industrialcolonies.space.enemy.EnemyMountedAssembly assembly){
        if(ship==null||ship.isRemoved()||travel==null||!travel.finite()||travel.length()>32
                ||!Double.isFinite(horizon)||horizon<=0||horizon>5||!Double.isFinite(accelerationBound)
                ||accelerationBound<0||accelerationBound>10)return denied("INVALID_ENVELOPE",0,0);
        var level=ship.getLevel();if(!level.getServer().isSameThread())return denied("WRONG_THREAD",0,0);
        var own=RigidBodyHandle.of(ship);if(!own.isValid())return denied("BODY_UNAVAILABLE",0,0);
        AABB current=assembly==null?ship.boundingBox().toMojang():assembly.bounds();
        if(!finite(current))return denied("INVALID_BOUNDS",0,0);
        double ownSpin=own.getAngularVelocity().length();
        if(!Double.isFinite(ownSpin))return denied("INVALID_MOTION",0,0);
        double radius=rotationRadius(ship,current);
        if(!Double.isFinite(radius))return denied("INVALID_MASS_CENTER",0,0);
        // Include angular acceleration reserve, not just the current spin. The
        // approach controller caps commanded alpha at .1 rad/s^2; .25 is reserved.
        double rotationReserve=.5*.25*horizon*horizon;
        double margin=.2+radius*Math.min(2,ownSpin*horizon+rotationReserve)+.5*accelerationBound*horizon*horizon;
        var velocity=own.getLinearVelocity();
        if(!Double.isFinite(velocity.length()))return denied("INVALID_MOTION",0,0);
        AABB envelope=current.minmax(current.move(travel.x(),travel.y(),travel.z()))
                .minmax(current.move(velocity.x()*horizon,velocity.y()*horizon,velocity.z()*horizon)).inflate(margin);
        if(!finite(envelope)||envelope.getXsize()>64||envelope.getYsize()>64||envelope.getZsize()>64)return denied("SCAN_LIMIT",0,0);
        int minX=(int)Math.floor(envelope.minX),maxX=(int)Math.floor(envelope.maxX);
        int minY=Math.max(level.getMinBuildHeight(),(int)Math.floor(envelope.minY)),maxY=Math.min(level.getMaxBuildHeight()-1,(int)Math.floor(envelope.maxY));
        int minZ=(int)Math.floor(envelope.minZ),maxZ=(int)Math.floor(envelope.maxZ);
        if((long)(maxX-minX+1)*Math.max(0,maxY-minY+1)*(maxZ-minZ+1)>65536)return denied("SCAN_LIMIT",0,0);
        for(int x=minX>>4;x<=maxX>>4;x++)for(int z=minZ>>4;z<=maxZ>>4;z++)
            if(!level.hasChunk(x,z))return denied("UNLOADED_CORRIDOR",0,0);
        var container=ServerSubLevelContainer.getContainer(level);if(container==null)return denied("BODY_INDEX_UNAVAILABLE",0,0);
        int bodies=0,blocks=0;
        for(var other:container.getAllSubLevels()){
            if(other==ship||other.isRemoved())continue;
            if(++bodies>128)return denied("BODY_SCAN_LIMIT",blocks,bodies);
            var handle=RigidBodyHandle.of(other);if(!handle.isValid())return denied("OTHER_BODY_UNAVAILABLE",blocks,bodies);
            var bounds=other.boundingBox().toMojang();var motion=handle.getLinearVelocity();double spin=handle.getAngularVelocity().length();
            if(!finite(bounds)||!Double.isFinite(motion.length())||!Double.isFinite(spin))return denied("OTHER_MOTION_INVALID",blocks,bodies);
            double otherRadius=rotationRadius(other,bounds);
            if(!Double.isFinite(otherRadius))return denied("OTHER_MASS_CENTER_INVALID",blocks,bodies);
            double otherMargin=.2+otherRadius*Math.min(2,spin*horizon+rotationReserve)+.5*accelerationBound*horizon*horizon;
            var swept=bounds.minmax(bounds.move(motion.x()*horizon,motion.y()*horizon,motion.z()*horizon)).inflate(otherMargin);
            // A world AABB includes empty corners around tilted ships. Only a
            // conservative separation proof may dismiss that broad-phase hit;
            // the destination keeps exactly the same motion/rotation reserves.
            if(envelope.intersects(swept)&&(assembly!=null||!RendezvousHullEnvelope.separated(corners(ship),corners(other),travel,
                    new V(velocity.x()*horizon,velocity.y()*horizon,velocity.z()*horizon),
                    new V(motion.x()*horizon,motion.y()*horizon,motion.z()*horizon),margin,otherMargin)))
                return denied("BODY_IN_CORRIDOR",blocks,bodies);
        }
        for(var p:BlockPos.betweenClosed(minX,minY,minZ,maxX,maxY,maxZ)){
            // betweenClosed normalizes endpoints, so explicitly skip an empty height range.
            if(minY>maxY)break;blocks++;
            if(!level.getBlockState(p).getCollisionShape(level,p).isEmpty()||!level.getFluidState(p).isEmpty())return denied("BLOCK_IN_CORRIDOR",blocks,bodies);
        }
        for(var entity:level.getEntities(null,envelope))
            if(!entity.isRemoved()&&Sable.HELPER.getTrackingOrVehicleSubLevel(entity)!=ship
                    &&(assembly==null||!assembly.owns(entity)
                    &&!dev.godpc.industrialcolonies.space.enemy.EnemySpentCasing.ownedBy(ship,entity)))return denied("ENTITY_IN_CORRIDOR",blocks,bodies);
        if(assembly!=null&&!assembly.current(ship))return denied("ASSEMBLY_CHANGED_DURING_AUDIT",blocks,bodies);
        return new Result(true,assembly==null?"CLEAR_BOUNDED_ENVELOPE":"CLEAR_BOUNDED_ASSEMBLY_ENVELOPE",blocks,bodies);
    }
    private static boolean finite(AABB b){return Double.isFinite(b.minX)&&Double.isFinite(b.minY)&&Double.isFinite(b.minZ)&&Double.isFinite(b.maxX)&&Double.isFinite(b.maxY)&&Double.isFinite(b.maxZ)&&Math.abs(b.minX)<30000000&&Math.abs(b.maxX)<30000000&&Math.abs(b.minZ)<30000000&&Math.abs(b.maxZ)<30000000;}
    private static V[] corners(ServerSubLevel body){
        var box=body.getPlot().getBoundingBox();if(box==null)return null;
        V[] points=new V[8];int i=0;
        // Native plot maxima are inclusive block coordinates (SubLevel.updateBoundingBox).
        for(double x:new double[]{box.minX(),(double)box.maxX()+1})
            for(double y:new double[]{box.minY(),(double)box.maxY()+1})
                for(double z:new double[]{box.minZ(),(double)box.maxZ()+1}){
                    var p=body.logicalPose().transformPosition(new org.joml.Vector3d(x,y,z));points[i++]=new V(p.x,p.y,p.z);
                }
        return points;
    }
    private static double rotationRadius(ServerSubLevel body,AABB bounds){
        // Farthest corner from the actual mass center bounds every hull point.
        // The full box diagonal needlessly doubled the reserve for centered hulls.
        var center=body.logicalPose().transformPosition(new org.joml.Vector3d(body.getMassTracker().getCenterOfMass()));
        double x=Math.max(Math.abs(bounds.minX-center.x),Math.abs(bounds.maxX-center.x));
        double y=Math.max(Math.abs(bounds.minY-center.y),Math.abs(bounds.maxY-center.y));
        double z=Math.max(Math.abs(bounds.minZ-center.z),Math.abs(bounds.maxZ-center.z));
        return Math.sqrt(x*x+y*y+z*z);
    }
    private static Result denied(String why,int blocks,int bodies){return new Result(false,why,blocks,bodies);}
}
