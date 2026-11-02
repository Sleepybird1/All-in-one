package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.NativeAccurateTerrain;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A raw fallback cell may predate tile hydration. Invalidate once per strict query, not per sample. */
@Pseudo
@Mixin(targets="raccoonman.reterraforged.world.worldgen.densityfunction.CellSampler$Cache2d",remap=false)
public abstract class NativeAccurateCellCacheMixin {
    @Shadow private long lastPos;
    @Unique private Object industrialColonies$accurateScope;

    @Inject(method="getAndUpdate(Lraccoonman/reterraforged/world/worldgen/cell/heightmap/WorldLookup;IIZ)Lraccoonman/reterraforged/world/worldgen/cell/Cell;",
            at=@At("HEAD"),remap=false)
    private void industrialColonies$invalidateRawCell(@Coerce Object lookup,int x,int z,boolean climate,CallbackInfoReturnable<?> callback) {
        Object token=NativeAccurateTerrain.tokenFor(lookup);
        if(token!=null&&token!=industrialColonies$accurateScope){
            lastPos=Long.MIN_VALUE;industrialColonies$accurateScope=token;
        }
    }
}
