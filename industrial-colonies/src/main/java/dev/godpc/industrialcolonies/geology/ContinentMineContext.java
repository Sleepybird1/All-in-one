package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.function.Supplier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.structure.Structure;

/** A scoped immutable admission frame for the synchronous native structure-start call only. */
public final class ContinentMineContext {
 private record Frame(ServerLevel level,List<MiningScanScope> scopes,boolean scheduled){}
 private static final ThreadLocal<Frame> CURRENT=new ThreadLocal<>();
 private ContinentMineContext(){}
 public static <T> T run(ServerLevel level,List<MiningScanScope> scopes,Supplier<T> generation){
  if(!level.getServer().isSameThread()||CURRENT.get()!=null)throw new IllegalStateException("Fresh server-thread structure admission required");
  if(!level.dimension().location().toString().equals("minecraft:overworld"))throw new IllegalArgumentException("Earth-only continent admission");
  var accepted=ContinentMineshafts.validatedAcrossContinents(scopes,level.getSeed(),level.getMinBuildHeight(),level.getMaxBuildHeight());
  CURRENT.set(new Frame(level,accepted,false));try{return Objects.requireNonNull(generation).get();}finally{CURRENT.remove();}
 }
 /** Only a scope already admitted by the current fresh native owner may be scheduled. */
 static <T>T scheduled(ServerLevel level,MiningScanScope scope,Supplier<T> generation){
  var previous=CURRENT.get();
  if(previous==null||previous.level()!=level||previous.scheduled()||!previous.scopes().contains(scope)||!level.getServer().isSameThread())throw new IllegalStateException("Existing exact owner admission required for scheduled mine");
  CURRENT.set(new Frame(level,List.of(scope),true));try{return Objects.requireNonNull(generation).get();}finally{CURRENT.set(previous);}
 }
 public static boolean scheduled(Structure.GenerationContext context){current(context).orElseThrow();return CURRENT.get().scheduled();}
 public static Optional<List<MiningScanScope>> current(Structure.GenerationContext context){
  var frame=CURRENT.get();if(frame==null)return Optional.empty();var level=frame.level();
  if(!level.getServer().isSameThread()||context.seed()!=level.getSeed()||context.randomState()!=level.getChunkSource().randomState()
      ||context.heightAccessor().getMinBuildHeight()!=level.getMinBuildHeight()||context.heightAccessor().getMaxBuildHeight()!=level.getMaxBuildHeight())throw new IllegalStateException("Structure context does not match admitted native world");
  return Optional.of(frame.scopes());
 }
}
