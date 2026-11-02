package dev.godpc.industrialcolonies.geology;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/** Deterministic allocation only. Native callers must supply verified continent/deposit identities
 * and qualify actual ReTerraForged terrain. This class neither places blocks nor admits a world. */
public final class WorldStartAllocation {
    private WorldStartAllocation() {}
    private static final double[] LIGHTNING={.25,.20,.10,.01};
    public record Scope(long seed,String dimension,String presetFingerprint,
                        ReTerraForgedGeography.ContinentKey continent) {
        public Scope {
            Objects.requireNonNull(continent);
            if(!"minecraft:overworld".equals(dimension)||presetFingerprint==null
                    ||!presetFingerprint.matches("[a-f0-9]{64}"))
                throw new IllegalArgumentException("Exact Earth preset/continent identity required");
        }
    }
    public record DragonSite(String identity,int x,int z,boolean nativeMountain,
                             ReTerraForgedGeography.ContinentKey continent) {
        public DragonSite { WorldStartAllocation.identity(identity);Objects.requireNonNull(continent); }
    }
    public record Veridium(boolean present,int hostBlocks,boolean visibleOre,int oreBlocks) {}
    /** Stops at the first failed conditional roll. Never creates a separate quota per dragon size. */
    public static int lightningCount(Scope scope) {
        int count=0;
        for(int i=0;i<LIGHTNING.length;i++) {
            if(unit(scope,"lightning-count",Integer.toString(i))>=LIGHTNING[i])break;
            count++;
        }
        return count;
    }
    /** A complete native candidate set must be supplied; a partial scan cannot certify allocation. */
    public static List<DragonSite> lightningSites(Scope scope,Collection<DragonSite> completeCandidates) {
        return lightningSites(scope,completeCandidates,site->true);
    }
    /** Native start/terrain qualification is evaluated in stable order, before spending a slot.
     * The supplied check must be deterministic and must not place blocks or entities. */
    public static List<DragonSite> lightningSites(Scope scope,Collection<DragonSite> completeCandidates,
                                                java.util.function.Predicate<DragonSite> eligibleStart) {
        Objects.requireNonNull(completeCandidates);
        Objects.requireNonNull(eligibleStart);
        if(completeCandidates.size()>65536)throw new IllegalArgumentException("Bounded native candidates required");
        Set<String> identities=new HashSet<>();Set<Long> chunks=new HashSet<>();
        var candidates=new ArrayList<DragonSite>();
        for(var site:completeCandidates) {
            Objects.requireNonNull(site);
            if(!identities.add(site.identity()))throw new IllegalArgumentException("Duplicate candidate identity");
            if(site.nativeMountain()&&scope.continent().equals(site.continent()))candidates.add(site);
        }
        candidates.sort(Comparator.comparingDouble((DragonSite s)->unit(scope,"lightning-site",s.identity()))
                .thenComparing(DragonSite::identity));
        var selected=new ArrayList<DragonSite>();int count=lightningCount(scope);
        for(var site:candidates) {
            if(selected.size()==count)break;
            long chunk=((long)Math.floorDiv(site.x(),16)<<32)^(Math.floorDiv(site.z(),16)&0xffffffffL);
            if(!chunks.contains(chunk)&&eligibleStart.test(site)){chunks.add(chunk);selected.add(site);}
        }
        return List.copyOf(selected);
    }
    /** One stable roll per actual vein; neighboring identities are not spatially excluded. */
    public static boolean mineshaft(Scope scope,String finiteVeinIdentity,boolean canSpawnMineshaft) {
        identity(finiteVeinIdentity);
        return canSpawnMineshaft&&unit(scope,"mineshaft",finiteVeinIdentity)<.10;
    }
    public static Veridium veridium(Scope scope) {
        if(unit(scope,"veridium-presence","")>=1.0/7)return new Veridium(false,0,false,0);
        int host=50000+(int)(unit(scope,"veridium-size","")*50001);
        boolean ore=unit(scope,"veridium-visible-ore","")<.10;
        // Round the conditional target density without an unbounded binomial tail.
        double expected=host/20000.0;int amount=(int)Math.floor(expected);
        if(unit(scope,"veridium-ore-count","")<expected-amount)amount++;
        return new Veridium(true,host,ore,ore?amount:0);
    }
    public static double unit(Scope scope,String purpose,String identity) {
        Objects.requireNonNull(scope);Objects.requireNonNull(purpose);Objects.requireNonNull(identity);
        try {
            var digest=MessageDigest.getInstance("SHA-256");
            for(String part:List.of("IC_WORLD_START_ALLOCATION_V1",Long.toString(scope.seed()),scope.dimension(),
                    scope.presetFingerprint(),Integer.toString(scope.continent().centerX()),
                    Integer.toString(scope.continent().centerZ()),Integer.toString(scope.continent().identityBits()),purpose,identity)) {
                byte[] bytes=part.getBytes(StandardCharsets.UTF_8);
                digest.update(ByteBuffer.allocate(4).putInt(bytes.length).array());digest.update(bytes);
            }
            return (ByteBuffer.wrap(digest.digest()).getLong()>>>11)*0x1.0p-53;
        } catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
    }
    private static void identity(String value) {
        if(value==null||value.isBlank()||value.length()>512)throw new IllegalArgumentException("Stable bounded identity required");
    }
}
