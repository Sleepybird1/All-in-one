package dev.godpc.industrialcolonies.space;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.api.sublevel.SubLevelContainer;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.*;
import net.minecraft.resources.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/** Explicit commissioning only; resolve is read-only and never loads chunks,
 * claims orbital instances, starts guidance, moves bodies or touches cargo. */
public final class NativeFreightDestination {
 public static final String KEY="IndustrialColoniesFreightDestination";
 private static final ResourceLocation DOCK=ResourceLocation.parse("simulated:docking_connector");
 public record Resolved(FreightDestinationReference reference,ServerSubLevel body,BlockPos port,BlockEntity blockEntity){}
 private NativeFreightDestination(){}
 private static BlockEntity loadedDock(ServerLevel level,BlockPos pos){
  if(!level.getServer().isSameThread()||!level.hasChunkAt(pos))throw new IllegalStateException("Destination must already be loaded on server thread");
  var be=level.getBlockEntity(pos);
  if(be==null||be.isRemoved()||!DOCK.equals(BuiltInRegistries.BLOCK.getKey(level.getBlockState(pos).getBlock()))||!be.getBlockState().hasProperty(BlockStateProperties.FACING))throw new IllegalStateException("Original physical docking connector unavailable");
  return be;
 }
 /** Caller must obtain explicit operator commissioning authority. Idempotent
  * for the same owner/physical dock; never silently adopts another binding. */
 public static FreightDestinationReference capture(ServerLevel level,BlockPos pos,UUID owner){
  var be=loadedDock(level,pos);
  if(be.getPersistentData().contains(KEY)){
   var existing=FreightDestinationReference.decode(be.getPersistentData().getString(KEY));
   var actual=resolve(level.getServer(),existing,owner);
   if(actual.blockEntity()!=be)throw new IllegalStateException("Binding identifies another physical dock");return existing;
  }
  if(!(Sable.HELPER.getContaining(be) instanceof ServerSubLevel body)||body.isRemoved())throw new IllegalStateException("Loaded physical destination body required");
  var center=body.getPlot().getCenterBlock();var facing=be.getBlockState().getValue(BlockStateProperties.FACING);
  var up=facing.getAxis()==Direction.Axis.Y?Direction.NORTH:Direction.UP;
  var result=new FreightDestinationReference(UUID.randomUUID(),owner,body.getUniqueId(),level.dimension().location().toString(),
    Math.subtractExact(pos.getX(),center.getX()),Math.subtractExact(pos.getY(),center.getY()),Math.subtractExact(pos.getZ(),center.getZ()),
    FreightDestinationReference.Face.valueOf(facing.name()),FreightDestinationReference.Face.valueOf(up.name()));
  be.getPersistentData().putString(KEY,result.encode());be.setChanged();return result;
 }
 public static Resolved resolve(MinecraftServer server,FreightDestinationReference ref,UUID owner){
  if(!server.isSameThread()||!ref.owner().equals(owner))throw new IllegalStateException("Destination owner or server-thread authority disagrees");
  var level=server.getLevel(ResourceKey.create(Registries.DIMENSION,ResourceLocation.parse(ref.dimension())));
  if(level==null)throw new IllegalStateException("Destination dimension unavailable");
  var container=SubLevelContainer.getContainer(level);var found=container==null?null:container.getSubLevel(ref.body());
  if(!(found instanceof ServerSubLevel body)||body.isRemoved())throw new IllegalStateException("Original destination body is not loaded");
  var center=body.getPlot().getCenterBlock();var pos=new BlockPos(Math.addExact(center.getX(),ref.x()),Math.addExact(center.getY(),ref.y()),Math.addExact(center.getZ(),ref.z()));
  var be=loadedDock(level,pos);
  if(Sable.HELPER.getContaining(be)!=body||!be.getPersistentData().getString(KEY).equals(ref.encode())
    ||!be.getBlockState().getValue(BlockStateProperties.FACING).name().equals(ref.facing().name()))throw new IllegalStateException("Destination dock identity or orientation changed");
  return new Resolved(ref,body,pos,be);
 }
}
