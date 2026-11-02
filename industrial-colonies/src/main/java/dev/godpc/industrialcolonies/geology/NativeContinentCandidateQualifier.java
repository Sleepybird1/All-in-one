package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import net.minecraft.server.level.ServerLevel;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Read-only native terrain/formation qualification. Never places ore or rolls presence.
 * Geometric fit is distinct from replaceable cells, recoverable reserve and survival yield. */
public final class NativeContinentCandidateQualifier implements ContinentCandidateSearch.Qualifier {
    public record Selection(int x, int y, int z, long geometrySeed, int cells, String biome) {}
    public record OccurrenceAdmission(ContinentOccurrenceLedger.Result decision, Optional<GeologyPlanner.Plan> plan) {}
    private final ServerLevel level;
    private final GeologyWorld world;
    private final ReTerraForgedGeography geography;
    private final JsonObject settings, biomes, deposits, definition;
    private final int cells, initialY;
    private final long shapeSalt;
    private final ContinentCandidateSearch.Key key;
    private final GeographicColumnSurvey.Window window;
    private final ContinentSpacing spacing;
    private final ContinentCandidateSearch.Traversal traversal;
    private final ContinentReservePolicy.BiomeChances biomeChances;
    private Selection selection;
    private Selection committed;
    private long reads, foreign, habitat, noFit;

    public NativeContinentCandidateQualifier(ServerLevel level, ReTerraForgedGeography.ContinentKey continent,
            String presetSha256, String family, int cells, int initialY, long shapeSalt) {
        this(level,continent,presetSha256,family,cells,initialY,shapeSalt,null);
    }
    public NativeContinentCandidateQualifier(ServerLevel level, ReTerraForgedGeography.ContinentKey continent,
            String presetSha256, String family, int cells, int initialY, long shapeSalt,ContinentSpacing spacing) {
        this(level,continent,presetSha256,family,cells,initialY,shapeSalt,spacing,ContinentCandidateSearch.Traversal.LINEAR_V1);
    }
    public NativeContinentCandidateQualifier(ServerLevel level, ReTerraForgedGeography.ContinentKey continent,
            String presetSha256, String family, int cells, int initialY, long shapeSalt,ContinentSpacing spacing,ContinentCandidateSearch.Traversal traversal) {
        this(level,continent,presetSha256,family,cells,initialY,shapeSalt,spacing,traversal,null,"");
    }
    public NativeContinentCandidateQualifier(ServerLevel level, ReTerraForgedGeography.ContinentKey continent,
            String presetSha256, String family, int cells, int initialY, long shapeSalt,ContinentSpacing spacing,
            ContinentCandidateSearch.Traversal traversal,ContinentReservePolicy.BiomeChances biomeChances,String sourcePolicy) {
        this.level = Objects.requireNonNull(level);
        this.biomeChances=biomeChances;
        Objects.requireNonNull(sourcePolicy);
        if(!sourcePolicy.isEmpty()&&!sourcePolicy.matches("[0-9a-f]{64}"))throw new IllegalArgumentException("Source policy fingerprint");
        this.spacing=spacing;
        this.traversal=Objects.requireNonNull(traversal);
        requireThread();
        if (!"minecraft:overworld".equals(level.dimension().location().toString()) || cells < 1 || cells > FiniteOreLimits.MAX_BLOCKS
                || initialY < level.getMinBuildHeight() || initialY >= level.getMaxBuildHeight())
            throw new IllegalArgumentException("Qualified Earth finite formation required");
        var config = GeologyConfig.get();
        if (MassiveDeposits.enabled(config)) throw new IllegalArgumentException("Massive geometry needs separate qualification");
        this.cells = cells; this.initialY = initialY; this.shapeSalt = shapeSalt;
        settings = config.settings().deepCopy(); biomes = config.biomes().deepCopy(); deposits = config.deposits().deepCopy();
        world = GeologyWorld.of(level);
        definition = world.planner.definitions().stream().filter(d -> GeologyConfig.string(d,"id","").equals(family))
                .findFirst().orElseThrow(() -> new IllegalArgumentException("Unknown resource family")).deepCopy();
        if(family.equals(WorldStartVeridiumPolicy.FAMILY)&&WorldStartVeridiumPolicy.enabled(config))
            WorldStartVeridiumPolicy.bindDefinition(definition,level.getSeed(),level.dimension().location().toString(),presetSha256,continent,cells);
        var state = level.getChunkSource().randomState();
        var envelope = ContinentEnvelope.around(continent, ReTerraForgedContinentEnvelope.read(state));
        window = new GeographicColumnSurvey.Window(envelope.minX(), envelope.minZ(), envelope.maxX(), envelope.maxZ());
        geography = ReTerraForgedGeography.fromRandomState(state);
        String policy=fingerprint(settings,biomes,deposits,definition,cells,initialY,shapeSalt);
        if(spacing!=null)policy=fingerprint("continent-spacing-v1",policy,spacing);
        if(traversal!=ContinentCandidateSearch.Traversal.LINEAR_V1)policy=fingerprint("candidate-traversal",policy,traversal);
        if(biomeChances!=null||!sourcePolicy.isEmpty())policy=fingerprint("selected-biome-policy-v1",policy,Objects.toString(biomeChances,"fixed"),sourcePolicy);
        key = new ContinentCandidateSearch.Key(level.getSeed(),level.dimension().location().toString(),presetSha256,
                continent,family,policy);
    }
    public ContinentCandidateSearch.Key key() { return key; }
    public ContinentCandidateSearch.Traversal traversal() { return traversal; }
    public GeographicColumnSurvey.Window window() { return window; }
    public Optional<Selection> selection() { return Optional.ofNullable(selection); }
    /** Only discovery's existing checksummed occurrence may pin placement geometry. */
    void retainCommitted(ContinentOccurrenceLedger.Entry entry){
        var request=entry.request();var c=request.candidate();
        if(!entry.present()||!request.key().equals(key)||c.cells()!=cells)
            throw new IllegalArgumentException("Exact present occurrence required for fixed geometry");
        var retained=new Selection(c.x(),c.y(),c.z(),c.geometrySeed(),c.cells(),c.biome());
        if(committed!=null&&!committed.equals(retained))throw new IllegalStateException("Committed geometry changed");
        committed=retained;
    }
    public long reads() { return reads; }
    public long foreign() { return foreign; }
    public long habitat() { return habitat; }
    public long noFit() { return noFit; }
    public double chanceFor(String biome,double fixedChance) { return biomeChances==null?fixedChance:biomeChances.at(biome); }
    /** Cheap scope check for retained absence; no terrain query is necessary. */
    public void checkConfiguration() {
        requireThread();
        var current = GeologyConfig.get();
        if (!settings.equals(current.settings()) || !biomes.equals(current.biomes()) || !deposits.equals(current.deposits()))
            throw new IllegalStateException("Geology configuration changed during candidate discovery");
    }
    @Override public boolean qualifies(int x, int z) {
        checkConfiguration();
        if (x < window.minX() || x > window.maxX() || z < window.minZ() || z > window.maxZ())
            throw new IllegalArgumentException("Outside qualified continent envelope");
        selection = null; reads++;
        if(committed!=null&&(committed.x()!=x||committed.z()!=z))
            throw new IllegalStateException("Committed location cannot be rediscovered");
        if(spacing!=null&&!spacing.allows(x,z))return false;
        if (!key.continent().equals(geography.continent(x,z))) { foreign++; return false; }
        var site = world.sample(x,z);
        if(biomeChances!=null&&biomeChances.at(site.biome())<=0){habitat++;return false;}
        if ((site.families().isEmpty()&&!definition.has("worldStartVeridiumOreBlocks")) || !GeologyPlacement.habitatAllows(definition,site)
                || world.planner.biomeWeight(definition,site) <= 0) { habitat++; return false; }
        // GeologyWorld caches shapes by geometry seed alone. Bind that seed to
        // family, configuration and reserve size, not merely this coordinate/salt.
        long scopedSalt = java.nio.ByteBuffer.wrap(HexFormat.of().parseHex(key.policySha256())).getLong();
        long seed = GeologyMath.seed(level.getSeed(),x,z,shapeSalt ^ scopedSalt);
        if(committed!=null&&(committed.geometrySeed()!=seed||!committed.biome().equals(site.biome()))){noFit++;return false;}
        // Verify the entire horizontal footprint, including the neighbor cover probes,
        // remains within native float precision and this exact continent identity.
        var columns = new HashSet<Long>();
        for (var p : GeologyMath.shape(seed,cells,false)) {
            long px = (long)x+p.x(), pz = (long)z+p.z();
            if (px <= -ContinentEnvelope.LIMIT || px >= ContinentEnvelope.LIMIT
                    || pz <= -ContinentEnvelope.LIMIT || pz >= ContinentEnvelope.LIMIT) { noFit++; return false; }
            long column = ((long)(int)px << 32) ^ ((int)pz & 0xffffffffL);
            if (columns.add(column) && !key.continent().equals(geography.continent((int)px,(int)pz))) {
                foreign++; return false;
            }
        }
        var candidate = new GeologyPlanner.Candidate(Math.floorDiv(x,world.planner.regionSize()),
                Math.floorDiv(z,world.planner.regionSize()),x,initialY,z,seed,site);
        var proposed = new GeologyPlanner.Plan(candidate,definition,1,cells,cells,1,0,List.of());
        boolean cave=GeologyConfig.bool(GeologyConfig.object(settings,"worldStartCaveLocations"),"enabled",false)
                &&CaveDirectedLocations.directed(key.toString());
        int y = cave?world.fitExistingCave(proposed,committed==null?null:committed.y())
                :committed==null?world.fitY(proposed):world.fitAtY(proposed,committed.y());
        if (y == Integer.MIN_VALUE) { noFit++; return false; }
        selection = new Selection(x,y,z,seed,cells,site.biome());
        return true;
    }
    /** Fresh independent admission before exposing a plan; callers still own occurrence,
     * spacing, custody and actual protected-cell placement. */
    public GeologyPlanner.Plan verifiedPlan(Selection expected) {
        Objects.requireNonNull(expected);
        if (!qualifies(expected.x(),expected.z()) || !expected.equals(selection))
            throw new IllegalStateException("Selected formation changed");
        var c = new GeologyPlanner.Candidate(Math.floorDiv(expected.x(),world.planner.regionSize()),
                Math.floorDiv(expected.z(),world.planner.regionSize()),expected.x(),expected.y(),expected.z(),
                expected.geometrySeed(),world.sample(expected.x(),expected.z()));
        return new GeologyPlanner.Plan(c,definition.deepCopy(),1,cells,cells,1,0,List.of());
    }
    /** The caller supplies the reviewed biome probability and an explicitly opened
     * continent ledger. Revalidate before committing; absence or changed inputs
     * return no plan. This grants no placement/custody authority and performs no writes to terrain. */
    public OccurrenceAdmission admitOccurrence(ContinentOccurrenceLedger ledger, Selection expected, double chance)
            throws java.io.IOException {
        Objects.requireNonNull(ledger);
        var request = new ContinentOccurrenceLedger.Request(key,new ContinentOccurrenceLedger.Candidate(
                expected.x(),expected.y(),expected.z(),expected.geometrySeed(),expected.cells(),expected.biome()),chance);
        var plan = verifiedPlan(expected);
        var decision = ledger.decide(request);
        boolean admitted = decision.status()!=ContinentOccurrenceLedger.Status.HELD_CHANGED_INPUT && decision.entry().present();
        return new OccurrenceAdmission(decision,admitted ? Optional.of(plan) : Optional.empty());
    }
    private void requireThread() {
        if (!level.getServer().isSameThread()) throw new IllegalStateException("Native server thread required");
    }
    private static String fingerprint(Object... values) {
        try {
            var digest = MessageDigest.getInstance("SHA-256");
            digest.update("industrial-colonies/native-candidate-qualifier/v1".getBytes(StandardCharsets.UTF_8));
            for (Object value : values) {
                byte[] b = value.toString().getBytes(StandardCharsets.UTF_8);
                digest.update(java.nio.ByteBuffer.allocate(4).putInt(b.length).array()); digest.update(b);
            }
            return HexFormat.of().formatHex(digest.digest());
        } catch (NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
}
