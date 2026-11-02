package dev.godpc.industrialcolonies.space.collision;

import java.util.*;

/** Staged work limiter only: no collision detection, ownership admission or block writes.
 * Conservatively groups the entire body pair, rather than allowing moving contact
 * regions to renew damage. A caller must submit every observed contact, including
 * zero-damage ones, and use persistent body identities rather than recycled IDs. */
public final class CollisionEpisodeBudget {
    public record Pair(UUID first,UUID second) {
        public Pair {
            Objects.requireNonNull(first);Objects.requireNonNull(second);
            if(first.equals(second))throw new IllegalArgumentException("Distinct bodies required");
            if(first.compareTo(second)>0){UUID swap=first;first=second;second=swap;}
        }
    }
    public record Grant(int blocks,String reason) {}
    private static final int EPISODE_CAP=16,SHIP_TICK_CAP=32,GLOBAL_TICK_CAP=64;
    private static final long RELEASE_AFTER=10;
    private static final class Episode { long lastContact; boolean charged; Episode(long t){lastContact=t;} }
    private final Map<Pair,Episode> episodes=new HashMap<>();
    private final Map<UUID,Integer> shipWork=new HashMap<>();
    private final int maxPairs;
    private long tick=-1;
    private int globalWork;
    public CollisionEpisodeBudget(int maxPairs){
        if(maxPairs<1||maxPairs>1024)throw new IllegalArgumentException("Bounded pair capacity required");
        this.maxPairs=maxPairs;
    }
    /** No reservation replay. A denied/partial positive request consumes this episode;
     * work is dropped, never deferred into a later tick. Zero requests refresh contact. */
    public synchronized Grant observe(long now,Pair pair,UUID damagedBody,int requested){
        Objects.requireNonNull(pair);Objects.requireNonNull(damagedBody);
        if(!damagedBody.equals(pair.first())&&!damagedBody.equals(pair.second()))throw new IllegalArgumentException("Foreign damage body");
        if(requested<0||requested>EPISODE_CAP)throw new IllegalArgumentException("Request outside episode cap");
        if(now<0||now<tick)return new Grant(0,"CLOCK_REVERSED");
        if(now!=tick){
            tick=now;globalWork=0;shipWork.clear();
            episodes.entrySet().removeIf(e->now-e.getValue().lastContact>RELEASE_AFTER);
        }
        Episode episode=episodes.get(pair);
        if(episode==null){
            if(episodes.size()>=maxPairs)return new Grant(0,"PAIR_CAPACITY");
            episode=new Episode(now);episodes.put(pair,episode);
        }
        episode.lastContact=now;
        if(requested==0)return new Grant(0,"CONTACT_ONLY");
        if(episode.charged)return new Grant(0,"EPISODE_ALREADY_CHARGED");
        episode.charged=true;
        int used=shipWork.getOrDefault(damagedBody,0);
        int grant=Math.max(0,Math.min(requested,Math.min(SHIP_TICK_CAP-used,GLOBAL_TICK_CAP-globalWork)));
        if(grant>0){globalWork+=grant;shipWork.put(damagedBody,used+grant);}
        return new Grant(grant,grant==requested?"GRANTED":"TICK_BUDGET_EXHAUSTED");
    }
    public synchronized int retainedPairs(){return episodes.size();}
}
