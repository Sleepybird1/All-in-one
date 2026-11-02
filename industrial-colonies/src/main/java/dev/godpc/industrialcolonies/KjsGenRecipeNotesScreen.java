package dev.godpc.industrialcolonies;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import java.util.List;

/** Scrollable explanation view, with no recipe or review mutations. */
public final class KjsGenRecipeNotesScreen extends Screen {
    private final Screen parent;
    private final Component text;
    private List<FormattedCharSequence> lines = List.of();
    private int offset;

    public KjsGenRecipeNotesScreen(Screen parent, Component text) {
        super(Component.literal("Recipe notes and explanations"));
        this.parent = parent;
        this.text = text;
    }

    @Override
    protected void init() {
        lines = font.split(text, Math.max(40, width - 40));
        offset = Math.min(offset, maximumOffset());
        addRenderableWidget(Button.builder(Component.literal("Back to recipe"), button -> onClose())
                .bounds(Math.max(0, width / 2 - 70), height - 26, 140, 20).build());
    }

    private int visibleLines() { return Math.max(1, (height - 70) / font.lineHeight); }
    private int maximumOffset() { return Math.max(0, lines.size() - visibleLines()); }

    @Override
    public boolean mouseScrolled(double x, double y, double horizontal, double vertical) {
        offset = Math.max(0, Math.min(maximumOffset(), offset - (int) Math.signum(vertical) * 3));
        return true;
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float delta) {
        graphics.fill(0, 0, width, height, 0xFF14161C);
        graphics.drawCenteredString(font, title, width / 2, 10, 0xFFFFFF);
        for (int i = 0; i < visibleLines() && offset + i < lines.size(); i++) {
            graphics.drawString(font, lines.get(offset + i), 20, 30 + i * font.lineHeight, 0xE0E0E5, false);
        }
        graphics.drawString(font, "Scroll to read more", 20, height - 39, 0xAAB5C8, false);
        super.render(graphics, mouseX, mouseY, delta);
    }

    @Override public void onClose() { minecraft.setScreen(parent); }
    @Override public boolean isPauseScreen() { return false; }
}
