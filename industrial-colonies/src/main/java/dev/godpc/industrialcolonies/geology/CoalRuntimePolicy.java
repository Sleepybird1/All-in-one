package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;

/** Explicit proposed coal policy; no implicit biome list, supply guarantee or activation. */
public final class CoalRuntimePolicy {
    private final CoalLayoutPolicy layout;
    private final Set<String> biomes;
    private final int initialY,spacing;
    private final String fingerprint;
    private final CoalHabitatPreference preference;
    private CoalRuntimePolicy(byte[] source,Set<String> biomes,Set<String> registered,int initialY,int spacing){
        this(source,biomes,registered,initialY,spacing,null);
    }
    private CoalRuntimePolicy(byte[] source,Set<String> biomes,Set<String> registered,int initialY,int spacing,CoalHabitatPreference preference){
        layout=CoalLayoutPolicy.read(source);this.biomes=Collections.unmodifiableSet(new TreeSet<>(biomes));
        this.preference=preference;
        if(preference!=null&&!preference.ranks().keySet().equals(this.biomes))throw new IllegalArgumentException("Every coal biome needs an explicit preference rank");
        if(this.biomes.isEmpty()||this.biomes.size()>4096||!registered.containsAll(this.biomes)
                ||this.biomes.stream().anyMatch(b->!b.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")))throw new IllegalArgumentException("Explicit registered coal biomes required");
        new ContinentSpacing(spacing,List.of());this.initialY=initialY;this.spacing=spacing;
        try{var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);out.writeUTF("IC_COAL_RUNTIME_POLICY_V1");
            out.writeUTF(layout.fingerprint());out.writeInt(initialY);out.writeInt(spacing);out.writeInt(this.biomes.size());
            for(String b:this.biomes)out.writeUTF(b);
            if(preference!=null){out.writeUTF("HABITAT_V1");out.writeUTF(preference.fingerprint());}
            out.flush();fingerprint=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray()));
        }catch(IOException|NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
    public static CoalRuntimePolicy read(byte[] source,Set<String> biomes,Set<String> registered,int initialY,int spacing){
        return new CoalRuntimePolicy(source,biomes,registered,initialY,spacing);
    }
    public static CoalRuntimePolicy readRanked(byte[] source,Map<String,Integer> ranks,Set<String> registered,int initialY,int spacing,int lookahead){
        var preference=new CoalHabitatPreference(ranks,lookahead);
        return new CoalRuntimePolicy(source,preference.ranks().keySet(),registered,initialY,spacing,preference);
    }
    public CoalHabitatPreference preference(){return preference;}
    public void checkHeight(int min,int max){if(initialY<min||initialY>=max)throw new IllegalArgumentException("Coal fitting height outside native world");}
    public CoalLayoutPolicy layout(){return layout;}public Set<String> biomes(){return biomes;}
    public int initialY(){return initialY;}public int spacing(){return spacing;}public String fingerprint(){return fingerprint;}
}
