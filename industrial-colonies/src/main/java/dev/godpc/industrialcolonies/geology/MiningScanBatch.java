package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import java.util.Set;

/** Bounded, read-only discovery. Returned scan progress is speculative, never a durable mining commit. */
public final class MiningScanBatch {
    public enum Status { BUDGET, EXHAUSTED, UNLOADED, TARGET }
    public record Result(Status status,long nextIndex,int inspected,BlockPos target) {}
    private MiningScanBatch(){}
    public static Result scan(ServerLevel level,MiningScanScope scope,long next,int budget,Set<Block> ores){
        if(budget<1||budget>4096)throw new IllegalArgumentException("Mining scan budget must be 1..4096");
        if(!level.getServer().isSameThread())throw new IllegalStateException("Mining scan requires server thread");
        if(!scope.dimension().equals(level.dimension().location().toString())||scope.minBuildY()!=level.getMinBuildHeight()||scope.maxBuildYExclusive()!=level.getMaxBuildHeight())throw new IllegalArgumentException("Mining scan scope mismatch");
        var cursor=scope.cursor(next);var probe=new MiningTargetProbe(scope,ores);int inspected=0;
        while(!cursor.exhausted()&&inspected<budget){
            var p=cursor.current();var pos=new BlockPos(p.x(),p.y(),p.z());
            var found=probe.inspect(level,pos);inspected++;
            if(found.status()==MiningTargetProbe.Status.UNLOADED)return new Result(Status.UNLOADED,cursor.nextIndex(),inspected,pos);
            if(found.status()==MiningTargetProbe.Status.NATURAL_ORE)return new Result(Status.TARGET,cursor.nextIndex(),inspected,pos);
            cursor.advance(cursor.nextIndex());
        }
        return new Result(cursor.exhausted()?Status.EXHAUSTED:Status.BUDGET,cursor.nextIndex(),inspected,null);
    }
}
