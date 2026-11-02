package dev.godpc.industrialcolonies.geology;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.LevelChunk;
import net.neoforged.neoforge.items.IItemHandler;
import java.util.UUID;

/** Extraction-only view of one retained operation. Does not load chunks or deliver into another inventory. */
public final class MiningOutputAccess implements IItemHandler {
    private final ServerLevel level;
    private final MiningScanScope scope;
    private final ChunkPos pos;
    private final UUID operation;
    public MiningOutputAccess(ServerLevel level,MiningScanScope scope,ChunkPos pos){
        this.level=level;this.scope=scope;this.pos=pos;
        var chunk=chunk();
        operation=chunk!=null&&chunk.hasData(MiningOreOwnership.OUTPUT)?chunk.getData(MiningOreOwnership.OUTPUT).token():null;
    }
    private LevelChunk chunk(){
        if(!level.getServer().isSameThread())throw new IllegalStateException("Mining output requires server thread");
        if(!scope.dimension().equals(level.dimension().location().toString())||scope.minBuildY()!=level.getMinBuildHeight()||scope.maxBuildYExclusive()!=level.getMaxBuildHeight())throw new IllegalArgumentException("Mining output scope mismatch");
        return level.getChunkSource().getChunkNow(pos.x,pos.z);
    }
    private MiningHarvestBuffer ready(LevelChunk chunk){
        if(operation==null||chunk==null||!chunk.hasData(MiningOreOwnership.OUTPUT))return null;
        var buffer=chunk.getData(MiningOreOwnership.OUTPUT);
        return buffer.state()==MiningHarvestBuffer.State.READY&&operation.equals(buffer.token())&&scope.key().equals(buffer.deposit())
            &&chunk.getBlockState(buffer.source()).isAir()&&!MiningOreOwnership.owns(chunk,scope,buffer.source())?buffer:null;
    }
    private static void slot(int slot){if(slot<0||slot>=64)throw new IndexOutOfBoundsException("Mining output slot "+slot);}
    @Override public int getSlots(){return 64;}
    @Override public ItemStack getStackInSlot(int slot){
        slot(slot);var buffer=ready(chunk());if(buffer==null)return ItemStack.EMPTY;
        var items=buffer.snapshot();return slot<items.size()?items.get(slot):ItemStack.EMPTY;
    }
    @Override public ItemStack insertItem(int slot,ItemStack stack,boolean simulate){slot(slot);return stack.copy();}
    @Override public ItemStack extractItem(int slot,int amount,boolean simulate){
        slot(slot);var chunk=chunk();var buffer=ready(chunk);if(buffer==null)return ItemStack.EMPTY;
        var result=buffer.extract(operation,slot,amount,simulate);
        if(!simulate&&!result.isEmpty())chunk.setUnsaved(true);
        return result;
    }
    @Override public int getSlotLimit(int slot){slot(slot);return 64;}
    @Override public boolean isItemValid(int slot,ItemStack stack){slot(slot);return false;}
}
