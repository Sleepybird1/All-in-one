package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.*;

/** Automatic source tickets use the original shared underground/surface transaction.
 * No chunk acquisition, synchronous future join, supplied source or per-chunk ore roll. */
public final class AutomaticCinnabarGeneration {
 private AutomaticCinnabarGeneration(){}
 public static CompletableFuture<ChunkAccess> afterCarvers(NativeContinentLevels.Binding ordinary,WorldStartCinnabarRuntime.Binding surface,
     WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,CompletableFuture<ChunkAccess> original){
  return NativeGenerationHandoff.afterCarvers(context,step,cache,owner,original,()->new NativeGenerationHandoff.Step(){
   ContinentGenerationSlice<NativeContinentRuntime.Owner,Integer> slice;
   @Override public boolean advance()throws Exception{
    if(slice==null){
     var progress=surface.ticket(owner).advance(budget);if(!progress.ready())return false;
     var runtime=ordinary.runtime();var ticket=runtime.prepareOwner(owner.getPos());
     var intent=progress.sources().isEmpty()?null:NativeCinnabarPlacement.intent(context.level(),owner.getPos(),progress.sources());
     slice=new ContinentGenerationSlice<>(ticket::acquire,group->group.advance(budget),group->intent==null
       ?group.place(new WorldGenRegion(context.level(),cache,step,owner),owner)
       :group.placeForSurface(new WorldGenRegion(context.level(),cache,step,owner),owner,intent));
    }
    return slice.advance();
   }
  });
 }
 public static CompletableFuture<ChunkAccess> beforeFeatures(WorldStartCinnabarRuntime.Binding surface,
     WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,Supplier<CompletableFuture<ChunkAccess>> original){
  if(step.targetStatus()!=ChunkStatus.FEATURES)throw new IllegalArgumentException("Native FEATURES required");
  var result=new CompletableFuture<ChunkAccess>();var holder=Objects.requireNonNull(cache.get(owner.getPos().x,owner.getPos().z));
  new Runnable(){
   boolean invoked;
   void post(){context.mainThreadMailBox().tell(ChunkTaskPriorityQueueSorter.message(this,owner.getPos().toLong(),holder::getTicketLevel));}
   @Override public void run(){
    if(result.isDone())return;
    try{
     if(invoked||!context.level().getServer().isSameThread())throw new IllegalStateException("Invalid native cinnabar feature continuation");
     var progress=surface.ticket(owner).advance(budget);if(!progress.ready()){post();return;}
     // An owner with no ordinary/surface reservations legitimately has no ledger:
     // NativeContinentCoordinator.placeOwners returns without creating one.
     // Existing open/failed authority still refuses; never create/seal it here.
     if(progress.sources().isEmpty()&&owner.hasData(MiningOreOwnership.LEDGER)
       &&(!owner.getData(MiningOreOwnership.LEDGER).sealed()||owner.getData(MiningOreOwnership.LEDGER).failed()))
      throw new IllegalStateException("Empty surface source cannot discard an unresolved owner transaction");
     invoked=true;
     var next=progress.sources().isEmpty()?original.get():NativeCinnabarGeneration.beforeFeatures(context,step,cache,owner,(level,pos)->progress.sources(),original);
     Objects.requireNonNull(next).whenComplete((generated,error)->{
      try{context.level().getServer().execute(()->surface.release(owner));}
      catch(Throwable cleanup){result.completeExceptionally(cleanup);return;}
      if(error!=null)result.completeExceptionally(error);
      else if(generated!=owner)result.completeExceptionally(new IllegalStateException("Native surface owner changed"));
      else result.complete(owner);
     });
    }catch(Throwable error){result.completeExceptionally(error);}
   }
  }.post();
  return result;
 }
}
