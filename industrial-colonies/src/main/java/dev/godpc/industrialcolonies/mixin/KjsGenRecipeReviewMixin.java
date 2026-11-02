package dev.godpc.industrialcolonies.mixin;

import com.zizazr.kjsgen.core.RecipeInstance;
import com.zizazr.kjsgen.core.RecipeProject;
import com.zizazr.kjsgen.integration.net.ClientEditSession;
import com.zizazr.kjsgen.ui.vanilla.VanillaEditorScreen;
import dev.godpc.industrialcolonies.KjsGenRecipeReviewStore;
import dev.godpc.industrialcolonies.KjsGenRecipeViewHistory;
import dev.godpc.industrialcolonies.KjsGenRejectReasonScreen;
import dev.godpc.industrialcolonies.KjsGenDeferReasonScreen;
import dev.godpc.industrialcolonies.KjsGenMoveRecipeScreen;
import dev.godpc.industrialcolonies.KjsGenProjectMove;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Optional;

/**
 * Adds a non-destructive review queue below KJSGen's recipe canvas.
 *
 * <p>The queue deliberately lives beside KJSGen rather than inside its project
 * model. Approving or rejecting a card must never dirty, export, or otherwise
 * change the recipe that is being reviewed.</p>
 */
@Mixin(value = VanillaEditorScreen.class, remap = false)
public abstract class KjsGenRecipeReviewMixin extends Screen {
    @Unique
    private static final int industrialColonies$PADDING = 4;

    @Unique
    private static final int industrialColonies$ROW_GAP = 3;

    @Unique
    private static final int industrialColonies$STATUS_HEIGHT = 22;

    @Unique
    private static final int industrialColonies$CONTROL_HEIGHT = 20;

	@Unique
	private static final int industrialColonies$ACTION_WIDTH = 24;

	@Unique
	private static final int industrialColonies$LIST_ROW_HEIGHT = 20;

	@Unique
	private static final int industrialColonies$BADGE_SIZE = 10;

	@Unique
	private static final int industrialColonies$SEARCH_HEIGHT = 20;

	@Unique
	private static final int industrialColonies$MIN_COMMENT_HEIGHT = 28;

	@Unique
	private static final int industrialColonies$DEFAULT_COMMENT_HEIGHT = 42;

	@Unique
	private static final int industrialColonies$DRAG_HANDLE_HALF_HEIGHT = 3;

	@Unique
	private static final int industrialColonies$DIVIDER_HEIGHT =
			2 * industrialColonies$DRAG_HANDLE_HALF_HEIGHT;

	@Unique
	private static final int industrialColonies$MIN_EDITOR_HEIGHT = 96;

    @Unique
    private static final String industrialColonies$APPROVED_PROJECT = "approved recipes";

    @Unique
    private static final String industrialColonies$REJECTED_PROJECT = "rejected recipes";

    @Unique
    private static final String industrialColonies$DEFERRED_PROJECT = "deferred";

    @Unique
    private static final String industrialColonies$MAYBE_PROJECT = "maybe recipes";

    @Unique
    private static final String industrialColonies$DISABLED_PROJECT = "disabled recipes";

    @Unique
    private static final String industrialColonies$DISABLE_CODE_PREFIX = "disable:";

    @Shadow
    private RecipeProject project;

    @Shadow
    private String selectedUid;

    @Shadow
    private int canvasBoxX;

    @Shadow
    private int canvasBoxY;

    @Shadow
    private int canvasBoxW;

    @Shadow
    private int canvasBoxH;

    @Shadow
    private int panelX;

    @Shadow
    private int panelY;

    @Shadow
    private int panelW;

    @Shadow
    private int panelH;

    @Shadow
    private int listY;

    @Shadow
    private int listX;

    @Shadow
    private int listW;

    @Shadow
    private int listViewH;

    @Shadow
    private int listScroll;

    @Shadow
    private int paramY;

    @Shadow
    private int previewY;

	@Shadow
	private int previewX;

	@Shadow
	private int previewW;

	@Shadow
	private int previewH;

    @Shadow
    private List<Component> hoverTooltip;

    @Shadow
    abstract Optional<RecipeInstance> selectedRecipe();

    @Unique
    private KjsGenRecipeReviewStore industrialColonies$reviewStore;

    @Unique
    private RecipeProject industrialColonies$reviewProject;

	@Unique
	private List<RecipeInstance> industrialColonies$visibleReviewQueue = List.of();

	@Unique
	private String industrialColonies$recipeSearchQuery = "";

	@Unique
	private EditBox industrialColonies$recipeSearchInput;

	@Unique
	private Button industrialColonies$previousButton;

	@Unique
	private Button industrialColonies$nextButton;

	@Unique
	private Button industrialColonies$rejectButton;

	@Unique
	private Button industrialColonies$deferButton;

	@Unique
	private Button industrialColonies$maybeButton;

	@Unique
	private Button industrialColonies$approveButton;

	@Unique
	private Button industrialColonies$commentTabButton;

	@Unique
	private Button industrialColonies$previewTabButton;

	@Unique
	private boolean industrialColonies$showCommentTab = true;

    @Unique
    private final KjsGenRecipeViewHistory industrialColonies$viewHistory =
            new KjsGenRecipeViewHistory();

	@Unique
	private int industrialColonies$reviewHeight = -1;

	@Unique
	private boolean industrialColonies$draggingReviewDivider;

	@Unique
	private int industrialColonies$reviewDividerDragY;

	@Unique
	private int industrialColonies$reviewDividerDragHeight;

    protected KjsGenRecipeReviewMixin(Component title) {
        super(title);
    }

    @Unique private Button industrialColonies$projectMove;

    /**
     * Bind the durable review store before KJSGen chooses its initial card.
     * If the prior selection has already been reviewed, select the first
     * visible queue card so reopening or rebuilding cannot land on a hidden
     * recipe.
     */
    @Inject(method = "init", at = @At("HEAD"))
	private void industrialColonies$prepareVisibleReviewQueue(CallbackInfo ci) {
		industrialColonies$bindReviewStore(project);
		industrialColonies$syncReviewHeight();
		industrialColonies$recipeSearchQuery = industrialColonies$normalizeRecipeSearch(
				industrialColonies$recipeSearchInput == null
						? industrialColonies$recipeSearchQuery
						: industrialColonies$recipeSearchInput.getValue()
		);
		industrialColonies$refreshVisibleReviewQueue(project);
		if (selectedUid == null || project == null) {
			return;
        }
        boolean selectedIsVisible = industrialColonies$visibleReviewQueue.stream()
                .anyMatch(recipe -> recipe.uid().equals(selectedUid));
        // A picker, duplicate action or edit can explicitly select a card which
        // no longer matches the old search. Keep that pending/unmanaged card
        // editable by clearing only the text filter. Never reveal a card which
        // the durable review projection itself excludes.
        if (!selectedIsVisible && !industrialColonies$recipeSearchQuery.isBlank()
                && industrialColonies$reviewStore.visibleRecipes(project).stream()
                        .anyMatch(recipe -> recipe.uid().equals(selectedUid))) {
            industrialColonies$recipeSearchQuery = "";
            if (industrialColonies$recipeSearchInput != null) {
                industrialColonies$recipeSearchInput.setValue("");
            }
            industrialColonies$refreshVisibleReviewQueue(project);
            selectedIsVisible = true;
        }
        if (!selectedIsVisible) {
            selectedUid = industrialColonies$visibleReviewQueue.isEmpty()
                    ? null
                    : industrialColonies$visibleReviewQueue.get(0).uid();
            listScroll = 0;
        }
    }

    /**
     * Give KJSGen a read-through projection for every operation that treats
     * project.recipes() as the visible sidebar. The canonical list is never
     * mutated by this filter, so export and ordinary editing retain the full
     * project while reviewed cards disappear from Default/Queue.
     */
    @Redirect(
            method = {
                    "init",
                    "refreshFromSession",
                    "setProject",
                    "drawRecipeList",
                    "doMouseClicked",
                    "mouseScrolled"
            },
            at = @At(
                    value = "INVOKE",
                    target = "Lcom/zizazr/kjsgen/core/RecipeProject;recipes()Ljava/util/List;"
            ),
            require = 10,
            allow = 10
    )
    private List<RecipeInstance> industrialColonies$visibleReviewRecipes(
            RecipeProject targetProject
    ) {
        industrialColonies$bindReviewStore(targetProject);
        return industrialColonies$visibleReviewQueue;
    }

    @Unique
    private void industrialColonies$bindReviewStore(RecipeProject targetProject) {
        if (industrialColonies$reviewStore == null
                || industrialColonies$reviewProject != targetProject) {
            industrialColonies$reviewStore = KjsGenRecipeReviewStore.forProject(targetProject);
            industrialColonies$reviewProject = targetProject;
            industrialColonies$refreshVisibleReviewQueue(targetProject);
        }
    }

    @Unique
	private void industrialColonies$refreshVisibleReviewQueue(RecipeProject targetProject) {
		List<RecipeInstance> sourceRecipes = industrialColonies$reviewStore == null
				? List.of()
				: industrialColonies$reviewStore.visibleRecipes(targetProject);
		String query = industrialColonies$recipeSearchQuery;
		if (query.isBlank()) {
			industrialColonies$visibleReviewQueue = sourceRecipes;
		} else {
			industrialColonies$visibleReviewQueue = sourceRecipes.stream()
					.filter(recipe -> industrialColonies$matchesRecipeSearch(recipe, query))
					.toList();
		}
	}

    @Inject(method = "init", at = @At("TAIL"))
    private void industrialColonies$addReviewControls(CallbackInfo ci) {
        industrialColonies$bindReviewStore(project);
        industrialColonies$projectMove = Button.builder(Component.literal("Move to..."), button ->
                selectedRecipe().ifPresent(recipe -> minecraft.setScreen(new KjsGenMoveRecipeScreen(this, project, recipe))))
                .bounds(0, 0, 82, 18)
                .tooltip(Tooltip.create(Component.literal("Move to another project; keep this recipe's approval status."))).build();
        addWidget(industrialColonies$projectMove);
		industrialColonies$syncReviewHeight();
        industrialColonies$viewHistory.observe(selectedUid);

		int maxListScroll = Math.max(
				0,
				industrialColonies$visibleReviewQueue.size()
						* industrialColonies$LIST_ROW_HEIGHT - listViewH);
		listScroll = Math.min(listScroll, maxListScroll);

		// Keep search on its own row: narrow lists cannot fit the count and hint together.
		int recipeSearchX = listX;
		int recipeSearchWidth = listW;
		int recipeSearchY = listY - 33;

		industrialColonies$recipeSearchInput = new EditBox(
				font,
				recipeSearchX,
				recipeSearchY,
				recipeSearchWidth,
				12,
				Component.translatable("industrial_colonies.kjsgen.review.search")
		);
		industrialColonies$recipeSearchInput.setMaxLength(128);
		industrialColonies$recipeSearchInput.setHint(
				Component.translatable("industrial_colonies.kjsgen.review.search"));
		industrialColonies$recipeSearchInput.setValue(industrialColonies$recipeSearchQuery);
		industrialColonies$recipeSearchInput.setResponder(
				this::industrialColonies$updateRecipeSearch
		);
		addRenderableWidget(industrialColonies$recipeSearchInput);

		int actionWidth = industrialColonies$ACTION_WIDTH;
		int actionGroupWidth = 4 * actionWidth + 3 * industrialColonies$ROW_GAP;
		int rejectX = canvasBoxX + Math.max(0, (canvasBoxW - actionGroupWidth) / 2);
		int deferX = rejectX + actionWidth + industrialColonies$ROW_GAP;
		int maybeX = deferX + actionWidth + industrialColonies$ROW_GAP;
		int approveX = maybeX + actionWidth + industrialColonies$ROW_GAP;
		int controlsY = canvasBoxY + canvasBoxH + 14;

		int navigationGap = industrialColonies$ROW_GAP;
		int navigationLabelWidth = Math.max(
				font.width(Component.translatable("industrial_colonies.kjsgen.review.previous_recipe")),
				font.width(Component.translatable("industrial_colonies.kjsgen.review.next_pending"))) + 12;
		int navigationWidth = Math.min(navigationLabelWidth, Math.max(42, (canvasBoxW - navigationGap) / 2));
		int navigationGroupWidth = 2 * navigationWidth + navigationGap;
		int navigationX = canvasBoxX + Math.max(0, (canvasBoxW - navigationGroupWidth) / 2);
		int navigationY = panelY + 24;
		int nextX = navigationX + navigationWidth + navigationGap;

		industrialColonies$previousButton = Button.builder(
						Component.translatable(
								"industrial_colonies.kjsgen.review.previous_recipe"),
						ignored -> industrialColonies$selectPreviousViewed())
				.bounds(navigationX, navigationY, navigationWidth, industrialColonies$CONTROL_HEIGHT)
				.tooltip(Tooltip.create(Component.translatable(
						"industrial_colonies.kjsgen.review.previous_recipe.tooltip")))
				.build();
		industrialColonies$nextButton = Button.builder(
						Component.translatable(
								"industrial_colonies.kjsgen.review.next_pending"),
						ignored -> industrialColonies$selectNextPending())
				.bounds(nextX, navigationY, navigationWidth, industrialColonies$CONTROL_HEIGHT)
				.tooltip(Tooltip.create(Component.translatable(
						"industrial_colonies.kjsgen.review.next_pending.tooltip")))
				.build();
		industrialColonies$rejectButton = Button.builder(
						Component.literal("\u2715").withStyle(ChatFormatting.RED),
						ignored -> industrialColonies$openManualRejection())
				.bounds(
						rejectX,
						controlsY,
						actionWidth,
						industrialColonies$CONTROL_HEIGHT)
				.tooltip(Tooltip.create(industrialColonies$shortcutTooltip(
						"industrial_colonies.kjsgen.review.reject", "Ctrl+R")))
				.build();
		industrialColonies$deferButton = Button.builder(
						Component.literal("D").withStyle(ChatFormatting.AQUA),
						ignored -> industrialColonies$deferSelected())
				.bounds(
						deferX,
						controlsY,
						actionWidth,
						industrialColonies$CONTROL_HEIGHT)
				.tooltip(Tooltip.create(industrialColonies$shortcutTooltip(
						"industrial_colonies.kjsgen.review.defer", "Ctrl+D")))
				.build();
		industrialColonies$maybeButton = Button.builder(
						Component.literal("?").withStyle(ChatFormatting.YELLOW),
						ignored -> industrialColonies$maybeSelected())
				.bounds(maybeX, controlsY, actionWidth, industrialColonies$CONTROL_HEIGHT)
				.tooltip(Tooltip.create(industrialColonies$shortcutTooltip(
						"industrial_colonies.kjsgen.review.maybe", "Ctrl+M")))
				.build();
		industrialColonies$approveButton = Button.builder(
						Component.literal("\u2713").withStyle(ChatFormatting.GREEN),
						ignored -> industrialColonies$approveSelected())
				.bounds(
						approveX,
						controlsY,
                        actionWidth,
                        industrialColonies$CONTROL_HEIGHT)
                .tooltip(Tooltip.create(industrialColonies$shortcutTooltip(
                        "industrial_colonies.kjsgen.review.approve", "Ctrl+A")))
				.build();

		int tabY = previewY - 12;
		int tabWidth = Math.max(1, (previewW - industrialColonies$ROW_GAP) / 2);
		industrialColonies$commentTabButton = Button.builder(
						Component.literal("Comments"),
						ignored -> industrialColonies$setPreviewTab(true))
				.bounds(previewX, tabY, tabWidth, 12)
				.build();
		industrialColonies$previewTabButton = Button.builder(
						Component.literal("KubeJS Preview"),
						ignored -> industrialColonies$setPreviewTab(false))
				.bounds(
						previewX + tabWidth + industrialColonies$ROW_GAP,
						tabY,
						previewW - tabWidth - industrialColonies$ROW_GAP,
						12)
				.build();
		industrialColonies$syncPreviewTabButtons();

        KjsGenRecipeReviewStore.Counts counts = industrialColonies$cachedCounts();
		boolean localReview = industrialColonies$reviewAvailable();
		boolean managedSelection = industrialColonies$managedSelection().isPresent();
		boolean hasPending = counts.remaining() > 0;

		industrialColonies$previousButton.active = localReview
				&& industrialColonies$viewHistory.hasPrevious(
				industrialColonies$thisRecipeStillExists());
		industrialColonies$nextButton.active = localReview && hasPending;
		industrialColonies$rejectButton.active = localReview && managedSelection;
		industrialColonies$deferButton.active = localReview && managedSelection;
		industrialColonies$maybeButton.active = localReview && managedSelection;
		industrialColonies$approveButton.active = localReview && managedSelection;

		addRenderableWidget(industrialColonies$previousButton);
		addRenderableWidget(industrialColonies$nextButton);
		addRenderableWidget(industrialColonies$rejectButton);
		addRenderableWidget(industrialColonies$deferButton);
		addRenderableWidget(industrialColonies$maybeButton);
		addRenderableWidget(industrialColonies$approveButton);
		addRenderableWidget(industrialColonies$commentTabButton);
		addRenderableWidget(industrialColonies$previewTabButton);
		industrialColonies$syncWidgetVisibility();
	}

	@Inject(method = "tick", at = @At("TAIL"))
	private void industrialColonies$refreshReviewActionsForNewCards(CallbackInfo ci) {
		industrialColonies$syncReviewActions();
	}

    /** Draw the Move button after the panels, independent of the removed footer. */
    @Inject(method = "render", at = @At("TAIL"))
    private void industrialColonies$drawMove(GuiGraphics graphics, int mouseX, int mouseY, float partialTick, CallbackInfo ci) {
        if (industrialColonies$projectMove == null || project == null) return;
        industrialColonies$projectMove.setX(previewX);
        industrialColonies$projectMove.setY(previewY + previewH + 4);
        industrialColonies$projectMove.setWidth(previewW);
        industrialColonies$projectMove.visible = true;
        String projectKey = com.zizazr.kjsgen.core.ProjectManager.sanitizeName(project.name()).toLowerCase(Locale.ROOT);
        industrialColonies$projectMove.active = selectedRecipe().isPresent()
                && (!ClientEditSession.isRemote() || minecraft.hasSingleplayerServer())
                && (!KjsGenProjectMove.archive(project.name()) || projectKey.equals("approved_recipes"));
        industrialColonies$projectMove.render(graphics, mouseX, mouseY, partialTick);
    }

    @Unique private double industrialColonies$commentScroll;
    @Unique private int industrialColonies$commentContentHeight;
    @Unique private String industrialColonies$commentScrollKey = "";

    @Unique
    private int industrialColonies$commentViewportHeight() {
        return Math.max(0, previewH - 2 * industrialColonies$PADDING);
    }

    @Unique
    private void industrialColonies$measureComments() {
        Component comment = industrialColonies$selectedRecipeComment();
        String key = String.valueOf(selectedUid) + "\n" + comment.getString();
        if (!key.equals(industrialColonies$commentScrollKey)) {
            industrialColonies$commentScrollKey = key;
            industrialColonies$commentScroll = 0;
        }
        int textWidth = Math.max(1, previewW - 2 * industrialColonies$PADDING - 6);
        if (comment.getString().isBlank()) comment = Component.translatable(
                "industrial_colonies.kjsgen.review.comment_empty");
        industrialColonies$commentContentHeight =
                (font.split(industrialColonies$statusText(), textWidth).size()
                + font.split(comment, textWidth).size()) * font.lineHeight
                + industrialColonies$ROW_GAP;
        industrialColonies$commentScroll = Mth.clamp(industrialColonies$commentScroll, 0,
                Math.max(0, industrialColonies$commentContentHeight - industrialColonies$commentViewportHeight()));
    }

    @Inject(method = "mouseScrolled", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$scrollComments(double x, double y, double horizontal,
            double vertical, CallbackInfoReturnable<Boolean> callback) {
        if (!industrialColonies$showCommentTab || x < previewX || x >= previewX + previewW
                || y < previewY || y >= previewY + previewH) return;
        industrialColonies$measureComments();
        industrialColonies$commentScroll = Mth.clamp(
                industrialColonies$commentScroll - vertical * font.lineHeight * 3, 0,
                Math.max(0, industrialColonies$commentContentHeight - industrialColonies$commentViewportHeight()));
        // Consume even at either limit so the recipe list/code pane cannot scroll behind it.
        callback.setReturnValue(true);
    }

    @Inject(method = "drawPreview", at = @At("HEAD"), cancellable = true)
    private void industrialColonies$drawCommentPreview(GuiGraphics graphics, CallbackInfo ci) {
        if (!industrialColonies$showCommentTab) return;
        ci.cancel();
        industrialColonies$measureComments();
        graphics.fill(previewX, previewY, previewX + previewW, previewY + previewH, 0xFF18181E);
        graphics.renderOutline(previewX, previewY, previewW, previewH, 0xFF53535E);
        int textWidth = Math.max(1, previewW - 2 * industrialColonies$PADDING - 6);
        int textX = previewX + industrialColonies$PADDING;
        int top = previewY + industrialColonies$PADDING;
        int viewport = industrialColonies$commentViewportHeight();
        if (viewport == 0 || previewW <= 2 * industrialColonies$PADDING) return;
        graphics.enableScissor(textX, top, previewX + previewW - industrialColonies$PADDING, top + viewport);
        try {
            int textY = top - (int) industrialColonies$commentScroll;
            for (var line : font.split(industrialColonies$statusText(), textWidth)) {
                graphics.drawString(font, line, textX, textY, 0xFFAAB5C8, false);
                textY += font.lineHeight;
            }
            textY += industrialColonies$ROW_GAP;
            Component comment = industrialColonies$selectedRecipeComment();
            if (comment.getString().isBlank()) comment = Component.translatable(
                    "industrial_colonies.kjsgen.review.comment_empty");
            for (var line : font.split(comment, textWidth)) {
                if (textY + font.lineHeight > top && textY < top + viewport)
                    graphics.drawString(font, line, textX, textY, 0xFFE0E0E5, false);
                textY += font.lineHeight;
            }
            int maximum = Math.max(0, industrialColonies$commentContentHeight - viewport);
            if (maximum > 0) {
                int barX = previewX + previewW - industrialColonies$PADDING - 3;
                int thumb = Math.min(viewport, Math.max(8, viewport * viewport / industrialColonies$commentContentHeight));
                int barY = top + (int) ((viewport - thumb) * industrialColonies$commentScroll / maximum);
                graphics.fill(barX, top, barX + 3, top + viewport, 0xFF33333E);
                graphics.fill(barX, barY, barX + 3, barY + thumb, 0xFFAAB5C8);
            }
        } finally {
            graphics.disableScissor();
        }
    }

	@Inject(method = "keyPressed", at = @At("HEAD"), cancellable = true)
	private void industrialColonies$handleReviewShortcuts(
			int keyCode,
			int scanCode,
			int modifiers,
			CallbackInfoReturnable<Boolean> callback
	) {
		if (!Screen.hasControlDown() || getFocused() instanceof EditBox
				|| !industrialColonies$reviewAvailable()
				|| industrialColonies$managedSelection().isEmpty()) {
			return;
		}

		boolean handled = true;
		switch (keyCode) {
			case GLFW.GLFW_KEY_A -> industrialColonies$approveSelected();
			case GLFW.GLFW_KEY_R -> industrialColonies$openManualRejection();
			case GLFW.GLFW_KEY_M -> industrialColonies$maybeSelected();
			case GLFW.GLFW_KEY_D -> industrialColonies$deferSelected();
			default -> handled = false;
		}
		if (handled) {
			callback.setReturnValue(true);
			callback.cancel();
		}
	}

    /**
     * Paint a durable decision badge into each visible managed recipe row.
     * This is deliberately render-only: KJSGen retains ownership of list
     * selection, scrolling, duplication, deletion, and view history.
     */
    @Inject(method = "drawRecipeList", at = @At("TAIL"))
    private void industrialColonies$drawRecipeDecisionBadges(
            GuiGraphics graphics,
            int mouseX,
            int mouseY,
            CallbackInfo ci
    ) {
        if (industrialColonies$reviewStore == null
                || !industrialColonies$reviewAvailable()
                || project == null) {
            return;
        }

        int badgeX = listX + listW - 43;
        graphics.enableScissor(
                listX + 1,
                listY + 1,
                listX + listW - 1,
                listY + listViewH - 1);
        try {
            List<RecipeInstance> recipes = industrialColonies$visibleReviewQueue;
            for (int index = 0; index < recipes.size(); index++) {
                RecipeInstance recipe = recipes.get(index);
                if (!industrialColonies$reviewStore.isManaged(recipe.uid())) {
                    continue;
                }

                int rowY = listY
                        + index * industrialColonies$LIST_ROW_HEIGHT
                        - listScroll;
                if (rowY + industrialColonies$LIST_ROW_HEIGHT < listY
                        || rowY > listY + listViewH) {
                    continue;
                }

                KjsGenRecipeReviewStore.Status status =
                        industrialColonies$reviewStore.status(recipe);
                int badgeY = rowY
                        + (industrialColonies$LIST_ROW_HEIGHT
                        - industrialColonies$BADGE_SIZE) / 2;
                int color = industrialColonies$statusColor(status);
                graphics.fill(
                        badgeX,
                        badgeY,
                        badgeX + industrialColonies$BADGE_SIZE,
                        badgeY + industrialColonies$BADGE_SIZE,
                        0xE6000000);
                graphics.renderOutline(
                        badgeX,
                        badgeY,
                        industrialColonies$BADGE_SIZE,
                        industrialColonies$BADGE_SIZE,
                        color);
                graphics.drawCenteredString(
                        font,
                        industrialColonies$statusBadge(status),
                        badgeX + industrialColonies$BADGE_SIZE / 2,
                        badgeY + 1,
                        color);

                if (mouseX >= badgeX
                        && mouseX < badgeX + industrialColonies$BADGE_SIZE
                        && mouseY >= badgeY
                        && mouseY < badgeY + industrialColonies$BADGE_SIZE) {
                    industrialColonies$appendStatusTooltip(recipe, status);
                }
            }
        } finally {
            graphics.disableScissor();
        }
    }

    @Unique
    private Component industrialColonies$statusBadge(
            KjsGenRecipeReviewStore.Status status
    ) {
        return Component.literal(switch (status) {
            case APPROVED -> "A";
            case REJECTED -> "R";
            case DEFERRED -> "D";
            case MAYBE -> "?";
            case DISABLED -> "X";
            case PENDING, STALE -> "!";
        });
    }

    @Unique
    private int industrialColonies$statusColor(
            KjsGenRecipeReviewStore.Status status
    ) {
        return switch (status) {
            case APPROVED -> 0xFF55FF55;
            case REJECTED -> 0xFFFF5555;
            case DEFERRED -> 0xFF55FFFF;
            case MAYBE -> 0xFFFFFF55;
            case DISABLED -> 0xFFFF55FF;
            case PENDING -> 0xFFFFAA00;
            case STALE -> 0xFFFF7F50;
        };
    }

    @Unique
    private ChatFormatting industrialColonies$statusFormatting(
            KjsGenRecipeReviewStore.Status status
    ) {
        return switch (status) {
            case APPROVED -> ChatFormatting.GREEN;
            case REJECTED -> ChatFormatting.RED;
            case DEFERRED -> ChatFormatting.AQUA;
            case MAYBE -> ChatFormatting.YELLOW;
            case DISABLED -> ChatFormatting.LIGHT_PURPLE;
            case PENDING -> ChatFormatting.GOLD;
            case STALE -> ChatFormatting.LIGHT_PURPLE;
        };
    }

    @Unique
    private void industrialColonies$appendStatusTooltip(
            RecipeInstance recipe,
            KjsGenRecipeReviewStore.Status status
    ) {
        List<Component> lines = hoverTooltip == null
                ? new ArrayList<>()
                : new ArrayList<>(hoverTooltip);
        lines.add(Component.translatable(
                        "industrial_colonies.kjsgen.review.list_status",
                        Component.translatable(
                                "industrial_colonies.kjsgen.review.status."
                                        + status.name().toLowerCase(Locale.ROOT)))
                .withStyle(industrialColonies$statusFormatting(status)));
        String note = industrialColonies$reviewStore.note(recipe);
        if (note != null && !note.isBlank()
                && (status == KjsGenRecipeReviewStore.Status.REJECTED
                || status == KjsGenRecipeReviewStore.Status.DEFERRED
                || status == KjsGenRecipeReviewStore.Status.MAYBE
                || status == KjsGenRecipeReviewStore.Status.DISABLED
                || status == KjsGenRecipeReviewStore.Status.STALE)) {
            lines.add(Component.literal(note).withStyle(ChatFormatting.GRAY));
        }
        hoverTooltip = List.copyOf(lines);
    }

    @Unique
    private int industrialColonies$reviewTop() {
        int contentBottom = Math.max(panelY + panelH, canvasBoxY + canvasBoxH);
		int overlayTop = Math.max(0, height - industrialColonies$reviewHeight());
		return Math.min(contentBottom, overlayTop);
    }

    @Unique
    private int industrialColonies$reviewX() {
        return Math.max(2, Math.min(panelX, canvasBoxX) + 4);
    }

    @Unique
    private int industrialColonies$reviewWidth() {
        int left = industrialColonies$reviewX();
        int right = Math.min(
                width - 2,
                Math.max(panelX + panelW, canvasBoxX + canvasBoxW) - 4);
        return Math.max(1, right - left);
    }

	@Unique
	private int industrialColonies$reviewHeight() {
		industrialColonies$syncReviewHeight();
		return industrialColonies$reviewHeight;
	}

	@Unique
	private int industrialColonies$layoutReviewHeight() {
		return Math.min(
				industrialColonies$reviewHeight(),
				Math.max(
						industrialColonies$DIVIDER_HEIGHT,
						height - industrialColonies$MIN_EDITOR_HEIGHT));
	}

	@Unique
	private int industrialColonies$commentHeight() {
		return Math.max(
				industrialColonies$MIN_COMMENT_HEIGHT,
				industrialColonies$reviewHeight()
						- industrialColonies$fixedReviewHeight());
	}

	@Unique
	private int industrialColonies$fixedReviewHeight() {
		return 2 * industrialColonies$PADDING
				+ industrialColonies$STATUS_HEIGHT
				+ industrialColonies$ROW_GAP
				+ industrialColonies$CONTROL_HEIGHT;
	}

	@Unique
	private void industrialColonies$syncReviewHeight() {
		int minimum = industrialColonies$DIVIDER_HEIGHT;
		int maximum = Math.max(
				minimum,
				height - industrialColonies$DIVIDER_HEIGHT);
		if (industrialColonies$reviewHeight < 0) {
			industrialColonies$reviewHeight = industrialColonies$fixedReviewHeight()
					+ industrialColonies$DEFAULT_COMMENT_HEIGHT;
		}
		industrialColonies$reviewHeight = Mth.clamp(
				industrialColonies$reviewHeight,
				minimum,
				maximum);
	}

	@Unique
    private void industrialColonies$syncWidgetVisibility() {
        // Native layoutParamWidgets owns clipping. Never re-enable off-screen inputs.
        if (industrialColonies$projectMove != null) industrialColonies$projectMove.visible = true;
    }

	@Unique
	private Component industrialColonies$shortcutTooltip(String key, String shortcut) {
		return Component.empty()
				.append(industrialColonies$actionTooltip(key))
				.append(Component.literal("\n" + shortcut).withStyle(ChatFormatting.GRAY));
	}

	@Unique
	private void industrialColonies$setPreviewTab(boolean showComment) {
		industrialColonies$showCommentTab = showComment;
		industrialColonies$syncPreviewTabButtons();
	}

	@Unique
	private void industrialColonies$syncPreviewTabButtons() {
		if (industrialColonies$commentTabButton == null
				|| industrialColonies$previewTabButton == null) {
			return;
		}
		industrialColonies$commentTabButton.active = !industrialColonies$showCommentTab;
		industrialColonies$previewTabButton.active = industrialColonies$showCommentTab;
	}

    @Unique private final dev.godpc.industrialcolonies.KjsGenUiCache<KjsGenRecipeReviewStore.Counts> industrialColonies$countCache=new dev.godpc.industrialcolonies.KjsGenUiCache<>();
    @Unique private KjsGenRecipeReviewStore.Counts industrialColonies$cachedCounts(){
        return industrialColonies$countCache.get(project,project.recipes().size(),System.nanoTime(),()->industrialColonies$reviewStore.counts(project));
    }
    @Inject(method={"markDirty","init","refreshFromSession"},at=@At("HEAD"))
    private void industrialColonies$invalidateCounts(CallbackInfo ci){industrialColonies$countCache.invalidate();}

    @Unique
    private Component industrialColonies$statusText() {
        if (!industrialColonies$reviewAvailable()) {
            return Component.translatable(
                    "industrial_colonies.kjsgen.review.status.remote_disabled");
        }

        KjsGenRecipeReviewStore.Counts counts = industrialColonies$cachedCounts();
        Optional<RecipeInstance> selected = selectedRecipe();
        if (selected.isEmpty() || !industrialColonies$reviewStore.canReview(selected.get())) {
            return Component.translatable(
                    "industrial_colonies.kjsgen.review.status.unmanaged",
                    counts.remaining(),
                    counts.managed());
        }

        KjsGenRecipeReviewStore.Status status =
                industrialColonies$reviewStore.status(selected.get());
        Component statusName = Component.translatable(
                "industrial_colonies.kjsgen.review.status."
                        + status.name().toLowerCase(Locale.ROOT));
        return Component.translatable(
                "industrial_colonies.kjsgen.review.status.summary",
                statusName,
                counts.remaining(),
                counts.approved(),
                counts.rejected(),
                counts.deferred(),
                counts.maybe(),
                counts.disabled());
    }

	@Unique
	private Component industrialColonies$actionTooltip(String actionKey) {
        return selectedRecipe()
                .filter(recipe -> industrialColonies$reviewStore != null
						&& industrialColonies$reviewStore.canReview(recipe))
                .map(recipe -> Component.translatable(
                        "industrial_colonies.kjsgen.review.action.tooltip",
                        Component.translatable(actionKey),
                        recipe.recipeId(),
                        recipe.uid()))
                .orElseGet(() -> Component.translatable(actionKey));
    }

    @Unique
    private Component industrialColonies$selectedRecipeComment() {
        if (industrialColonies$reviewStore == null) {
            return Component.empty();
        }
        return selectedRecipe()
                .map(recipe -> dev.godpc.industrialcolonies.KjsGenRecipeHelp.describe(
                        recipe.recipeId(), recipe.toJson(), industrialColonies$reviewStore.note(recipe)))
                .map(Component::literal)
                .orElse(Component.empty());
    }

    @Unique
    private Optional<RecipeInstance> industrialColonies$managedSelection() {
        if (industrialColonies$reviewStore == null || !industrialColonies$reviewAvailable()) {
            return Optional.empty();
        }
        return selectedRecipe().filter(
				recipe -> industrialColonies$reviewStore.canReview(recipe)
						&& industrialColonies$reviewStore
                        .isVisibleInReviewQueue(project, recipe));
    }

    @Unique
    private void industrialColonies$approveSelected() {
        industrialColonies$managedSelection().ifPresent(recipe -> {
            Optional<String> archiveNext =
                    industrialColonies$nextArchiveRecipeUid(recipe.uid());
            if (industrialColonies$reviewStore.approve(recipe)) {
                industrialColonies$advanceAfterDecision(
                        recipe.uid(),
                        KjsGenRecipeReviewStore.Status.APPROVED,
                        archiveNext);
            }
        });
    }

    @Unique
    private void industrialColonies$maybeSelected() {
        industrialColonies$managedSelection().ifPresent(recipe -> {
            Optional<String> archiveNext =
                    industrialColonies$nextArchiveRecipeUid(recipe.uid());
            if (industrialColonies$reviewStore.maybe(recipe)) {
                industrialColonies$advanceAfterDecision(
                        recipe.uid(),
                        KjsGenRecipeReviewStore.Status.MAYBE,
                        archiveNext);
            }
        });
    }

    @Unique
    private void industrialColonies$deferSelected() {
        industrialColonies$managedSelection().ifPresent(recipe -> {
            Screen editor = (Screen) (Object) this;
            Minecraft.getInstance().setScreen(new KjsGenDeferReasonScreen(
                    editor, Component.literal(recipe.recipeId()), note -> {
                        Optional<String> archiveNext =
                                industrialColonies$nextArchiveRecipeUid(recipe.uid());
                        if (!industrialColonies$reviewStore.defer(recipe, note)) return false;
                        industrialColonies$advanceAfterDecision(
                                recipe.uid(), KjsGenRecipeReviewStore.Status.DEFERRED, archiveNext);
                        return true;
                    }));
        });
    }

    @Unique
    private void industrialColonies$openManualRejection() {
        industrialColonies$managedSelection().ifPresent(recipe -> {
            Screen editor = (Screen) (Object) this;
            Minecraft.getInstance().setScreen(new KjsGenRejectReasonScreen(
                    editor,
                    Component.literal(recipe.recipeId()),
                    (code, note) -> {
                        Optional<String> archiveNext =
                                industrialColonies$nextArchiveRecipeUid(recipe.uid());
                        boolean disabling = code != null
                                && code.startsWith(industrialColonies$DISABLE_CODE_PREFIX);
                        boolean saved = disabling
                                ? industrialColonies$reviewStore.disable(
                                        recipe,
                                        code.substring(
                                                industrialColonies$DISABLE_CODE_PREFIX.length()),
                                        note)
                                : industrialColonies$reviewStore.reject(recipe, code, note);
                        if (saved) {
                            industrialColonies$advanceAfterDecision(
                                    recipe.uid(),
                                    disabling
                                            ? KjsGenRecipeReviewStore.Status.DISABLED
                                            : KjsGenRecipeReviewStore.Status.REJECTED,
                                    archiveNext);
                            return true;
                        }
                        return false;
                    }));
        });
    }

    @Unique
    private void industrialColonies$selectNextPending() {
        if (industrialColonies$reviewStore == null || !industrialColonies$reviewAvailable()) {
            return;
        }
        industrialColonies$navigateTo(
                industrialColonies$reviewStore.nextPending(project, selectedUid));
    }

    @Unique
    private void industrialColonies$selectPreviousViewed() {
        if (!industrialColonies$reviewAvailable()) {
            return;
        }
        industrialColonies$viewHistory.observe(selectedUid);
        industrialColonies$viewHistory.previous(
                        industrialColonies$thisRecipeStillExists())
                .ifPresent(uid -> {
                    selectedUid = uid;
                    rebuildWidgets();
                });
    }

    @Unique
    private void industrialColonies$advanceAfterDecision(
            String reviewedUid,
            KjsGenRecipeReviewStore.Status destination,
            Optional<String> archiveNext
    ) {
        Optional<KjsGenRecipeReviewStore.Status> archiveStatus =
                industrialColonies$currentArchiveStatus();
        if (archiveStatus.isPresent()) {
            // Store persistence moves the snapshot between archive projects.
            // Keep this screen's local project model in sync immediately;
            // rebuilding then reloads ledger-backed counts and button state.
            if (archiveStatus.get() != destination) {
                project.recipes().removeIf(recipe -> recipe.uid().equals(reviewedUid));
            }
            Optional<String> next = archiveNext.filter(
                    industrialColonies$thisRecipeStillExists());
            if (next.isPresent()) {
                selectedUid = next.get();
            } else if (project.recipes().stream()
                    .noneMatch(recipe -> recipe.uid().equals(selectedUid))) {
                selectedUid = project.recipes().isEmpty()
                        ? null
                        : project.recipes().get(0).uid();
            }
            rebuildWidgets();
            return;
        }

        Optional<RecipeInstance> next =
                industrialColonies$reviewStore.nextPending(project, reviewedUid);
        if (next.isPresent()) {
            industrialColonies$navigateTo(next);
        } else {
            rebuildWidgets();
        }
    }

    @Unique
    private Optional<String> industrialColonies$nextArchiveRecipeUid(String currentUid) {
        if (industrialColonies$currentArchiveStatus().isEmpty()
                || project == null
                || industrialColonies$visibleReviewQueue.size() <= 1) {
            return Optional.empty();
        }
        List<RecipeInstance> recipes = industrialColonies$visibleReviewQueue;
        int index = -1;
        for (int candidate = 0; candidate < recipes.size(); candidate++) {
            if (recipes.get(candidate).uid().equals(currentUid)) {
                index = candidate;
                break;
            }
        }
        if (index < 0) {
            return Optional.of(recipes.get(0).uid());
        }
        int nextIndex = index + 1 < recipes.size() ? index + 1 : index - 1;
        return Optional.of(recipes.get(nextIndex).uid());
    }

	@Unique
	private Optional<KjsGenRecipeReviewStore.Status>
			industrialColonies$currentArchiveStatus() {
        if (project == null || project.name() == null) {
            return Optional.empty();
		}
        String name = project.name().trim().toLowerCase(Locale.ROOT).replace('_', ' ');
        return switch (name) {
            case industrialColonies$APPROVED_PROJECT ->
                    Optional.of(KjsGenRecipeReviewStore.Status.APPROVED);
            case industrialColonies$REJECTED_PROJECT ->
                    Optional.of(KjsGenRecipeReviewStore.Status.REJECTED);
            case industrialColonies$DEFERRED_PROJECT ->
                    Optional.of(KjsGenRecipeReviewStore.Status.DEFERRED);
            case industrialColonies$MAYBE_PROJECT ->
                    Optional.of(KjsGenRecipeReviewStore.Status.MAYBE);
            case industrialColonies$DISABLED_PROJECT ->
                    Optional.of(KjsGenRecipeReviewStore.Status.DISABLED);
            default -> Optional.empty();
        };
    }

	@Unique
	private void industrialColonies$updateRecipeSearch(String query) {
		String priorSelection = selectedUid;
		boolean restoreSearchFocus = getFocused() == industrialColonies$recipeSearchInput;
		int searchCursor = industrialColonies$recipeSearchInput == null ? 0
				: industrialColonies$recipeSearchInput.getCursorPosition();
		industrialColonies$recipeSearchQuery = industrialColonies$normalizeRecipeSearch(query);
		industrialColonies$refreshVisibleReviewQueue(project);

		boolean selectedStillVisible = selectedUid != null && industrialColonies$visibleReviewQueue
				.stream()
				.anyMatch(recipe -> recipe.uid().equals(selectedUid));
		if (!selectedStillVisible) {
			selectedUid = industrialColonies$visibleReviewQueue.isEmpty()
					? null
					: industrialColonies$visibleReviewQueue.get(0).uid();
		}

		int maxListScroll = Math.max(
				0,
				industrialColonies$visibleReviewQueue.size()
						* industrialColonies$LIST_ROW_HEIGHT - listViewH);
		listScroll = Math.min(listScroll, maxListScroll);
		if (!java.util.Objects.equals(priorSelection, selectedUid)) {
			// Native parameter widgets capture the recipe they were built for.
			// Changing only selectedUid leaves live controls bound to the old card.
			rebuildWidgets();
			if (restoreSearchFocus && industrialColonies$recipeSearchInput != null) {
				setFocused(industrialColonies$recipeSearchInput);
				industrialColonies$recipeSearchInput.setCursorPosition(Math.min(searchCursor,
						industrialColonies$recipeSearchInput.getValue().length()));
			}
		}
		industrialColonies$syncReviewActions();
	}

	@Unique
	private void industrialColonies$syncReviewActions() {
		if (industrialColonies$previousButton == null
				|| industrialColonies$nextButton == null
				|| industrialColonies$rejectButton == null
				|| industrialColonies$deferButton == null
				|| industrialColonies$maybeButton == null
				|| industrialColonies$approveButton == null) {
			return;
		}
		KjsGenRecipeReviewStore.Counts counts = industrialColonies$reviewStore == null
				|| project == null ? null : industrialColonies$cachedCounts();
		boolean localReview = industrialColonies$reviewAvailable();
		boolean managedSelection = industrialColonies$managedSelection().isPresent();
		boolean hasPending = counts != null && counts.remaining() > 0;

		industrialColonies$previousButton.active = localReview
				&& industrialColonies$viewHistory.hasPrevious(
						industrialColonies$thisRecipeStillExists());
		industrialColonies$nextButton.active = localReview && hasPending;
		industrialColonies$rejectButton.active = localReview && managedSelection;
		industrialColonies$deferButton.active = localReview && managedSelection;
		industrialColonies$maybeButton.active = localReview && managedSelection;
		industrialColonies$approveButton.active = localReview && managedSelection;
	}

	@Unique
	private static String industrialColonies$normalizeRecipeSearch(String query) {
		return query == null ? "" : query.strip().toLowerCase(Locale.ROOT);
	}

	@Unique
	private boolean industrialColonies$matchesRecipeSearch(
			RecipeInstance recipe,
			String normalizedQuery
	) {
		if (normalizedQuery == null || normalizedQuery.isBlank() || recipe == null) {
			return true;
		}
		String recipeId = recipe.recipeId() == null ? "" : recipe.recipeId().toLowerCase(Locale.ROOT);
		String uid = recipe.uid() == null ? "" : recipe.uid().toLowerCase(Locale.ROOT);
		return recipeId.contains(normalizedQuery)
				|| uid.contains(normalizedQuery);
	}

    @Unique
    private void industrialColonies$navigateTo(Optional<RecipeInstance> recipe) {
        recipe.ifPresent(next -> {
            industrialColonies$viewHistory.navigateTo(next.uid());
            selectedUid = next.uid();
            rebuildWidgets();
        });
    }

    @Unique
    private java.util.function.Predicate<String> industrialColonies$thisRecipeStillExists() {
        return uid -> project != null
                && industrialColonies$reviewStore != null
                && industrialColonies$visibleReviewQueue.stream()
                .anyMatch(recipe -> recipe.uid().equals(uid));
    }

    @Unique
    private boolean industrialColonies$reviewAvailable() {
        // KJSGen marks its edit session as "remote" even in single-player
        // after the integrated server sends the project snapshot. That is
        // still the user's local project and must remain reviewable. Only a
        // genuine multiplayer server session is read-only here.
        Minecraft minecraft = Minecraft.getInstance();
        return !ClientEditSession.isRemote() || minecraft.hasSingleplayerServer();
    }
}
