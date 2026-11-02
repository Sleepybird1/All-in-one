package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.*;

/** Opt-in fresh STRUCTURE_STARTS prerequisite. No production registration or saved-start retrofit. */
public final class NativeStructureHandoff {
 public static CompletableFuture<ChunkAccess> beforeStarts(WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,Supplier<? extends NativeGenerationHandoff.Step> preparation,
   Supplier<List<MiningScanScope>> scopes,Supplier<CompletableFuture<ChunkAccess>> original){
  Objects.requireNonNull(context);Objects.requireNonNull(step);Objects.requireNonNull(cache);Objects.requireNonNull(owner);
  Objects.requireNonNull(preparation);Objects.requireNonNull(scopes);Objects.requireNonNull(original);
  if(step.targetStatus()!=ChunkStatus.STRUCTURE_STARTS)throw new IllegalArgumentException("STRUCTURE_STARTS prerequisite required");
  var holder=Objects.requireNonNull(cache.get(owner.getPos().x,owner.getPos().z));var result=new CompletableFuture<ChunkAccess>();
  new Job(context,holder,owner,preparation,scopes,original,result).post();return result;
 }
 private static final class Job implements Runnable {
  final WorldGenContext context;final GenerationChunkHolder holder;final ChunkAccess owner;
  final Supplier<? extends NativeGenerationHandoff.Step> preparation;final Supplier<List<MiningScanScope>> scopes;
  final Supplier<CompletableFuture<ChunkAccess>> original;final CompletableFuture<ChunkAccess> result;
  NativeGenerationHandoff.Step work;boolean invoked;
  Job(WorldGenContext c,GenerationChunkHolder h,ChunkAccess o,Supplier<? extends NativeGenerationHandoff.Step> p,Supplier<List<MiningScanScope>> s,Supplier<CompletableFuture<ChunkAccess>> nativeCall,CompletableFuture<ChunkAccess> r){context=c;holder=h;owner=o;preparation=p;scopes=s;original=nativeCall;result=r;}
  void post(){if(result.isDone())return;try{context.mainThreadMailBox().tell(ChunkTaskPriorityQueueSorter.message(this,owner.getPos().toLong(),holder::getTicketLevel));}catch(Throwable e){result.completeExceptionally(e);}}
  @Override public void run(){
   if(result.isDone())return;
   try{
    if(!context.level().getServer().isSameThread())throw new IllegalStateException("Structure prerequisite ran off server thread");
    if(!(owner instanceof ProtoChunk)||owner instanceof ImposterProtoChunk||owner.isUpgrading()||!owner.getPersistedStatus().isBefore(ChunkStatus.STRUCTURE_STARTS)||!owner.getAllStarts().isEmpty())throw new IllegalStateException("Existing or uncertain structure starts must not be replaced");
    if(invoked)throw new IllegalStateException("Native structure generation already invoked");
    if(work==null)work=Objects.requireNonNull(preparation.get());
    if(!work.advance()){post();return;}
    var snapshot=List.copyOf(scopes.get());invoked=true;
    var generated=ContinentMineContext.run(context.level(),snapshot,()->{
     var future=Objects.requireNonNull(original.get());
     // Inspected native generateStructureStarts is synchronous. Refuse an unsupported async override.
     if(!future.isDone())throw new IllegalStateException("Asynchronous structure generation cannot outlive admission frame");
     var generatedOwner=future.getNow(null);
     if(generatedOwner!=owner)throw new IllegalStateException("Native structure owner changed");
     ContinentMineScheduler.starts(context.level(),owner,snapshot);
     return generatedOwner;
    });
    if(generated!=owner)throw new IllegalStateException("Native structure owner changed");result.complete(owner);
   }catch(NativeTerrainYield.Pending pending){
    pending.ready().whenComplete((ignored,failure)->{if(failure!=null)result.completeExceptionally(failure);else post();});
   }catch(Throwable e){result.completeExceptionally(e);}
  }
 }
 private NativeStructureHandoff(){}
}
