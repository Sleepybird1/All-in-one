package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import com.mojang.serialization.Codec;
import com.mojang.serialization.JsonOps;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;
import net.minecraft.resources.RegistryOps;
import net.minecraft.server.level.ServerLevel;

/** Canonical configured-preset identity. Does not hash reflective runtime caches or map iteration order. */
public final class WorldStartPresetIdentity {
 private WorldStartPresetIdentity(){}
 public static JsonElement canonical(JsonElement source){
  if(source.isJsonObject()){
   var result=new JsonObject();var object=source.getAsJsonObject();
   for(String name:new TreeSet<>(object.keySet()))result.add(name,canonical(object.get(name)));
   return result;
  }
  if(source.isJsonArray()){
   var result=new JsonArray();for(var item:source.getAsJsonArray())result.add(canonical(item));return result;
  }
  return source.deepCopy();
 }
 public static JsonElement configured(ServerLevel level){
  try{
   var api=Class.forName("raccoonman.reterraforged.world.worldgen.RTFRandomState");var state=level.getChunkSource().randomState();
   if(!api.isInstance(state))throw new IllegalStateException("Actual native terrain required");
   var context=api.getMethod("generatorContext").invoke(state);var preset=context.getClass().getField("preset").get(context);
   @SuppressWarnings("unchecked") var codec=(Codec<Object>)preset.getClass().getField("DIRECT_CODEC").get(null);
   return canonical(codec.encodeStart(RegistryOps.create(JsonOps.INSTANCE,level.registryAccess()),preset).getOrThrow());
  }catch(ReflectiveOperationException e){throw new IllegalStateException("Native configured-preset codec unavailable",e);}
 }
 public static String fingerprint(ServerLevel level){
  try{
   String text="IC_WORLD_START_NATIVE_PRESET_V1\n"+configured(level);
   return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8)));
  }catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
 }
}
