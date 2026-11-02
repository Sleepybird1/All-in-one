package dev.godpc.industrialcolonies.mixin.client;

import com.ldtteam.blockui.views.ZoomDragView;
import com.minecolonies.api.colony.buildings.views.IBuildingView;
import com.minecolonies.api.research.IGlobalResearch;
import com.minecolonies.api.research.IGlobalResearchTree;
import com.minecolonies.api.research.ILocalResearchTree;
import com.minecolonies.core.client.gui.WindowResearchTree;
import com.mojang.logging.LogUtils;
import dev.godpc.industrialcolonies.client.research.TechTreeConnectionsPane;
import dev.godpc.industrialcolonies.client.research.TechTreeLayout;
import dev.godpc.industrialcolonies.research.IndustrialResearchIds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.gen.Invoker;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;
import java.util.Optional;

/**
 * Replaces MineColonies' recursive six-column renderer only for the pack's
 * single Tech Tree branch. Research cards and their normal click/tooltip state
 * remain native MineColonies controls; only layout and connection rendering
 * are custom.
 */
@Mixin(value = WindowResearchTree.class, remap = false)
public abstract class WindowResearchTreeMixin {
    @Unique
    private static final Logger INDUSTRIAL_COLONIES_LOGGER = LogUtils.getLogger();
    @Unique
    private static final double MINIMUM_ALLOWED_SCALE = 0.035D;
    @Unique
    private static final double MAXIMUM_INITIAL_SCALE = 1.0D;
    @Unique
    private static final double UNKNOWN_VIEWPORT_FALLBACK_SCALE = 0.2D;

    @Shadow
    @Final
    private ResourceLocation branch;

    @Unique
    private boolean industrialColonies$customRendered;

    @Invoker(value = "drawResearchItem", remap = false)
    protected abstract boolean industrialColonies$drawResearchItem(
            ZoomDragView view,
            int x,
            int y,
            IGlobalResearch research,
            boolean abandoned
    );

    @Inject(method = "drawTree", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$drawSingleTechTree(
            int height,
            int depth,
            ZoomDragView view,
            List<ResourceLocation> researchList,
            boolean abandoned,
            CallbackInfoReturnable<Integer> callback
    ) {
        if (!IndustrialResearchIds.isTechTree(branch)) {
            return;
        }

        Optional<TechTreeLayout> loaded = TechTreeLayout.load();
        if (loaded.isEmpty() || !industrialColonies$allResearchIsAvailable(loaded.get())) {
            return;
        }

        TechTreeLayout layout = loaded.get();
        view.addChild(new TechTreeConnectionsPane(layout), 0);
        for (TechTreeLayout.Node node : layout.nodes()) {
            IGlobalResearch research = IGlobalResearchTree.getInstance().getResearch(branch, node.research());
            industrialColonies$drawResearchItem(view, node.x(), node.y(), research, false);
        }

        view.computeContentSize();
        industrialColonies$configureViewport(view, layout);
        industrialColonies$customRendered = true;
        callback.setReturnValue(0);
    }

    @Inject(method = "drawTreeBackground", at = @At("HEAD"), cancellable = true, remap = false)
    private void industrialColonies$skipSixColumnBackground(
            ZoomDragView view,
            int maxHeight,
            CallbackInfo callback
    ) {
        if (industrialColonies$customRendered) {
            callback.cancel();
        }
    }

    /**
     * MineColonies evaluates the structural parent before its normal Creative
     * override, so a missing parent leaves a Creative author with an inert lock
     * icon. Treat only that client-side parent probe as fulfilled in Creative.
     * The card then becomes the normal clickable AVAILABLE card and sends the
     * stock TryResearchMessage; the server mixin still enforces every parent
     * and explicit AND requirement for non-Creative players.
     */
    @Redirect(
            method = "drawResearchItem",
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/minecolonies/api/research/ILocalResearchTree;hasCompletedResearch(Lnet/minecraft/resources/ResourceLocation;)Z"
            ),
            remap = false
    )
    private boolean industrialColonies$allowCreativeForceUnlock(
            ILocalResearchTree localTree,
            ResourceLocation parent
    ) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (IndustrialResearchIds.isTechTree(branch)
                && player != null
                && player.isCreative()) {
            return true;
        }

        return localTree.hasCompletedResearch(parent);
    }

    /**
     * MineColonies checks University level twice: once while choosing the card
     * state and again when processing the click. The latter value also serves
     * as its simultaneous-research slot limit. Report an unlimited level only
     * for a Creative player viewing this Tech Tree, so the untouched stock
     * click handler sends exactly one TryResearchMessage for any unfinished
     * card. Every other branch and every non-Creative player sees the real
     * building level.
     */
    @Redirect(
            method = {"getResearchButtonState", "onButtonClicked"},
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/minecolonies/api/colony/buildings/views/IBuildingView;getBuildingLevel()I"
            ),
            remap = false
    )
    private int industrialColonies$allowCreativeUnlimitedUniversity(IBuildingView building) {
        LocalPlayer player = Minecraft.getInstance().player;
        if (IndustrialResearchIds.isTechTree(branch)
                && player != null
                && player.isCreative()) {
            return Integer.MAX_VALUE;
        }

        return building.getBuildingLevel();
    }

    @Unique
    private boolean industrialColonies$allResearchIsAvailable(TechTreeLayout layout) {
        for (TechTreeLayout.Node node : layout.nodes()) {
            IGlobalResearch research = IGlobalResearchTree.getInstance().getResearch(branch, node.research());
            if (research == null || !branch.equals(research.getBranch())) {
                INDUSTRIAL_COLONIES_LOGGER.error(
                        "Tech Tree layout references unavailable MineColonies research {}; using stock renderer",
                        node.research());
                return false;
            }
        }
        return true;
    }

    @Unique
    private static void industrialColonies$configureViewport(ZoomDragView view, TechTreeLayout layout) {
        double fitScale;
        if (view.getWidth() <= 16 || view.getHeight() <= 16) {
            fitScale = UNKNOWN_VIEWPORT_FALLBACK_SCALE;
        } else {
            double widthScale = (view.getWidth() - 8) / (double) layout.canvasWidth();
            double heightScale = (view.getHeight() - 8) / (double) layout.canvasHeight();
            fitScale = Math.min(widthScale, heightScale);
        }
        double minScale = Math.max(MINIMUM_ALLOWED_SCALE, Math.min(0.15D, fitScale * 0.45D));

        view.enableDrag();
        view.enableZoom();
        view.setMinScale(minScale);
        view.setScaleRaw(Math.max(minScale, Math.min(MAXIMUM_INITIAL_SCALE, fitScale)));
        view.setScrollX(0.0D);
        view.setScrollY(0.0D);
    }
}
