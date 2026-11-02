package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;

/** Explicit per-vein opt-in gate. Does not schedule a mine, relax fit, create a node or alter stock. */
public final class WorldStartMinePolicy {
 private WorldStartMinePolicy(){}
 public static boolean enabled(JsonObject settings){
  if(!settings.has("worldStartMineSelection"))return false;
  var config=settings.getAsJsonObject("worldStartMineSelection");
  if(!booleanValue(config,"enabled",false))return false;
  if(!config.has("chancePerVein")||!config.get("chancePerVein").isJsonPrimitive()
    ||!config.getAsJsonPrimitive("chancePerVein").isNumber()
    ||config.get("chancePerVein").getAsBigDecimal().compareTo(new java.math.BigDecimal("0.10"))!=0)
   throw new IllegalArgumentException("Selected world-start mine chance must be 0.10");
  return true;
 }
 public static boolean allows(JsonObject settings,JsonObject definition,WorldStartAllocation.Scope scope,String veinKey){
  if(!booleanValue(definition,"canSpawnMineshaft",true))return false;
  if(!enabled(settings))return true; // Preserve existing uncommissioned worlds.
  return WorldStartAllocation.mineshaft(scope,veinKey,true);
 }
 private static boolean booleanValue(JsonObject object,String key,boolean fallback){
  if(!object.has(key))return fallback;
  if(!object.get(key).isJsonPrimitive()||!object.getAsJsonPrimitive(key).isBoolean())
   throw new IllegalArgumentException("Boolean required: "+key);
  return object.get(key).getAsBoolean();
 }
}
