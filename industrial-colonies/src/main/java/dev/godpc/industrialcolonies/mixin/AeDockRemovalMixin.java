package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.space.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(BlockEntity.class)
public abstract class AeDockRemovalMixin {
 @Inject(method="setRemoved",at=@At("HEAD"))
 private void ic$unloadAe(CallbackInfo ci){if(this instanceof AeDockAccess)AeDockService.invalidate((BlockEntity)(Object)this);}
}
