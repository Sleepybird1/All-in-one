package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeValidator;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.ArrayList;
import java.util.List;

/** Keep validation in its one reserved row, above the review action buttons. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenValidationLayoutMixin extends Screen {
    @Shadow private List<RecipeValidator.Issue> issues;
    @Shadow private int canvasBoxX;
    @Shadow private int canvasBoxY;
    @Shadow private int canvasBoxW;
    @Shadow private int canvasBoxH;
    protected KjsGenValidationLayoutMixin(Component title) { super(title); }

    @Inject(method = "drawValidation", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$singleValidationRow(GuiGraphics graphics, CallbackInfo ci) {
        if (issues == null || issues.isEmpty()) return; // Preserve native green Valid state.
        int y = canvasBoxY + canvasBoxH + 3;
        boolean error = issues.stream().anyMatch(issue -> issue.severity() == RecipeValidator.Severity.ERROR);
        int color = error ? 0xFFFF6B6B : 0xFFFFC857;
        var first = issues.getFirst();
        String message = Component.translatable(first.messageKey(), first.args()).getString();
        String suffix = issues.size() > 1 ? " (+" + (issues.size() - 1) + ")" : "";
        int width = Math.max(1, canvasBoxW - 8);
        int messageWidth = Math.max(0, width - font.width(suffix));
        if (font.width(message) > messageWidth) {
            message = font.plainSubstrByWidth(message, Math.max(0, messageWidth - font.width("..."))) + "...";
        }
        graphics.enableScissor(canvasBoxX, y, canvasBoxX + canvasBoxW, y + 9);
        graphics.fill(canvasBoxX, y + 1, canvasBoxX + 3, y + 7, color);
        graphics.drawString(font, message + suffix, canvasBoxX + 6, y, color, true);
        graphics.disableScissor();
        ci.cancel();
    }

    @Inject(method = "render", at = @At("TAIL"))
    private void industrialColonies$validationDetails(GuiGraphics graphics, int mouseX, int mouseY, float delta, CallbackInfo ci) {
        int y = canvasBoxY + canvasBoxH + 3;
        if (issues == null || issues.isEmpty() || minecraft == null || minecraft.screen != (Object) this
                || mouseX < canvasBoxX || mouseX >= canvasBoxX + canvasBoxW || mouseY < y || mouseY >= y + 9) return;
        var lines = new ArrayList<Component>();
        for (var issue : issues.stream().limit(12).toList()) {
            lines.add(Component.translatable(issue.messageKey(), issue.args()));
        }
        if (issues.size() > 12) lines.add(Component.literal((issues.size() - 12) + " more validation issues"));
        graphics.renderComponentTooltip(font, lines, mouseX, mouseY);
    }
}
