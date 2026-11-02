package dev.godpc.industrialcolonies.mixin;
import com.simibubi.create.content.kinetics.press.PressingBehaviour;
import com.simibubi.create.content.processing.basin.BasinRecipe;
import dev.godpc.industrialcolonies.processing.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Heated compaction dwells at contact before consuming; native press animation and ordinary recipes stay intact. */
@Mixin(PressingBehaviour.class)
public abstract class CompactingAssemblyTimeMixin {
    @Shadow public int runningTicks;
    @Shadow public boolean running;
    @Shadow public PressingBehaviour.Mode mode;
    @Unique private AssemblyCookTimer.State industrialColonies$assemblyDwell;
    @Inject(method="tick",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$dwell(CallbackInfo ci) {
        var behaviour=(PressingBehaviour)(Object)this;
        var level=behaviour.getWorld();
        if (level==null || level.isClientSide || !running || mode!=PressingBehaviour.Mode.BASIN || runningTicks!=120) {
            industrialColonies$assemblyDwell=null;return;
        }
        var machine=level.getBlockEntity(behaviour.getPos());
        if (machine instanceof com.simibubi.create.content.kinetics.base.KineticBlockEntity kinetic && kinetic.getSpeed()==0) {
            industrialColonies$assemblyDwell=null;return;
        }
        if (!(machine instanceof BasinCurrentRecipeAccessor access) || !(access.industrialColonies$currentRecipe() instanceof BasinRecipe recipe)) return;
        var match=AssemblyRuntime.basinMatch(recipe);
        if (match==null) return;
        industrialColonies$assemblyDwell=AssemblyCookTimer.tick(industrialColonies$assemblyDwell,match.key(),match.ticks(),level.getGameTime());
        if (industrialColonies$assemblyDwell.remaining()>0) ci.cancel();
    }
}
