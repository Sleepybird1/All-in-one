package dev.godpc.industrialcolonies.geology;

import net.minecraft.nbt.*;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.ChunkAccess;
import java.util.*;

/** Scan progress saved with the affected chunk's blocks, provenance and retained output. */
public final class MiningChunkProgress {
    public record Range(long start,long end) {}
    private record Entry(MiningScanScope scope,long next) {}
    private final Map<String,Entry> entries=new LinkedHashMap<>();
    public static Range range(MiningScanScope scope,ChunkPos pos){
        var b=scope.bounds();int minX=Math.floorDiv(b.minX(),16),minZ=Math.floorDiv(b.minZ(),16);
        int maxX=Math.floorDiv(b.maxX(),16),maxZ=Math.floorDiv(b.maxZ(),16);
        if(pos.x<minX||pos.x>maxX||pos.z<minZ||pos.z>maxZ)throw new IllegalArgumentException("Chunk outside deposit scan");
        long height=Math.max(0L,Math.min((long)b.maxY()+1,scope.maxBuildYExclusive())-Math.max(b.minY(),scope.minBuildY()));
        long cells=Math.multiplyExact(height,256),index=((long)pos.z-minZ)*((long)maxX-minX+1)+pos.x-minX;
        long start=Math.multiplyExact(index,cells);return new Range(start,Math.addExact(start,cells));
    }
    public synchronized long next(MiningScanScope scope,ChunkPos pos){
        var r=range(scope,pos);var e=entries.get(scope.key());
        if(e==null)return r.start();
        if(!e.scope().equals(scope)||e.next()<r.start()||e.next()>r.end())throw new IllegalStateException("Mining chunk scope changed; migration required");
        return e.next();
    }
    synchronized void advance(MiningScanScope scope,ChunkPos pos,long expected,long target){
        if(next(scope,pos)!=expected||target<=expected||target>range(scope,pos).end())throw new IllegalStateException("Invalid chunk mining progress");
        if(!entries.containsKey(scope.key())&&entries.size()>=128)throw new IllegalStateException("Too many chunk mining scopes");
        entries.put(scope.key(),new Entry(scope,target));
    }
    synchronized void begin(MiningScanScope scope,ChunkPos pos){
        long next=next(scope,pos);
        if(entries.containsKey(scope.key()))return;
        if(entries.size()>=128)throw new IllegalStateException("Too many chunk mining scopes");
        entries.put(scope.key(),new Entry(scope,next));
    }
    public synchronized CompoundTag save(){
        var tag=new CompoundTag();tag.putInt("Version",1);var list=new ListTag();
        for(var e:entries.values()){
            var t=MiningScopeTags.save(e.scope());
            t.putLong("Next",e.next());list.add(t);
        }
        tag.put("Entries",list);return tag;
    }
    public static MiningChunkProgress load(ChunkAccess chunk,CompoundTag tag){
        if(tag.getInt("Version")!=1||!tag.contains("Entries",Tag.TAG_LIST))throw new IllegalArgumentException("Invalid mining chunk progress version/list");
        var raw=(ListTag)tag.get("Entries");
        if(!raw.isEmpty()&&raw.getElementType()!=Tag.TAG_COMPOUND)throw new IllegalArgumentException("Invalid saved mining entry type");
        var list=tag.getList("Entries",Tag.TAG_COMPOUND);if(list.size()>128)throw new IllegalArgumentException("Too many saved mining scopes");
        var result=new MiningChunkProgress();
        for(int i=0;i<list.size();i++){
            var t=list.getCompound(i);
            if(!t.contains("Next",Tag.TAG_LONG))throw new IllegalArgumentException("Missing saved mining cursor");
            var s=MiningScopeTags.load(t);
            var r=range(s,chunk.getPos());long n=t.getLong("Next");
            if(s.minBuildY()!=chunk.getMinBuildHeight()||s.maxBuildYExclusive()!=chunk.getMaxBuildHeight()||n<r.start()||n>r.end()||result.entries.containsKey(s.key()))throw new IllegalArgumentException("Invalid saved mining scope/cursor");
            result.entries.put(s.key(),new Entry(s,n));
        }
        return result;
    }
}
