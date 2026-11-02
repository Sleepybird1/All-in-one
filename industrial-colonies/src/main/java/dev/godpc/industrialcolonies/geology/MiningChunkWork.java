package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import java.util.Set;

/** One bounded controller step. Call only after the physical controller has authorized power/work. */
public final class MiningChunkWork {
    public enum Status { UNLOADED, BUDGET, RETAINED, OUTPUT_BLOCKED, ORE_BLOCKED, COMPLETE }
    public record Result(Status status,int inspected,long nextIndex) {}
    private MiningChunkWork(){}
    public static Result step(ServerLevel level,MiningScanScope scope,ChunkPos pos,int budget,Set<Block> ores,ItemStack tool){
        if(budget<1||budget>4096)throw new IllegalArgumentException("Mining budget must be 1..4096");
        if(!level.getServer().isSameThread())throw new IllegalStateException("Mining work requires server thread");
        if(!scope.dimension().equals(level.dimension().location().toString())||scope.minBuildY()!=level.getMinBuildHeight()||scope.maxBuildYExclusive()!=level.getMaxBuildHeight())throw new IllegalArgumentException("Mining work scope mismatch");
        var range=MiningChunkProgress.range(scope,pos);var probe=new MiningTargetProbe(scope,ores);
        var chunk=level.getChunkSource().getChunkNow(pos.x,pos.z);if(chunk==null)return new Result(Status.UNLOADED,0,-1);
        var progress=chunk.getData(MiningOreOwnership.PROGRESS);long next=progress.next(scope,pos);
        var recovery=MiningPhysicalHarvest.recover(level,scope,pos,ores);
        if(recovery!=MiningPhysicalHarvest.Recovery.EMPTY&&recovery!=MiningPhysicalHarvest.Recovery.RETRYABLE)return new Result(Status.OUTPUT_BLOCKED,0,next);
        // Reserve scope capacity before any physical removal can occur.
        progress.begin(scope,pos);chunk.setUnsaved(true);
        int remaining=chunk.hasData(MiningOreOwnership.LEDGER)?chunk.getData(MiningOreOwnership.LEDGER).remaining(scope.key()):0;
        if(remaining<0)return new Result(Status.ORE_BLOCKED,0,next);
        if(remaining==0){
            if(next<range.end()){progress.advance(scope,pos,next,range.end());chunk.setUnsaved(true);}
            return new Result(Status.COMPLETE,0,range.end());
        }
        int inspected=0;
        while(next<range.end()&&inspected<budget){
            var p=scope.cursor(next).current();var target=new BlockPos(p.x(),p.y(),p.z());
            var found=probe.inspect(level,target);inspected++;
            if(found.status()==MiningTargetProbe.Status.UNLOADED)return new Result(Status.UNLOADED,inspected,next);
            boolean ore=found.status()==MiningTargetProbe.Status.NATURAL_ORE;
            if(ore&&MiningPhysicalHarvest.harvest(level,scope,target,ores,tool)!=MiningPhysicalHarvest.Result.RETAINED)return new Result(Status.ORE_BLOCKED,inspected,next);
            // A snapshot taken during removal can only retain an older cursor, which safely rescans.
            progress.advance(scope,pos,next,next+1);next++;chunk.setUnsaved(true);
            if(ore)return new Result(Status.RETAINED,inspected,next);
        }
        return new Result(next==range.end()?Status.COMPLETE:Status.BUDGET,inspected,next);
    }
}
