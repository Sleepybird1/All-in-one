package dev.godpc.industrialcolonies.geology;

import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Explicit habitat ranks within fixed traversal windows, not another occurrence roll.
 * Rank zero is preferred. Unknown biomes are refused rather than assigned a fallback. */
public final class CoalHabitatPreference {
    private final Map<String,Integer> ranks;
    private final int window;
    private final String fingerprint;
    public CoalHabitatPreference(Map<String,Integer> ranks,int window) {
        if(window<1||window>4096||ranks.isEmpty()||ranks.size()>4096)throw new IllegalArgumentException("Coal preference requires1..4096sites and explicit biomes");
        var sorted=new TreeMap<String,Integer>();
        ranks.forEach((biome,rank)->{
            if(biome==null||!biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")||rank==null||rank<0||rank>2)
                throw new IllegalArgumentException("Coal habitat ranks must be0..2");
            sorted.put(biome,rank);
        });
        if(!sorted.containsValue(0))throw new IllegalArgumentException("At least one preferred coal habitat required");
        this.ranks=Collections.unmodifiableMap(sorted);this.window=window;
        try {fingerprint=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(
                ("IC_COAL_HABITAT_PREFERENCE_V1\n"+window+"\n"+sorted).getBytes(StandardCharsets.UTF_8)));
        }catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
    public int rank(String biome){var rank=ranks.get(biome);if(rank==null)throw new IllegalArgumentException("Unranked coal biome: "+biome);return rank;}
    public int window(){return window;}
    public Map<String,Integer> ranks(){return ranks;}
    public String fingerprint(){return fingerprint;}
}
