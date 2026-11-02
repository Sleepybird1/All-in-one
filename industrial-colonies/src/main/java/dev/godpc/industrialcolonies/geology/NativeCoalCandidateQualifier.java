package dev.godpc.industrialcolonies.geology;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.*;

/** Native geometric qualification for a previously saved guaranteed-coal slot.
 * Does not roll presence, place blocks, shrink reserves or certify recoverable supply. */
public final class NativeCoalCandidateQualifier {
    public record Selection(int x,int y,int z,long geometrySeed,int cells,String biome){}
    private final ServerLevel level;
    private final GeologyWorld world;
    private final GeologyConfig.Config config;
    private final ReTerraForgedGeography geography;
    private final com.google.gson.JsonObject definition;
    private final Set<String> eligibleBiomes;
    private final ContinentSpacing coalSpacing,otherSpacing;
    private final GeographicColumnSurvey.Window window;
    private final CoalPlacementRequest request;
    private final int initialY;
    private final CoalHabitatPreference preference;
    private Selection selection;

    public NativeCoalCandidateQualifier(ServerLevel level,CoalAllocationJournal allocation,String slot,
            String expectedPreset,int initialY,Set<String> eligibleBiomes,ContinentSpacing coalSpacing,
            ContinentSpacing otherSpacing)throws IOException{
        this(level,allocation,slot,expectedPreset,initialY,eligibleBiomes,coalSpacing,otherSpacing,null);
    }
    public NativeCoalCandidateQualifier(ServerLevel level,CoalAllocationJournal allocation,String slot,
            String expectedPreset,int initialY,Set<String> eligibleBiomes,ContinentSpacing coalSpacing,
            ContinentSpacing otherSpacing,CoalHabitatPreference preference)throws IOException{
        this.level=Objects.requireNonNull(level);requireThread();
        this.preference=preference;
        if(preference!=null&&!preference.ranks().keySet().equals(eligibleBiomes))throw new IllegalArgumentException("Coal habitat policy and eligibility differ");
        Objects.requireNonNull(allocation);
        var scope=allocation.scope();
        if(scope.worldSeed()!=level.getSeed()||!scope.dimension().equals(level.dimension().location().toString())
                ||!scope.presetSha256().equals(expectedPreset)||initialY<level.getMinBuildHeight()||initialY>=level.getMaxBuildHeight())
            throw new IllegalArgumentException("Coal allocation and native world/preset/height disagree");
        if(!GeologyConfig.enabled()||MassiveDeposits.enabled(GeologyConfig.get()))throw new IllegalStateException("Exclusive finite geology required");
        this.initialY=initialY;this.coalSpacing=Objects.requireNonNull(coalSpacing);this.otherSpacing=Objects.requireNonNull(otherSpacing);
        this.eligibleBiomes=Collections.unmodifiableSet(new TreeSet<>(eligibleBiomes));
        if(this.eligibleBiomes.isEmpty()||this.eligibleBiomes.size()>4096)throw new IllegalArgumentException("Explicit coal biome eligibility required");
        var registry=level.registryAccess().registryOrThrow(Registries.BIOME);
        for(String biome:this.eligibleBiomes)if(!biome.matches("[a-z0-9_.-]+:[a-z0-9_./-]+")||!registry.containsKey(ResourceLocation.parse(biome)))
            throw new IllegalArgumentException("Unknown coal biome: "+biome);
        var c=GeologyConfig.get();config=new GeologyConfig.Config(c.settings().deepCopy(),c.biomes().deepCopy(),c.deposits().deepCopy());
        world=GeologyWorld.of(level);
        definition=world.planner.definitions().stream().filter(d->GeologyConfig.string(d,"id","").equals("coal")).findFirst().orElseThrow(()->new IllegalArgumentException("Missing coal definition")).deepCopy();
        // Exact eligibility is supplied above. Old coal biome preference magnitudes are not reused
        // as placement probabilities, a guarantee or a claim that the new preference is implemented.
        var state=level.getChunkSource().randomState();geography=ReTerraForgedGeography.fromRandomState(state);
        var e=ContinentEnvelope.around(allocation.continent(),ReTerraForgedContinentEnvelope.read(state));
        window=new GeographicColumnSurvey.Window(e.minX(),e.minZ(),e.maxX(),e.maxZ());
        String terrain=fingerprint(config,definition,initialY,this.eligibleBiomes,coalSpacing,otherSpacing,window);
        if(preference!=null)terrain=fingerprint(terrain,"HABITAT_V1",preference.fingerprint());
        request=CoalPlacementRequest.bind(allocation,slot,terrain);
    }
    public CoalPlacementRequest request(){return request;}
    public GeographicColumnSurvey.Window window(){return window;}
    public CoalHabitatPreference preference(){return preference;}
    public Optional<Selection> selection(){return Optional.ofNullable(selection);}
    public void checkConfiguration()throws IOException{
        requireThread();if(!config.equals(GeologyConfig.get()))throw new IOException("Coal terrain configuration changed");request.verify();
    }
    public boolean qualifies(int x,int z)throws IOException{
        checkConfiguration();selection=null;
        if(x<window.minX()||x>window.maxX()||z<window.minZ()||z>window.maxZ())throw new IllegalArgumentException("Outside coal continent envelope");
        if(Math.abs((long)x)>=ContinentEnvelope.LIMIT||Math.abs((long)z)>=ContinentEnvelope.LIMIT)return false;
        if(!coalSpacing.allows(x,z)||!otherSpacing.allows(x,z))return false;
        if(!request.continent().equals(geography.sample(x,z).continent()))return false;
        var site=world.sample(x,z);
        if(!eligibleBiomes.contains(site.biome())||site.families().isEmpty()||!GeologyPlacement.habitatAllows(definition,site))return false;
        long seed=request.geometrySeed(x,z);int cells=request.deposit().oreBlocks();var columns=new HashSet<Long>();
        for(var p:coalFootprint(seed,cells)){
            long px=(long)x+p.x(),pz=(long)z+p.z();
            if(px<=-ContinentEnvelope.LIMIT||px>=ContinentEnvelope.LIMIT||pz<=-ContinentEnvelope.LIMIT||pz>=ContinentEnvelope.LIMIT)return false;
            if(columns.add(((long)(int)px<<32)^((int)pz&0xffffffffL))&&!request.continent().equals(geography.sample((int)px,(int)pz).continent()))return false;
        }
        var candidate=new GeologyPlanner.Candidate(Math.floorDiv(x,world.planner.regionSize()),Math.floorDiv(z,world.planner.regionSize()),x,initialY,z,seed,site);
        var proposed=new GeologyPlanner.Plan(candidate,definition,1,cells,cells,1,0,List.of());
        boolean cave=GeologyConfig.bool(GeologyConfig.object(config.settings(),"worldStartCaveLocations"),"enabled",false)
                &&CaveDirectedLocations.directed(request.fingerprint());
        int y=cave?world.fitExistingCave(proposed,null):world.fitY(proposed);
        if(y==Integer.MIN_VALUE)return false;
        selection=new Selection(x,y,z,seed,cells,site.biome());return true;
    }
    public GeologyPlanner.Plan verifiedPlan(Selection expected)throws IOException{
        Objects.requireNonNull(expected);
        if(!qualifies(expected.x(),expected.z())||!expected.equals(selection))throw new IllegalStateException("Selected coal formation changed");
        var c=new GeologyPlanner.Candidate(Math.floorDiv(expected.x(),world.planner.regionSize()),Math.floorDiv(expected.z(),world.planner.regionSize()),expected.x(),expected.y(),expected.z(),expected.geometrySeed(),world.sample(expected.x(),expected.z()));
        return new GeologyPlanner.Plan(c,definition.deepCopy(),1,expected.cells(),expected.cells(),1,0,List.of());
    }
    private void requireThread(){if(!level.getServer().isSameThread())throw new IllegalStateException("Native server thread required");}
    /** Must match GeologyWorld.shape/fitY's coal seam, including its wider horizontal footprint. */
    public static List<GeologyMath.Voxel> coalFootprint(long seed,int cells){return GeologyMath.shape(seed,cells,true);}
    private static String fingerprint(Object... values){
        try{
            var digest=MessageDigest.getInstance("SHA-256");digest.update("industrial-colonies/native-coal-qualifier/v2-coal-seam".getBytes(StandardCharsets.UTF_8));
            for(Object value:values){byte[] bytes=value.toString().getBytes(StandardCharsets.UTF_8);digest.update(java.nio.ByteBuffer.allocate(4).putInt(bytes.length).array());digest.update(bytes);}
            return HexFormat.of().formatHex(digest.digest());
        }catch(NoSuchAlgorithmException e){throw new AssertionError(e);}
    }
}
