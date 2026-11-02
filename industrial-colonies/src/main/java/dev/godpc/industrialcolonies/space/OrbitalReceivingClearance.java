package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.godpc.industrialcolonies.space.RendezvousGuidance.V;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.AABB;

/** Read-only receiving footprint for an orientation-preserving frame change.
 * The coordinate gap is not a swept flight corridor. No body, including the
 * intended destination, is exempt. Unknown chunks and oversized scans refuse.
 * Half-second prediction assumes acceleration <= 1m/s^2 and angular acceleration
 * <= .25rad/s^2; the caller must establish those bounds for the actual craft.
 */
public final class OrbitalReceivingClearance {
 private OrbitalReceivingClearance(){}
 public record Result(boolean clear,String reason,int blocks,int bodies,int entities){}
 private static Result denied(String reason,int blocks,int bodies,int entities){return new Result(false,reason,blocks,bodies,entities);}
 public static Result check(ServerSubLevel ship,V receivingPosition,V receivingVelocity){
  if(ship==null||ship.isRemoved()||receivingPosition==null||receivingVelocity==null
    ||!receivingPosition.finite()||!receivingVelocity.finite()||receivingVelocity.length()>1)
   return denied("INVALID_RECEIVING_STATE",0,0,0);
  var level=ship.getLevel();if(!level.getServer().isSameThread())return denied("WRONG_THREAD",0,0,0);
  var nativeBody=RigidBodyHandle.of(ship);if(!nativeBody.isValid())return denied("BODY_UNAVAILABLE",0,0,0);
  var current=ship.boundingBox().toMojang();var origin=ship.logicalPose().position();
  if(!finite(current)||!Double.isFinite(origin.x())||!Double.isFinite(origin.y())||!Double.isFinite(origin.z()))return denied("INVALID_BODY_BOUNDS",0,0,0);
  double spin=nativeBody.getAngularVelocity().length();if(!Double.isFinite(spin)||spin>.01)return denied("UNRESOLVED_ROTATION",0,0,0);
  double dx=receivingPosition.x()-origin.x(),dy=receivingPosition.y()-origin.y(),dz=receivingPosition.z()-origin.z();
  var placed=current.move(dx,dy,dz);
  double radius=radius(current,origin.x(),origin.y(),origin.z());
  double margin=.25+radius*Math.min(2,spin*.5+.5*.25*.5*.5)+.5*.5*.5;
  var envelope=placed.minmax(placed.move(receivingVelocity.x()*.5,receivingVelocity.y()*.5,receivingVelocity.z()*.5)).inflate(margin);
  if(!finite(envelope)||envelope.getXsize()>64||envelope.getYsize()>64||envelope.getZsize()>64)return denied("RECEIVING_SCAN_LIMIT",0,0,0);
  int x0=(int)Math.floor(envelope.minX),x1=(int)Math.floor(envelope.maxX),z0=(int)Math.floor(envelope.minZ),z1=(int)Math.floor(envelope.maxZ);
  int y0=Math.max(level.getMinBuildHeight(),(int)Math.floor(envelope.minY)),y1=Math.min(level.getMaxBuildHeight()-1,(int)Math.floor(envelope.maxY));
  if((long)(x1-x0+1)*Math.max(0,y1-y0+1)*(z1-z0+1)>65536)return denied("RECEIVING_SCAN_LIMIT",0,0,0);
  for(int x=x0>>4;x<=x1>>4;x++)for(int z=z0>>4;z<=z1>>4;z++)if(!level.hasChunk(x,z))return denied("UNLOADED_RECEIVING_SPACE",0,0,0);
  var container=ServerSubLevelContainer.getContainer(level);if(container==null)return denied("BODY_INDEX_UNAVAILABLE",0,0,0);
  int bodies=0,blocks=0,entities=0;
  for(var other:container.getAllSubLevels()){
   if(other==ship||other.isRemoved())continue;if(++bodies>128)return denied("BODY_SCAN_LIMIT",blocks,bodies,entities);
   var handle=RigidBodyHandle.of(other);if(!handle.isValid())return denied("OTHER_BODY_UNAVAILABLE",blocks,bodies,entities);
   var bounds=other.boundingBox().toMojang();var velocity=handle.getLinearVelocity();double angular=handle.getAngularVelocity().length();var p=other.logicalPose().position();
   if(!finite(bounds)||!Double.isFinite(velocity.length())||!Double.isFinite(angular))return denied("OTHER_BODY_STATE_INVALID",blocks,bodies,entities);
   double reserve=.25+radius(bounds,p.x(),p.y(),p.z())*Math.min(2,angular*.5+.5*.25*.5*.5)+.5*.5*.5;
   var swept=bounds.minmax(bounds.move(velocity.x()*.5,velocity.y()*.5,velocity.z()*.5)).inflate(reserve);
   if(!finite(swept))return denied("OTHER_BODY_STATE_INVALID",blocks,bodies,entities);
   if(envelope.intersects(swept))return denied("BODY_IN_RECEIVING_SPACE",blocks,bodies,entities);
  }
  if(y0<=y1)for(var pos:BlockPos.betweenClosed(x0,y0,z0,x1,y1,z1)){
   blocks++;if(!level.getBlockState(pos).getCollisionShape(level,pos).isEmpty()||!level.getFluidState(pos).isEmpty())return denied("BLOCK_IN_RECEIVING_SPACE",blocks,bodies,entities);
  }
  for(var entity:level.getAllEntities()){
   if(++entities>4096)return denied("ENTITY_SCAN_LIMIT",blocks,bodies,entities);
   if(!entity.isRemoved()&&entity.getBoundingBox().intersects(envelope))return denied("ENTITY_IN_RECEIVING_SPACE",blocks,bodies,entities);
  }
  return new Result(true,"CLEAR_BOUNDED_RECEIVING_FOOTPRINT",blocks,bodies,entities);
 }
 private static double radius(AABB b,double x,double y,double z){double dx=Math.max(Math.abs(b.minX-x),Math.abs(b.maxX-x)),dy=Math.max(Math.abs(b.minY-y),Math.abs(b.maxY-y)),dz=Math.max(Math.abs(b.minZ-z),Math.abs(b.maxZ-z));return Math.sqrt(dx*dx+dy*dy+dz*dz);}
 private static boolean finite(AABB b){return Double.isFinite(b.minX)&&Double.isFinite(b.minY)&&Double.isFinite(b.minZ)&&Double.isFinite(b.maxX)&&Double.isFinite(b.maxY)&&Double.isFinite(b.maxZ)&&Math.abs(b.minX)<30000000&&Math.abs(b.maxX)<30000000&&Math.abs(b.minY)<30000000&&Math.abs(b.maxY)<30000000&&Math.abs(b.minZ)<30000000&&Math.abs(b.maxZ)<30000000;}
}
