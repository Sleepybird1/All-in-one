package dev.godpc.industrialcolonies.geology;

import com.google.gson.JsonObject;
import java.util.*;
import static dev.godpc.industrialcolonies.geology.GeologyConfig.*;
import static dev.godpc.industrialcolonies.geology.GeologyMath.*;

/** Applies existing mineral grades to an already selected, fixed reserve.
 * No size multiplier, presence roll, relocation or additional associated reserve. */
public final class ContinentPlanComposition {
    public static GeologyPlanner.Plan compose(GeologyPlanner.Plan geometry,GeologyPlanner planner,JsonObject settings) {
        Objects.requireNonNull(geometry);Objects.requireNonNull(planner);Objects.requireNonNull(settings);
        int reserve=geometry.intendedSize();
        if(reserve<1||reserve>FiniteOreLimits.MAX_BLOCKS)throw new IllegalArgumentException("Earth reserve must be within 1..300000");
        var c=geometry.candidate();var d=geometry.definition().deepCopy();
        double suitability=(planner.biomeWeight(d,c.site())+planner.depthWeight(d,c.y()))/2;
        if(!Double.isFinite(suitability)||suitability<0)throw new IllegalArgumentException("Invalid mineral suitability");
        double[] probabilities=planner.qualityProbabilities(suitability);
        if(probabilities.length!=4)throw new IllegalArgumentException("Four existing mineral grades required");
        double sum=0;
        for(double p:probabilities){if(!Double.isFinite(p)||p<0)throw new IllegalArgumentException("Invalid grade weight");sum+=p;}
        if(!Double.isFinite(sum)||sum<=0)throw new IllegalArgumentException("Empty grade distribution");
        int quality=weighted(probabilities,unit(c.seed()+22));
        double[] multipliers=numbers(object(settings,"quality"),"richMultipliers");
        if(multipliers.length!=4)throw new IllegalArgumentException("Four rich multipliers required");
        for(double p:multipliers)if(!Double.isFinite(p)||p<0)throw new IllegalArgumentException("Invalid rich multiplier");
        double base=number(d,"normalRichOrePercent",0);
        if(!Double.isFinite(base)||base<0||base>1)throw new IllegalArgumentException("Invalid rich fraction");
        double rich=Math.min(1,base*multipliers[quality]);
        if(array(d,"richOres").isEmpty())rich=0;
        // Associated rules are retained verbatim in the copied definition. The existing
        // writer replaces cells inside this same body, never appends another volume.
        return new GeologyPlanner.Plan(c,d,quality,reserve,reserve,suitability,rich,List.copyOf(geometry.eligibleFamilies()));
    }
    private ContinentPlanComposition(){}
}
