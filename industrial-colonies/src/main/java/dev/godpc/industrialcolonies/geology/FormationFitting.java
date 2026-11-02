package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.function.BiFunction;

/** Translate a whole finite formation vertically; never shrink, clip, reroll or write terrain. */
public final class FormationFitting {
    private FormationFitting() {}
    public record Column(int minimumY,int maximumY) {}
    public record Result(boolean fits,int centerY,int sampledColumns,String reason) {}
    private record Extent(int x,int z,int low,int high) {}
    /** Validate this exact center; an invalid saved location must never clamp to another Y. */
    public static Result at(int x,int centerY,int z,List<GeologyMath.Voxel> shape,
                            Column centerBounds,BiFunction<Integer,Integer,Column> terrain){
        return fit(x,centerY,z,shape,new Column(Math.max(centerBounds.minimumY(),centerY),
                Math.min(centerBounds.maximumY(),centerY)),terrain);
    }
    public static Result fit(int x,int preferredY,int z,List<GeologyMath.Voxel> shape,
                             Column centerBounds,BiFunction<Integer,Integer,Column> terrain){
        Objects.requireNonNull(shape);Objects.requireNonNull(centerBounds);Objects.requireNonNull(terrain);
        if(shape.isEmpty()||shape.size()>FiniteOreLimits.MAX_BLOCKS)throw new IllegalArgumentException("Finite formation must contain 1..300000 positions");
        Map<Long,Extent> columns=new HashMap<>();
        for(var p:shape){
            long wx=(long)x+p.x(),wz=(long)z+p.z();
            if(wx<Integer.MIN_VALUE||wx>Integer.MAX_VALUE||wz<Integer.MIN_VALUE||wz>Integer.MAX_VALUE)
                return new Result(false,preferredY,0,"coordinate overflow");
            long key=(wx<<32)^(wz&0xffffffffL);var previous=columns.get(key);
            columns.put(key,new Extent((int)wx,(int)wz,previous==null?p.y():Math.min(previous.low,p.y()),previous==null?p.y():Math.max(previous.high,p.y())));
        }
        long low=centerBounds.minimumY,high=centerBounds.maximumY;int sampled=0;
        // Fixed traversal makes diagnostics and early refusals independent of hash iteration order.
        var ordered=new ArrayList<>(columns.values());ordered.sort(Comparator.comparingInt(Extent::x).thenComparingInt(Extent::z));
        for(var c:ordered){
            Column allowed=terrain.apply(c.x,c.z);sampled++;
            if(allowed==null||allowed.minimumY>allowed.maximumY)return new Result(false,preferredY,sampled,"ineligible terrain column");
            low=Math.max(low,(long)allowed.minimumY-c.low);high=Math.min(high,(long)allowed.maximumY-c.high);
            if(low>high)return new Result(false,preferredY,sampled,"no whole-formation vertical interval");
        }
        if(low>high||low<Integer.MIN_VALUE||high>Integer.MAX_VALUE)return new Result(false,preferredY,sampled,"invalid center interval");
        return new Result(true,(int)Math.max(low,Math.min(high,preferredY)),sampled,"fitted");
    }
}
