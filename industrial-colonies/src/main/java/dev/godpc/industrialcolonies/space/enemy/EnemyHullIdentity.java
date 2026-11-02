package dev.godpc.industrialcolonies.space.enemy;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.nbt.CompoundTag;
import java.util.UUID;

/** Trusted commissioning metadata, bound to physical UUID. Copied fragment tags
 * confer no controller authority. No automatic commissioning or spawn hook. */
public final class EnemyHullIdentity {
 public static final String KEY="IndustrialColoniesEnemyHullV1";
 public record Identity(UUID encounter, UUID root, boolean originalBody) {}
 private EnemyHullIdentity(){}
 private static void thread(ServerSubLevel b){if(!b.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread identity required");}
 public static void commission(ServerSubLevel body, UUID encounter){
  thread(body);if(body.isRemoved()||encounter==null||EnemyCaptureHold.inhibits(body.getUserDataTag())||(body.getUserDataTag()!=null&&body.getUserDataTag().contains(KEY)))throw new IllegalStateException("Fresh explicit NPC commission required");
  if(body.getUserDataTag()==null)body.setUserDataTag(new CompoundTag());
  var tag=new CompoundTag();tag.putUUID("Encounter",encounter);tag.putUUID("Root",body.getUniqueId());
  body.getUserDataTag().put(KEY,tag);
 }
 public static Identity read(ServerSubLevel body){
  thread(body);if(body.isRemoved()||body.getUserDataTag()==null||!body.getUserDataTag().contains(KEY,10))throw new IllegalStateException("No valid NPC commission");
  var tag=body.getUserDataTag().getCompound(KEY);
  if(!tag.hasUUID("Encounter")||!tag.hasUUID("Root")||tag.getAllKeys().size()!=2)throw new IllegalStateException("Malformed NPC commission");
  var root=tag.getUUID("Root");return new Identity(tag.getUUID("Encounter"),root,root.equals(body.getUniqueId()));
 }
 public static boolean mayControl(ServerSubLevel body, NativeEnemyHull hull){
  try{return !EnemyCaptureHold.inhibits(body.getUserDataTag())&&hull!=null&&hull.belongsTo(body)&&read(body).originalBody()&&hull.validate();}catch(IllegalStateException refused){return false;}
 }
}
