package dev.godpc.industrialcolonies.space.enemy;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Staged admission accounting, not a spawner. Held encounters retain their budget.
 * Before enabling a future runtime, rebuild reservations from authoritative native
 * NPC bodies (including held survivors); a fresh budget alone must not enable spawning.
 */
public final class EnemyEncounterBudget {
    private final int maxEncounters;
    private final long maxBlocks;
    private final Map<UUID,Long> reservations = new HashMap<>();
    private long usedBlocks;
    public EnemyEncounterBudget(int maxEncounters, long maxBlocks) {
        if (maxEncounters < 1 || maxBlocks < 1) throw new IllegalArgumentException("Positive caps required");
        this.maxEncounters=maxEncounters; this.maxBlocks=maxBlocks;
    }
    public synchronized boolean reserve(UUID encounter, long blocks) {
        if (encounter==null || blocks<1 || reservations.containsKey(encounter)
                || reservations.size()>=maxEncounters || blocks>maxBlocks-usedBlocks) return false;
        reservations.put(encounter,blocks); usedBlocks+=blocks; return true;
    }
    /** Reconcile larger/smaller actual bodies before allowing another action. */
    public synchronized boolean resize(UUID encounter, long blocks) {
        Long old=reservations.get(encounter);
        if (old==null || blocks<1 || blocks>maxBlocks-(usedBlocks-old)) return false;
        usedBlocks=usedBlocks-old+blocks; reservations.put(encounter,blocks); return true;
    }
    /** Call only after verified removal or ownership transfer, never merely on hold/stop. */
    public synchronized boolean release(UUID encounter) {
        Long old=reservations.remove(encounter);
        if (old==null) return false;
        usedBlocks-=old; return true;
    }
    public synchronized long usedBlocks() { return usedBlocks; }
    /** Atomic restart reconstruction. Failure leaves existing reservations exact. */
    public synchronized boolean restore(Map<UUID,Long> surviving) {
        if(surviving==null||surviving.size()>maxEncounters)return false;
        var candidate=new HashMap<UUID,Long>();long total=0;
        for(var entry:surviving.entrySet()){
            if(entry.getKey()==null||entry.getValue()==null||entry.getValue()<1
                    ||entry.getValue()>maxBlocks-total)return false;
            total+=entry.getValue();candidate.put(entry.getKey(),entry.getValue());
        }
        reservations.clear();reservations.putAll(candidate);usedBlocks=total;return true;
    }
    public synchronized int activeEncounters() { return reservations.size(); }
}
