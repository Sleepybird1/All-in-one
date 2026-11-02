package dev.godpc.industrialcolonies.geology;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;
import net.minecraft.server.level.*;
import net.minecraft.util.StaticCache2D;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.*;
import net.minecraft.world.level.chunk.status.*;

/** Explicit, unregistered integration for completed saved surface selections.
 * Does not select a density/count, survey ranges, acquire chunks or activate a worldgen hook. */
public final class NativeCinnabarGeneration {
    /** Called on the server thread. Return completed saved sources only; never advance a survey here. */
    @FunctionalInterface public interface SavedSources {
        List<NativeMountainRangeSurvey.SavedConcentrations> read(ServerLevel level,ChunkPos owner) throws Exception;
    }
    private NativeCinnabarGeneration() {}

    /** Alternative to the ordinary CARVERS continuation, never in addition to it for the same owner. */
    public static CompletableFuture<ChunkAccess> afterCarvers(NativeContinentRuntime runtime,
            WorldGenContext context,ChunkStep step,StaticCache2D<GenerationChunkHolder> cache,
            ChunkAccess owner,int discoveryBudget,SavedSources sources,CompletableFuture<ChunkAccess> original) {
        Objects.requireNonNull(runtime);Objects.requireNonNull(context);Objects.requireNonNull(step);
        Objects.requireNonNull(cache);Objects.requireNonNull(owner);Objects.requireNonNull(original);
        if(discoveryBudget<1||discoveryBudget>4096)throw new IllegalArgumentException("Bounded discovery budget1..4096 required");
        var saved=new OwnerSources(context.level(),owner.getPos(),sources);
        return NativeGenerationHandoff.afterCarvers(context,step,cache,owner,original,()->new NativeGenerationHandoff.Step(){
            ContinentGenerationSlice<NativeContinentRuntime.Owner,Integer> slice;
            @Override public boolean advance() throws Exception {
                runtime.requireLevel(context.level());
                if(slice==null){
                    var intent=saved.intent();
                    var ticket=runtime.prepareOwner(owner.getPos());
                    slice=new ContinentGenerationSlice<>(ticket::acquire,group->group.advance(discoveryBudget),
                        group->group.placeForSurface(new WorldGenRegion(context.level(),cache,step,owner),owner,intent));
                }
                return slice.advance();
            }
        });
    }

    /** Revalidate the same persisted source authority, physically finish it, then run decorators once. */
    public static CompletableFuture<ChunkAccess> beforeFeatures(WorldGenContext context,ChunkStep step,
            StaticCache2D<GenerationChunkHolder> cache,ChunkAccess owner,SavedSources sources,
            Supplier<CompletableFuture<ChunkAccess>> original) {
        Objects.requireNonNull(context);Objects.requireNonNull(step);Objects.requireNonNull(cache);
        Objects.requireNonNull(owner);Objects.requireNonNull(original);
        var saved=new OwnerSources(context.level(),owner.getPos(),sources);
        return NativeSurfaceHandoff.beforeSavedFeatures(context,step,cache,owner,saved::intent,original,
            ()->new NativeGenerationHandoff.Step(){
                boolean attempted;
                @Override public boolean advance() throws Exception {
                    if(attempted)throw new IllegalStateException("Surface placement is terminal; never replay writes");
                    attempted=true;
                    var intent=saved.intent();
                    var result=NativeCinnabarPlacement.place(new WorldGenRegion(context.level(),cache,step,owner),owner,saved.sources());
                    if(result.status()!=CinnabarOwnerPlacement.Status.WRITTEN||result.expected()!=intent.targets().size()
                            ||result.written()!=result.expected())throw new IllegalStateException("Saved surface placement held or incomplete: "+result);
                    return true;
                }
            });
    }

    private static final class OwnerSources {
        final ServerLevel level;final ChunkPos owner;final SavedSources source;
        List<NativeMountainRangeSurvey.SavedConcentrations> saved;
        CinnabarOwnerPlacement.Intent intent;
        OwnerSources(ServerLevel level,ChunkPos owner,SavedSources source){this.level=Objects.requireNonNull(level);this.owner=Objects.requireNonNull(owner);this.source=Objects.requireNonNull(source);}
        List<NativeMountainRangeSurvey.SavedConcentrations> sources() throws Exception {
            if(!level.getServer().isSameThread())throw new IllegalStateException("Saved surface source resolution requires server thread");
            if(saved==null){
                var read=List.copyOf(Objects.requireNonNull(source.read(level,owner)));
                if(read.isEmpty()||read.size()>64)throw new IllegalArgumentException("Explicit bounded saved range group required");
                // requireLevel also checks unchanged configuration, saved allocation and native context.
                for(var value:read){value.requireLevel(level);value.completed();}
                saved=read;
            }
            return saved;
        }
        CinnabarOwnerPlacement.Intent intent() throws Exception {
            var current=NativeCinnabarPlacement.intent(level,owner,sources());
            if(intent!=null&&!intent.equals(current))throw new IllegalStateException("Saved surface authority changed during generation");
            intent=current;return current;
        }
    }
}
