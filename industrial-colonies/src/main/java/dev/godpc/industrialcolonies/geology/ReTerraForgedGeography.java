package dev.godpc.industrialcolonies.geology;

import java.lang.reflect.*;
import java.util.Objects;

/** Read-only, optional installed-terrain adapter. Never substitutes a grid for native geography.
 * These are generator regions, not certified connected landmasses or mountain ranges. */
public final class ReTerraForgedGeography {
    private static final String ROOT="raccoonman.reterraforged.world.worldgen.";
    public record ContinentKey(int centerX,int centerZ,int identityBits) {}
    public record TerrainKey(int centerXBits,int centerZBits,int identityBits) {}
    public record Sample(ContinentKey continent,TerrainKey region,String terrain,boolean mountain,
                         float continentEdge,float regionEdge,float normalizedHeight) {}
    private final Object heightmap,lookup;
    private final Constructor<?> newCell;
    private final Method applyTerrain,terrainName,isMountain;
    private final Field continentX,continentZ,continentId,regionX,regionZ,regionId,terrain,continentEdge,regionEdge,height;
    private volatile NativeContinentIdentity.Reader identityReader;

    /** Uses the world's existing initialized generator. Missing context is a refusal, not a new preset. */
    public static ReTerraForgedGeography fromRandomState(Object state) {
        Objects.requireNonNull(state,"random state");
        try {
            Class<?> api=Class.forName(ROOT+"RTFRandomState");
            if(!api.isInstance(state))throw new IllegalStateException("World has no ReTerraForged random state");
            Object context=api.getMethod("generatorContext").invoke(state);
            if(context==null)throw new IllegalStateException("World has no active ReTerraForged generator context");
            Object lookup=context.getClass().getField("lookup").get(context);
            return new ReTerraForgedGeography(lookup,lookup.getClass().getMethod("getHeightmap").invoke(lookup));
        } catch(ReflectiveOperationException e) { throw new IllegalStateException("Unable to read installed ReTerraForged geography",e); }
    }
    private ReTerraForgedGeography(Object lookup,Object heightmap) throws ReflectiveOperationException {
        this.lookup=Objects.requireNonNull(lookup,"lookup");
        this.heightmap=Objects.requireNonNull(heightmap,"heightmap");
        Class<?> cell=Class.forName(ROOT+"cell.Cell"),type=Class.forName(ROOT+"cell.terrain.Terrain");
        newCell=cell.getConstructor();applyTerrain=heightmap.getClass().getMethod("applyTerrain",cell,float.class,float.class);
        terrainName=type.getMethod("getName");isMountain=type.getMethod("isMountain");
        continentX=cell.getField("continentX");continentZ=cell.getField("continentZ");continentId=cell.getField("continentId");
        regionX=cell.getField("terrainRegionCenterX");regionZ=cell.getField("terrainRegionCenterZ");regionId=cell.getField("terrainRegionId");
        terrain=cell.getField("terrain");continentEdge=cell.getField("continentEdge");regionEdge=cell.getField("terrainRegionEdge");height=cell.getField("height");
    }
    /** Identity only, staged for exact processed-native comparison before any caller activation.
     * Existing full terrain/mountain/biome callers continue to use sample(). */
    public ContinentKey continent(int x,int z) {
        if(!NativeAccurateTerrain.enabled())return sample(x,z).continent();
        return identity().sample(x,z);
    }
    /** Exact pinned native branch observation; does not reinterpret a default identity as ocean. */
    public boolean skipped(ContinentKey key) {
        if(!NativeAccurateTerrain.enabled())throw new IllegalStateException("Qualified native skip reader requires accurate terrain");
        return identity().skipped(key);
    }
    private NativeContinentIdentity.Reader identity() {
        var reader=identityReader;
        if(reader==null)synchronized(this){
            reader=identityReader;
            if(reader==null)identityReader=reader=new NativeContinentIdentity.Reader(heightmap);
        }
        return reader;
    }
    public Sample sample(int x,int z) {
        // Installed noise API takes floats. Refuse silent coordinate rounding at large world coordinates.
        if((double)(float)x!=x||(double)(float)z!=z)throw new IllegalArgumentException("Geography coordinate loses float precision");
        try {
            // Fresh caller-owned cell; no pooled/tile-cache cell mutation or chunk generation.
            Object cell=newCell.newInstance();
            if(NativeAccurateTerrain.enabled())NativeAccurateTerrain.fill(lookup,cell,x,z);
            else applyTerrain.invoke(heightmap,cell,(float)x,(float)z);
            Object nativeTerrain=Objects.requireNonNull(terrain.get(cell),"native terrain");
            return new Sample(new ContinentKey(continentX.getInt(cell),continentZ.getInt(cell),bits(continentId.getFloat(cell))),
                    new TerrainKey(bits(regionX.getFloat(cell)),bits(regionZ.getFloat(cell)),bits(regionId.getFloat(cell))),
                    (String)terrainName.invoke(nativeTerrain),(Boolean)isMountain.invoke(nativeTerrain),
                    finite(continentEdge.getFloat(cell)),finite(regionEdge.getFloat(cell)),finite(height.getFloat(cell)));
        } catch(ReflectiveOperationException e) { throw new IllegalStateException("Installed geography sampling failed",e); }
    }
    private static int bits(float value){return Float.floatToIntBits(finite(value));}
    private static float finite(float value){if(!Float.isFinite(value))throw new IllegalStateException("Nonfinite native geography");return value;}
}
