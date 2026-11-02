package dev.godpc.industrialcolonies.geology;

import java.io.*;
import java.security.*;
import java.util.*;
import java.util.function.Consumer;

/** One optional-resource decision from a complete, externally qualified district survey.
 * Does not discover continents, certify survey completeness, place blocks or allocate reserves.
 * Area-weighted district selection is a staged proposal, not an approved balance setting. */
public final class ContinentResourceDecision {
    public record Scope(long worldSeed, String dimension, String presetSha256) {
        public Scope {
            if (!"minecraft:overworld".equals(dimension)) throw new IllegalArgumentException("Earth scope required");
            if (presetSha256 == null || !presetSha256.matches("[0-9a-f]{64}"))
                throw new IllegalArgumentException("Canonical preset SHA256 required");
        }
    }
    public record District(String id, ReTerraForgedGeography.ContinentKey continent,
                           String biome, long areaWeight, int fittingOreBlocks) {
        public District {
            Objects.requireNonNull(continent);
            if (id == null || id.isBlank() || id.length() > 256) throw new IllegalArgumentException("District ID");
            if (biome == null || !biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+"))
                throw new IllegalArgumentException("Canonical biome ID");
            if (areaWeight <= 0 || fittingOreBlocks < 0 || fittingOreBlocks > FiniteOreLimits.MAX_BLOCKS)
                throw new IllegalArgumentException("District area/capacity");
        }
    }
    public record Survey(Scope scope, ReTerraForgedGeography.ContinentKey continent,
                         boolean complete, List<District> districts) {
        public Survey {
            Objects.requireNonNull(scope); Objects.requireNonNull(continent);
            districts = List.copyOf(districts);
            Set<String> ids = new HashSet<>();
            long area = 0;
            for (District d : districts) {
                if (!continent.equals(d.continent()) || !ids.add(d.id()))
                    throw new IllegalArgumentException("Foreign or duplicate district");
                area = Math.addExact(area, d.areaWeight());
            }
        }
    }
    public enum Status { INCOMPLETE_SURVEY, NO_ELIGIBLE_DISTRICT, ABSENT, PRESENT }
    public record Decision(Status status, String district, Double chance, Double roll,
                           int requestedOreBlocks, String surveySha256) {}

    /** Same existing presence domain for a separately qualified selected candidate.
     * This draws no district ticket and certifies no survey or formation. */
    public static double presenceRoll(Scope scope, ReTerraForgedGeography.ContinentKey continent, String resource) {
        if (resource == null || !resource.matches("[a-z0-9_]+") || resource.equals("coal") || resource.equals("cinnabar"))
            throw new IllegalArgumentException("Optional resource family required");
        return random(new Survey(scope,continent,false,List.of()),resource,"presence").nextDouble();
    }

    /** Missing/zero chance excludes a biome. Select one fitting district, then roll once;
     * failure never selects another district. No chunk coordinate participates in either draw. */
    public static Decision decide(Survey survey, String resource, int oreBlocks, Map<String, Double> chances) {
        Objects.requireNonNull(survey);
        if (resource == null || !resource.matches("[a-z0-9_]+")) throw new IllegalArgumentException("Family ID");
        if (resource.equals("coal") || resource.equals("cinnabar"))
            throw new IllegalArgumentException("Guaranteed resource requires its own allocation policy");
        if (oreBlocks < 1 || oreBlocks > FiniteOreLimits.MAX_BLOCKS) throw new IllegalArgumentException("Earth ore cap");
        Map<String, Double> probabilities = Map.copyOf(chances);
        probabilities.forEach((biome, p) -> {
            if (!biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+") || !Double.isFinite(p) || p < 0 || p > 1)
                throw new IllegalArgumentException("Biome probability");
        });
        List<District> sorted = survey.districts().stream().sorted(Comparator.comparing(District::id)).toList();
        String digest = HexFormat.of().formatHex(hash(out -> {
            scope(out, survey, "survey", ""); write(out, survey.complete());
            for (District d : sorted) {
                write(out, d.id()); write(out, d.biome()); write(out, d.areaWeight()); write(out, d.fittingOreBlocks());
            }
        }));
        if (!survey.complete()) return new Decision(Status.INCOMPLETE_SURVEY, null, null, null, oreBlocks, digest);
        List<District> eligible = sorted.stream().filter(d -> d.fittingOreBlocks() >= oreBlocks
                && probabilities.getOrDefault(d.biome(), 0.0) > 0).toList();
        if (eligible.isEmpty()) return new Decision(Status.NO_ELIGIBLE_DISTRICT, null, null, null, oreBlocks, digest);
        long total = 0;
        for (District d : eligible) total = Math.addExact(total, d.areaWeight());
        long ticket = random(survey, resource, "district").nextLong(total);
        District chosen = null;
        for (District d : eligible) {
            if (ticket < d.areaWeight()) { chosen = d; break; }
            ticket -= d.areaWeight();
        }
        Objects.requireNonNull(chosen);
        double roll = random(survey, resource, "presence").nextDouble();
        double chance = probabilities.get(chosen.biome());
        return new Decision(roll < chance ? Status.PRESENT : Status.ABSENT, chosen.id(), chance, roll, oreBlocks, digest);
    }
    private static SplittableRandom random(Survey s, String resource, String domain) {
        byte[] bytes = hash(out -> scope(out, s, domain, resource));
        long seed = 0;
        for (int i = 0; i < 8; i++) seed = (seed << 8) | (bytes[i] & 255L);
        return new SplittableRandom(seed);
    }
    private static void scope(DataOutputStream out, Survey s, String domain, String resource) {
        write(out, "industrial-colonies/continent-resource/v1"); write(out, domain); write(out, resource);
        write(out, s.scope().worldSeed()); write(out, s.scope().dimension()); write(out, s.scope().presetSha256());
        write(out, s.continent().centerX()); write(out, s.continent().centerZ()); write(out, s.continent().identityBits());
    }
    private static byte[] hash(Consumer<DataOutputStream> writer) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        writer.accept(new DataOutputStream(bytes));
        try { return MessageDigest.getInstance("SHA-256").digest(bytes.toByteArray()); }
        catch (NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
    private static void write(DataOutputStream out, Object value) {
        try {
            if (value instanceof String s) { byte[] bytes = s.getBytes(java.nio.charset.StandardCharsets.UTF_8); out.writeInt(bytes.length); out.write(bytes); }
            else if (value instanceof Long l) out.writeLong(l);
            else if (value instanceof Integer i) out.writeInt(i);
            else if (value instanceof Boolean b) out.writeBoolean(b);
            else throw new IllegalArgumentException("Unsupported digest value");
        } catch (IOException e) { throw new UncheckedIOException(e); }
    }
    private ContinentResourceDecision() {}
}
