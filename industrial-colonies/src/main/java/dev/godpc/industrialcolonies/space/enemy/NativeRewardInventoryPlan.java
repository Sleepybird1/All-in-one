package dev.godpc.industrialcolonies.space.enemy;

import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import net.minecraft.resources.RegistryOps;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Staged ordinary-inventory grant adapter. Prepare before reserving a claim;
 * pass deliver only to EnemyRewardDelivery.attempt. Failed partial application
 * is held by that coordinator, never rolled back or automatically retried.
 * This does not establish world-save atomicity or authorize any loot table. */
public final class NativeRewardInventoryPlan {
 private final ServerPlayer player;
 private final long tick;
 private final net.minecraft.server.level.ServerLevel level;
 private final List<ItemStack> before,after;
 private final String digest;
 private boolean consumed;
 private NativeRewardInventoryPlan(ServerPlayer p,List<ItemStack> before,List<ItemStack> after,String digest){
  player=p;level=p.serverLevel();tick=level.getGameTime();this.before=before;this.after=after;this.digest=digest;
 }
 public String rewardPlanDigest(){return digest;}
 private static void available(ServerPlayer p)throws IOException{
  var server=p.getServer();
  if(server==null||!server.isSameThread()||server.getPlayerList().getPlayer(p.getUUID())!=p
      ||!p.isAlive()||p.isRemoved()||p.containerMenu!=p.inventoryMenu||!p.containerMenu.getCarried().isEmpty()
      ||p.getInventory().getContainerSize()!=41||p.getInventory().items.size()!=36)
   throw new IOException("Ordinary recipient inventory unavailable");
 }
 private static List<ItemStack> snapshot(ServerPlayer p){
  var result=new ArrayList<ItemStack>();for(int i=0;i<41;i++)result.add(p.getInventory().getItem(i).copy());return result;
 }
 private static void matches(ServerPlayer p,List<ItemStack> expected)throws IOException{
  for(int i=0;i<41;i++)if(!ItemStack.matches(expected.get(i),p.getInventory().getItem(i)))throw new IOException("Reward inventory changed at slot "+i);
 }
 public static NativeRewardInventoryPlan prepare(ServerPlayer p,List<ItemStack> rewards)throws IOException{
  Objects.requireNonNull(p);available(p);
  if(rewards==null||rewards.isEmpty()||rewards.size()>128)throw new IOException("Invalid reward plan size");
  var level=p.serverLevel();long tick=level.getGameTime();var before=snapshot(p);
  var after=new ArrayList<ItemStack>();for(var stack:before)after.add(stack.copy());
  var encoded=new JsonArray();var ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
  try {
   for(var supplied:rewards){
    if(supplied==null||supplied.isEmpty()||supplied.getCount()<1||supplied.getCount()>4096)throw new IOException("Invalid reward stack");
    var reward=supplied.copy();encoded.add(ItemStack.CODEC.encodeStart(ops,reward).getOrThrow());int remaining=reward.getCount();
    // Main storage only. Never auto-equip armor, fill offhand, or drop overflow.
    for(int pass=0;pass<2&&remaining>0;pass++)for(int i=0;i<36&&remaining>0;i++){
     var target=after.get(i);boolean empty=target.isEmpty();
     if((pass==0&&empty)||(pass==1&&!empty)||(!empty&&!ItemStack.isSameItemSameComponents(target,reward)))continue;
     int limit=Math.min(p.getInventory().getMaxStackSize(),reward.getMaxStackSize());
     int count=empty?0:target.getCount();int add=Math.min(remaining,Math.max(0,limit-count));
     if(add>0){var updated=empty?reward.copy():target.copy();updated.setCount(count+add);after.set(i,updated);remaining-=add;}
    }
    if(remaining!=0)throw new IOException("Entire reward does not fit; no items changed");
   }
   var plan=new JsonObject();plan.addProperty("profile","reward-ordinary-inventory-plan-v1");plan.add("rewards",encoded);
   var bytes=NativeRewardInventoryObserver.canonical(plan,0).toString().getBytes(StandardCharsets.UTF_8);
   if(bytes.length>1024*1024)throw new IOException("Reward plan too large");
   available(p);if(p.serverLevel()!=level||level.getGameTime()!=tick)throw new IOException("Reward scope changed during planning");matches(p,before);
   return new NativeRewardInventoryPlan(p,before,after,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
  }catch(RuntimeException failure){throw new IOException("Reward plan encoding failed",failure);}
  catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 public synchronized EnemyRewardDelivery.Observation deliver(EnemyRewardReservation.HeldClaim claim)throws IOException{
  if(consumed)throw new IOException("Reward plan already consumed");consumed=true;
  available(player);
  if(claim==null||!player.getUUID().equals(claim.beneficiary())||!digest.equals(claim.rewardPlanDigest())
      ||player.serverLevel()!=level||level.getGameTime()!=tick)throw new IOException("Reward claim or planning scope changed");
  matches(player,before);
  for(int i=0;i<36;i++)if(!ItemStack.matches(before.get(i),after.get(i)))player.getInventory().setItem(i,after.get(i).copy());
  player.getInventory().setChanged();matches(player,after);
  var observed=new NativeRewardInventoryObserver(player).observe(claim);
  return new EnemyRewardDelivery.Observation(claim.encounter(),claim.beneficiary(),digest,observed.inventoryEvidenceDigest());
 }
}
