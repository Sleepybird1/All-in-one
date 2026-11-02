package dev.godpc.industrialcolonies.geology;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Objects;
import java.util.function.Supplier;
import net.minecraft.server.level.ServerLevel;

/** Opt-in processed native terrain reads. Never loads Minecraft chunks or changes saved decisions. */
public final class NativeAccurateTerrain {
    private static final String ROOT="raccoonman.reterraforged.world.worldgen.";
    private record Scope(Object lookup,Object token) {}
    private static final ThreadLocal<Scope> CURRENT=new ThreadLocal<>();
    private static volatile boolean verified;
    /** Queue the exact native tile, but do not join its future on a discovery slice. */
    public static void awaitReady(Object lookup,int blockX,int blockZ) {
        if(!NativeTerrainYield.active()||tokenFor(lookup)==null)return;
        try {
            var field=lookup.getClass().getDeclaredField("cache");field.setAccessible(true);
            Object cache=Objects.requireNonNull(field.get(lookup));
            var type=cache.getClass();
            int tx=(Integer)type.getMethod("chunkToTile",int.class).invoke(cache,blockX>>4);
            int tz=(Integer)type.getMethod("chunkToTile",int.class).invoke(cache,blockZ>>4);
            var compute=type.getDeclaredMethod("computeEntry",int.class,int.class);compute.setAccessible(true);
            Object entry=compute.invoke(cache,tx,tz);
            var taskField=entry.getClass().getDeclaredField("task");taskField.setAccessible(true);
            Object task=taskField.get(entry);
            if(!(task instanceof java.util.concurrent.CompletableFuture<?> future))throw new IllegalStateException("Unsupported native tile future");
            if(!future.isDone())throw new NativeTerrainYield.Pending(future);
        }catch(InvocationTargetException e){throw new IllegalStateException("Native terrain readiness failed",e.getCause());}
        catch(ReflectiveOperationException e){throw new IllegalStateException("Native terrain readiness contract unavailable",e);}
    }
    private NativeAccurateTerrain() {}

    public static boolean enabled() {
        return GeologyConfig.bool(GeologyConfig.object(GeologyConfig.get().settings(),"worldStartAccurateTerrain"),"enabled",false);
    }
    /** Exact lookup identity also isolates other worlds and nested native operations. */
    public static Object tokenFor(Object lookup) {
        Scope scope=CURRENT.get();return scope!=null&&scope.lookup()==lookup?scope.token():null;
    }
    public static Object lookup(Object state) {
        try {
            Class<?> api=Class.forName(ROOT+"RTFRandomState");
            if(!api.isInstance(state))throw new IllegalStateException("Accurate terrain requires native RTF state");
            Object context=Objects.requireNonNull(api.getMethod("generatorContext").invoke(state),"native generator context");
            return Objects.requireNonNull(context.getClass().getField("lookup").get(context),"native world lookup");
        } catch(ReflectiveOperationException e) {throw new IllegalStateException("Native terrain lookup unavailable",e);}
    }
    public static <T> T query(ServerLevel level,Supplier<T> operation) {
        if(!enabled()||!level.dimension().location().toString().equals("minecraft:overworld"))return operation.get();
        return queryLookup(lookup(level.getChunkSource().randomState()),operation);
    }
    public static <T> T queryLookup(Object lookup,Supplier<T> operation) {
        verifyContract();Scope previous=CURRENT.get();
        if(previous!=null&&previous.lookup()==lookup)return operation.get();
        CURRENT.set(new Scope(lookup,new Object()));
        try{return operation.get();}finally{if(previous==null)CURRENT.remove();else CURRENT.set(previous);}
    }
    /** Copies a processed tile cell into a fresh caller-owned cell through the installed native API. */
    static void fill(Object lookup,Object cell,int x,int z) {
        queryLookup(lookup,()->{
            try {
                boolean present=(Boolean)lookup.getClass().getMethod("applyCell",cell.getClass(),int.class,int.class,boolean.class,boolean.class)
                        .invoke(lookup,cell,x,z,true,false);
                if(!present)throw new IllegalStateException("Processed native terrain cell unavailable");
                return null;
            }catch(InvocationTargetException e){
                if(e.getCause() instanceof NativeTerrainYield.Pending pending)throw pending;
                throw new IllegalStateException("Processed native terrain failed",e.getCause());}
            catch(ReflectiveOperationException e){throw new IllegalStateException("Processed native terrain API unavailable",e);}
        });
    }
    private static void verifyContract() {
        if(verified)return;
        synchronized(NativeAccurateTerrain.class){
            if(verified)return;
            verify("cell/heightmap/WorldLookup.class","60a780ea73427f2eccaa09a0c796c6d62ab787f88ece9e1c257f672c7b13c224");
            verify("densityfunction/CellSampler$Cache2d.class","db417fa8db02f49f25250104dea078faa9716695175d6d11ebf54168c0b0bff5");
            verify("densityfunction/tile/TileCache.class","91c4b0fcbfcc8b5799aafefa5769b0c2596654942d48c5aa37d114fbf61f3266");
            verifyResource("raccoonman/reterraforged/concurrent/cache/CacheEntry.class","a2fa416c3df3e94e7fa3a654a2fd5a9455fdc5716f7e1bf4270b5ab02817af3a");
            verified=true;
        }
    }
    private static void verify(String name,String expected) {
        String resource=ROOT.replace('.','/')+name;
        verifyResource(resource,expected);
    }
    private static void verifyResource(String resource,String expected) {
        try(var input=NativeAccurateTerrain.class.getClassLoader().getResourceAsStream(resource)){
            if(input==null)throw new IOException("Missing native contract "+resource);
            String actual=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(input.readAllBytes()));
            if(!actual.equals(expected))throw new IllegalStateException("Unqualified native terrain contract: "+resource);
        }catch(IOException|java.security.NoSuchAlgorithmException e){throw new IllegalStateException("Cannot verify native terrain contract",e);}
    }
}
