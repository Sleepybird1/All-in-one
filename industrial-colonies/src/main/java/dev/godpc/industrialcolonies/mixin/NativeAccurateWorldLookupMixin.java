package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.geology.NativeAccurateTerrain;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Coerce;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Only scoped planning reads request native processed tiles; normal generation retains its own flags. */
@Pseudo
@Mixin(targets="raccoonman.reterraforged.world.worldgen.cell.heightmap.WorldLookup",remap=false)
public abstract class NativeAccurateWorldLookupMixin {
    @Inject(method="applyCell(Lraccoonman/reterraforged/world/worldgen/cell/Cell;IIZZ)Z",at=@At("HEAD"),remap=false)
    private void industrialColonies$yieldPendingTerrain(@Coerce Object cell,int x,int z,boolean accurate,boolean cached,CallbackInfoReturnable<Boolean> result) {
        NativeAccurateTerrain.awaitReady(this,x,z);
    }
    @ModifyVariable(method="applyCell(Lraccoonman/reterraforged/world/worldgen/cell/Cell;IIZZ)Z",
            at=@At("HEAD"),argsOnly=true,ordinal=0,remap=false)
    private boolean industrialColonies$processedPlanningCell(boolean accurate) {
        return accurate||NativeAccurateTerrain.tokenFor(this)!=null;
    }
}
