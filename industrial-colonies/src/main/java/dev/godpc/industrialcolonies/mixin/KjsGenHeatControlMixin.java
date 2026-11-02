package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeTypeRegistry;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import java.util.Optional;

/** Keep heat accessible even when the right parameter column is clipped at large GUI scales. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenHeatControlMixin {
    @Shadow private int canvasBoxX, canvasBoxY, canvasBoxW, canvasBoxH;
    @Shadow private boolean menuOpen;
    @Shadow abstract Optional<RecipeInstance> selectedRecipe();
    @Shadow abstract void markDirty();
    @Shadow abstract void buildParamWidgets();

    @Unique private boolean industrialColonies$hasHeat(RecipeInstance recipe) {
        return RecipeTypeRegistry.get(recipe.typeId()).flatMap(t -> t.parameter("heat"))
                .map(p -> !p.options().isEmpty()).orElse(false);
    }
    @Unique private int industrialColonies$heatX() { return canvasBoxX + 5; }
    @Unique private int industrialColonies$heatY() { return canvasBoxY + canvasBoxH - 23; }
    @Unique private int industrialColonies$heatWidth() { return Math.min(118, canvasBoxW - 10); }

    @Inject(method = "drawCanvas", at = @At("TAIL"))
    private void industrialColonies$drawHeat(GuiGraphics graphics, int mouseX, int mouseY, CallbackInfo ci) {
        var selected = selectedRecipe();
        if (selected.isEmpty() || !industrialColonies$hasHeat(selected.get()) || canvasBoxW < 80 || canvasBoxH < 70) return;
        var recipe = selected.get();
        var type = RecipeTypeRegistry.get(recipe.typeId()).orElseThrow();
        String value = recipe.param(type, "heat");
        String label = switch (value) {
            case "lowheated" -> "Heat: Low Heated";
            case "heated" -> "Heat: Heated";
            case "superheated" -> "Heat: Superheated";
            default -> "Heat: None";
        };
        int x = industrialColonies$heatX(), y = industrialColonies$heatY(), w = industrialColonies$heatWidth();
        graphics.fill(x, y, x + w, y + 18, 0xFF303440);
        graphics.renderOutline(x, y, w, 18, 0xFF9299B0);
        var font = Minecraft.getInstance().font;
        graphics.drawString(font, font.plainSubstrByWidth(label, w - 8), x + 4, y + 5, 0xFFFFFFFF, false);
    }

    @Inject(method = "mouseClicked", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$cycleHeat(double x, double y, int button, CallbackInfoReturnable<Boolean> ci) {
        if (menuOpen || canvasBoxW < 80 || canvasBoxH < 70) return;
        if (x < industrialColonies$heatX() || x >= industrialColonies$heatX() + industrialColonies$heatWidth()
                || y < industrialColonies$heatY() || y >= industrialColonies$heatY() + 18) return;
        var selected = selectedRecipe();
        if (selected.isEmpty() || !industrialColonies$hasHeat(selected.get())) return;
        if (button == 0 || button == 1) {
            var recipe = selected.get();
            var type = RecipeTypeRegistry.get(recipe.typeId()).orElseThrow();
            var options = type.parameter("heat").orElseThrow().options();
            int index = options.indexOf(recipe.param(type, "heat"));
            recipe.setParam("heat", options.get(Math.floorMod(index + (button == 0 ? 1 : -1), options.size())));
            markDirty();
            buildParamWidgets();
        }
        ci.setReturnValue(true);
    }
}
