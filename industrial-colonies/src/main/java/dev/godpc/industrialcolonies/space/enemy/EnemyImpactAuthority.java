package dev.godpc.industrialcolonies.space.enemy;

import dev.godpc.industrialcolonies.space.SpaceflightAuthorization;
import dev.ryanhcode.sable.Sable;
import dev.ryanhcode.sable.sublevel.ServerSubLevel;
import net.minecraft.world.phys.BlockHitResult;
import java.util.*;

/** World-read-only, finite ship-only impact authority. This is not permission
 * to fire or adopt a projectile. A future firing owner must bind its own exact
 * native projectile and invoke this before every damage and impact-force entry.
 * Nothing registers automatically or restores this authority after restart. */
public final class EnemyImpactAuthority {
    public record Result(boolean allowed,String reason) {}
    private final ServerSubLevel source,target;
    private final NativeEnemyHull hull;
    private final Set<UUID> hostile,players,friendly;
    private final EnemyTargetSelector.Selection admitted;
    private final EnemyHullIdentity.Identity originalSource;
    private final long created;
    private final int lifetime;
    private String refused;
    private EnemyImpactAuthority(ServerSubLevel source,NativeEnemyHull hull,
            ServerSubLevel target,Set<UUID> hostile,Set<UUID> players,Set<UUID> friendly,
            EnemyTargetSelector.Selection admitted,int lifetime) {
        this.source=source;this.hull=hull;this.target=target;
        this.hostile=Set.copyOf(hostile);this.players=Set.copyOf(players);
        this.friendly=Set.copyOf(friendly);this.admitted=admitted;
        originalSource=EnemyHullIdentity.read(source);
        created=source.getLevel().getGameTime();this.lifetime=lifetime;
    }
    public static Optional<EnemyImpactAuthority> commission(ServerSubLevel source,
            NativeEnemyHull hull,ServerSubLevel target,Set<UUID> hostile,
            Set<UUID> players,Set<UUID> friendly,int lifetime) {
        if(source==null||hull==null||target==null||hostile==null||players==null
                ||friendly==null||hostile.size()>128||players.size()>128
                ||friendly.size()>128||lifetime<1||lifetime>20
                ||!source.getLevel().getServer().isSameThread())return Optional.empty();
        try {
            if(SpaceflightAuthorization.automationDisabled(source))return Optional.empty();
            var selection=EnemyTargetSelector.choose(source,hull,target,hostile,players,friendly);
            if(selection.isEmpty())return Optional.empty();
            return Optional.of(new EnemyImpactAuthority(source,hull,target,hostile,players,
                    friendly,selection.get(),lifetime));
        }catch(RuntimeException unavailable){return Optional.empty();}
    }
    private Result current() {
        if(!source.getLevel().getServer().isSameThread())
            throw new IllegalStateException("Server-thread impact authority required");
        if(refused!=null)return new Result(false,refused);
        try {
            long now=source.getLevel().getGameTime();
            if(now<created||now-created>=lifetime)return refuse("EXPIRED");
            if(SpaceflightAuthorization.automationDisabled(source))return refuse("DISABLED");
            if(!EnemyHullIdentity.read(source).equals(originalSource))return refuse("SOURCE_CHANGED");
            if(!hull.validate())return refuse("SOURCE_HULL_"+hull.reason());
            var fresh=EnemyTargetSelector.choose(source,hull,target,hostile,players,friendly);
            if(fresh.isEmpty())return refuse("AUTHORITY_LOST");
            var s=fresh.get();
            if(!s.source().equals(admitted.source())||!s.target().equals(admitted.target())
                    ||!s.authority().equals(admitted.authority())
                    ||!s.dimension().equals(admitted.dimension()))return refuse("AUTHORITY_CHANGED");
            return new Result(true,"CURRENT_AUTHORITY_ONLY");
        }catch(RuntimeException unavailable){return refuse("OBSERVATION_UNAVAILABLE");}
    }
    /** Hit coordinates must be the native plot block coordinates from CBC. */
    public Result block(BlockHitResult hit) {
        var valid=current();if(!valid.allowed())return valid;
        if(hit==null)return refuse("INVALID_HIT");
        try {
            var level=source.getLevel();var pos=hit.getBlockPos();
            if(!level.hasChunkAt(pos)||!level.getFluidState(pos).isEmpty())
                return refuse("UNQUALIFIED_HIT");
            var body=Sable.HELPER.getContaining(level,pos);
            if(body!=target||!body.getUniqueId().equals(admitted.target()))
                return refuse("FOREIGN_OR_MAIN_BODY");
            return new Result(true,"CURRENT_TARGET_BODY_ONLY");
        }catch(RuntimeException unavailable){return refuse("OBSERVATION_UNAVAILABLE");}
    }
    /** This ship-only policy never grants entity damage or knockback. */
    public Result entity() {var valid=current();return valid.allowed()?refuse("ENTITY_DAMAGE_UNQUALIFIED"):valid;}
    Result flight(){return current();}
    ServerSubLevel source(){return source;}
    NativeEnemyHull hull(){return hull;}
    boolean targets(ServerSubLevel candidate){return target==candidate;}
    private Result refuse(String why){refused=why;return new Result(false,why);}
}
