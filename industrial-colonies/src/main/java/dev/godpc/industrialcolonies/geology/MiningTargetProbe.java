package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import java.util.Set;

/** Read-only physical target discovery. CANDIDATE is not proof of natural provenance or permission to mine. */
public final class MiningTargetProbe {
    public enum Status { OUTSIDE, UNLOADED, NOT_ORE, BLOCK_ENTITY, CANDIDATE, NATURAL_ORE }
    public record Result(Status status,BlockState state) {}
    private final MiningScanScope scope;
    private final Set<Block> ores;
    public MiningTargetProbe(MiningScanScope scope,Set<Block> ores) {
        this.scope=java.util.Objects.requireNonNull(scope);
        this.ores=Set.copyOf(ores);
        if(this.ores.isEmpty())throw new IllegalArgumentException("Empty mining ore palette");
    }
    /** Never loads a chunk, evaluates loot, changes a block or advances extraction progress. */
    public Result inspect(ServerLevel level,BlockPos pos) {
        if(!level.getServer().isSameThread())throw new IllegalStateException("Mining probe requires the server thread");
        if(!level.dimension().location().toString().equals(scope.dimension())
                ||level.getMinBuildHeight()!=scope.minBuildY()||level.getMaxBuildHeight()!=scope.maxBuildYExclusive())
            throw new IllegalArgumentException("Mining scope does not match this native level");
        int x=pos.getX(),y=pos.getY(),z=pos.getZ();
        if(y<=scope.minBuildY()||y>=scope.maxBuildYExclusive()-1
                ||!scope.bounds().contains(x,y,z)||!scope.contains(x,y,z))
            return new Result(Status.OUTSIDE,null);
        var chunk=level.getChunkSource().getChunkNow(x>>4,z>>4);
        if(chunk==null)return new Result(Status.UNLOADED,null);
        var state=chunk.getBlockState(pos);
        if(state.hasBlockEntity())return new Result(Status.BLOCK_ENTITY,state);
        if(state.isAir()||!state.getFluidState().isEmpty()||!ores.contains(state.getBlock())
                ||state.getDestroySpeed(level,pos)<0)return new Result(Status.NOT_ORE,state);
        return new Result(MiningOreOwnership.owns(chunk,scope,pos)?Status.NATURAL_ORE:Status.CANDIDATE,state);
    }
}
