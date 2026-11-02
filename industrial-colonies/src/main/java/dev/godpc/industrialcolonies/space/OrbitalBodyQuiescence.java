package dev.godpc.industrialcolonies.space;

import dev.devce.rocketnautics.content.blocks.RocketThrusterBlockEntity;
import dev.devce.rocketnautics.content.blocks.RCSThrusterBlockEntity;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import dev.ryanhcode.sable.sublevel.system.SubLevelPhysicsSystem;
import java.io.IOException;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.phys.AABB;
import org.joml.Vector3dc;

/** Immediate read-only gate, not a reservation or a guarantee about future forces.
 * Ownership, stored authority, motion resolution and destination clearance remain
 * separate requirements. Unknown propulsion mechanisms are not certified here.
 */
public final class OrbitalBodyQuiescence {
 private OrbitalBodyQuiescence(){}
 public record Controls(int rockets,int rcs){}
 public record Snapshot(OrbitalBodyCustody.Snapshot custody,Controls controls,int scannedEntities,int forceGroups){}
 private static void require(boolean value,String message){if(!value)throw new IllegalStateException(message);}
 private static OrbitalBodyCustody.Snapshot begin(ServerSubLevel body)throws IOException{
  require(!SubLevelPhysicsSystem.IN_PHYSICS_STEP,"Encounter check cannot run during physics");
  return OrbitalBodyCustody.read(body);
 }
 public static Controls controls(ServerSubLevel body)throws IOException{
  var custody=begin(body);return controls(body,custody);
 }
 private static Controls controls(ServerSubLevel body,OrbitalBodyCustody.Snapshot custody){
  var level=body.getLevel();int rockets=0,rcs=0;
  for(var pos:BlockPos.betweenClosed(custody.minimum(),custody.maximum())){
   var be=level.getBlockEntity(pos);
   if(be instanceof RocketThrusterBlockEntity engine){
    rockets++;var saved=engine.saveWithoutMetadata(level.registryAccess());
    require(!engine.isActive()&&engine.getCurrentPower()==0&&!level.hasNeighborSignal(pos)
      &&!saved.getBoolean("TargetActive")&&saved.getFloat("TargetThrottle")==0
      &&!engine.getPersistentData().contains(RocketActuatorLease.SAVED_MARKER),"Rocket control remains armed or leased");
   }
   if(be instanceof RCSThrusterBlockEntity engine){
    rcs++;var saved=engine.saveWithoutMetadata(level.registryAccess());
    require(!engine.isActive()&&!engine.currentlyBurning&&!level.hasNeighborSignal(pos)
      &&!saved.getBoolean("ComputerActive")&&saved.getFloat("ComputerThrottle")==0
      &&!engine.getPersistentData().contains(RcsActuatorLease.SAVED_MARKER),"RCS control remains armed or leased");
   }
  }
  return new Controls(rockets,rcs);
 }
 public static Snapshot read(ServerSubLevel body)throws IOException{return read(body,4096);}
 public static Snapshot read(ServerSubLevel body,int entityBudget)throws IOException{
  require(entityBudget>0&&entityBudget<=4096,"Invalid complete entity scan budget");
  var custody=begin(body);var level=body.getLevel();
  for(var pos:BlockPos.betweenClosed(custody.minimum(),custody.maximum())){
   var be=level.getBlockEntity(pos);if(be==null)continue;
   if(BuiltInRegistries.BLOCK.getKey(be.getBlockState().getBlock()).toString().equals("simulated:docking_connector")){
    try{
     require(!(Boolean)be.getClass().getMethod("isLocked").invoke(be)
       &&!(Boolean)be.getClass().getMethod("hasOtherConnector").invoke(be),"Physical connector remains attached");
    }catch(ReflectiveOperationException|ClassCastException failure){throw new IllegalStateException("Native connector state unavailable",failure);}
   }
  }
  for(var actor:body.getPlot().getBlockEntityActors()){
   var dependencies=actor.sable$getConnectionDependencies();
   if(dependencies!=null)for(var other:dependencies)require(other==body,"Physical body dependency remains attached");
  }
  var controls=controls(body,custody);int groups=0;
  // Native Sable initializes this map lazily and skips null in applyQueuedForces.
  var queued=body.getQueuedForceGroups();
  if(queued!=null)for(var group:queued.values()){
   require(++groups<=256,"Queued force scan budget exceeded");var total=group.getForceTotal();
   require(zero(total.getLocalForce())&&zero(total.getLocalTorque()),"Native force or torque remains queued");
  }
  var hull=body.boundingBox().toMojang();
  require(finite(hull)&&hull.getXsize()>0&&hull.getYsize()>0&&hull.getZsize()>0,"Invalid physical hull bounds");
  var plot=new AABB(custody.minimum().getX(),custody.minimum().getY(),custody.minimum().getZ(),
    (double)custody.maximum().getX()+1,(double)custody.maximum().getY()+1,(double)custody.maximum().getZ()+1);
  int entities=0;
  for(var entity:level.getAllEntities()){
   require(++entities<=entityBudget,"Complete entity scan budget exceeded");if(entity.isRemoved())continue;
   require(Sable.HELPER.getTrackingOrVehicleSubLevel(entity)!=body
     &&!entity.getBoundingBox().intersects(hull.inflate(.25))&&!entity.getBoundingBox().intersects(plot),
     "Entity or passenger remains on ship");
  }
  require(custody.equals(OrbitalBodyCustody.read(body)),"Body changed during quiescence check");
  return new Snapshot(custody,controls,entities,groups);
 }
 private static boolean zero(Vector3dc v){return Double.isFinite(v.x())&&Double.isFinite(v.y())&&Double.isFinite(v.z())&&v.x()==0&&v.y()==0&&v.z()==0;}
 private static boolean finite(AABB b){return Double.isFinite(b.minX)&&Double.isFinite(b.minY)&&Double.isFinite(b.minZ)&&Double.isFinite(b.maxX)&&Double.isFinite(b.maxY)&&Double.isFinite(b.maxZ);}
}
