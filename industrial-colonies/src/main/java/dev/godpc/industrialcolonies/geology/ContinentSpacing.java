package dev.godpc.industrialcolonies.geology;

import java.util.*;

/** Immutable preceding reservations, fixed before a family's search starts. */
public record ContinentSpacing(int minimumDistance,List<Center> preceding) {
    public record Center(String family,int x,int z) {
        public Center {
            if(family==null||!family.matches("[a-z0-9_]+")||Math.abs((long)x)>ContinentEnvelope.LIMIT||Math.abs((long)z)>ContinentEnvelope.LIMIT)
                throw new IllegalArgumentException("Invalid reservation center");
        }
    }
    public ContinentSpacing {
        if(minimumDistance<0||minimumDistance>100000)throw new IllegalArgumentException("Spacing0..100000 required");
        preceding=preceding.stream().sorted(Comparator.comparing(Center::family)).toList();
        if(preceding.stream().map(Center::family).distinct().count()!=preceding.size())throw new IllegalArgumentException("Duplicate prior family");
    }
    public boolean allows(int x,int z){
        for(var c:preceding){
            long dx=(long)x-c.x(),dz=(long)z-c.z();
            // Only square bounded near distances; far coordinates cannot overflow.
            if(Math.abs(dx)>=minimumDistance||Math.abs(dz)>=minimumDistance)continue;
            if(dx*dx+dz*dz<(long)minimumDistance*minimumDistance)return false;
        }
        return true;
    }
}
