package dev.godpc.industrialcolonies.mixin;
import dev.godpc.industrialcolonies.client.VeinRockView;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.RenderShape;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Registered client-only: hide terrain and its occlusion, not its actual blocks. */
@Mixin(BlockBehaviour.BlockStateBase.class)
public abstract class VeinRockStateMixin {
 private BlockState industrialColonies$rockViewState(){return (BlockState)(Object)this;}
 @Inject(method="getRenderShape",at=@At("HEAD"),cancellable=true)
 private void hideModel(CallbackInfoReturnable<RenderShape> cir){if(VeinRockView.hidden(industrialColonies$rockViewState()))cir.setReturnValue(RenderShape.INVISIBLE);}
 @Inject(method="canOcclude",at=@At("HEAD"),cancellable=true)
 private void exposeFaces(CallbackInfoReturnable<Boolean> cir){if(VeinRockView.hidden(industrialColonies$rockViewState()))cir.setReturnValue(false);}
 @Inject(method="isSolidRender",at=@At("HEAD"),cancellable=true)
 private void exposeChunks(CallbackInfoReturnable<Boolean> cir){if(VeinRockView.hidden(industrialColonies$rockViewState()))cir.setReturnValue(false);}
 @Inject(method="emissiveRendering",at=@At("HEAD"),cancellable=true)
 private void lightRocks(CallbackInfoReturnable<Boolean> cir){if(VeinRockView.visibleRock(industrialColonies$rockViewState()))cir.setReturnValue(true);}
}
