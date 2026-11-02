package dev.godpc.industrialcolonies;

import java.util.List;

/** Bounded JEI geometry for the vat's 24 direct item feed slots and four fluid channels. */
public final class ExpandedVatJeiLayout {
    public static final int WIDTH = 320;
    public static final int HEIGHT = 144;
    public static final int ITEM_COLUMNS = 6;
    public static final int MAX_ITEMS = 24;
    public static final int VAT_X = 134;
    public record Position(int x, int y) { }
    private ExpandedVatJeiLayout() { }
    public static boolean expanded(int condensedItemInputs) { return condensedItemInputs > 4; }
    /** Render each required attachment once; native contains-based artwork implies fixed counts. */
    public static List<KjsGenVatCanvasModel.Attachment> machineAttachments(List<String> ids) {
        if (ids.size() > 3) throw new IllegalArgumentException("Chemical Vat has three attachment positions");
        int drives = 0;
        for (String id : ids) {
            switch (id) {
                case "tfmg:mixing", "tfmg:centrifuge" -> drives++;
                case "tfmg:electrode", "tfmg:graphite_electrode" -> { }
                default -> throw new IllegalArgumentException("Unknown Chemical Vat attachment: " + id);
            }
        }
        if (drives > 1) throw new IllegalArgumentException("Chemical Vat has one central drive position");
        return KjsGenVatCanvasModel.attachments(String.join(",", ids));
    }
    public static Position itemInput(int index) {
        bounded(index, MAX_ITEMS);
        return new Position(4 + index % ITEM_COLUMNS * 20, 18 + index / ITEM_COLUMNS * 20);
    }
    public static Position fluidInput(int index, int count) {
        if (count < 1 || count > 4) throw new IllegalArgumentException("Chemical Vat has four fluid inputs");
        bounded(index, count);
        return new Position(64 - count * 20 / 2 + (count == 1 ? 2 : count == 4 ? 0 : 1) + index * 21, 112);
    }
    public static Position itemOutput(int index) { bounded(index, 4); return new Position(270, 90 - index * 21); }
    public static Position fluidOutput(int index) { bounded(index, 4); return new Position(292, 90 - index * 21); }
    public static void requireCapacity(int items, int fluids, int itemOutputs, int fluidOutputs) {
        if (items < 0 || items > MAX_ITEMS || fluids < 0 || fluids > 4
                || itemOutputs < 0 || itemOutputs > 4 || fluidOutputs < 0 || fluidOutputs > 4)
            throw new IllegalArgumentException("Expanded Chemical Vat JEI layout supports 24 item inputs, four fluid inputs and four outputs of each kind");
    }
    private static void bounded(int value, int limit) {
        if (value < 0 || value >= limit) throw new IllegalArgumentException("Chemical Vat slot index out of bounds");
    }
}
