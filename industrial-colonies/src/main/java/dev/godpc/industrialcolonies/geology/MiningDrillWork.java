package dev.godpc.industrialcolonies.geology;

import com.simibubi.create.content.kinetics.drill.DrillBlock;
import com.simibubi.create.content.kinetics.drill.DrillBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import java.util.Set;

/** Physical power gate. The node caller must supply its authenticated saved mine scope and work cadence. */
public final class MiningDrillWork {
    public enum Status { UNLOADED, NO_DRILL, WRONG_FACING, UNPOWERED, WORK }
    public record Result(Status status,MiningChunkWork.Result work) {}
    private MiningDrillWork(){}
    public static Result step(ServerLevel level,BlockPos node,BlockPos drillPos,MiningScanScope scope,ChunkPos target,int budget,Set<Block> ores){
        var status=inspect(level,node,drillPos);if(status!=Status.WORK)return new Result(status,null);
        return new Result(Status.WORK,MiningChunkWork.step(level,scope,target,budget,ores,ItemStack.EMPTY));
    }
    public static Status inspect(ServerLevel level,BlockPos node,BlockPos drillPos){
        if(!level.getServer().isSameThread())throw new IllegalStateException("Drill work requires server thread");
        var drillChunk=level.getChunkSource().getChunkNow(drillPos.getX()>>4,drillPos.getZ()>>4);
        if(drillChunk==null||level.getChunkSource().getChunkNow(node.getX()>>4,node.getZ()>>4)==null)return Status.UNLOADED;
        var state=drillChunk.getBlockState(drillPos);
        if(!(state.getBlock() instanceof DrillBlock)||!(drillChunk.getBlockEntity(drillPos) instanceof DrillBlockEntity drill)||drill.isRemoved())return Status.NO_DRILL;
        if(!drillPos.relative(state.getValue(DrillBlock.FACING)).equals(node))return Status.WRONG_FACING;
        float speed=drill.getSpeed();
        return !Float.isFinite(speed)||speed==0?Status.UNPOWERED:Status.WORK;
    }
}
