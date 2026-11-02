package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.math.BigInteger;
import java.security.*;
import java.util.*;

/** Bounded, resumable discovery of ONE qualified location, before any occurrence roll.
 * This is not an area estimate or the existing area-weighted district policy.
 * Native identity, habitat and complete formation fit belong to the supplied qualifier.
 * A selected location never falls back to another location if later invalidated. */
public final class ContinentCandidateSearch {
    public record Key(long worldSeed, String dimension, String presetSha256,
                      ReTerraForgedGeography.ContinentKey continent, String family, String policySha256) {
        public Key {
            Objects.requireNonNull(continent);
            if (!"minecraft:overworld".equals(dimension) || !digest(presetSha256) || !digest(policySha256)
                    || family == null || !family.matches("[a-z0-9_]+")
                    || family.equals("coal") || family.equals("cinnabar"))
                throw new IllegalArgumentException("Scoped optional-resource search required");
        }
    }
    public record Site(int x, int z) {}
    public enum Status { SEARCHING, SELECTED, EXHAUSTED_WINDOW, HELD_CHANGED_CANDIDATE }
    public enum Traversal { LINEAR_V1, PERMUTED_V2, LOCAL_V3 }
    public record Checkpoint(Key key, GeographicColumnSurvey.Window window, long visited,
                             Status status, Site selected) {}
    @FunctionalInterface public interface Qualifier {
        /** Read-only full native identity/habitat/formation check. Throw on unavailable data. */
        boolean qualifies(int x, int z);
    }
    private final Key key;
    private final GeographicColumnSurvey.Window window;
    private final Qualifier qualifier;
    private final long start, stride, count;
    private final Traversal traversal;
    private final long permutationKey;
    private final ContinentLocalTraversal local;
    private long visited, index;
    private Status status = Status.SEARCHING;
    private Site selected;

    public ContinentCandidateSearch(Key key, GeographicColumnSurvey.Window window, Qualifier qualifier) {
        this(key,window,qualifier,Traversal.LINEAR_V1);
    }
    public ContinentCandidateSearch(Key key, GeographicColumnSurvey.Window window, Qualifier qualifier,Traversal traversal) {
        this.key = Objects.requireNonNull(key); this.window = Objects.requireNonNull(window);
        this.traversal=Objects.requireNonNull(traversal);this.permutationKey=seed(key,window);
        local=traversal==Traversal.LOCAL_V3?new ContinentLocalTraversal(window,key.continent().centerX(),key.continent().centerZ(),permutationKey):null;
        this.qualifier = Objects.requireNonNull(qualifier); count = window.columns();
        var random = new SplittableRandom(seed(key, window));
        start = random.nextLong(count);
        long step = count == 1 ? 1 : random.nextLong(1, count);
        while (gcd(step, count) != 1) step = step == count - 1 ? 1 : step + 1;
        stride = step; index = traversal==Traversal.LINEAR_V1?start:at(0);
    }
    /** At most budget reads; failed reads retry the same location. A hit ends discovery. */
    public Checkpoint advance(int budget) {
        if (budget < 1 || budget > 4096) throw new IllegalArgumentException("Search budget1..4096");
        for (int i = 0; i < budget && status == Status.SEARCHING; i++) {
            Site site = site(index);
            boolean eligible = qualifier.qualifies(site.x(), site.z());
            long nextVisited=visited+1;
            long nextIndex=eligible||nextVisited==count?0:
                    traversal==Traversal.LINEAR_V1?(index+stride)%count:at(nextVisited);
            visited=nextVisited;index=nextIndex;
            if (eligible) { selected = site; status = Status.SELECTED; }
            else if (visited == count) status = Status.EXHAUSTED_WINDOW;
        }
        return checkpoint();
    }
    /** Caller must supply the original scoped native qualifier. Reopening a selected
     * candidate rechecks that same site, never discovers a replacement or rolls presence. */
    public static ContinentCandidateSearch restore(Key expected, GeographicColumnSurvey.Window window,
                                                   Qualifier qualifier, Checkpoint saved) {
        return restore(expected,window,qualifier,saved,Traversal.LINEAR_V1);
    }
    public static ContinentCandidateSearch restore(Key expected, GeographicColumnSurvey.Window window,
                                                   Qualifier qualifier, Checkpoint saved,Traversal traversal) {
        Objects.requireNonNull(saved);
        if (!expected.equals(saved.key()) || !window.equals(saved.window()))
            throw new IllegalArgumentException("Search configuration changed");
        var search = new ContinentCandidateSearch(expected, window, qualifier,traversal);
        if (saved.status() == null || saved.visited() < 0 || saved.visited() > search.count)
            throw new IllegalArgumentException("Invalid search cursor");
        boolean chosen = saved.status() == Status.SELECTED || saved.status() == Status.HELD_CHANGED_CANDIDATE;
        if (chosen != (saved.selected() != null) || chosen && saved.visited() == 0
                || saved.status() == Status.SEARCHING && saved.visited() == search.count
                || saved.status() == Status.EXHAUSTED_WINDOW && saved.visited() != search.count)
            throw new IllegalArgumentException("Inconsistent search checkpoint");
        search.visited = saved.visited(); search.status = saved.status(); search.selected = saved.selected();
        search.index = search.status==Status.SEARCHING?search.at(search.visited):0;
        if (chosen && !search.site(search.at(search.visited - 1)).equals(search.selected))
            throw new IllegalArgumentException("Selected location does not match cursor");
        if (search.status == Status.SELECTED && !qualifier.qualifies(search.selected.x(), search.selected.z()))
            search.status = Status.HELD_CHANGED_CANDIDATE;
        return search;
    }
    public Checkpoint checkpoint() { return new Checkpoint(key, window, visited, status, selected); }
    private Site site(long n) { return new Site((int)(window.minX() + n % window.width()),
            (int)(window.minZ() + n / window.width())); }
    private long at(long n) {
        if(traversal==Traversal.LOCAL_V3)return local.at(n%count);
        if(traversal==Traversal.PERMUTED_V2)return permuted(n%count);
        return BigInteger.valueOf(stride).multiply(BigInteger.valueOf(n)).add(BigInteger.valueOf(start))
                .mod(BigInteger.valueOf(count)).longValueExact();
    }
    /** Six balanced Feistel rounds form a bijection on a power-of-four envelope.
     * Cycle walking restricts that bijection to the exact window, without duplicates.
     * A defensive bound refuses a pathological walk rather than skipping an ordinal. */
    private long permuted(long ordinal){
        return permuted(ordinal,count,permutationKey);
    }
    static long permuted(long ordinal,long count,long permutationKey){
        if(count==1)return 0;
        int bits=64-Long.numberOfLeadingZeros(count-1),half=(bits+1)/2;
        long mask=(1L<<half)-1,value=ordinal;
        for(int walk=0;walk<128;walk++){
            long left=value>>>half,right=value&mask;
            for(int round=0;round<6;round++){
                long x=right^permutationKey^(0x9e3779b97f4a7c15L*(round+1));
                x=(x^(x>>>30))*0xbf58476d1ce4e5b9L;x=(x^(x>>>27))*0x94d049bb133111ebL;x^=x>>>31;
                long next=left^(x&mask);left=right;right=next;
            }
            value=(left<<half)|right;if(value<count)return value;
        }
        throw new IllegalStateException("Candidate permutation exceeded bounded cycle walk");
    }
    private static long gcd(long a, long b) { while (b != 0) { long c = a % b; a = b; b = c; } return a; }
    private static boolean digest(String s) { return s != null && s.matches("[0-9a-f]{64}"); }
    private static long seed(Key k, GeographicColumnSurvey.Window w) {
        try {
            var bytes = new ByteArrayOutputStream(); var out = new DataOutputStream(bytes);
            out.writeUTF("industrial-colonies/candidate-search/v1"); out.writeLong(k.worldSeed());
            out.writeUTF(k.dimension()); out.writeUTF(k.presetSha256()); out.writeUTF(k.policySha256());
            out.writeInt(k.continent().centerX()); out.writeInt(k.continent().centerZ());
            out.writeInt(k.continent().identityBits()); out.writeUTF(k.family());
            out.writeInt(w.minX()); out.writeInt(w.minZ()); out.writeInt(w.maxX()); out.writeInt(w.maxZ());
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray());
            return java.nio.ByteBuffer.wrap(hash).getLong();
        } catch (IOException | NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }
}
