package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.SlotContent;
import dev.godpc.industrialcolonies.KjsGenItemReference;
import dev.godpc.industrialcolonies.KjsGenJeiItemCatalog;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Saved ITEM canvas/hover previews must render the same full stack selected from JEI. */
@Mixin(targets="com.zizazr.kjsgen.ui.vanilla.VanillaTheme",remap=false)
public abstract class KjsGenComponentPreviewMixin {
    @Inject(method="stackOf",at=@At("HEAD"),cancellable=true)
    private static void industrialColonies$fullItemPreview(SlotContent content,CallbackInfoReturnable<ItemStack> cir) {
        if(content.kind()!=ContentKind.ITEM||content.components()==null||content.components().isBlank())return;
        try {
            String key=KjsGenItemReference.key(content.id(),content.components());
            ItemStack stack=KjsGenJeiItemCatalog.resolve(key).map(KjsGenJeiItemCatalog.Choice::stack).orElse(ItemStack.EMPTY);
            if(!stack.isEmpty())stack.setCount(content.count());
            cir.setReturnValue(stack);
        }catch(RuntimeException invalid){cir.setReturnValue(ItemStack.EMPTY);}
    }
}
