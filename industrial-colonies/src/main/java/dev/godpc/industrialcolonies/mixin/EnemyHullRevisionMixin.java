package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.enemy.EnemyHullRevisionAccess;
import dev.ryanhcode.sable.sublevel.plot.heat.SubLevelHeatMapManager;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** Staged observation only. Adds/removals invalidate commissioned enemy hulls. */
@Mixin(value=SubLevelHeatMapManager.class,remap=false)
public abstract class EnemyHullRevisionMixin implements EnemyHullRevisionAccess {
 @Unique private long industrialColonies$revision;
 @Override public long industrialColonies$hullRevision(){return industrialColonies$revision;}
 @Inject(method={"onSolidAdded","onSolidRemoved"},at=@At("HEAD"),remap=false)
 private void industrialColonies$changed(BlockPos pos,CallbackInfo ci){
  if(industrialColonies$revision<Long.MAX_VALUE)industrialColonies$revision++;
 }
}
