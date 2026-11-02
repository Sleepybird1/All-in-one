package dev.godpc.industrialcolonies.geology;

import com.google.gson.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;

/** Opt-in separation without a second resource roll or a new diamond height distribution. */
public final class GraphitePlacement {
    public static final String DIAMOND="industrial_colonies:diamond_ore";
    private GraphitePlacement() {}
    public static boolean enabled(JsonObject definition){
        return bool(object(definition,"placement"),"diamondDepthException",false);
    }
    public static boolean ordinary(JsonObject definition,int y){
        double[] band=numbers(object(definition,"placement"),"absoluteY");
        return y>=band[0]&&y<=band[1];
    }
    public static boolean diamondDepth(JsonObject definition,int y){
        if(!enabled(definition))return false;
        for(var e:array(definition,"associated")){
            JsonObject rule=e.getAsJsonObject();
            if(!DIAMOND.equals(string(rule,"block","")))continue;
            for(var b:array(rule,"depthBands")){
                JsonObject band=b.getAsJsonObject();
                if(y>=integer(band,"minY",0)&&y<=integer(band,"maxY",0)){
                    for(double fraction:numbers(band,"byQuality"))if(fraction>0)return true;
                }
            }
        }
        return false;
    }
    public static void validate(JsonObject definition){
        if(!enabled(definition))return;
        if(!"graphite_rock".equals(string(definition,"id",""))
                ||!"industrial_colonies:graphite_rock".equals(string(definition,"hostRock",""))
                ||!object(definition,"placement").has("absoluteY")
                ||array(definition,"associated").size()!=1||!array(definition,"richOres").isEmpty()
                ||bool(object(definition,"micro"),"enabled",false))
            throw new IllegalArgumentException("Diamond-depth exception requires the single graphite/diamond host route and no graphite micro route");
        var rule=array(definition,"associated").get(0).getAsJsonObject();
        if(!DIAMOND.equals(string(rule,"block",""))||!"depth_percentage".equals(string(rule,"type",""))||array(rule,"depthBands").isEmpty())
            throw new IllegalArgumentException("Diamond-depth exception requires explicit existing diamond depth bands");
        for(var b:array(rule,"depthBands")){
            JsonObject band=b.getAsJsonObject();
            if(integer(band,"maxY",0)>=numbers(object(definition,"placement"),"absoluteY")[0])
                throw new IllegalArgumentException("Diamond-associated and ordinary graphite bands must not overlap");
        }
    }
}
