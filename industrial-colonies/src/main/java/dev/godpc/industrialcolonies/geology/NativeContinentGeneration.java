package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.*;

/** Opt-in dispatcher for a commissioned runtime; no production registration or implicit policy creation. */
public final class NativeContinentGeneration {
 @FunctionalInterface private interface Source { NativeContinentRuntime get()throws Exception; }
 private NativeContinentGeneration(){}
 public static CompletableFuture<ChunkAccess> beforeBoundStarts(NativeContinentLevels.Binding binding,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,Supplier<CompletableFuture<ChunkAccess>> original){
  return before(binding::runtime,context,step,cache,owner,budget,original);
 }
 public static CompletableFuture<ChunkAccess> afterBoundCarvers(NativeContinentLevels.Binding binding,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,CompletableFuture<ChunkAccess> original){
  return after(binding::runtime,context,step,cache,owner,budget,original);
 }
 public static CompletableFuture<ChunkAccess> beforeStarts(NativeContinentRuntime runtime,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,Supplier<CompletableFuture<ChunkAccess>> original){
  return before(()->runtime,context,step,cache,owner,budget,original);
 }
 private static CompletableFuture<ChunkAccess> before(Source source,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,Supplier<CompletableFuture<ChunkAccess>> original){
  var operation=new Operation<List<MiningScanScope>>(source,context,owner,budget,NativeContinentRuntime.Owner::mineScopes);
  return NativeStructureHandoff.beforeStarts(context,step,cache,owner,()->operation,operation::result,original);
 }
 public static CompletableFuture<ChunkAccess> afterCarvers(NativeContinentRuntime runtime,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,CompletableFuture<ChunkAccess> original){
  return after(()->runtime,context,step,cache,owner,budget,original);
 }
 private static CompletableFuture<ChunkAccess> after(Source source,WorldGenContext context,ChunkStep step,
   StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,int budget,CompletableFuture<ChunkAccess> original){
  var operation=new Operation<Integer>(source,context,owner,budget,group->group.place(new WorldGenRegion(context.level(),cache,step,owner),owner));
  return NativeGenerationHandoff.afterCarvers(context,step,cache,owner,original,()->operation);
 }
 /** Created on a generator worker; all runtime access starts inside the prioritized native main mailbox. */
 private static final class Operation<R> implements NativeGenerationHandoff.Step {
  private final Source source;private final WorldGenContext context;private final ChunkAccess owner;private final int budget;
  private final ContinentGenerationSlice.Finish<NativeContinentRuntime.Owner,R> finish;
  private ContinentGenerationSlice<NativeContinentRuntime.Owner,R> slice;
  Operation(Source source,WorldGenContext context,ChunkAccess owner,int budget,ContinentGenerationSlice.Finish<NativeContinentRuntime.Owner,R> finish){
   this.source=Objects.requireNonNull(source);this.context=Objects.requireNonNull(context);this.owner=Objects.requireNonNull(owner);this.finish=finish;
   if(budget<1||budget>4096)throw new IllegalArgumentException("Generation discovery budget1..4096");this.budget=budget;
  }
  @Override public boolean advance()throws Exception{
   var runtime=Objects.requireNonNull(source.get());runtime.requireLevel(context.level());
   if(slice==null){var ticket=runtime.prepareOwner(owner.getPos());slice=new ContinentGenerationSlice<>(ticket::acquire,group->NativeTerrainYield.during(()->group.advance(budget)),finish);}
   return slice.advance();
  }
  R result(){if(slice==null)throw new IllegalStateException("Generation prerequisite has not run");return slice.result();}
 }
}
