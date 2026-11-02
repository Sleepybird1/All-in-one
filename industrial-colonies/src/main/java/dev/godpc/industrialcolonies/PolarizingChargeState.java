package dev.godpc.industrialcolonies;

/** Persistent paid progress; no credit can move between input/recipe fingerprints or duplicate ticks. */
public final class PolarizingChargeState {
    private String binding = "";
    private int paid, required;
    private long lastTick = Long.MIN_VALUE;
    public String binding() { return binding; }
    public int paid() { return paid; }
    public int required() { return required; }
    public long lastTick() { return lastTick; }
    public void clear() { binding = ""; paid = required = 0; lastTick = Long.MIN_VALUE; }
    public void bind(String key, int ticks) {
        if (!key.matches("[0-9a-f]{64}") || ticks < 1 || ticks > AtmPolarizingPolicy.MAX_TICKS)
            throw new IllegalArgumentException("Invalid polarizing work binding");
        if (!binding.equals(key) || required != ticks) { clear(); binding = key; required = ticks; }
    }
    public boolean credit(String key, int ticks, long gameTime, boolean supplied) {
        bind(key, ticks);
        if (!supplied || gameTime < 0 || gameTime <= lastTick || paid >= required) return false;
        paid++; lastTick = gameTime; return true;
    }
    public boolean ready(String key, int ticks, boolean supplied) {
        return supplied && binding.equals(key) && required == ticks && paid == required;
    }
    public int displayedCharge() { return required == 0 ? 0 : (int) ((long) paid * 200 / required); }
    public void restore(String key, int ticks, int completed, long creditedTick) {
        clear();
        if (key == null || !key.matches("[0-9a-f]{64}") || ticks < 1
            || ticks > AtmPolarizingPolicy.MAX_TICKS || completed < 0 || completed > ticks
            || completed > 0 && creditedTick < 0) return;
        binding = key; required = ticks; paid = completed; lastTick = creditedTick;
    }
}
