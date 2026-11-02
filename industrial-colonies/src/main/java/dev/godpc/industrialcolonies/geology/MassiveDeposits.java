package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Opt-in, restart-scoped descriptor geometry. No structure references or saved-chunk queries. */
public final class MassiveDeposits {
    private MassiveDeposits() {}
    public record Settings(double referenceBlocks,double radiusX,double radiusY,double radiusZ,int maxReach) {}
    public record Deposit(GeologyPlanner.Plan plan,MassiveDepositGeometry.Body body) {}

    public static boolean enabled(Config config) {
        return bool(object(object(config.settings(),"geometry"),"massive"),"enabled",false);
    }
    /** Values are deliberately required: enabling a fixture must not silently select gameplay balance. */
    public static Settings settings(Config config) {
        JsonObject data=object(object(config.settings(),"geometry"),"massive");
        if(!enabled(config))throw new IllegalStateException("Massive geometry is not enabled");
        if(number(data,"version",0)!=1)throw new IllegalArgumentException("Unsupported massive geometry version");
        double reference=positive(data,"referenceBlocks"),x=positive(data,"radiusX"),y=positive(data,"radiusY"),z=positive(data,"radiusZ");
        double multiplier=Arrays.stream(numbers(object(config.settings(),"quality"),"sizeMultipliers")).max().orElseThrow();
        double largest=0;
        for(var value:array(config.deposits(),"deposits"))largest=Math.max(largest,Math.max(1,Math.round(integer(value.getAsJsonObject(),"normalSizeMax",0)*multiplier)));
        double scale=Math.cbrt(largest/reference);
        if(!Double.isFinite(scale)||scale<=0||Math.max(x,z)*scale>1024||y*scale>256)
            throw new IllegalArgumentException("Massive radii exceed bounded 1024 horizontal / 256 vertical safety limits");
        int reach=(int)Math.ceil(1.3*Math.max(x,z)*scale)+1;
        long cellsPerAxis=(long)Math.ceil((2.0*reach+16)/integer(config.settings(),"regionSize",512))+1;
        long verticalSpan=(long)Math.ceil(2.6*y*scale)+2;
        if(cellsPerAxis*cellsPerAxis*256L*verticalSpan>4_000_000L)
            throw new IllegalArgumentException("Massive geometry exceeds four million conservative candidate visits per owner chunk");
        return new Settings(reference,x,y,z,reach);
    }
    private static double positive(JsonObject data,String key) {
        double value=number(data,key,Double.NaN);
        if(!Double.isFinite(value)||value<=0)throw new IllegalArgumentException("Missing or invalid massive geometry "+key);
        return value;
    }
    public static MassiveDepositGeometry.Body body(GeologyPlanner.Plan plan,Settings settings) {
        double scale=Math.cbrt(plan.intendedSize()/settings.referenceBlocks());
        var c=plan.candidate();
        return new MassiveDepositGeometry.Body(c.seed(),c.x(),c.y(),c.z(),settings.radiusX()*scale,settings.radiusY()*scale,settings.radiusZ()*scale);
    }
    /** Region order is canonical even for overlapping bodies. Every owner chunk discovers its own deposits. */
    public static List<Deposit> discover(GeologyPlanner planner,Settings settings,int chunkX,int chunkZ) {
        long minX=(long)chunkX*16,minZ=(long)chunkZ*16,maxX=minX+15,maxZ=minZ+15;
        if(minX<Integer.MIN_VALUE||maxX>Integer.MAX_VALUE||minZ<Integer.MIN_VALUE||maxZ>Integer.MAX_VALUE)return List.of();
        int region=planner.regionSize(),reach=settings.maxReach();
        int rx0=(int)Math.floorDiv(minX-reach,region),rx1=(int)Math.floorDiv(maxX+reach,region);
        int rz0=(int)Math.floorDiv(minZ-reach,region),rz1=(int)Math.floorDiv(maxZ+reach,region);
        List<Deposit> result=new ArrayList<>();
        for(int x=rx0;x<=rx1;x++)for(int z=rz0;z<=rz1;z++){
            if(!planner.mayReach(x,z,(int)minX,(int)minZ,(int)maxX,(int)maxZ,reach))continue;
            var plan=planner.decide(x,z).plan();if(plan==null)continue;
            var body=body(plan,settings);
            if(body.bounds().intersectsChunk(chunkX,chunkZ))result.add(new Deposit(plan,body));
        }
        return List.copyOf(result);
    }
}
