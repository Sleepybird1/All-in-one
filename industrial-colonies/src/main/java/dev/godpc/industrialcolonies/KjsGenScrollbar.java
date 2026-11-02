package dev.godpc.industrialcolonies;

/** Geometry shared by rendering and hit testing. Coordinates use scaled GUI pixels. */
public record KjsGenScrollbar(int x, int y, int height, int contentHeight, int scroll) {
    public static final int GUTTER = 18;
    public static final int WIDTH = 14;

    public int maxScroll() { return Math.max(0, contentHeight - height); }
    public int clamp(int value) { return Math.max(0, Math.min(maxScroll(), value)); }
    public int thumbHeight() {
        if (height <= 0) return 0;
        return Math.min(height, Math.max(24, (int)((long)height * height / Math.max(1, contentHeight))));
    }
    public int thumbY() {
        return y + (maxScroll() == 0 ? 0 : (int)Math.round((double)(height - thumbHeight()) * clamp(scroll) / maxScroll()));
    }
    public boolean contains(double mouseX, double mouseY) {
        return height > 0 && mouseX >= x && mouseX < x + GUTTER && mouseY >= y && mouseY < y + height;
    }
    public boolean onThumb(double mouseY) { return mouseY >= thumbY() && mouseY < thumbY() + thumbHeight(); }
    public int scrollAt(double mouseY, double grabOffset) {
        int travel = height - thumbHeight();
        if (travel <= 0) return 0;
        double fraction = Math.max(0, Math.min(1, (mouseY - y - grabOffset) / travel));
        return clamp((int)Math.round(fraction * maxScroll()));
    }
}
