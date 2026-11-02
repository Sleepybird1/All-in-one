package dev.godpc.industrialcolonies.space.enemy;

import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.nbt.*;
import java.util.*;

/** Persistent hold, not completed capture. No removal or resume API. Caller
 * must first stop actuators and verify cargo; this marker does not itself drain
 * queued thrust or establish inventory/ownership transfer or save atomicity. */
public final class EnemyCaptureHold {
 public static final String KEY="IndustrialColoniesEnemyCaptureHoldV1";
 public record Record(UUID encounter,UUID root,UUID claimant,String custodyDigest){
  public Record {
   Objects.requireNonNull(encounter);Objects.requireNonNull(root);Objects.requireNonNull(claimant);
   if(custodyDigest==null||!custodyDigest.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Invalid capture custody digest");
  }
 }
 private EnemyCaptureHold(){}
 /** Unknown or malformed data must inhibit control, never be treated as absent. */
 public static boolean inhibits(CompoundTag metadata){return metadata!=null&&metadata.contains(KEY);}
 public static CompoundTag encode(Record record){
  var tag=new CompoundTag();tag.putInt("format",1);tag.putString("state","HELD");
  tag.putUUID("encounter",record.encounter());tag.putUUID("root",record.root());tag.putUUID("claimant",record.claimant());
  tag.putString("custody",record.custodyDigest());return tag;
 }
 public static Record decode(CompoundTag tag){
  if(!tag.getAllKeys().equals(Set.of("format","state","encounter","root","claimant","custody"))
      ||!tag.contains("format",Tag.TAG_INT)||tag.getInt("format")!=1
      ||!tag.contains("state",Tag.TAG_STRING)||!tag.getString("state").equals("HELD")
      ||!tag.hasUUID("encounter")||!tag.hasUUID("root")||!tag.hasUUID("claimant")||!tag.contains("custody",Tag.TAG_STRING))
   throw new IllegalArgumentException("Unknown or malformed capture hold");
  return new Record(tag.getUUID("encounter"),tag.getUUID("root"),tag.getUUID("claimant"),tag.getString("custody"));
 }
 public static void requireBinding(Record record,UUID encounter,UUID root,UUID claimant,String custodyDigest){
  if(record==null||!record.encounter().equals(encounter)||!record.root().equals(root)
      ||!record.claimant().equals(claimant)||!record.custodyDigest().equals(custodyDigest))
   throw new IllegalArgumentException("Capture hold binding changed");
 }
 public static Record beginHeld(ServerSubLevel body,UUID claimant,String custodyDigest){
  if(!body.getLevel().getServer().isSameThread())throw new IllegalStateException("Server-thread capture required");
  var identity=EnemyHullIdentity.read(body);
  if(!identity.originalBody()||inhibits(body.getUserDataTag()))throw new IllegalStateException("Fresh original capture hold required");
  var record=new Record(identity.encounter(),identity.root(),claimant,custodyDigest);
  body.getUserDataTag().put(KEY,encode(record));return record;
 }
}
