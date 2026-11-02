package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.MachineRecipeRouting;
import dev.godpc.industrialcolonies.KjsGenFluidRendering;
import dev.godpc.industrialcolonies.KjsGenChemicalRendering;
import com.zizazr.kjsgen.core.ContentKind;
import com.zizazr.kjsgen.core.SlotContent;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Optional;

/** Materializes the inferred base/legacy machine so its real item is visible in the canvas slot. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenEditorScreenMixin {
    @Shadow
    protected abstract void drawChanceBadge(GuiGraphics graphics,int x,int y,SlotContent content);

    @Inject(method="drawSlotContent",at=@At("HEAD"),cancellable=true)
    private void industrialColonies$drawFluid(GuiGraphics graphics,int x,int y,SlotContent content,CallbackInfo ci) {
        if(!content.isEmpty() && KjsGenFluidRendering.isFluid(content)) {
            KjsGenFluidRendering.draw(graphics,x,y,content);
            drawChanceBadge(graphics,x,y,content);
            ci.cancel();
        } else if (!content.isEmpty()
                && (content.kind() == ContentKind.CHEMICAL || content.kind() == ContentKind.CHEMICAL_TAG)
                && net.neoforged.fml.ModList.get().isLoaded("mekanism")) {
            KjsGenChemicalRendering.draw(graphics,x,y,content);
            drawChanceBadge(graphics,x,y,content);
            ci.cancel();
        }
    }
    @Shadow
    abstract Optional<RecipeInstance> selectedRecipe();

    @Shadow
    abstract void markDirty();

    @Inject(method = "drawCanvas", at = @At("HEAD"))
    private void industrialColonies$showSelectedMachine(
            GuiGraphics graphics,
            int mouseX,
            int mouseY,
            CallbackInfo ci
    ) {
        selectedRecipe().ifPresent(recipe -> RecipeTypeRegistry.get(recipe.typeId()).ifPresent(type -> {
            if (MachineRecipeRouting.ensureEditorDefaults(recipe, type)) {
                markDirty();
            }
        }));
    }
}
