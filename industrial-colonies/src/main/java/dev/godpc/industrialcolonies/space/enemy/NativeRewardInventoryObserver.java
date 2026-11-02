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

/** Staged read-only observation of the beneficiary's ordinary player inventory.
 * This is not a grant, an inventory delta proof, or coverage of arbitrary mod
 * capabilities/ender storage. Rearranged or consumed rewards will remain held.
 * No registration installs this observer into production. */
public final class NativeRewardInventoryObserver implements EnemyRewardRestartAudit.Observer {
 private final ServerPlayer player;
 public NativeRewardInventoryObserver(ServerPlayer player){this.player=Objects.requireNonNull(player);}
 private void verify(EnemyRewardReservation.HeldClaim claim)throws IOException{
  var server=player.getServer();
  if(server==null||!server.isSameThread()||server.getPlayerList().getPlayer(claim.beneficiary())!=player
      ||!player.getUUID().equals(claim.beneficiary())||!player.isAlive()||player.isRemoved()
      ||player.containerMenu!=player.inventoryMenu||!player.containerMenu.getCarried().isEmpty())
   throw new IOException("Reward inventory owner unavailable or menu in use");
 }
 @Override public EnemyRewardRestartAudit.Observation observe(EnemyRewardReservation.HeldClaim claim)throws IOException{
  Objects.requireNonNull(claim);verify(claim);
  var level=player.serverLevel();long tick=level.getGameTime();var inventory=player.getInventory();
  int size=inventory.getContainerSize();if(size<1||size>128)throw new IOException("Unsupported inventory size");
  var copies=new ArrayList<ItemStack>(size);
  for(int i=0;i<size;i++)copies.add(inventory.getItem(i).copy());
  var json=new JsonObject();json.addProperty("profile","reward-player-inventory-v1");
  json.addProperty("beneficiary",player.getUUID().toString());var slots=new JsonArray();
  var ops=RegistryOps.create(JsonOps.INSTANCE,level.registryAccess());
  try {
   for(var stack:copies)slots.add(stack.isEmpty()?JsonNull.INSTANCE:ItemStack.CODEC.encodeStart(ops,stack).getOrThrow());
   json.add("slots",slots);var canonical=canonical(json,0);var bytes=canonical.toString().getBytes(StandardCharsets.UTF_8);
   if(bytes.length>1024*1024)throw new IOException("Reward inventory evidence too large");
   verify(claim);
   if(player.serverLevel()!=level||level.getGameTime()!=tick||player.getInventory()!=inventory||inventory.getContainerSize()!=size)
    throw new IOException("Reward inventory scope changed while reading");
   for(int i=0;i<size;i++)if(!ItemStack.matches(copies.get(i),inventory.getItem(i)))throw new IOException("Reward slot changed while reading");
   return new EnemyRewardRestartAudit.Observation(claim,tick,true,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
  }catch(RuntimeException failure){throw new IOException("Reward inventory encoding failed",failure);}
  catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
 }
 static JsonElement canonical(JsonElement value,int depth)throws IOException{
  if(depth>64)throw new IOException("Reward component nesting too deep");
  if(value.isJsonObject()){
   var out=new JsonObject();for(var key:new TreeSet<>(value.getAsJsonObject().keySet()))out.add(key,canonical(value.getAsJsonObject().get(key),depth+1));return out;
  }
  if(value.isJsonArray()){
   var out=new JsonArray();for(var child:value.getAsJsonArray())out.add(canonical(child,depth+1));return out;
  }
  return value.deepCopy();
 }
}
