package dev.godpc.industrialcolonies.geology;

/** Exact native structure placement frame; never grants permission to unrelated mines. */
public final class VeinMinePlacement {
    private static final ThreadLocal<Boolean> LINKED = new ThreadLocal<>();
    private VeinMinePlacement() {}
    public static boolean linked() { return Boolean.TRUE.equals(LINKED.get()); }
    public static void during(boolean linked,Runnable placement) {
        Boolean before=LINKED.get(); LINKED.set(linked);
        try { placement.run(); }
        finally { if(before==null)LINKED.remove();else LINKED.set(before); }
    }
}
