package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.*;
import net.minecraft.server.level.GenerationChunkHolder;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.*;
import java.util.concurrent.CompletableFuture;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import com.llamalad7.mixinextras.injector.wrapmethod.WrapMethod;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;

/** No binding is installed automatically. Loading existing structure starts is not intercepted. */
@Mixin(ChunkStatusTasks.class)
public abstract class ContinentGenerationMixin {
 @WrapMethod(method="generateStructureStarts")
 private static CompletableFuture<ChunkAccess> colonies$continentStarts(WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,
   ChunkAccess owner,Operation<CompletableFuture<ChunkAccess>> original){
  var binding=NativeContinentLevels.find(context.level());
  if(binding.isEmpty())return original.call(context,step,cache,owner);
  return NativeContinentGeneration.beforeBoundStarts(binding.get(),context,step,cache,owner,32,()->original.call(context,step,cache,owner));
 }
 @Inject(method="generateCarvers",at=@At("RETURN"),cancellable=true)
 private static void colonies$continentPlacement(WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,
   ChunkAccess owner,CallbackInfoReturnable<CompletableFuture<ChunkAccess>> cir){
  var binding=NativeContinentLevels.find(context.level());
  if(binding.isPresent()){
   var surface=WorldStartCinnabarRuntime.find(context.level());
   cir.setReturnValue(surface.isPresent()?AutomaticCinnabarGeneration.afterCarvers(binding.get(),surface.get(),context,step,cache,owner,512,cir.getReturnValue())
      :NativeContinentGeneration.afterBoundCarvers(binding.get(),context,step,cache,owner,32,cir.getReturnValue()));
  }
 }
 @WrapMethod(method="generateFeatures")
 private static CompletableFuture<ChunkAccess> colonies$cinnabarFeatures(WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,
   ChunkAccess owner,Operation<CompletableFuture<ChunkAccess>> original){
  var surface=WorldStartCinnabarRuntime.find(context.level());
  if(surface.isEmpty())return original.call(context,step,cache,owner);
  return AutomaticCinnabarGeneration.beforeFeatures(surface.get(),context,step,cache,owner,512,()->original.call(context,step,cache,owner));
 }
}
