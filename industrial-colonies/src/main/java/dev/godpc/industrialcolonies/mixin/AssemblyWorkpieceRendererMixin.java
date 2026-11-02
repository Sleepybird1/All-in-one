package dev.godpc.industrialcolonies.mixin;

import dev.godpc.industrialcolonies.AssemblyWorkpieceItem;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Render the chosen model; inventory identity and progress-bar calculation remain on the workpiece. */
@Mixin(ItemRenderer.class)
public abstract class AssemblyWorkpieceRendererMixin {
    @Inject(method="getModel", at=@At("HEAD"), cancellable=true)
    private void industrialColonies$appearance(ItemStack stack, Level level, LivingEntity entity, int seed,
                                               CallbackInfoReturnable<BakedModel> cir) {
        var appearance = AssemblyWorkpieceItem.appearance(stack);
        if (!appearance.isEmpty()) cir.setReturnValue(((ItemRenderer)(Object)this).getModel(appearance, level, entity, seed));
    }
    @ModifyVariable(method="render", at=@At("HEAD"), argsOnly=true, ordinal=0)
    private ItemStack industrialColonies$renderAppearance(ItemStack stack) {
        var appearance = AssemblyWorkpieceItem.appearance(stack);
        return appearance.isEmpty() ? stack : appearance;
    }
}
