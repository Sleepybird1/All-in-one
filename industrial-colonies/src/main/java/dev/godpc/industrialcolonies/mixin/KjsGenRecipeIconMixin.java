package dev.godpc.industrialcolonies.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Local;
import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.core.SlotContent;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenRecipeIconSelection;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/** Recipe-list output thumbnails use slot metadata and the complete authored content. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenRecipeIconMixin {
    @Shadow private int listX;
    @Shadow abstract void drawSlotContent(GuiGraphics graphics, int x, int y, SlotContent content);

    @WrapOperation(method = "drawRecipeList", at = @At(value = "INVOKE", target =
            "Lcom/zizazr/kjsgen/ui/vanilla/VanillaEditorScreen;iconForRecipe(Lcom/zizazr/kjsgen/core/RecipeInstance;)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack industrialColonies$outputThumbnail(VanillaEditorScreen screen,
            RecipeInstance recipe, Operation<ItemStack> original,
            @Local(argsOnly = true) GuiGraphics graphics, @Local(index = 7) int rowY) {
        var selected = RecipeTypeRegistry.get(recipe.typeId())
                .flatMap(type -> KjsGenRecipeIconSelection.output(recipe, type));
        if (selected.isEmpty()) return original.call(screen, recipe);
        // This call is merged into VanillaEditorScreen itself. Its native renderer
        // may legally access the package-private Theme and retains the installed
        // full-item, fluid and chemical rendering hooks. No foreign static bridge.
        drawSlotContent(graphics, listX + 21, rowY + 1, selected.get());
        return ItemStack.EMPTY; // Already drawn at the native icon's +1,+1 inset.
    }
}
