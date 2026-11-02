package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.storage.LevelResource;

/** Explicit world-start commissioning for the selected optional-mineral catalog.
 * Coal, cinnabar and oil retain their separate policies. No old journal is repaired or reset. */
public final class WorldStartOreRuntime {
 private WorldStartOreRuntime(){}
 public static boolean enabled(){
  return GeologyConfig.bool(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartResources"),"enabled",false);
 }
 public static String presetFingerprint(ServerLevel level){
  return WorldStartPresetIdentity.fingerprint(level);
 }
 private static byte[] source(String name)throws IOException{
  Path path=GeologyConfig.directory().resolve(name);
  if(!Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS)||Files.size(path)<1||Files.size(path)>4194304)
   throw new IOException("Missing or unbounded selected resource policy: "+name);
  return Files.readAllBytes(path);
 }
 public static void load(ServerLevel level){
  // Superflat has no ReTerraForged context or continent-based ore ownership.
  if(level.getChunkSource().getGenerator() instanceof net.minecraft.world.level.levelgen.FlatLevelSource)return;
  if(!enabled()||!level.dimension().location().toString().equals("minecraft:overworld"))return;
  if(!level.getServer().isSameThread())throw new IllegalStateException("Server-thread resource commissioning required");
  if(NativeContinentLevels.find(level).isPresent())throw new IllegalStateException("Resource runtime already commissioned");
  try{
   // Qualify the installed geometry contract before granting replacement ownership.
   ReTerraForgedContinentEnvelope.read(level.getChunkSource().randomState());
   var registered=new HashSet<String>();
   level.registryAccess().registryOrThrow(Registries.BIOME).keySet().forEach(id->registered.add(id.toString()));
   var policy=ContinentRuntimePolicy.read(source("world_start_resource_catalog.json"),source("world_start_biome_bindings.json"),GeologyConfig.get(),registered);
   var parent=level.getServer().getWorldPath(LevelResource.ROOT).resolve("data/industrial_colonies").toAbsolutePath().normalize();
   Files.createDirectories(parent);
   var root=parent.resolve("world-start-optional-minerals-v1");
   var mode=Files.exists(root,LinkOption.NOFOLLOW_LINKS)?NativeContinentLevels.Mode.OPEN:NativeContinentLevels.Mode.CREATE;
   boolean hasCatalog=Files.exists(GeologyConfig.directory().resolve("new_continent_resource_catalog.json"),LinkOption.NOFOLLOW_LINKS);
   boolean hasBindings=Files.exists(GeologyConfig.directory().resolve("new_continent_biome_bindings.json"),LinkOption.NOFOLLOW_LINKS);
   if(hasCatalog!=hasBindings)throw new IOException("Incomplete new-continent rollout policy");
   if(hasCatalog){
    var rollout=ContinentRuntimePolicy.read(source("new_continent_resource_catalog.json"),source("new_continent_biome_bindings.json"),GeologyConfig.get(),registered);
    NativeContinentLevels.bindWithRollout(level,root,presetFingerprint(level),policy,mode,8,rollout);
   }else NativeContinentLevels.bind(level,root,presetFingerprint(level),policy,mode,8);
  }catch(IOException e){throw new IllegalStateException("World-start resource commissioning refused",e);}
 }
}
