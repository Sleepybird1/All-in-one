package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.*;
import net.minecraft.world.entity.Entity;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Read-only, explicit CBC attachment census. Not part of the accepted roster
 * schema until native same-tick and restart qualification. Full contraption NBT
 * is retained; no cooldown, inventory, orientation or unknown field is omitted.
 * Other mounted entity types and passengers are not certified by this reader. */
public final class EnemyMountedCannonCustody {
 private EnemyMountedCannonCustody(){}
 public record Attachment(BlockPos mount,UUID entity,int blocks,String digest){}
 public record Snapshot(UUID body,List<Attachment> attachments){
  public Snapshot {attachments=List.copyOf(attachments);}
 }
 public static Snapshot read(ServerSubLevel body)throws IOException {
  return read(body,false);
 }
 /** Held restart may never admit a saved native automatic firing setting. */
 public static Snapshot readHeld(ServerSubLevel body)throws IOException {
  return read(body,true);
 }
 private static Snapshot read(ServerSubLevel body,boolean held)throws IOException {
  if(body==null||body.isRemoved()||!body.getLevel().getServer().isSameThread())throw new IOException("Live same-thread body required");
  EnemyHullIdentity.read(body);
  var level=body.getLevel();var bounds=body.getPlot().getBoundingBox();
  if(bounds==null)throw new IOException("Missing native body bounds");
  long x=(long)bounds.maxX()-bounds.minX()+1,y=(long)bounds.maxY()-bounds.minY()+1,z=(long)bounds.maxZ()-bounds.minZ()+1;
  if(x<1||y<1||z<1||x>256||y>256||z>256||x*y*z>65536)throw new IOException("Complete bounded attachment census required");
  var entries=new ArrayList<Attachment>();var ids=new HashSet<UUID>();
  for(var pos:BlockPos.betweenClosed(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX(),bounds.maxY(),bounds.maxZ())){
   if(!level.hasChunkAt(pos))throw new IOException("Attachment plot not loaded");
   var state=level.getBlockState(pos);var be=level.getBlockEntity(pos);
   if(state.hasBlockEntity()&&be==null)throw new IOException("Expected native block entity absent");
   if(be==null||!be.getClass().getName().equals("rbasamoyai.createbigcannons.cannon_control.cannon_mount.CannonMountBlockEntity"))continue;
   if(be.isRemoved()||Sable.HELPER.getContaining(be)!=body)throw new IOException("Mount body custody changed");
   try {
    Object mounted=be.getClass().getMethod("getContraption").invoke(be);
    boolean running=Boolean.TRUE.equals(be.getClass().getMethod("isRunning").invoke(be));
    if(mounted==null&&!running)continue;
    if(!running||!(mounted instanceof Entity entity)||entity.isRemoved()||entity.level()!=level
       ||level.getEntity(entity.getUUID())!=entity||!entity.getPassengers().isEmpty()
       ||!ids.add(entity.getUUID())||entries.size()>=64)throw new IOException("Unknown, duplicate or occupied native attachment");
    if(mounted.getClass().getMethod("getController").invoke(mounted)!=be)throw new IOException("Native reciprocal mount controller changed");
    Object cannon=mounted.getClass().getMethod("getContraption").invoke(mounted);
    if(cannon==null||!cannon.getClass().getName().equals("rbasamoyai.createbigcannons.cannon_control.contraption.MountedAutocannonContraption"))throw new IOException("Unsupported mounted cannon type");
    var blocks=(Map<?,?>)cannon.getClass().getMethod("getBlocks").invoke(cannon);
    if(blocks.isEmpty()||blocks.size()>256)throw new IOException("Invalid complete native cannon blocks");
    if(held){
     var entities=(Map<?,?>)cannon.getClass().getField("presentBlockEntities").get(cannon);
     Object start=cannon.getClass().getMethod("getStartPos").invoke(cannon);
     Object breech=entities.get(start);
     if(breech==null||!Integer.valueOf(0).equals(breech.getClass().getMethod("getFireRate").invoke(breech)))
      throw new IOException("Native mounted cannon is not explicitly disarmed");
    }
    Object value=cannon.getClass().getMethod("writeNBT",HolderLookup.Provider.class,boolean.class).invoke(cannon,level.registryAccess(),false);
    if(!(value instanceof CompoundTag nbt))throw new IOException("Native contraption NBT unavailable");
    entries.add(new Attachment(pos.immutable(),entity.getUUID(),blocks.size(),digest(nbt)));
   }catch(ReflectiveOperationException|RuntimeException invalid){throw new IOException("Optional native attachment audit unavailable",invalid);}
  }
  entries.sort(Comparator.comparing(e->e.mount().toShortString()));
  return new Snapshot(body.getUniqueId(),entries);
 }
 private static String digest(CompoundTag tag)throws IOException {
  try{var digest=MessageDigest.getInstance("SHA-256");var bytes=new ByteArrayOutputStream();
   try(var out=new DataOutputStream(bytes)){text(out,"IC_MOUNTED_AUTOCANNON_FULL_NBT_V1");canonical(out,tag,0,bytes);}
   return HexFormat.of().formatHex(digest.digest(bytes.toByteArray()));
  }catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 private static void canonical(DataOutputStream out,Tag tag,int depth,ByteArrayOutputStream bytes)throws IOException {
  if(tag==null||depth>64||bytes.size()>8*1024*1024)throw new IOException("Native attachment data exceeds bounded audit");
  out.writeByte(tag.getId());
  if(tag instanceof CompoundTag compound){var keys=compound.getAllKeys().stream().sorted().toList();out.writeInt(keys.size());for(var key:keys){text(out,key);canonical(out,compound.get(key),depth+1,bytes);}}
  else if(tag instanceof ListTag list){out.writeInt(list.size());for(var child:list)canonical(out,child,depth+1,bytes);}
  else text(out,tag.toString());
  if(bytes.size()>8*1024*1024)throw new IOException("Native attachment data exceeds bounded audit");
 }
 private static void text(DataOutputStream out,String value)throws IOException {
  byte[] encoded=value.getBytes(StandardCharsets.UTF_8);if(encoded.length>8*1024*1024)throw new IOException("Oversized native field");out.writeInt(encoded.length);out.write(encoded);
 }
}
