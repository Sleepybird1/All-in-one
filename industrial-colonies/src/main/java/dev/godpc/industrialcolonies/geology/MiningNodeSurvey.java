package dev.godpc.industrialcolonies.geology;

import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;

/** Tick-sliced physical observations. No chunk requests, predicted reserves or persisted count authority. */
public final class MiningNodeSurvey {
    private MiningNodeSurvey() {}
    public record Result(boolean complete,Map<String,Long> blocks,String status) {
        public Result {blocks=Map.copyOf(blocks);}
        public long total(){return blocks.values().stream().mapToLong(Long::longValue).reduce(0L,Math::addExact);}
    }
    private record Proof(long chunk,MiningOreLedger ledger,long revision) {}
    public static final class Session {
        private final ServerLevel level;
        private final MiningScanScope scope;
        private final Set<Block> palette;
        private final List<Long> chunks;
        private final List<Proof> proofs=new ArrayList<>();
        private final Map<String,Long> counts=new TreeMap<>();
        private int chunkIndex,nextCell;
        private BitSet cells;
        private Proof active;
        private boolean incomplete,finished;
        private Result result=new Result(false,Map.of(),"Counting");
        public Session(ServerLevel level,MiningScanScope scope,Set<Block> palette){
            requireThread(level);this.level=level;this.scope=scope;this.palette=Set.copyOf(palette);
            if(!scope.dimension().equals(level.dimension().location().toString())||scope.minBuildY()!=level.getMinBuildHeight()||scope.maxBuildYExclusive()!=level.getMaxBuildHeight())throw new IllegalArgumentException("Survey scope mismatch");
            chunks=scope.observationChunks();
        }
        private static void requireThread(ServerLevel level){if(!level.getServer().isSameThread())throw new IllegalStateException("Server thread required");}
        public Result result(){requireThread(level);return result.complete()&&!valid()?new Result(false,result.blocks(),"Not fully counted"):result;}
        public boolean finished(){return finished;}
        private boolean unchanged(Proof proof){
            var chunk=level.getChunkSource().getChunkNow(ChunkPos.getX(proof.chunk()),ChunkPos.getZ(proof.chunk()));
            return chunk!=null&&chunk.hasData(MiningOreOwnership.LEDGER)&&chunk.getData(MiningOreOwnership.LEDGER)==proof.ledger()
                    &&proof.ledger().sealed()&&!proof.ledger().failed()&&proof.ledger().revision()==proof.revision();
        }
        public boolean valid(){requireThread(level);return finished&&result.complete()&&proofs.stream().allMatch(this::unchanged);}
        public void tick(int budget){
            requireThread(level);if(finished)return;if(budget<1||budget>4096)throw new IllegalArgumentException("Survey budget 1..4096");
            int chunkBudget=64;
            while(budget>0&&chunkBudget>0){
                if(cells==null){
                    if(chunkIndex==chunks.size()){finish();return;}
                    chunkBudget--;long key=chunks.get(chunkIndex++);
                    var chunk=level.getChunkSource().getChunkNow(ChunkPos.getX(key),ChunkPos.getZ(key));
                    if(chunk==null||!chunk.hasData(MiningOreOwnership.LEDGER)){incomplete=true;continue;}
                    var ledger=chunk.getData(MiningOreOwnership.LEDGER);var snapshot=ledger.snapshot(scope.key());
                    if(!snapshot.complete()){incomplete=true;continue;}
                    active=new Proof(key,ledger,snapshot.revision());proofs.add(active);cells=snapshot.cells();nextCell=cells.nextSetBit(0);
                }
                if(nextCell<0){cells=null;active=null;continue;}
                budget--;int index=nextCell;nextCell=cells.nextSetBit(index+1);
                if(!unchanged(active)){incomplete=true;cells=null;active=null;continue;}
                int x=(ChunkPos.getX(active.chunk())<<4)+(index&15),z=(ChunkPos.getZ(active.chunk())<<4)+((index>>>4)&15),y=scope.minBuildY()+index/256;
                if(!scope.contains(x,y,z)){incomplete=true;continue;}
                var chunk=level.getChunkSource().getChunkNow(x>>4,z>>4);
                var state=chunk.getBlockState(new BlockPos(x,y,z));
                if(!palette.contains(state.getBlock())||state.isAir()){incomplete=true;continue;}
                counts.merge(BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString(),1L,Math::addExact);
            }
        }
        private void finish(){
            boolean stable=proofs.stream().allMatch(this::unchanged);
            boolean complete=!incomplete&&stable&&proofs.size()==chunks.size();
            result=new Result(complete,counts,complete?"Counted":"Not fully counted");finished=true;
        }
    }
}
