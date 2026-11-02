package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import java.util.*;

/** Explicit chart proposal loader, never auto-registered. Missing biome decisions refuse. */
public final class ContinentResourceCatalog {
    private final Map<String, ContinentReservePolicy.Family> families;
    private final String sourceSha256;
    public record Request(ContinentReservePolicy.Selection reserve, ContinentReservePolicy.BiomeChances chances) {}
    public record Bindings(Map<String,ContinentReservePolicy.BiomeChances> chances,Map<String,Integer> initialHeights) {
        public Bindings {chances=Map.copyOf(chances);initialHeights=Map.copyOf(initialHeights);}
    }
    private ContinentResourceCatalog(Map<String, ContinentReservePolicy.Family> families, String sourceSha256) {
        this.families = Collections.unmodifiableMap(new TreeMap<>(families)); this.sourceSha256 = sourceSha256;
    }
    public static ContinentResourceCatalog read(JsonObject json, Set<String> expectedOptionalFamilies) {
        if (!"continent-resource-catalog-v1".equals(json.get("schema").getAsString())
                || !"PROPOSAL_NOT_INSTALLED".equals(json.get("status").getAsString()))
            throw new IllegalArgumentException("Explicit staged catalog required");
        String hash = json.get("chartSHA256").getAsString();
        if (!hash.matches("[0-9a-f]{64}")) throw new IllegalArgumentException("Chart fingerprint required");
        Map<String, ContinentReservePolicy.Family> families = new TreeMap<>();
        for (JsonElement row : json.getAsJsonArray("families")) {
            var r = row.getAsJsonObject(); String id = r.get("family").getAsString();
            var tiers = new ArrayList<ContinentReservePolicy.Tier>();
            for (JsonElement tier : r.getAsJsonArray("tiers")) {
                var t = tier.getAsJsonObject();
                tiers.add(new ContinentReservePolicy.Tier(t.get("oreBlocks").getAsBigDecimal().intValueExact(),
                        t.get("weightPercent").getAsBigDecimal().intValueExact()));
            }
            if (families.put(id, new ContinentReservePolicy.Family(id, tiers)) != null)
                throw new IllegalArgumentException("Duplicate family");
        }
        if (families.isEmpty() || families.size() > 128 || !families.keySet().equals(expectedOptionalFamilies))
            throw new IllegalArgumentException("Catalog must exactly cover declared optional families");
        return new ContinentResourceCatalog(families, hash);
    }
    public Set<String> familyIds() { return families.keySet(); }
    public String chartSha256() { return sourceSha256; }
    /** Exact source bytes and actual registry IDs are required; no unknown biome is silently dropped. */
    public Bindings readBindings(JsonObject json,String catalogBytesSha256,Set<String> registeredBiomes) {
        if(!"continent-biome-bindings-v1".equals(json.get("schema").getAsString())
                ||!"PROPOSAL_NOT_INSTALLED".equals(json.get("status").getAsString())
                ||catalogBytesSha256==null||!catalogBytesSha256.matches("[0-9a-f]{64}")
                ||!catalogBytesSha256.equals(json.get("catalogSHA256").getAsString()))
            throw new IllegalArgumentException("Bindings require exact catalog and proposal schema");
        var registry=Set.copyOf(registeredBiomes);var chances=new TreeMap<String,ContinentReservePolicy.BiomeChances>();var heights=new TreeMap<String,Integer>();
        for(var element:json.getAsJsonArray("families")) {
            var row=element.getAsJsonObject();String id=row.get("family").getAsString();
            var values=new TreeMap<String,Double>();
            for(var entry:row.getAsJsonObject("biomeChances").entrySet()) {
                if(!registry.contains(entry.getKey()))throw new IllegalArgumentException("Unregistered biome "+entry.getKey());
                values.put(entry.getKey(),entry.getValue().getAsDouble());
            }
            if(chances.put(id,new ContinentReservePolicy.BiomeChances(values))!=null)throw new IllegalArgumentException("Duplicate binding family");
            int y=row.get("initialY").getAsBigDecimal().intValueExact();
            if(y< -2048||y>=2032)throw new IllegalArgumentException("Initial height outside supported bounds");
            heights.put(id,y);
        }
        if(!chances.keySet().equals(families.keySet()))throw new IllegalArgumentException("Bindings must cover all optional families exactly");
        return new Bindings(chances,heights);
    }
    public String policySha256() {
        try {
            return HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(
                    ("continent-resource-catalog/v1\n"+sourceSha256+"\n"+families).getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        } catch(java.security.NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
    public List<Request> requests(ContinentResourceDecision.Scope scope, ReTerraForgedGeography.ContinentKey continent,
            Map<String, ContinentReservePolicy.BiomeChances> reviewedChances) {
        var snapshot = Map.copyOf(reviewedChances);
        if (!snapshot.keySet().equals(families.keySet()))
            throw new IllegalArgumentException("Exact biome probabilities required for every optional family");
        return families.values().stream().map(f -> new Request(f.select(scope, continent), snapshot.get(f.id()))).toList();
    }
}
