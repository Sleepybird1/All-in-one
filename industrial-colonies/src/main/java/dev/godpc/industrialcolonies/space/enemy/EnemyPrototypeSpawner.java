package dev.godpc.industrialcolonies.space.enemy;
import dev.godpc.industrialcolonies.space.AutonomousShipControl;
import dev.ryanhcode.sable.api.SubLevelAssemblyHelper;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.api.sublevel.ticket.SubLevelLoadingTicketType;
import dev.ryanhcode.sable.api.physics.handle.RigidBodyHandle;
import dev.ryanhcode.sable.companion.math.BoundingBox3i;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Unit;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import java.util.*;

/** Explicit staging-only unarmed prototype. No timer/event registration.
 * Admission checks physical hulls from native logical poses, not stale cached
 * broad-phase bounds. This proves instantaneous placement, not future traffic
 * clearance. Failed assembly retains its reservation and any body for audit. */
public final class EnemyPrototypeSpawner {
 public record Result(boolean admitted,String reason,ServerSubLevel body,NativeEnemyHull hull){}
 private EnemyPrototypeSpawner(){}
 public static Result spawn(ServerLevel level,BlockPos origin,UUID encounter,Set<String> allowedDimensions,EnemyEncounterBudget budget){
  if(!level.getServer().isSameThread()||origin==null||encounter==null||allowedDimensions==null||budget==null)return denied("INVALID_REQUEST");
  String dimension=level.dimension().location().toString();
  if(!allowedDimensions.contains(dimension)||dimension.equals("rocketnautics:deep_space"))return denied("DIMENSION_NOT_COMMISSIONED");
  if(AutonomousShipControl.get(level.getServer()).allDisabled())return denied("AUTOMATION_DISABLED");
  var area=new AABB(origin.getX()-1,origin.getY(),origin.getZ(),origin.getX()+2,origin.getY()+2,origin.getZ()+1).inflate(1);
  if(area.minY<level.getMinBuildHeight()||area.maxY>level.getMaxBuildHeight()||Math.abs(area.minX)>29999900||Math.abs(area.maxX)>29999900||Math.abs(area.minZ)>29999900||Math.abs(area.maxZ)>29999900)return denied("WORLD_LIMIT");
  for(var p:BlockPos.betweenClosed((int)Math.floor(area.minX),(int)Math.floor(area.minY),(int)Math.floor(area.minZ),(int)Math.floor(area.maxX),(int)Math.floor(area.maxY),(int)Math.floor(area.maxZ))){
   if(!level.hasChunkAt(p))return denied("UNLOADED_PLACEMENT");
   if(!level.getBlockState(p).isAir()||!level.getFluidState(p).isEmpty())return denied("OCCUPIED_PLACEMENT");
  }
  if(!level.getEntities(null,area).isEmpty())return denied("ENTITY_IN_PLACEMENT");
  int bodies=0;
  for(var other:SubLevelContainer.getContainer(level).getAllSubLevels()){
   if(other.isRemoved())continue;if(++bodies>128)return denied("BODY_SCAN_LIMIT");
   if(!RigidBodyHandle.of(other).isValid())return denied("BODY_UNAVAILABLE");
   var box=other.getPlot().getBoundingBox();if(box==null)return denied("BODY_BOUNDS_UNAVAILABLE");
   AABB physical=null;
   for(double x:new double[]{box.minX(),(double)box.maxX()+1})for(double y:new double[]{box.minY(),(double)box.maxY()+1})for(double z:new double[]{box.minZ(),(double)box.maxZ()+1}){
    var v=other.logicalPose().transformPosition(new org.joml.Vector3d(x,y,z));
    if(!Double.isFinite(v.x+v.y+v.z))return denied("INVALID_BODY_POSE");
    var point=new AABB(v.x,v.y,v.z,v.x,v.y,v.z);physical=physical==null?point:physical.minmax(point);
   }
   if(area.intersects(physical))return denied("BODY_IN_PLACEMENT");
  }
  var transponder=BuiltInRegistries.BLOCK.get(ResourceLocation.parse("create_aeronautics_automated_logistics:ship_transponder"));
  if(transponder==Blocks.AIR)return denied("TEMPLATE_UNAVAILABLE");
  if(!budget.reserve(encounter,4))return denied("BUDGET_REFUSED");
  ServerSubLevel body=null;
  try{
   var positions=List.of(origin,origin.east(),origin.west(),origin.above());
   level.setBlock(origin,transponder.defaultBlockState(),3);level.setBlock(origin.east(),Blocks.IRON_BLOCK.defaultBlockState(),3);
   level.setBlock(origin.west(),Blocks.GLASS.defaultBlockState(),3);level.setBlock(origin.above(),Blocks.IRON_BLOCK.defaultBlockState(),3);
   body=SubLevelAssemblyHelper.assembleBlocks(level,origin,positions,new BoundingBox3i(origin.getX()-1,origin.getY(),origin.getZ(),origin.getX()+1,origin.getY()+1,origin.getZ()));
   if(body==null)return new Result(false,"ASSEMBLY_HELD",null,null);
   SubLevelContainer.getContainer(level).addForceLoadTicket(body,SubLevelLoadingTicketType.COMMAND_FORCED,Unit.INSTANCE);
   EnemyHullIdentity.commission(body,encounter);var center=body.getPlot().getCenterBlock();
   var hull=NativeEnemyHull.commission(body,List.of(center,center.east(),center.west(),center.above()));
   return new Result(true,"COMMISSIONED_UNARMED_PROTOTYPE",body,hull);
  }catch(RuntimeException failure){return new Result(false,"ASSEMBLY_HELD_"+failure.getClass().getSimpleName(),body,null);}
 }
 private static Result denied(String reason){return new Result(false,reason,null,null);}
}
