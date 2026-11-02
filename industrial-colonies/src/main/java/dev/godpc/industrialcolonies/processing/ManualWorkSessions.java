package dev.godpc.industrialcolonies.processing;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Small server-thread state machine: one real player, one station, one item, no queued work. */
public final class ManualWorkSessions {
    public record Station(String dimension, long position) {}
    public record Session(UUID player, Station station, long startedAt) {}
    private final Map<UUID, Session> players = new HashMap<>();
    private final Map<Station, UUID> stations = new HashMap<>();

    public boolean begin(UUID player, Station station, long now) {
        if (players.containsKey(player) || stations.containsKey(station)) return false;
        players.put(player, new Session(player, station, now));
        stations.put(station, player);
        return true;
    }

    public Session get(UUID player) { return players.get(player); }
    public void cancel(UUID player) {
        Session session = players.remove(player);
        if (session != null) stations.remove(session.station(), player);
    }
    public void clear() { players.clear(); stations.clear(); }
    public int size() { return players.size(); }

    public static boolean mayContinue(int count, boolean alive, boolean sameDimension,
                                      boolean sameItem, boolean lit, boolean inReach, boolean aimedAt) {
        return count == 1 && alive && sameDimension && sameItem && lit && inReach && aimedAt;
    }

    public static boolean finished(long startedAt, long now, int requiredTicks) {
        if (requiredTicks < 1) throw new IllegalArgumentException("Positive manual duration required");
        return now >= startedAt && now - startedAt >= requiredTicks;
    }
}
