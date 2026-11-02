package dev.godpc.industrialcolonies.space;

/** Rated capacity, not used contents: partitioning/empty cells cannot bypass the budget. */
public final class ShipAeBudget {
    public static final long MAX_ITEM_BYTES = 4096;
    private long bytes;
    private long cells;
    private boolean denied;
    public boolean add(long ratedBytes, long count, boolean itemStorage, boolean measurable) {
        if (!measurable || !itemStorage || ratedBytes <= 0 || count <= 0
                || ratedBytes > MAX_ITEM_BYTES || count > (MAX_ITEM_BYTES - bytes) / ratedBytes) {
            denied = true;
        } else {
            bytes += ratedBytes * count;
            cells += count;
        }
        return allowed();
    }
    public boolean allowed() { return !denied; }
    public boolean authorized(int stabilizers) { return stabilizers > 0 && cells <= stabilizers && allowed(); }
    public long cells() { return cells; }
    public long bytes() { return bytes; }
}
