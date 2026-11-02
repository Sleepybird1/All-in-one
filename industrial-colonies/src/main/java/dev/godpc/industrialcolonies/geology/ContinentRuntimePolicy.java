package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Immutable, explicit optional-resource proposal binding; does not enable generation. */
public final class ContinentRuntimePolicy {
 private final ContinentResourceCatalog catalog;
 private final ContinentResourceCatalog.Bindings bindings;
 private final GeologyConfig.Config config;
 private final int spacing;private final String fingerprint;
 private ContinentRuntimePolicy(byte[] catalogBytes,byte[] bindingBytes,GeologyConfig.Config supplied,Set<String> registered){
  Objects.requireNonNull(catalogBytes);Objects.requireNonNull(bindingBytes);Objects.requireNonNull(supplied);
  if(catalogBytes.length<1||catalogBytes.length>4194304||bindingBytes.length<1||bindingBytes.length>4194304)throw new IllegalArgumentException("Bounded policy source required");
  config=new GeologyConfig.Config(supplied.settings().deepCopy(),supplied.biomes().deepCopy(),supplied.deposits().deepCopy());
  if(!GeologyConfig.bool(config.settings(),"enabled",true)||MassiveDeposits.enabled(config))throw new IllegalArgumentException("Enabled finite geology without competing massive ownership required");
  var expected=new TreeSet<String>();
  for(var row:config.deposits().getAsJsonArray("deposits"))if(!expected.add(row.getAsJsonObject().get("id").getAsString()))throw new IllegalArgumentException("Duplicate geology family");
  expected.removeAll(Set.of("coal","cinnabar"));
  if(WorldStartVeridiumPolicy.enabled(config)){WorldStartVeridiumPolicy.validate(config);expected.remove(WorldStartVeridiumPolicy.FAMILY);}
  catalog=ContinentResourceCatalog.read(JsonParser.parseString(new String(catalogBytes,StandardCharsets.UTF_8)).getAsJsonObject(),expected);
  var json=JsonParser.parseString(new String(bindingBytes,StandardCharsets.UTF_8)).getAsJsonObject();
  bindings=catalog.readBindings(json,hash(catalogBytes),Set.copyOf(registered));
  spacing=json.get("proposedMinimumSpacing").getAsBigDecimal().intValueExact();new ContinentSpacing(spacing,List.of());
  fingerprint=hash("IC_CONTINENT_RUNTIME_POLICY_V1".getBytes(StandardCharsets.UTF_8),catalogBytes,bindingBytes,config.toString().getBytes(StandardCharsets.UTF_8));
 }
 public static ContinentRuntimePolicy read(byte[] catalogBytes,byte[] bindingBytes,GeologyConfig.Config config,Set<String> registered){return new ContinentRuntimePolicy(catalogBytes,bindingBytes,config,registered);}
 public void check(GeologyConfig.Config current){if(!config.equals(current))throw new IllegalStateException("Commissioned geology configuration changed");}
 public int spacing(){return spacing;}public String fingerprint(){return fingerprint;}
 public Set<String> familyIds(){
  if(!WorldStartVeridiumPolicy.enabled(config))return catalog.familyIds();
  var ids=new HashSet<>(catalog.familyIds());ids.add(WorldStartVeridiumPolicy.FAMILY);return Set.copyOf(ids);
 }
 public List<NativeContinentCoordinator.Family> families(long seed,String dimension,String preset,ReTerraForgedGeography.ContinentKey continent){
  var scope=new ContinentResourceDecision.Scope(seed,dimension,preset);
  var families=new ArrayList<>(NativeContinentCoordinator.catalogFamilies(catalog,scope,continent,bindings.chances(),bindings.initialHeights()));
  if(WorldStartVeridiumPolicy.enabled(config))WorldStartVeridiumPolicy.family(seed,dimension,preset,continent).ifPresent(families::add);
  return List.copyOf(families);
 }
 private static String hash(byte[]... fields){
  try{var digest=MessageDigest.getInstance("SHA-256");
   // Catalog source binding uses plain SHA256. Composite policy fields are length-prefixed.
   for(var field:fields){if(fields.length>1)digest.update(ByteBuffer.allocate(4).putInt(field.length).array());digest.update(field);}
   return HexFormat.of().formatHex(digest.digest());
  }catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
 }
}
