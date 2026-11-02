package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.enemy.NativeBossConstituentReader.*;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.server.level.ServerLevel;
import rbasamoyai.createbigcannons.cannon_control.cannon_mount.CannonMountBlockEntity;
import rbasamoyai.createbigcannons.cannon_control.contraption.*;
import java.util.*;

/** Structural witness for one native mount-break bracket. Not durable authority,
 * not inventory custody and not proof that an absent gun was destroyed. Capture
 * before mutation; a coordinator must persist intent before allowing the call. */
public final class NativeBossPendingMountBreak {
 private final UUID encounter,authority;
 private final ServerLevel level;
 private final Map<UUID,ServerSubLevel> bodies;
 private final Map<String,Part> parts;
 private final String mountName;
 private final HullCell mountCell;
 private final CannonMountBlockEntity mount;
 private final PitchOrientedContraptionEntity entity;
 private final MountedAutocannonContraption cannon;
 private final Set<String> gunParts;
 private final long tick,revision;
 private boolean consumed,held;
 private NativeBossDisassemblyObservation placement;

 private NativeBossPendingMountBreak(UUID encounter,UUID authority,ServerLevel level,
       Map<UUID,ServerSubLevel> bodies,long revision,Map<String,Part> parts,String mountName,
       HullCell cell,PitchOrientedContraptionEntity entity,MountedAutocannonContraption cannon,Set<String> gunParts){
  this.encounter=encounter;this.authority=authority;this.level=level;this.bodies=Map.copyOf(bodies);
  this.revision=revision;this.parts=Map.copyOf(parts);this.mountName=mountName;mountCell=cell;
  this.entity=entity;this.cannon=cannon;this.gunParts=Set.copyOf(gunParts);tick=level.getGameTime();
  mount=(CannonMountBlockEntity)level.getBlockEntity(cell.position());
 }
 public static NativeBossPendingMountBreak capture(UUID encounter,UUID authority,ServerLevel level,
       Map<UUID,ServerSubLevel> bodies,long revision,Map<String,Part> parts,String mountName){
  if(!new NativeBossConstituentReader(encounter,authority,level,bodies,revision,parts).observe(true).completeCustody())
   throw new IllegalStateException("Complete pre-break custody required");
  var part=Objects.requireNonNull(parts.get(mountName));
  if(!(part.address() instanceof HullCell cell)||!(level.getBlockEntity(cell.position()) instanceof CannonMountBlockEntity mount)
      ||!mount.isRunning()||mount.getContraption()==null)
   throw new IllegalStateException("Commissioned running mount required");
  var entity=mount.getContraption();
  if(!(entity.getContraption() instanceof MountedAutocannonContraption cannon))throw new IllegalStateException("Autocannon required");
  var names=new HashSet<String>();var local=new HashSet<net.minecraft.core.BlockPos>();
  for(var entry:parts.entrySet())if(entry.getValue().address() instanceof MountedCell m&&m.entity().equals(entity.getUUID())){
   if(!m.body().equals(cell.body())||!m.mount().equals(cell.position()))throw new IllegalStateException("Foreign mounted constituent");
   names.add(entry.getKey());local.add(m.local());
  }
  if(names.isEmpty()||!local.equals(cannon.getBlocks().keySet()))throw new IllegalStateException("Complete commissioned gun required");
  return new NativeBossPendingMountBreak(encounter,authority,level,bodies,revision,parts,mountName,cell,entity,cannon,names);
 }
 private void current(){
  if(held||consumed||!level.getServer().isSameThread()||level.getGameTime()!=tick)
   throw new IllegalStateException("Pending mount witness unavailable");
  var body=bodies.get(mountCell.body());
  if(body==null||body.isRemoved()||body.getLevel()!=level||!level.hasChunkAt(mountCell.position())
      ||Sable.HELPER.getContaining(level,mountCell.position())!=body)
   throw new IllegalStateException("Mount body custody unavailable");
 }
 /** Only the captured mount/controller relationship may be in removal. Every
  * gun cell must still belong to the very same registered entity and contraption. */
 public void verifyDuring(PitchOrientedContraptionEntity observed){
  try {
   current();
   var mountState=level.getBlockState(mountCell.position());var mountBE=level.getBlockEntity(mountCell.position());
   if(!mountState.isAir()&&!mountState.equals(parts.get(mountName).expected())||mountBE!=null&&mountBE!=mount)
    throw new IllegalStateException("Mount replaced during removal");
   if(observed!=entity||entity.isRemoved()||entity.level()!=level||level.getEntity(entity.getUUID())!=entity
       ||entity.getContraption()!=cannon||!entity.getPassengers().isEmpty())throw new IllegalStateException("Captured cannon changed");
   var others=new HashMap<>(parts);others.remove(mountName);gunParts.forEach(others::remove);
   intact(others);
   var local=new HashSet<net.minecraft.core.BlockPos>();
   for(var name:gunParts){
    var part=parts.get(name);var cell=(MountedCell)part.address();local.add(cell.local());
    var block=cannon.getBlocks().get(cell.local());
    if(block==null||!block.state().equals(part.expected()))throw new IllegalStateException("Captured gun cell changed");
    var be=cannon.presentBlockEntities.get(cell.local());
    if(part.expected().hasBlockEntity()&&(be==null||be.isRemoved()||!be.getBlockState().equals(part.expected()))
        ||!part.expected().hasBlockEntity()&&be!=null)throw new IllegalStateException("Captured gun machine changed");
   }
   if(!local.equals(cannon.getBlocks().keySet()))throw new IllegalStateException("Gun membership changed");
  }catch(RuntimeException failure){held=true;throw failure;}
 }
 public void verifyBinding(UUID encounter,UUID authority,PitchOrientedContraptionEntity entity,
       Map<UUID,ServerSubLevel> bodies,long revision,Map<String,Part> parts){
  current();
  if(!this.encounter.equals(encounter)||!this.authority.equals(authority)||this.entity!=entity
      ||this.revision!=revision||!this.bodies.equals(bodies)||!this.parts.equals(parts))
   throw new IllegalStateException("Foreign pending mount scope");
 }
 /** Hook must pass the transform from the actual addBlocksToWorld call. */
 public void capturePlacement(PitchOrientedContraptionEntity observed,com.simibubi.create.content.contraptions.StructureTransform transform){
  try {
   current();if(placement!=null||observed!=entity)throw new IllegalStateException("Duplicate or foreign placement");
   placement=NativeBossDisassemblyObservation.beforePending(encounter,authority,entity,transform,bodies,revision,parts,this);
  }catch(RuntimeException failure){held=true;throw failure;}
 }
 /** Call only after the outer native break returns. No caller-supplied mapping
  * is accepted: destinations come from the captured placement observation. */
 public Map<String,Part> finish(boolean nativeSuccess){
  try {
   current();consumed=true;
   if(!nativeSuccess||placement==null)throw new IllegalStateException("Missing successful break or placement witness");
   var mapped=placement.after();
   if(!nativeSuccess||!entity.isRemoved()||!level.getBlockState(mountCell.position()).isAir()
       ||level.getBlockEntity(mountCell.position())!=null||!mapped.keySet().equals(parts.keySet()))
    throw new IllegalStateException("Outer mount break unproven");
   for(var entry:parts.entrySet()){
    var next=mapped.get(entry.getKey());
    if(gunParts.contains(entry.getKey())){
     if(!(next.address() instanceof HullCell))throw new IllegalStateException("Gun not relocated to hull");
    }else if(!next.equals(entry.getValue()))throw new IllegalStateException("Unrelated manifest changed");
   }
   var survivors=new HashMap<>(mapped);survivors.remove(mountName);intact(survivors);
   return Map.copyOf(survivors);
  }catch(RuntimeException failure){held=true;throw failure;}
 }
 private void intact(Map<String,Part> manifest){
  if(!manifest.isEmpty()&&!new NativeBossConstituentReader(encounter,authority,level,bodies,revision,manifest).observe(true).completeCustody())
   throw new IllegalStateException("Surviving structural custody unavailable");
 }
 public void hold(){held=true;}
 public boolean held(){return held;}
 public String mountPart(){return mountName;}
}
