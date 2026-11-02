package dev.godpc.industrialcolonies.geology;

import java.lang.reflect.*;
import java.io.*;
import java.security.*;
import java.util.*;

/** Read-only admission of the inspected native continent search/warp contract. */
public final class ReTerraForgedContinentEnvelope {
    private static final String ROOT="raccoonman.reterraforged.world.worldgen.";
    private static final Map<String,String> PINS=Map.ofEntries(
        // Filled from the inspected installed class bytes by the fixture preparation script.
        Map.entry("cell/continent/advanced/AdvancedContinentGenerator","6190b195cd02bce217d100075fc0eaac7d05e8b9c29d72fd7b8831f2f76805ff"),
        Map.entry("noise/NoiseUtil","2193e3d44a031e97cf2a784ab68cd94b06dac2fda52c676ebddaf69e81895dfc"),
        Map.entry("noise/domain/Domain","ddf89942e709e4c5fe3c56c5848ac712b4c10a18a79ac163744b42213b7cbd86"),
        Map.entry("noise/domain/DomainWarp","77c83ea9e95c89e4cf6728625219a97e82b7a813e8afb3235725e7c1da4bae6e"),
        Map.entry("noise/module/Perlin2","87a15662949969e6844534a0cc6dc9b74e12e261267b6eec3e6f64fe795532ff"),
        Map.entry("noise/module/Map","03eadda656fd3920f991fb80402646c539b4e8c05dc68431082d2dae9b4bede1"),
        Map.entry("noise/module/Constant","11fc0f5d5f6a7a9d715536c4f524069eb7e32928070286339b179ac6918a8075")
    );
    public static ContinentEnvelope.Parameters read(Object state){
        try{
            for(var entry:PINS.entrySet()){
                String path=ROOT.replace('.','/')+entry.getKey()+".class";
                try(var in=ReTerraForgedContinentEnvelope.class.getClassLoader().getResourceAsStream(path)){
                    if(in==null)throw new IllegalStateException("Missing native continent resource: "+entry.getKey());
                    String actual=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));
                    if(!actual.equals(entry.getValue()))
                        throw new IllegalStateException("Unqualified native continent bytecode: "+entry.getKey()+" actual="+actual);
                }
            }
            Class<?> api=Class.forName(ROOT+"RTFRandomState");
            if(!api.isInstance(state))throw new IllegalStateException("Native RTF state required");
            Object context=api.getMethod("generatorContext").invoke(state);
            if(context==null)throw new IllegalStateException("Active RTF context required");
            Object lookup=context.getClass().getField("lookup").get(context);
            Object heightmap=lookup.getClass().getMethod("getHeightmap").invoke(lookup);
            Object continent=heightmap.getClass().getMethod("continent").invoke(heightmap);
            exact(continent,"cell.continent.advanced.AdvancedContinentGenerator");
            float frequency=number(continent,"frequency"),jitter=number(continent,"jitter");
            Object warp=field(continent,"warp");exact(warp,"noise.domain.DomainWarp");
            float distance=constant(field(warp,"distance"));
            for(String axis:List.of("X","Z")){
                Object noise=field(warp,axis.toLowerCase(Locale.ROOT));exact(noise,"noise.module.Perlin2");
                float min=number(noise,"min"),max=number(noise,"max"),f=number(noise,"frequency"),gain=number(noise,"gain"),lac=number(noise,"lacunarity");
                int oct=(Integer)field(noise,"octaves");
                if(!Float.isFinite(min)||!Float.isFinite(max)||min>=max||!Float.isFinite(f)||f<=0||!Float.isFinite(gain)||gain<=0||gain>1||!Float.isFinite(lac)||lac<1||lac>8||oct<1||oct>16
                   ||(ContinentEnvelope.LIMIT+Math.abs((double)distance))*f*Math.pow(lac,oct-1)>(1<<20))
                    throw new IllegalStateException("Unqualified finite Perlin parameters");
                Object mapped=field(warp,"mapped"+axis);exact(mapped,"noise.module.Map");
                if(field(mapped,"alpha")!=noise||constant(field(mapped,"from"))!=-.5f||constant(field(mapped,"to"))!=.5f)
                    throw new IllegalStateException("Unexpected mapped warp graph");
            }
            // Native cell() indexes all256 vectors. Validate the actual live table, not a sample.
            Object[] cells=(Object[])Class.forName(ROOT+"noise.NoiseUtil").getField("CELL_2D").get(null);
            if(cells.length!=256)throw new IllegalStateException("Unexpected native cell table");
            for(Object vector:cells)for(String axis:List.of("x","y")){
                float value=(Float)vector.getClass().getMethod(axis).invoke(vector);
                if(!Float.isFinite(value)||Math.abs(value)>1)throw new IllegalStateException("Unbounded native cell jitter vector");
            }
            return new ContinentEnvelope.Parameters(frequency,jitter,distance);
        }catch(ReflectiveOperationException|IOException|NoSuchAlgorithmException e){throw new IllegalStateException("Native continent envelope unavailable",e);}
    }
    private static Object field(Object object,String name)throws ReflectiveOperationException{
        for(Class<?> type=object.getClass();type!=null;type=type.getSuperclass()){
            try{Field f=type.getDeclaredField(name);f.setAccessible(true);return f.get(object);}catch(NoSuchFieldException ignored){}
        }
        throw new NoSuchFieldException(name);
    }
    private static float number(Object o,String name)throws ReflectiveOperationException{return (Float)field(o,name);}
    private static float constant(Object o)throws ReflectiveOperationException{exact(o,"noise.module.Constant");float v=number(o,"value");if(!Float.isFinite(v))throw new IllegalStateException("Nonfinite constant");return v;}
    private static void exact(Object o,String name){if(o==null||!o.getClass().getName().equals(ROOT+name))throw new IllegalStateException("Unqualified native type: "+name);}
    private ReTerraForgedContinentEnvelope(){}
}
