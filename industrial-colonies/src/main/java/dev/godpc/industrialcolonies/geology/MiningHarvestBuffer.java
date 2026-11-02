package dev.godpc.industrialcolonies.geology;

import net.minecraft.core.*;
import net.minecraft.nbt.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.chunk.ChunkAccess;
import java.util.*;

/** One bounded retained batch in the source chunk. Extraction requires the current operation token. */
public final class MiningHarvestBuffer {
    public enum State { EMPTY, PREPARED, READY, CONFLICTED }
    private State state=State.EMPTY;
    private UUID token;
    private String deposit;
    private BlockPos source;
    private List<ItemStack> drops=List.of();
    public synchronized State state(){return state;}
    public synchronized List<ItemStack> snapshot(){return drops.stream().map(ItemStack::copy).toList();}
    public synchronized UUID token(){return token;}
    public synchronized BlockPos source(){return source;}
    public synchronized String deposit(){return deposit;}
    synchronized ItemStack extract(UUID operation,int slot,int amount,boolean simulate){
        if(state!=State.READY||!Objects.equals(token,operation)||slot<0||slot>=drops.size()||amount<=0)return ItemStack.EMPTY;
        var stack=drops.get(slot);int count=Math.min(amount,stack.getCount());
        var result=stack.copyWithCount(count);
        if(!simulate){
            var remaining=new ArrayList<>(drops);var rest=stack.copy();rest.shrink(count);
            if(rest.isEmpty())remaining.remove(slot);else remaining.set(slot,rest);
            drops=List.copyOf(remaining);
            if(drops.isEmpty()){state=State.EMPTY;token=null;deposit=null;source=null;}
        }
        return result;
    }
    synchronized UUID prepare(String key,BlockPos pos,List<ItemStack> items){
        if(state!=State.EMPTY)throw new IllegalStateException("Retained mining output is occupied");
        if(key==null||!key.matches("[0-9a-f]{64}")||items.isEmpty()||items.size()>64
                ||items.stream().anyMatch(s->s.isEmpty()||s.getCount()>s.getMaxStackSize()))throw new IllegalArgumentException("Invalid retained drops");
        token=UUID.randomUUID();deposit=key;source=pos.immutable();drops=items.stream().map(ItemStack::copy).toList();state=State.PREPARED;return token;
    }
    synchronized void sourceChanged(BlockPos pos,boolean air,UUID active){
        if(state==State.PREPARED&&source.equals(pos))state=air&&token.equals(active)?State.READY:State.CONFLICTED;
    }
    synchronized void failed(UUID operation,boolean unchanged){
        if(state!=State.PREPARED||!Objects.equals(token,operation))return;
        if(unchanged){state=State.EMPTY;token=null;deposit=null;source=null;drops=List.of();}else state=State.CONFLICTED;
    }
    public synchronized CompoundTag save(HolderLookup.Provider registries){
        var tag=new CompoundTag();tag.putInt("Version",1);tag.putString("State",state.name());
        if(state!=State.EMPTY){tag.putUUID("Token",token);tag.putString("Deposit",deposit);tag.putLong("Source",source.asLong());var list=new ListTag();for(var item:drops)list.add(item.save(registries));tag.put("Drops",list);}
        return tag;
    }
    public static MiningHarvestBuffer load(ChunkAccess chunk,CompoundTag tag,HolderLookup.Provider registries){
        if(tag.getInt("Version")!=1)throw new IllegalArgumentException("Unsupported harvest custody version");
        State state=State.valueOf(tag.getString("State"));var buffer=new MiningHarvestBuffer();if(state==State.EMPTY)return buffer;
        var source=BlockPos.of(tag.getLong("Source"));
        if((source.getX()>>4)!=chunk.getPos().x||(source.getZ()>>4)!=chunk.getPos().z||source.getY()<chunk.getMinBuildHeight()||source.getY()>=chunk.getMaxBuildHeight())throw new IllegalArgumentException("Foreign retained mining source");
        var list=tag.getList("Drops",Tag.TAG_COMPOUND);var items=new ArrayList<ItemStack>();if(list.size()>64)throw new IllegalArgumentException("Oversized retained mining batch");
        for(int i=0;i<list.size();i++){var stack=ItemStack.parseOptional(registries,list.getCompound(i));if(stack.isEmpty())throw new IllegalArgumentException("Invalid saved mining drop");items.add(stack);}
        buffer.prepare(tag.getString("Deposit"),source,items);buffer.token=tag.getUUID("Token");buffer.state=state;return buffer;
    }
}
