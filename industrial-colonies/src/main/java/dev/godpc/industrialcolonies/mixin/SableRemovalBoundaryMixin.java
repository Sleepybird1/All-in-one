package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.space.InterstellarWarpRemovalScope;
import dev.ryanhcode.sable.api.sublevel.ServerSubLevelContainer;
import dev.ryanhcode.sable.sublevel.SubLevel;
import dev.ryanhcode.sable.sublevel.storage.SubLevelRemovalReason;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Marks Sable's destructive source-removal boundary before its first side effect. */
@Mixin(value = ServerSubLevelContainer.class, remap = false)
public abstract class SableRemovalBoundaryMixin {
    @Inject(
            method = "removeSubLevel(IILdev/ryanhcode/sable/sublevel/storage/"
                    + "SubLevelRemovalReason;)V",
            at = @At("HEAD"),
            require = 1)
    private void industrialColonies$markDestructiveRemoval(
            int plotX,
            int plotZ,
            SubLevelRemovalReason reason,
            CallbackInfo callback
    ) {
        SubLevel candidate = ((ServerSubLevelContainer) (Object) this)
                .getSubLevel(plotX, plotZ);
        InterstellarWarpRemovalScope.markRemovalStarted(candidate);
    }
}
