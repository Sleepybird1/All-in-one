package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;

/** Explicit bindings only: an unbound world keeps its existing generation. Never reads an enable flag
 * or creates policy defaults. Runtime commissioning is lazy, server-thread-only and terminal on failure. */
public final class NativeContinentLevels {
 public enum Mode { CREATE, OPEN }
 public record RecordedLookup(Path directory,ContinentResourceDecision.Scope scope) {}
 private static final Map<ServerLevel,Binding> LEVELS=new ConcurrentHashMap<>();
 private NativeContinentLevels(){}
 public static Binding bind(ServerLevel level,Path root,String preset,ContinentRuntimePolicy policy,Mode mode,int capacity){
  return bindInternal(level,root,preset,policy,mode,capacity,null);
 }
 public static Binding bindWithRollout(ServerLevel level,Path root,String preset,ContinentRuntimePolicy policy,Mode mode,int capacity,ContinentRuntimePolicy rollout){
  Objects.requireNonNull(rollout);rollout.check(GeologyConfig.get());
  if(rollout.spacing()!=policy.spacing()||!rollout.familyIds().equals(policy.familyIds()))throw new IllegalArgumentException("Rollout must retain spacing and family ownership");
  var binding=bindInternal(level,root,preset,policy,mode,capacity,null);binding.rollout=rollout;return binding;
 }
 public static Binding bindWithCoal(ServerLevel level,Path root,String preset,ContinentRuntimePolicy policy,Mode mode,int capacity,CoalRuntimePolicy coal){
  return bindInternal(level,root,preset,policy,mode,capacity,Objects.requireNonNull(coal));
 }
 private static Binding bindInternal(ServerLevel level,Path root,String preset,ContinentRuntimePolicy policy,Mode mode,int capacity,CoalRuntimePolicy coal){
  Objects.requireNonNull(level);thread(level);Objects.requireNonNull(root);Objects.requireNonNull(policy);Objects.requireNonNull(mode);
  if(!level.dimension().location().toString().equals("minecraft:overworld")||preset==null||!preset.matches("[a-f0-9]{64}")||capacity<1||capacity>64)throw new IllegalArgumentException("Explicit bounded Earth runtime binding required");
  policy.check(GeologyConfig.get());if(coal!=null)coal.checkHeight(level.getMinBuildHeight(),level.getMaxBuildHeight());
  var binding=new Binding(level,root.toAbsolutePath().normalize(),preset,policy,mode,capacity,coal);
  if(LEVELS.putIfAbsent(level,binding)!=null)throw new IllegalStateException("Native level already commissioned");return binding;
 }
 /** Safe lookup from a generation worker. It grants no access to server-thread state or journals. */
 public static Optional<Binding> find(ServerLevel level){return Optional.ofNullable(LEVELS.get(level));}
 public static Set<String> excludedFamilies(ServerLevel level){var binding=LEVELS.get(level);return binding==null?Set.of():binding.excludedFamilies();}
 private static void thread(ServerLevel level){if(!level.getServer().isSameThread())throw new IllegalStateException("Native level owner thread required");}
 public static void unload(ServerLevel level){
  // Unbound worlds are a no-op, including event threads with no commissioned state.
  var binding=LEVELS.get(level);if(binding==null)return;thread(level);
  binding.close();LEVELS.remove(level,binding);
 }
 public static void stop(MinecraftServer server){for(var level:List.copyOf(LEVELS.keySet()))if(level.getServer()==server)unload(level);}
 public static final class Binding {
  private final ServerLevel level;private final Path root;private final String preset;private final ContinentRuntimePolicy policy;private final Mode mode;private final int capacity;private final CoalRuntimePolicy coal;
  private ContinentRuntimePolicy rollout;
  private NativeContinentRuntime runtime;private volatile boolean closed,failed;private boolean opening;
  private Binding(ServerLevel level,Path root,String preset,ContinentRuntimePolicy policy,Mode mode,int capacity,CoalRuntimePolicy coal){this.level=level;this.root=root;this.preset=preset;this.policy=policy;this.mode=mode;this.capacity=capacity;this.coal=coal;}
  private Set<String> excludedFamilies(){
   if(closed||failed)throw new IllegalStateException("Continent binding unavailable; legacy fallback refused");
   policy.check(GeologyConfig.get());if(coal==null)return policy.familyIds();
   var result=new HashSet<>(policy.familyIds());result.add("coal");return Set.copyOf(result);
  }
  public Set<String> locatableFamilies(){
   thread(level);if(closed||failed)throw new IllegalStateException("Continent binding unavailable");policy.check(GeologyConfig.get());return policy.familyIds();
  }
  /** Immutable read descriptor only: never opens/commissions the generation runtime. */
  public RecordedLookup recordedLookup(){
   thread(level);if(closed||failed)throw new IllegalStateException("Continent binding unavailable");policy.check(GeologyConfig.get());
   return new RecordedLookup(root,new ContinentResourceDecision.Scope(level.getSeed(),level.dimension().location().toString(),preset));
  }
  public NativeContinentRuntime runtime()throws IOException{
   thread(level);if(closed||failed||opening)throw new IllegalStateException("Continent binding closed, failed or reentrant");
   try{
    policy.check(GeologyConfig.get());if(rollout!=null)rollout.check(GeologyConfig.get());
    if(runtime==null){
     opening=true;
     NativeContinentRuntime.Families families=key->{policy.check(GeologyConfig.get());return policy.families(level.getSeed(),level.dimension().location().toString(),preset,key);};
     if(coal==null)runtime=mode==Mode.CREATE?NativeContinentRuntime.create(root,level,preset,policy.fingerprint(),policy.spacing(),capacity,families):NativeContinentRuntime.open(root,level,preset,policy.fingerprint(),policy.spacing(),capacity,families);
     else runtime=mode==Mode.CREATE?NativeContinentRuntime.createWithCoal(root,level,preset,policy.fingerprint(),policy.spacing(),capacity,families,coal):NativeContinentRuntime.openWithCoal(root,level,preset,policy.fingerprint(),policy.spacing(),capacity,families,coal);
    }
    if(opening&&rollout!=null){
     var selectedRollout=rollout;
     runtime.configureRollout(selectedRollout.fingerprint(),key->{selectedRollout.check(GeologyConfig.get());return selectedRollout.families(level.getSeed(),level.dimension().location().toString(),preset,key);});
    }
    runtime.requireLevel(level);return runtime;
   }catch(IOException|RuntimeException|Error failure){failed=true;throw failure;}
   finally{opening=false;}
  }
  private void close(){thread(level);if(!closed){if(runtime!=null)runtime.close();closed=true;}}
 }
}
