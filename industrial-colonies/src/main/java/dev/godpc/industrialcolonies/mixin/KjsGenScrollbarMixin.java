package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenScrollbar;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Keep sidebar scrolling outside recipe selection, duplication and deletion hitboxes. */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenScrollbarMixin {
    @Shadow private int listX;
    @Shadow private int listY;
    @Shadow private int listW;
    @Shadow private int listViewH;
    @Shadow private int listScroll;
    @Shadow private boolean menuOpen;
    @Unique private int industrialColonies$scrollContentHeight;
    @Unique private boolean industrialColonies$scrollDragging;
    @Unique private double industrialColonies$scrollGrabOffset;

    @Inject(method = "computeGeometry", at = @At("TAIL"))
    private void industrialColonies$reserveScrollGutter(CallbackInfo ci) {
        // Native geometry recomputes listW from scratch on each rebuild.
        listW -= KjsGenScrollbar.GUTTER;
        industrialColonies$scrollDragging = false;
    }

    @Unique private KjsGenScrollbar industrialColonies$bar() {
        return new KjsGenScrollbar(listX + listW, listY, listViewH,
                industrialColonies$scrollContentHeight, listScroll);
    }

    @Redirect(method = "drawRecipeList", at = @At(value = "INVOKE",
            target = "Lcom/zizazr/kjsgen/ui/vanilla/VanillaEditorScreen;drawScrollbar(Lnet/minecraft/client/gui/GuiGraphics;IIIII)V"), require = 1, allow = 1)
    private void industrialColonies$drawWideScrollbar(VanillaEditorScreen screen, GuiGraphics graphics,
            int oldX, int oldY, int viewHeight, int contentHeight, int scroll) {
        // This argument already reflects the review/search filter. Do not count the full project.
        industrialColonies$scrollContentHeight = contentHeight;
        var bar = industrialColonies$bar();
        listScroll = bar.clamp(listScroll);
        int x = bar.x() + 2;
        graphics.fill(bar.x(), bar.y(), bar.x() + KjsGenScrollbar.GUTTER, bar.y() + bar.height(), 0xFF18202C);
        graphics.fill(x, bar.y(), x + KjsGenScrollbar.WIDTH, bar.y() + bar.height(), 0xFF293547);
        if (bar.maxScroll() > 0) {
            graphics.fill(x, bar.thumbY(), x + KjsGenScrollbar.WIDTH, bar.thumbY() + bar.thumbHeight(),
                    industrialColonies$scrollDragging ? 0xFF9BD7FF : 0xFF5CBAFF);
            int grip = bar.thumbY() + bar.thumbHeight() / 2;
            graphics.fill(x + 3, grip - 2, x + KjsGenScrollbar.WIDTH - 3, grip - 1, 0xFF23405B);
            graphics.fill(x + 3, grip + 1, x + KjsGenScrollbar.WIDTH - 3, grip + 2, 0xFF23405B);
        }
    }

    @Inject(method = "mouseClicked", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$grabScrollbar(double x, double y, int button, CallbackInfoReturnable<Boolean> ci) {
        var bar = industrialColonies$bar();
        if (menuOpen || !bar.contains(x, y)) return;
        // Consume all buttons even for an empty/non-scrolling list: never reach recipe actions.
        if (button == 0 && bar.maxScroll() > 0) {
            industrialColonies$scrollGrabOffset = bar.onThumb(y) ? y - bar.thumbY() : bar.thumbHeight() / 2.0;
            industrialColonies$scrollDragging = true;
            listScroll = bar.scrollAt(y, industrialColonies$scrollGrabOffset);
        }
        ci.setReturnValue(true);
    }

    @Inject(method = "mouseDragged", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$dragScrollbar(double x, double y, int button, double dx, double dy,
            CallbackInfoReturnable<Boolean> ci) {
        if (!industrialColonies$scrollDragging || button != 0) return;
        listScroll = industrialColonies$bar().scrollAt(y, industrialColonies$scrollGrabOffset);
        ci.setReturnValue(true);
    }

    @Inject(method = "mouseReleased", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$releaseScrollbar(double x, double y, int button, CallbackInfoReturnable<Boolean> ci) {
        if (!industrialColonies$scrollDragging || button != 0) return;
        industrialColonies$scrollDragging = false;
        ci.setReturnValue(true);
    }

    @Inject(method = "mouseScrolled", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$wheelOnScrollbar(double x, double y, double horizontal, double vertical,
            CallbackInfoReturnable<Boolean> ci) {
        var bar = industrialColonies$bar();
        if (menuOpen || !bar.contains(x, y)) return;
        listScroll = bar.clamp(listScroll - (int)(vertical * 20));
        ci.setReturnValue(true);
    }
}
