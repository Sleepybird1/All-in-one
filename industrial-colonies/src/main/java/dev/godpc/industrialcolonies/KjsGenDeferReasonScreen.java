package dev.godpc.industrialcolonies;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import java.util.Objects;
import java.util.function.Function;

/** Two different user intents, kept in the compatible Deferred note field. */
public final class KjsGenDeferReasonScreen extends Screen {
    public static final String NEEDS_EXPLANATION =
            "Needs explanation: I don't know what this machine or item does. Explain its function, uses, progression and overlap before another review.";
    public static final String PARK_FOR_LATER =
            "Parked for later: Put this item aside until I choose to revisit it. Do not redesign or automatically return it to review.";
    private final Screen parent;
    private final Component recipeLabel;
    private final Function<String, Boolean> onSubmit;
    private boolean failed;
    private int left, top, panelWidth, panelHeight;

    public KjsGenDeferReasonScreen(Screen parent, Component recipeLabel,
                                  Function<String, Boolean> onSubmit) {
        super(Component.literal("Why defer this recipe?"));
        this.parent = Objects.requireNonNull(parent);
        this.recipeLabel = Objects.requireNonNull(recipeLabel);
        this.onSubmit = Objects.requireNonNull(onSubmit);
    }

    @Override
    protected void init() {
        panelWidth = Math.max(1, Math.min(430, width - 16));
        panelHeight = Math.max(1, Math.min(164, height - 12));
        left = (width - panelWidth) / 2;
        top = (height - panelHeight) / 2;
        int row = Math.max(16, Math.min(22, (panelHeight - 68) / 4));
        int y = top + 47;
        addRenderableWidget(Button.builder(Component.literal("I don't know what this does"),
                ignored -> submit(NEEDS_EXPLANATION))
                .bounds(left + 10, y, Math.max(1, panelWidth - 20), row)
                .tooltip(Tooltip.create(Component.literal(
                        "Needs a description of its purpose, uses, progression and similar machines. This is not a rejection.")))
                .build());
        addRenderableWidget(Button.builder(Component.literal("Put this aside for later"),
                ignored -> submit(PARK_FOR_LATER))
                .bounds(left + 10, y + row + 6, Math.max(1, panelWidth - 20), row)
                .tooltip(Tooltip.create(Component.literal(
                        "Keep it parked until you choose to revisit it. No automatic redesign or return to review.")))
                .build());
        addRenderableWidget(Button.builder(Component.literal("Cancel"), ignored -> onClose())
                .bounds(left + 10, top + panelHeight - row - 10,
                        Math.max(1, panelWidth - 20), row).build());
    }

    private void submit(String note) {
        if (Boolean.TRUE.equals(onSubmit.apply(note))) {
            minecraft.setScreen(parent);
        } else {
            failed = true;
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        // Never render the parent: its item models previously overlapped modal controls.
        graphics.fill(0, 0, width, height, 0xFF14161C);
        graphics.renderOutline(left, top, panelWidth, panelHeight, 0xFF9EA9BC);
        graphics.drawCenteredString(font, title, width / 2, top + 9, 0xFFFFFFFF);
        graphics.drawString(font, font.plainSubstrByWidth(recipeLabel.getString(),
                Math.max(1, panelWidth - 20)), left + 10, top + 26, 0xFFB8C7DD);
        if (failed) graphics.drawString(font, "Could not save. Try again or cancel.",
                left + 10, top + panelHeight - 43, 0xFFFF7070);
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override public void onClose() { minecraft.setScreen(parent); }
    @Override public boolean isPauseScreen() { return false; }
}
