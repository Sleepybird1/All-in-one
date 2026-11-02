package dev.godpc.industrialcolonies.space.enemy;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.storage.LevelResource;
import java.io.IOException;
import java.nio.file.Path;

/** Native save-location/claimant binding, not a defeat or loot authority adapter.
 * Raw file APIs remain useful for offline tests; native callers use this store.
 * Existing external lab records are never moved or silently adopted. */
public final class NativeEnemyOutcomeStore {
 private NativeEnemyOutcomeStore(){}
 private static Path world(MinecraftServer server)throws IOException{
  if(server==null||!server.isSameThread())throw new IOException("Server-thread outcome store required");
  return server.getWorldPath(LevelResource.ROOT);
 }
 public static Path directory(MinecraftServer server,boolean create)throws IOException{
  var root=world(server);return EnemyOutcomeDirectory.require(root,EnemyOutcomeDirectory.expected(root),create);
 }
 public static Path requireDirectory(MinecraftServer server,Path supplied,boolean create)throws IOException{
  return EnemyOutcomeDirectory.require(world(server),supplied,create);
 }
 public static EnemyRewardDelivery reserveReward(ServerPlayer player,EnemyRewardAdmission.Evidence evidence,String plan)throws IOException{
  fixtureClaimant(player,evidence);
  return EnemyRewardDelivery.reserve(directory(player.getServer(),true),evidence,plan);
 }
 private static void fixtureClaimant(ServerPlayer player,EnemyRewardAdmission.Evidence evidence)throws IOException{
  // Supplied-evidence overload exists only for the isolated inventory fixture.
  // No production reward route may treat a caller-built record as native defeat.
  if(!Boolean.getBoolean("ic.boss.rewardProbe"))throw new IOException("Supplied reward evidence is fixture-only");
  if(player==null||player.getServer()==null||player.getServer().getPlayerList().getPlayer(player.getUUID())!=player
      ||!player.isAlive()||player.isRemoved()||evidence==null||!player.getUUID().equals(evidence.beneficiary())
      ||evidence.now()!=player.serverLevel().getGameTime())throw new IOException("Current online reward claimant required");
 }
 public static EnemyRewardDelivery reserveReward(ServerPlayer player,EnemyRewardAdmission.Evidence evidence,String plan,NativeRewardOwnership ownership)throws IOException{
  return reserveReward(player,evidence,plan,ownership,()->{});
 }
 /** Additional fixture guard; a callback is not production defeat authority. */
 @FunctionalInterface public interface FixtureCheck {void check()throws IOException;}
 public static EnemyRewardDelivery reserveReward(ServerPlayer player,EnemyRewardAdmission.Evidence evidence,String plan,NativeRewardOwnership ownership,FixtureCheck structure)throws IOException{
  fixtureClaimant(player,evidence);
  if(structure==null)throw new IOException("Structural fixture check required");
  structure.check();
  if(ownership==null)throw new IOException("Native reward ownership observation required");
  ownership.consume(evidence);
  // Remains fixture-only until the separate durable native defeat adapter is qualified.
  fixtureClaimant(player,evidence);
  return EnemyRewardDelivery.reserveGuarded(directory(player.getServer(),true),evidence,plan,()->{fixtureClaimant(player,evidence);structure.check();ownership.recheck();});
 }
}
