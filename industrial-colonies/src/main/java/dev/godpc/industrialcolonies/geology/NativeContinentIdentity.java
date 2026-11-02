package dev.godpc.industrialcolonies.geology;

import java.lang.reflect.*;
import java.security.*;
import java.util.*;

/** Exact installed continent function only. Does not supply height, biome, terrain or mountain data.
 * Staged for processed-native equality qualification; no production caller is switched by this class. */
public final class NativeContinentIdentity {
    private static final String ROOT="raccoonman.reterraforged.world.worldgen.";
    private static final Map<String,String> PINS=Map.of(
        "cell/Cell.class","edab8fc22e4422857db874a0b3d303dfd021123793c7474fab650b48675ad798",
        "cell/continent/advanced/AdvancedContinentGenerator.class","6190b195cd02bce217d100075fc0eaac7d05e8b9c29d72fd7b8831f2f76805ff",
        "cell/heightmap/Heightmap.class","3c6e59dbd834a82204082d504292b05fa7039d932d41af1d8830e23e85ea5ee3",
        "WorldFilters.class","a2598062e0ee086e6b78a4294d8245a640cad6ef932767e353a25dfc469dc5f6",
        "densityfunction/tile/generation/TileGenerator.class","a36502de7518ee3504c6af120e039bc398b5396dc113a2c78698d1c4c37797f1");
    private static volatile boolean verified;
    private NativeContinentIdentity() {}
    public static final class Reader {
        private final Object continent;
        private final Constructor<?> newCell;
        private final Method apply;
        private final Field x,z,id;
        public Reader(Object heightmap) {
            Objects.requireNonNull(heightmap);verify();
            try {
                if(!heightmap.getClass().getName().equals(ROOT+"cell.heightmap.Heightmap"))throw new IllegalStateException("Exact qualified native heightmap required");
                continent=Objects.requireNonNull(heightmap.getClass().getMethod("continent").invoke(heightmap));
                if(!continent.getClass().getName().equals(ROOT+"cell.continent.advanced.AdvancedContinentGenerator"))throw new IllegalStateException("Exact qualified installed advanced continent required");
                Class<?> cell=Class.forName(ROOT+"cell.Cell");newCell=cell.getConstructor();apply=continent.getClass().getMethod("apply",cell,float.class,float.class);
                x=cell.getField("continentX");z=cell.getField("continentZ");id=cell.getField("continentId");
            }catch(ReflectiveOperationException error){throw new IllegalStateException("Native continent identity API unavailable",error);}
        }
        public ReTerraForgedGeography.ContinentKey sample(int blockX,int blockZ) {
            if((double)(float)blockX!=blockX||(double)(float)blockZ!=blockZ)throw new IllegalArgumentException("Native identity coordinate loses float precision");
            try {
                // Heightmap.applyTerrain invokes this same installed method with the same
                // unscaled coordinates. Its bytecode does not read any incoming Cell field.
                Object cell=newCell.newInstance();apply.invoke(continent,cell,(float)blockX,(float)blockZ);
                float identity=id.getFloat(cell);if(!Float.isFinite(identity))throw new IllegalStateException("Nonfinite native continent identity");
                return new ReTerraForgedGeography.ContinentKey(x.getInt(cell),z.getInt(cell),Float.floatToIntBits(identity));
            }catch(InvocationTargetException error){throw new IllegalStateException("Installed native continent identity failed",error.getCause());}
            catch(ReflectiveOperationException error){throw new IllegalStateException("Installed native identity read failed",error);}
        }
        /** Observe the pinned native early return directly. A zero ID alone is never a skip signal. */
        public boolean skipped(ReTerraForgedGeography.ContinentKey expected) {
            int bx=expected.centerX(),bz=expected.centerZ();
            if((double)(float)bx!=bx||(double)(float)bz!=bz)throw new IllegalArgumentException("Native center loses float precision");
            try {
                Object cell=newCell.newInstance();float defaultId=id.getFloat(cell);
                int sentinel=0x7fc12345;id.setFloat(cell,Float.intBitsToFloat(sentinel));
                apply.invoke(continent,cell,(float)bx,(float)bz);
                float actual=id.getFloat(cell);boolean skipped=Float.floatToRawIntBits(actual)==sentinel;
                float identity=skipped?defaultId:actual;
                if(!Float.isFinite(identity))throw new IllegalStateException("Native skip observation produced invalid identity");
                var observed=new ReTerraForgedGeography.ContinentKey(x.getInt(cell),z.getInt(cell),Float.floatToIntBits(identity));
                if(!observed.equals(expected))throw new IllegalStateException("Supplied continent does not match its native center");
                return skipped;
            }catch(InvocationTargetException error){throw new IllegalStateException("Installed native skip observation failed",error.getCause());}
            catch(ReflectiveOperationException error){throw new IllegalStateException("Installed native skip read failed",error);}
        }
    }
    private static void verify() {
        if(verified)return;
        synchronized(NativeContinentIdentity.class){
            if(verified)return;
            for(var entry:PINS.entrySet()){
                String path=ROOT.replace('.','/')+entry.getKey();
                try(var stream=NativeContinentIdentity.class.getClassLoader().getResourceAsStream(path)){
                    if(stream==null)throw new IllegalStateException("Missing native identity contract: "+entry.getKey());
                    String actual=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(stream.readAllBytes()));
                    if(!actual.equals(entry.getValue()))throw new IllegalStateException("Unqualified native identity bytecode: "+entry.getKey());
                }catch(java.io.IOException|NoSuchAlgorithmException error){throw new IllegalStateException("Cannot verify installed identity contract",error);}
            }
            verified=true;
        }
    }
}
