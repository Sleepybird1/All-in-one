package dev.godpc.industrialcolonies.space.enemy;

import com.simibubi.create.content.contraptions.StructureTransform;
import dev.godpc.industrialcolonies.space.enemy.NativeBossConstituentReader.*;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import rbasamoyai.createbigcannons.cannon_control.contraption.PitchOrientedContraptionEntity;
import rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption;
import java.util.*;

/** Read-only conversion witness. Capture at the actual addBlocksToWorld call,
 * finish after outer entity disassemble returns. A discarded entity alone
 * proves nothing. No damage, inventory, journal, control or restart authority. */
public final class NativeBossDisassemblyObservation {
 private record Destination(String part,ServerSubLevel body,BlockPos position,BlockState state,NativeBossBreechContents contents){}
 private final ServerLevel level;
 private final PitchOrientedContraptionEntity entity;
 private final Map<String,Part> before;
 private final List<Destination> destinations;
 private final long tick;
 private final UUID encounter,authority;
 private final long revision;
 private final Map<UUID,ServerSubLevel> knownBodies;
 private final String pendingMount;
 private boolean consumed;
 private NativeBossDisassemblyObservation(ServerLevel level,PitchOrientedContraptionEntity entity,
       Map<String,Part> before,List<Destination> destinations,UUID encounter,UUID authority,
       long revision,Map<UUID,ServerSubLevel> knownBodies,String pendingMount){
  this.level=level;this.entity=entity;this.before=Map.copyOf(before);this.destinations=List.copyOf(destinations);tick=level.getGameTime();
  this.encounter=encounter;this.authority=authority;this.revision=revision;this.knownBodies=Map.copyOf(knownBodies);
  this.pendingMount=pendingMount;
 }
 public static NativeBossDisassemblyObservation before(UUID encounter,UUID authority,
       PitchOrientedContraptionEntity entity,StructureTransform transform,
       Map<UUID,ServerSubLevel> knownBodies,long revision,Map<String,Part> parts){
  return capture(encounter,authority,entity,transform,knownBodies,revision,parts,null);
 }
 static NativeBossDisassemblyObservation beforePending(UUID encounter,UUID authority,
       PitchOrientedContraptionEntity entity,StructureTransform transform,
       Map<UUID,ServerSubLevel> knownBodies,long revision,Map<String,Part> parts,NativeBossPendingMountBreak pending){
  pending.verifyBinding(encounter,authority,entity,knownBodies,revision,parts);
  pending.verifyDuring(entity);
  return capture(encounter,authority,entity,transform,knownBodies,revision,parts,pending.mountPart());
 }
 private static NativeBossDisassemblyObservation capture(UUID encounter,UUID authority,
       PitchOrientedContraptionEntity entity,StructureTransform transform,
       Map<UUID,ServerSubLevel> knownBodies,long revision,Map<String,Part> parts,String pendingMount){
  Objects.requireNonNull(transform);Objects.requireNonNull(entity);
  if(!(entity.level() instanceof ServerLevel level)||!level.getServer().isSameThread()||entity.isRemoved()
      ||level.getEntity(entity.getUUID())!=entity||!entity.getPassengers().isEmpty()
      ||!(entity.getContraption() instanceof MountedAutocannonContraption cannon))
   throw new IllegalStateException("Complete live native cannon required");
  if(pendingMount==null&&!new NativeBossConstituentReader(encounter,authority,level,knownBodies,revision,parts).observe(true).completeCustody())
   throw new IllegalStateException("Pre-disassembly constituent custody unavailable");
  var mapped=new ArrayList<Destination>();var positions=new HashSet<BlockPos>();var covered=new HashSet<BlockPos>();
  for(var entry:parts.entrySet()){
   if(!(entry.getValue().address() instanceof MountedCell cell)||!cell.entity().equals(entity.getUUID()))continue;
   covered.add(cell.local());var position=transform.apply(cell.local()).immutable();
   if(!positions.add(position)||!level.hasChunkAt(position)||!level.getBlockState(position).isAir()
       ||!level.getFluidState(position).isEmpty()||level.getBlockEntity(position)!=null)
    throw new IllegalStateException("Mapped destination obstructed, aliased or unavailable");
   if(!(Sable.HELPER.getContaining(level,position) instanceof ServerSubLevel destination)
       ||knownBodies.get(destination.getUniqueId())!=destination||destination.isRemoved())
    throw new IllegalStateException("Mapped destination is outside verified live lineage");
   var sourceState=entry.getValue().expected();
   // Installed CBC addBlocksToWorld clears ASSEMBLED before delegating to Create.
   var assembled=rbasamoyai.createbigcannons.cannons.autocannon.AutocannonBarrelBlock.ASSEMBLED;
   if(sourceState.hasProperty(assembled))sourceState=sourceState.setValue(assembled,false);
   var state=transform.apply(sourceState);
   if(state.isAir())throw new IllegalStateException("Transform erased a constituent");
   var sourceBE=cannon.presentBlockEntities.get(cell.local());
   var contents=sourceBE instanceof rbasamoyai.createbigcannons.cannons.autocannon.breech.AbstractAutocannonBreechBlockEntity breech
       ?NativeBossBreechContents.capture(breech):null;
   mapped.add(new Destination(entry.getKey(),destination,position,state,contents));
  }
  if(mapped.isEmpty()||!covered.equals(cannon.getBlocks().keySet()))
   throw new IllegalStateException("Every mounted cannon block must be commissioned");
  // Do not permit a new world address to alias any other commissioned hull cell.
  for(var part:parts.values())if(part.address() instanceof HullCell cell&&positions.contains(cell.position()))
   throw new IllegalStateException("Mapped address aliases existing constituent");
  return new NativeBossDisassemblyObservation(level,entity,parts,mapped,encounter,authority,revision,knownBodies,pendingMount);
 }
 public Map<String,Part> after(){
  if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");
  if(consumed)throw new IllegalStateException("Disassembly witness consumed");consumed=true;
  if(tick!=level.getGameTime()||!entity.isRemoved())throw new IllegalStateException("Native disassembly not complete in captured tick");
  var result=new HashMap<>(before);
  for(var destination:destinations){
   var p=destination.position();
   if(destination.body().isRemoved()||destination.body().getLevel()!=level||!level.hasChunkAt(p)
       ||Sable.HELPER.getContaining(level,p)!=destination.body()||!level.getBlockState(p).equals(destination.state()))
    throw new IllegalStateException("Completed destination state/custody mismatch");
   var be=level.getBlockEntity(p);
   if(destination.state().hasBlockEntity()&&(be==null||be.isRemoved()||Sable.HELPER.getContaining(be)!=destination.body())
       ||!destination.state().hasBlockEntity()&&be!=null)
    throw new IllegalStateException("Completed constituent block entity mismatch");
   if(destination.contents()!=null&&(!(be instanceof rbasamoyai.createbigcannons.cannons.autocannon.breech.AbstractAutocannonBreechBlockEntity breech)
       ||!destination.contents().matches(breech)))throw new IllegalStateException("Breech ammunition custody changed");
   result.put(destination.part(),new Part(new HullCell(destination.body().getUniqueId(),p),destination.state()));
  }
  // Native placement can invoke other block callbacks. Recheck every retained
  // constituent, not only the gun's new cells, before exposing the proposal.
  // This is still a structural witness, not inventory or durable authority.
  var surviving=new HashMap<>(result);
  if(pendingMount!=null)surviving.remove(pendingMount);
  if(!new NativeBossConstituentReader(encounter,authority,level,knownBodies,revision,surviving).observe(true).completeCustody())
   throw new IllegalStateException("Post-disassembly complete constituent custody unavailable");
  return Map.copyOf(result);
 }
}
