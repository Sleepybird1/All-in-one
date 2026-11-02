package dev.godpc.industrialcolonies.geology;

import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.*;

/** Unregistered prerequisite before native FEATURES for an already reserved surface transaction.
 * The caller supplies validated saved selections; this bridge never chooses deposits or loads chunks. */
public final class NativeSurfaceHandoff {
    @FunctionalInterface public interface SavedIntent { CinnabarOwnerPlacement.Intent read() throws Exception; }
    private NativeSurfaceHandoff() {}

    public static CompletableFuture<ChunkAccess> beforeFeatures(WorldGenContext context,ChunkStep step,
            StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,CinnabarOwnerPlacement.Intent intent,
            Supplier<CompletableFuture<ChunkAccess>> original,Supplier<? extends NativeGenerationHandoff.Step> work) {
        Objects.requireNonNull(context);Objects.requireNonNull(step);Objects.requireNonNull(cache);
        Objects.requireNonNull(owner);Objects.requireNonNull(intent);Objects.requireNonNull(original);Objects.requireNonNull(work);
        if(step.targetStatus()!=ChunkStatus.FEATURES||intent.chunkX()!=owner.getPos().x||intent.chunkZ()!=owner.getPos().z)
            throw new IllegalArgumentException("Exact FEATURES surface owner required");
        return beforeSavedFeatures(context,step,cache,owner,()->intent,original,work);
    }
    /** Resolve saved authority only after entering the server mailbox; never on a generation worker. */
    public static CompletableFuture<ChunkAccess> beforeSavedFeatures(WorldGenContext context,ChunkStep step,
            StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,SavedIntent intent,
            Supplier<CompletableFuture<ChunkAccess>> original,Supplier<? extends NativeGenerationHandoff.Step> work) {
        Objects.requireNonNull(context);Objects.requireNonNull(step);Objects.requireNonNull(cache);
        Objects.requireNonNull(owner);Objects.requireNonNull(intent);Objects.requireNonNull(original);Objects.requireNonNull(work);
        if(step.targetStatus()!=ChunkStatus.FEATURES)throw new IllegalArgumentException("FEATURES surface phase required");
        var result=new CompletableFuture<ChunkAccess>();
        var pos=owner.getPos();var holder=Objects.requireNonNull(cache.get(pos.x,pos.z));
        new Job(context,holder,owner,intent,work,original,result).post();
        return result;
    }
    private static final class Job implements Runnable {
        final WorldGenContext context;final GenerationChunkHolder holder;final ChunkAccess owner;
        final SavedIntent savedIntent;CinnabarOwnerPlacement.Intent intent;final Supplier<? extends NativeGenerationHandoff.Step> factory;
        final Supplier<CompletableFuture<ChunkAccess>> original;
        final CompletableFuture<ChunkAccess> result;NativeGenerationHandoff.Step work;boolean invoked;
        Job(WorldGenContext context,GenerationChunkHolder holder,ChunkAccess owner,SavedIntent intent,
                Supplier<? extends NativeGenerationHandoff.Step> factory,Supplier<CompletableFuture<ChunkAccess>> original,
                CompletableFuture<ChunkAccess> result){
            this.context=context;this.holder=holder;this.owner=owner;this.savedIntent=intent;this.factory=factory;this.original=original;this.result=result;
        }
        void post(){
            if(result.isDone())return;
            try{context.mainThreadMailBox().tell(ChunkTaskPriorityQueueSorter.message(this,owner.getPos().toLong(),holder::getTicketLevel));}
            catch(Throwable error){result.completeExceptionally(error);}
        }
        @Override public void run(){
            if(result.isDone())return;
            try{
                if(!context.level().getServer().isSameThread())throw new IllegalStateException("Surface mailbox ran off server thread");
                if(invoked)throw new IllegalStateException("Native features already invoked");
                if(!(owner instanceof ProtoChunk)||owner instanceof ImposterProtoChunk||owner.isUpgrading()
                        ||owner.getPersistedStatus().isBefore(ChunkStatus.CARVERS)||!owner.getPersistedStatus().isBefore(ChunkStatus.FEATURES)
                        ||!owner.hasData(MiningOreOwnership.LEDGER))throw new IllegalStateException("Fresh native surface phase required");
                var ledger=owner.getData(MiningOreOwnership.LEDGER);
                if(intent==null)intent=Objects.requireNonNull(savedIntent.read());
                if(intent.chunkX()!=owner.getPos().x||intent.chunkZ()!=owner.getPos().z)throw new IllegalStateException("Foreign saved surface owner");
                if(ledger.failed()||ledger.sealed()||!ledger.surfacePending(intent.identity()))
                    throw new IllegalStateException("Original open shared surface intent required");
                if(work==null)work=Objects.requireNonNull(factory.get());
                if(!work.advance()){post();return;}
                // Completing a future alone cannot certify physical writes or close an unresolved ledger.
                if(owner.getData(MiningOreOwnership.LEDGER)!=ledger||!ledger.surfaceFinished(intent.identity()))throw new IllegalStateException("Surface work did not finish original provenance");
                // Decorators run only after the surface transaction closes. Their legitimate later
                // block changes still revoke provenance through the existing mutation hook.
                invoked=true;Objects.requireNonNull(original.get()).whenComplete((generated,failure)->{
                    if(failure!=null)result.completeExceptionally(failure);
                    else if(generated!=owner)result.completeExceptionally(new IllegalStateException("Native features changed owner"));
                    else if(owner.getData(MiningOreOwnership.LEDGER)!=ledger||!ledger.surfaceFinished(intent.identity()))
                        result.completeExceptionally(new IllegalStateException("Native features changed surface authority"));
                    else result.complete(owner);
                });
            }catch(Throwable error){result.completeExceptionally(error);}
        }
    }
}
