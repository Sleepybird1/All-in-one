package dev.godpc.industrialcolonies.space.enemy;
import dev.godpc.industrialcolonies.space.AutonomousShipControl;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import java.util.*;

/** Explicitly started, finite staging-prototype batch. Never self-registers or
 * restores running authority. One bounded placement attempt per cadence; held
 * survivors retain all budget. No body/cargo deletion or automatic retry. */
public final class EnemySpawnScheduler {
 private final ServerLevel level;private final List<BlockPos> places;private final Set<String> dimensions;
 private final EnemyEncounterBudget budget;private final int cadence;
 private long lastTick,nextAt;private int index,attempts;private boolean held=true;private String reason="NOT_STARTED";
 private EnemySpawnScheduler(ServerLevel level,List<BlockPos> places,Set<String> dimensions,EnemyEncounterBudget budget,int cadence){
  this.level=Objects.requireNonNull(level);this.places=places.stream().map(BlockPos::immutable).toList();this.dimensions=Set.copyOf(dimensions);this.budget=Objects.requireNonNull(budget);this.cadence=cadence;
 }
 public static EnemySpawnScheduler start(ServerLevel level,List<BlockPos> places,Set<String> dimensions,EnemyEncounterBudget budget,int cadence){
  if(!level.getServer().isSameThread()||places==null||places.isEmpty()||places.size()>32||cadence<20||cadence>72000)throw new IllegalArgumentException("Bounded server-owned spawn batch required");
  var result=new EnemySpawnScheduler(level,places,dimensions,budget,cadence);result.lastTick=level.getGameTime();result.nextAt=result.lastTick;
  if(AutonomousShipControl.get(level.getServer()).allDisabled())result.reason="GLOBAL_DISABLED";else{result.held=false;result.reason="RUNNING";}
  return result;
 }
 public Optional<EnemyPrototypeSpawner.Result> tick(){
  if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread scheduler required");
  if(held)return Optional.empty();long now=level.getGameTime();
  if(now<lastTick||now-lastTick>2){stop("STALE_CLOCK");return Optional.empty();}
  if(now==lastTick)return Optional.empty();lastTick=now;
  if(now<0||now>Long.MAX_VALUE-cadence){stop("CLOCK_LIMIT");return Optional.empty();}
  if(AutonomousShipControl.get(level.getServer()).allDisabled()){stop("GLOBAL_DISABLED");return Optional.empty();}
  if(now<nextAt)return Optional.empty();attempts++;nextAt=now+cadence;
  var spawned=EnemyPrototypeSpawner.spawn(level,places.get(index),UUID.randomUUID(),dimensions,budget);
  if(!spawned.admitted())stop(spawned.reason());else if(++index==places.size())stop("BATCH_COMPLETE");
  return Optional.of(spawned);
 }
 public void stop(String why){if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread stop required");held=true;reason=Objects.requireNonNull(why);}
 public boolean held(){return held;}public String reason(){return reason;}public int attempts(){return attempts;}public int spawned(){return index;}
}
