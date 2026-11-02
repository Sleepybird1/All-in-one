package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.ChunkPos;
import java.util.*;

/** Physical removal into source-chunk custody. The caller must separately enforce drill power and progression. */
public final class MiningPhysicalHarvest {
    public enum Result { RETAINED, OUTPUT_OCCUPIED, NOT_NATURAL_ORE, NO_DROPS, OUTPUT_TOO_LARGE, STALE, REJECTED }
    public enum Recovery { EMPTY, UNLOADED, RETRYABLE, READY, HELD, WRONG_DEPOSIT }
    private static final ThreadLocal<UUID> ACTIVE=new ThreadLocal<>();
    static UUID activeOperation(){return ACTIVE.get();}
    private MiningPhysicalHarvest(){}
    /** Never infers successful removal from a pending record or releases ambiguous items. */
    public static Recovery recover(ServerLevel level,MiningScanScope scope,ChunkPos pos,Set<Block> ores){
        if(!level.getServer().isSameThread()||ACTIVE.get()!=null)throw new IllegalStateException("Recovery requires an idle server thread");
        if(!scope.dimension().equals(level.dimension().location().toString())||scope.minBuildY()!=level.getMinBuildHeight()||scope.maxBuildYExclusive()!=level.getMaxBuildHeight())throw new IllegalArgumentException("Recovery scope mismatch");
        var chunk=level.getChunkSource().getChunkNow(pos.x,pos.z);if(chunk==null)return Recovery.UNLOADED;
        if(!chunk.hasData(MiningOreOwnership.OUTPUT))return Recovery.EMPTY;
        var buffer=chunk.getData(MiningOreOwnership.OUTPUT);if(buffer.state()==MiningHarvestBuffer.State.EMPTY)return Recovery.EMPTY;
        if(!scope.key().equals(buffer.deposit()))return Recovery.WRONG_DEPOSIT;
        if(buffer.state()==MiningHarvestBuffer.State.READY)
            return chunk.getBlockState(buffer.source()).isAir()&&!MiningOreOwnership.owns(chunk,scope,buffer.source())?Recovery.READY:Recovery.HELD;
        if(buffer.state()==MiningHarvestBuffer.State.PREPARED
                &&new MiningTargetProbe(scope,ores).inspect(level,buffer.source()).status()==MiningTargetProbe.Status.NATURAL_ORE){
            buffer.failed(buffer.token(),true);chunk.setUnsaved(true);return Recovery.RETRYABLE;
        }
        return Recovery.HELD;
    }
    public static Result harvest(ServerLevel level,MiningScanScope scope,BlockPos pos,Set<Block> ores,ItemStack tool){
        if(ACTIVE.get()!=null)throw new IllegalStateException("Reentrant mining harvest");
        var probe=new MiningTargetProbe(scope,ores);var found=probe.inspect(level,pos);
        if(found.status()!=MiningTargetProbe.Status.NATURAL_ORE)return Result.NOT_NATURAL_ORE;
        var chunk=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4);
        var buffer=chunk.getData(MiningOreOwnership.OUTPUT);
        if(buffer.state()!=MiningHarvestBuffer.State.EMPTY)return Result.OUTPUT_OCCUPIED;
        var drops=Block.getDrops(found.state(),level,pos,null,null,tool.copy()).stream().filter(s->!s.isEmpty()).map(ItemStack::copy).toList();
        if(drops.isEmpty())return Result.NO_DROPS;
        if(drops.size()>64||drops.stream().anyMatch(s->s.getCount()>s.getMaxStackSize()))return Result.OUTPUT_TOO_LARGE;
        if(!level.getBlockState(pos).equals(found.state())||probe.inspect(level,pos).status()!=MiningTargetProbe.Status.NATURAL_ORE)return Result.STALE;
        UUID token=buffer.prepare(scope.key(),pos,drops);chunk.setUnsaved(true);ACTIVE.set(token);
        try {
            level.setBlock(pos,Blocks.AIR.defaultBlockState(),3);
            return buffer.state()==MiningHarvestBuffer.State.READY?Result.RETAINED:Result.REJECTED;
        }finally{
            ACTIVE.remove();
            boolean unchanged=level.getBlockState(pos).equals(found.state())&&MiningOreOwnership.owns(chunk,scope,pos);
            buffer.failed(token,unchanged);chunk.setUnsaved(true);
        }
    }
}
