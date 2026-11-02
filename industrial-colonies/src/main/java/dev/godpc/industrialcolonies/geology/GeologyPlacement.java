package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Optional surface habitat gates. One explicit override avoids ambiguous overlapping priorities. */
public final class GeologyPlacement {
    private GeologyPlacement() {}
    public static boolean habitatAllows(JsonObject definition,GeologyPlanner.Site site){
        var families=array(object(definition,"placement"),"requiredSurfaceFamilies");
        if(families.isEmpty())return true;
        for(var family:families)if(site.families().contains(family.getAsString()))return true;
        return false;
    }
    private static JsonObject override(JsonObject definition,GeologyPlanner.Site site){
        var override=object(object(definition,"placement"),"surfaceFamilyOverride");
        return override.has("family")&&site.families().contains(override.get("family").getAsString())?override:new JsonObject();
    }
    public static double[] absoluteY(JsonObject definition,GeologyPlanner.Site site){
        var override=override(definition,site);
        return numbers(override.has("absoluteY")?override:object(definition,"placement"),"absoluteY");
    }
    public static int centerCover(JsonObject definition,GeologyPlanner.Site site,int fallback){
        return integer(override(definition,site),"centerCover",fallback);
    }
    public static int exteriorCover(JsonObject definition,GeologyPlanner.Site site,int fallback){
        if(!object(definition,"placement").has("surfaceFamilyOverride"))return fallback;
        return integer(override(definition,site),"exteriorCover",fallback);
    }
    /** Intersect with depth below the generator's highest solid surface (surfaceY-1).
     * Unlike legacy surfaceDepthMin/Max, this explicitly composes with absoluteY. */
    public static int[] restrictSurfaceDepth(JsonObject definition,GeologyPlanner.Site site,int low,int high){
        var rules=object(definition,"placement");
        if(!rules.has("surfaceDepth"))return new int[]{low,high};
        double[] depth=numbers(rules,"surfaceDepth");
        long surface=(long)site.surfaceY()-1;
        long a=Math.max((long)low,surface-(int)depth[1]);
        long b=Math.min((long)high,surface-(int)depth[0]);
        return a>b?new int[]{1,0}:new int[]{(int)a,(int)b};
    }
    public static void validate(JsonObject definition,JsonObject biomeFamilies){
        var rules=object(definition,"placement");var required=array(rules,"requiredSurfaceFamilies");
        if(rules.has("surfaceDepth")){
            var depth=numbers(rules,"surfaceDepth");
            if(!rules.has("absoluteY")||depth.length!=2||depth[0]>depth[1])throw new IllegalArgumentException("Surface depth requires ordered interval and absolute Y");
            for(double d:depth)if(!Double.isFinite(d)||d!=Math.rint(d)||d<0||d>256)throw new IllegalArgumentException("Invalid surface depth");
            if(GraphitePlacement.enabled(definition))throw new IllegalArgumentException("Do not combine graphite exception with surface depth");
        }
        for(var f:required)if(!f.isJsonPrimitive()||!biomeFamilies.has(f.getAsString()))throw new IllegalArgumentException("Unknown required surface family");
        if(!rules.has("surfaceFamilyOverride"))return;
        var o=object(rules,"surfaceFamilyOverride");
        if(!rules.has("absoluteY")||!o.has("family")||!contains(required,o.get("family").getAsString()))throw new IllegalArgumentException("Surface override must refine an admitted family with explicit base elevations");
        var band=numbers(o,"absoluteY");
        if(band.length!=2||band[0]>band[1])throw new IllegalArgumentException("Invalid surface override elevation band");
        for(double y:band)if(!Double.isFinite(y)||y!=Math.rint(y)||y< -2048||y>=2032)throw new IllegalArgumentException("Invalid surface override elevation");
        for(String key:new String[]{"centerCover","exteriorCover"}){
            double value=number(o,key,Double.NaN);int minimum=key.equals("centerCover")?1:0;
            if(!Double.isFinite(value)||value!=Math.rint(value)||value<minimum||value>256)throw new IllegalArgumentException("Invalid surface override "+key);
        }
        if(GraphitePlacement.enabled(definition))throw new IllegalArgumentException("Do not combine graphite-depth and surface-family exceptions");
    }
}
