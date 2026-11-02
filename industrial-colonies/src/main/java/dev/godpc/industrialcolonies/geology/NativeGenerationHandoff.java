package dev.godpc.industrialcolonies.geology;

import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;

/** Unregistered CARVERS future continuation. Uses the same native prioritized main
 * mailbox as FULL conversion; never joins a future or blocks a generation worker.
 * A caller's step must be bounded and must not request chunks it is holding. */
public final class NativeGenerationHandoff {
    @FunctionalInterface public interface Step { boolean advance() throws Exception; }
    public static CompletableFuture<ChunkAccess> afterCarvers(WorldGenContext context,ChunkStep step,
            StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,CompletableFuture<ChunkAccess> original,
            Supplier<? extends Step> work) {
        Objects.requireNonNull(context);Objects.requireNonNull(step);Objects.requireNonNull(cache);
        Objects.requireNonNull(owner);Objects.requireNonNull(original);Objects.requireNonNull(work);
        if(step.targetStatus()!=ChunkStatus.CARVERS)throw new IllegalArgumentException("CARVERS owner required");
        var result=new CompletableFuture<ChunkAccess>();
        original.whenComplete((generated,failure)->{
            if(result.isDone())return;
            if(failure!=null){result.completeExceptionally(failure);return;}
            if(generated!=owner){result.completeExceptionally(new IllegalStateException("Generation owner changed"));return;}
            var position=owner.getPos();
            try {
                var holder=Objects.requireNonNull(cache.get(position.x,position.z));
                new Job(context,holder,owner,work,result).post();
            }catch(Throwable error){result.completeExceptionally(error);}
        });
        return result;
    }
    private static final class Job implements Runnable {
        final WorldGenContext context;final GenerationChunkHolder holder;final ChunkAccess owner;
        final Supplier<? extends Step> factory;final CompletableFuture<ChunkAccess> result;
        Step work;
        Job(WorldGenContext context,GenerationChunkHolder holder,ChunkAccess owner,Supplier<? extends Step> factory,CompletableFuture<ChunkAccess> result){
            this.context=context;this.holder=holder;this.owner=owner;this.factory=factory;this.result=result;
        }
        void post(){
            if(result.isDone())return;
            try {context.mainThreadMailBox().tell(ChunkTaskPriorityQueueSorter.message(this,owner.getPos().toLong(),holder::getTicketLevel));}
            catch(Throwable error){result.completeExceptionally(error);}
        }
        @Override public void run(){
            if(result.isDone())return;
            try {
                if(!context.level().getServer().isSameThread())throw new IllegalStateException("Native main mailbox ran off server thread");
                if(owner.isUpgrading()||!owner.getPersistedStatus().isBefore(ChunkStatus.CARVERS))
                    throw new IllegalStateException("Cannot retrofit or advance an already completed owner");
                if(work==null)work=Objects.requireNonNull(factory.get());
                if(work.advance())result.complete(owner);else post();
            }catch(NativeTerrainYield.Pending pending){
                pending.ready().whenComplete((ignored,failure)->{if(failure!=null)result.completeExceptionally(failure);else post();});
            }catch(Throwable error){result.completeExceptionally(error);}
        }
    }
    private NativeGenerationHandoff(){}
}
